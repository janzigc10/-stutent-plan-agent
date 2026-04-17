import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select

from app.agent.llm_client import create_llm_client
from app.agent.loop import run_agent_loop
from app.agent.session_lifecycle import end_session
from app.auth.jwt import verify_token
from app.database import get_db
from app.models.user import User

router = APIRouter(tags=["chat"])


@router.websocket("/ws/chat")
async def chat_websocket(websocket: WebSocket) -> None:
    await websocket.accept()
    user_id: str | None = None
    session_id: str | None = None
    llm_client = None

    try:
        auth_message = await websocket.receive_json()
        token = auth_message.get("token")
        if not token:
            await websocket.send_json({"type": "error", "message": "Missing token"})
            await websocket.close()
            return

        user_id = verify_token(token)
        if not user_id:
            await websocket.send_json({"type": "error", "message": "Invalid token"})
            await websocket.close()
            return
    except WebSocketDisconnect:
        return
    except RuntimeError:
        return
    except Exception:
        try:
            await websocket.close()
        except RuntimeError:
            pass
        return

    session_id = str(uuid.uuid4())
    llm_client = create_llm_client()
    try:
        await websocket.send_json({"type": "connected", "session_id": session_id})
    except (RuntimeError, WebSocketDisconnect):
        return

    try:
        while True:
            data = await websocket.receive_json()
            user_message = str(data.get("message") or "").strip()
            if not user_message:
                orphan_answer = str(data.get("answer") or "").strip()
                if orphan_answer:
                    try:
                        await websocket.send_json(
                            {
                                "type": "error",
                                "message": "当前没有待确认的问题，请先发送消息或重新触发操作。",
                            }
                        )
                    except (RuntimeError, WebSocketDisconnect):
                        return
                continue

            async for db in get_db():
                result = await db.execute(select(User).where(User.id == user_id))
                user = result.scalar_one_or_none()
                if user is None:
                    await websocket.send_json({"type": "error", "message": "User not found"})
                    break

                generator = run_agent_loop(user_message, user, session_id, db, llm_client)
                try:
                    event = await generator.__anext__()
                    while True:
                        await websocket.send_json(event)
                        if event["type"] == "ask_user":
                            while True:
                                user_response = await websocket.receive_json()
                                user_answer = (
                                    user_response.get("answer")
                                    or user_response.get("message")
                                    or ""
                                ).strip()
                                if user_answer:
                                    break
                                await websocket.send_json(
                                    {"type": "error", "message": "请输入回复内容后再提交"}
                                )
                            event = await generator.asend(user_answer)
                        elif event["type"] == "done":
                            break
                        else:
                            event = await generator.__anext__()
                except StopAsyncIteration:
                    pass
                except WebSocketDisconnect:
                    return
                except Exception:
                    try:
                        await websocket.send_json(
                            {"type": "error", "message": "聊天暂时不可用，请稍后重试"}
                        )
                    except (RuntimeError, WebSocketDisconnect):
                        return
    except WebSocketDisconnect:
        return
    finally:
        if user_id and session_id and llm_client is not None:
            async for db in get_db():
                await end_session(db, user_id, session_id, llm_client)
