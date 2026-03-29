from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.context import build_dynamic_context
from app.models.user import User

AGENT_MD_PATH = Path(__file__).parent.parent.parent / "Agent.md"


def load_agent_md() -> str:
    """Load Agent.md static rules."""
    return AGENT_MD_PATH.read_text(encoding="utf-8")


async def build_system_prompt(user: User, db: AsyncSession) -> str:
    """Assemble full system prompt = Agent.md + dynamic context."""
    agent_md = load_agent_md()
    dynamic_context = await build_dynamic_context(user, db)
    return f"{agent_md}\n\n---\n\n## 当前上下文\n\n{dynamic_context}"