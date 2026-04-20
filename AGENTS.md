# Student Planner - 项目上下文

## 这是什么项目
AI 驱动的学生时间规划 Agent，核心功能：课前提醒 + AI 任务拆解。  
技术栈：FastAPI + React PWA + 国产 LLM（OpenAI 兼容接口）。

## 关键文件（每次新 session 必读）
1. **本文件** - 项目上下文和当前进度
2. `docs/superpowers/specs/2026-03-29-student-time-planner-design.md` - 完整设计文档
3. `docs/superpowers/plans/2026-03-29-plan1-backend-foundation.md` - Plan 1: 后端基础
4. `docs/superpowers/plans/2026-03-29-plan2-agent-core.md` - Plan 2: Agent 核心
5. `docs/superpowers/plans/2026-03-30-plan3-schedule-import.md` - Plan 3: 课表导入
6. `docs/superpowers/plans/2026-03-30-plan4-memory-context.md` - Plan 4: Memory + 上下文管理
7. `docs/superpowers/plans/2026-03-30-plan5-push-notifications.md` - Plan 5: 推送系统
8. `docs/superpowers/specs/2026-03-30-frontend-pwa-design.md` - 前端 PWA 设计
9. `docs/superpowers/plans/2026-03-30-plan6-frontend-pwa.md` - Plan 6: 前端 PWA
10. `docs/superpowers/plans/2026-04-18-plan7-frontend-ui-modernization.md` - Plan 7: 前端 UI 现代化重构

## 当前进度
- [x] Plan 1: 后端基础（9 个 task）
- [x] Plan 2: Agent 核心（10 个 task）
- [x] Plan 3: 课表导入（9 个 task）
- [x] Plan 4: Memory + 上下文管理（10 个 task）
- [x] Plan 5: 推送系统（9 个 task）
- [x] Plan 6: 前端 PWA（7 个 task）
- [x] Plan 7: 前端 UI 现代化重构（5 个 task）

## 当前正在执行
**下一优先级：Plan 7 已完成，进入视觉细节验收与交互微调（动效节奏、触控命中、文案密度）。**
（每完成一个 task，更新这里指向下一个 task）

## 交接摘要（2026-04-17）
- 已完成：
  - 课表节次追问改为自然聊天输入（无结构化 `data/options` 的 `review` 不再渲染确认卡片按钮）。
  - 修复确认卡片“点确认后看似卡住”：WebSocket 重连新会话时前端清理旧 `pendingAsk`，后端对“非等待态 answer”返回明确错误提示。
  - 修复 `schedule_parser` 回归：不再把 `1-16周` 误当节次覆盖 period；修复空行分块导致“操场”被识别为新课程的问题。
  - 完成附件链路最终回归与真实浏览器 smoke 验证（两图待发送、移除、混发拦截、合法批次发送后进入确认卡片）。
  - 完成日历页联调收口：顶部 `+` 与任务弹层联动、月视图按天选择回填日期并触发当日数据重载。
  - 修复日历“前一天/后一天”日期跳转异常：根因是前端 `toISOString()` 的 UTC 截断导致时区偏移（在 Asia/Shanghai 表现为“后一天不变、前一天跳两天”）；已改为本地日期格式化。
  - 补充日历回归测试：新增 store 层 `shiftDate(+/-1)` 单测与页面层“前一天/后一天仅跳 1 天”集成测试。
  - 开发环境补充 Service Worker 清理：`main.tsx` 在非生产模式自动注销已注册 SW，避免 IAB 命中旧缓存导致“修复未生效”的假象。
- 关键提交：
  - `20f6412` - `feat: stabilize schedule import chat workflow`
  - `99d0ff2` - `fix: restore period parsing and course block grouping`
- 本轮验证：
  - `py -3.12 -m pytest tests/test_schedule_parser.py tests/test_schedule_import_api.py tests/test_agent_loop.py tests/test_chat_ws.py -q`（31 passed）
  - `npm --prefix frontend run test -- src/pages/ChatPage.test.tsx src/stores/chatStore.test.ts`（17 passed）
  - `py -3.12 -m pytest tests/test_schedule_import_api.py tests/test_schedule_integration.py tests/test_chat_ws.py -v`（15 passed）
  - `npm --prefix frontend test -- src/pages/ChatPage.test.tsx src/stores/chatStore.test.ts`（17 passed）
  - `npm --prefix frontend run build`（PASS）
  - `npm --prefix frontend test -- src/App.test.tsx src/stores/calendarStore.test.ts src/pages/CalendarPage.test.tsx`（6 passed）
  - `npm --prefix frontend run build`（PASS）
  - `npm --prefix frontend test -- src/stores/calendarStore.test.ts`（3 passed）
  - `npm --prefix frontend test -- src/pages/CalendarPage.test.tsx src/stores/calendarStore.test.ts`（6 passed）
  - `npm --prefix frontend test -- src/pages/CalendarPage.test.tsx src/App.test.tsx src/stores/calendarStore.test.ts`（9 passed）
  - `npm --prefix frontend run build`（PASS）

## 交接补充（2026-04-18）

### 本 session 已解决
1. 多轮对话“你继续”循环（高优先级）已修复：
   - `list_courses` 压缩结果改为可执行结构化候选，固定前缀 `[TOOL_SUMMARY:list_courses:v1]`。
   - 候选字段包含：`id/name/location/weekday/start_time/end_time`。
   - 采用稳定排序，并显式输出 `truncated/omitted_groups/omitted_options`，避免“前 5 条同名”摘要偏差。
2. 跨轮工具上下文可恢复：
   - 工具结果摘要以 `assistant` 压缩消息持久化（`is_compressed=True`），不直接持久化 `role=tool`，规避 `tool_call_id` 链路风险。
   - 第二轮用户仅输入“你继续”时，可复用上一轮 `list_courses` 候选推进到 `delete_course`。
3. 回归测试已补齐并通过：
   - 新增/更新 `tests/test_context_compressor.py`：结构化摘要字段、稳定排序、截断标记验证。
   - 新增 `tests/test_agent_loop.py::test_continue_message_can_reuse_persisted_list_course_summary`。

### 本 session 关键提交
- `787440c` - `fix: persist actionable course summaries across chat turns`

### 本 session 关键验证
- `py -3.12 -m pytest tests/test_context_compressor.py tests/test_agent_loop.py tests/test_chat_ws.py -q`（18 passed）

## 交接补充（2026-04-18，UI 现代化）

### 本 session 已解决
1. 完成 Plan 7（前端 UI 现代化重构）正式落地：
   - 新增 `docs/superpowers/plans/2026-04-18-plan7-frontend-ui-modernization.md`，并按 step 全量勾选完成。
2. 建立统一前端设计系统底座：
   - `frontend/src/index.css` 重构为 token 驱动（颜色、层级、圆角、阴影、动效时序、字体链）。
   - 增加 `prefers-reduced-motion` 降级策略，保证动效可访问。
3. 全站图标统一矢量化（去 emoji）：
   - 新增 `frontend/src/components/icons.tsx`，并替换 Shell/Chat/Calendar/Me/Courses/Preferences/Notifications 页面图标。
4. 全量页面视觉统一完成：
   - 主三页（聊天/日历/我的）与登录注册、课表管理、偏好设置、通知设置统一到同一视觉语法。
5. TDD 回归约束补齐：
   - 新增 `frontend/src/components/AppShell.test.tsx`（tab 使用 SVG 且不含 emoji）。
   - 补充 `frontend/src/pages/CalendarPage.test.tsx` 的无 emoji 前缀断言。

### 本 session 关键验证
- `npm --prefix D:\student_time_plan\student-planner\frontend test -- src/components/AppShell.test.tsx src/pages/CalendarPage.test.tsx`（5 passed）
- `npm --prefix D:\student_time_plan\student-planner\frontend test -- src/App.test.tsx src/pages/ChatPage.test.tsx src/pages/CalendarPage.test.tsx src/stores/chatStore.test.ts src/stores/calendarStore.test.ts`（27 passed）
- `npm --prefix D:\student_time_plan\student-planner\frontend test`（30 passed）
- `npm --prefix D:\student_time_plan\student-planner\frontend run build`（PASS）

## 规则
- 严格按 plan 文件中的 step 顺序执行
- 每完成一个 step，在 plan 文件中把 `- [ ]` 改成 `- [x]`
- 每完成一个 task，更新本文件的“当前正在执行”
- 遇到问题记录到下面的“问题记录”区域，不要自己改设计
- 测试必须通过才能进入下一个 task

## 问题记录
- 2026-03-29: 当前环境没有 `python` / `py` 命令，执行 Plan 中的 Python、pip、pytest 命令时需要改用 `C:\Users\Chen\anaconda3\python.exe`。
- 2026-03-29: `apply_patch` 在嵌套目录下落盘失败，当前改用 PowerShell 写文件继续执行；未改变设计或文件内容目标。
- 2026-03-29: PowerShell 默认 UTF-8 with BOM 会导致 `pyproject.toml` 解析失败，后续写文件统一改为 UTF-8 without BOM。
- 2026-03-29: `pip install -e '.[dev]'` 在当前 Anaconda 基础环境中提示 `pyasn1-modules` 与新装 `pyasn1` 版本冲突；Plan 1 已完成，但需要后续关注环境隔离。
- 2026-03-29: 首次 commit 因仓库缺少 git 用户名 / 邮箱失败，已在本仓库本地配置 `user.name=Codex`、`user.email=codex@local.invalid` 后继续执行。
- 2026-03-29: FastAPI 当前版本下 `/api/auth/me` 无 token 的默认行为与计划测试预期不一致，已在认证依赖中显式处理为 `403 Not authenticated` 以匹配计划。
- 2026-03-29: `pytest` 生成的 `student-planner/.pytest_cache` 目录当前权限异常，git 状态会给出访问警告，但未阻塞 Plan 1 完成。
- 2026-03-29: 早期用全文替换勾选 commit step 时误影响了后续 task 的同名 step，现已改为按 task 区段精确更新。
- 2026-03-29: Task 4 提交时混入了 `__pycache__/*.pyc` 运行产物，Task 5 已新增 `.gitignore` 并将这些文件从版本控制中移除。
- 2026-03-29: 当前账户对 `D:\student_time_plan` 仓库触发 git `dubious ownership` 安全检查，Task 1 提交前需要先将该目录加入 git `safe.directory`。
- 2026-03-30: Plan 3 / Task 2 添加 `openpyxl` 依赖时，`pip install -e '.[dev]'` 因 setuptools 将 `app` 与 `alembic` 同时识别为顶层包而失败；当前环境已存在 `openpyxl 3.1.2`，因此先继续执行 parser 开发，后续需要单独修复打包配置。
- 2026-04-13: 当前 PATH 上的 `python` 是 3.8.10；项目后端测试改用 `py -3.12 -m pytest`。
- 2026-04-13: Plan 6 / Task 1 使用 `py -3.12 -m pip install -e ".[dev]"` 时仍复现 setuptools 顶层包冲突；已改为安装 pyproject 中的直接依赖和测试依赖来继续验证。
- 2026-04-13: Python 3.12 环境缺少既有 LLM client 所需 `openai` 包，Plan 6 / Task 1 已补入 `pyproject.toml`；`passlib[bcrypt]` 拉到 `bcrypt 5.0.0` 会导致认证测试失败，已 pin `bcrypt<5`。
- 2026-04-17: WebSocket 重连后会话切换导致旧确认卡片可见但 answer 落到新会话，出现“已选择确认但流程不继续”。已修复：前端在 `connected` 事件清理 `pendingAsk`，后端在非等待态收到 `answer` 返回明确错误事件，避免静默吞包。
- 2026-04-17: `schedule_parser` 曾将周次（如 `1-16周`）误识别为节次并覆盖 `period`，且空行分块会把“操场”误识别为独立课程。已修复并补回归测试。
- 2026-04-17: Final regression（`tests/test_schedule_integration.py`）暴露 `DEFAULT_SCHEDULE` 回归导入错误。已在 `app/services/period_converter.py` 恢复兼容常量并补齐分隔符归一化（`—/–/〞/每`）。
- 2026-04-17: 附件 smoke 中，合法课表文件发送后会先进入“节次作息追问”，补全作息后再出现确认卡片；与“自然聊天追问”改造一致，非卡死。
- 2026-04-17: 日历页“单双周显示未生效”问题已在后续 session 修复：日历渲染已结合 `current_semester_start` 计算教学周奇偶，并联合课程周次字段完成过滤。
- 2026-04-18: 多轮聊天在“先 `list_courses` 再精确删除”的场景出现“你继续”循环（重复口头回复、不推进工具）。已修复：`list_courses` 压缩改为可执行候选结构化摘要 + 跨轮持久化工具摘要。
- 2026-04-18: 当前环境 `rg.exe` 无法执行（Access is denied），本 session 前端检索改用 PowerShell `Get-ChildItem + Select-String` 替代；未影响功能设计与实现。

## 当前正在执行（2026-04-18 晚间更新）
**下一优先级：Chat 确认后空窗衔接优化（后续 session 处理）。**
- 目标：在不破坏当前稳定链路的前提下，提升“确认 -> 下一步处理”的连续感。
- 状态：本 session 先冻结在稳定版，延期到后续 session 继续。

## 交接补充（2026-04-18，UI 会话晚间补充）

### 本 session 已完成
1. Chat 输入区交互统一为图标模式：
   - 无输入且无待发附件时右侧显示 `+`（添加附件）。
   - 有文字或附件时右侧切换为发送图标。
   - 语音入口统一为图标按钮（不显示文字标签）。
2. Chat 时间线层级修复：
   - 进度卡与确认卡按 anchor 固定在对应消息后。
   - 新用户消息与后续 assistant 回复均渲染在卡片下方，避免“插入到卡片上方”的错位。
3. 课表确认卡可读性升级：
   - `review` 数据优先渲染为课程卡片和键值详情，不再直接输出 JSON 原文块。
4. “确认卡片/处理卡片”链路稳定化：
   - `ask_user` 到达即收起处理卡并展示确认卡。
   - 已根据用户反馈回退到稳定版本：确认后仅显示“已选择：xxx”，下一次 `tool_call` 才重新出现处理卡。
5. 工程稳定性修复：
   - 修复本地撤销导致 `ChatPage.tsx` 混入冲突标记（`<<<<<<< / ======= / >>>>>>>`）并恢复可编译状态。

### 本 session 关键验证
- `npm --prefix student-planner/frontend test -- src/pages/ChatPage.test.tsx src/stores/chatStore.test.ts`（33 passed）
- `npm --prefix student-planner/frontend test`（51 passed）
- `npm --prefix student-planner/frontend run build`（PASS）

### 留到后续 session 的待解决问题
- Chat 在“点击确认后 -> 后端下一次 tool_call 前”的短暂空窗衔接仍可继续优化。
- 当前决策：保持稳定版（仅显示“已选择”），后续再设计不突兀的轻量过渡方案，避免处理卡与确认卡并存、闪烁或文案突兀。

## 问题记录（晚间补充）
- 2026-04-18: IAB/本地撤销可能把 `ChatPage.tsx` 写入 Git 冲突标记，导致前端编译失败。已恢复并补测通过；后续若再次出现，优先全局检索 `<<<<<<<|=======|>>>>>>>`。
- 2026-04-20: 本地开发库 `student_planner.db` 曾处于旧版 `9f3e2d4a1b6c` schema（`courses.week_type`），与当前代码读取的 `week_pattern/week_text` 不兼容，导致课程查询统一报 `sqlite3.OperationalError: no such column: courses.week_pattern`。已通过兼容迁移 `c4c3b8a92f1d` 修复并执行本地升级。
## Session Update (2026-04-19, Streaming Output)
- Completed chat streaming output end-to-end: backend now emits `text_delta` chunks with a stable `message_id`, and emits final `text` with the same `message_id` for deduplicated finalization.
- Added streaming support in `student-planner/app/agent/llm_client.py` via `chat_completion_stream`.
- Updated `student-planner/app/agent/loop.py` to forward stream deltas and keep a non-stream fallback path.
- Updated frontend reducer in `student-planner/frontend/src/stores/chatStore.ts` to incrementally render streamed assistant content and avoid duplicate final bubbles.
- Added regression tests for streaming behavior:
  - `student-planner/tests/test_agent_loop.py`
  - `student-planner/tests/test_integration.py`
  - `student-planner/tests/test_loop_compression.py`
  - `student-planner/frontend/src/stores/chatStore.test.ts`
  - `student-planner/frontend/src/pages/ChatPage.test.tsx`
- Verification:
  - `py -3.12 -m pytest tests/test_agent_loop.py tests/test_chat_ws.py tests/test_integration.py tests/test_loop_compression.py -q` (12 passed)
  - `npm --prefix frontend test -- src/stores/chatStore.test.ts src/pages/ChatPage.test.tsx` (40 passed)
  - `npm --prefix frontend run build` (PASS)

## Session Update (2026-04-20, Async Image Parse Backend)
- Completed image-upload async backend tasking for schedule screenshots:
  - `POST /api/schedule/upload` now returns immediately for image batches with `status=processing` and a `file_id`.
  - Image OCR parsing moved to background tasks; upload cache now tracks `status/progress/error/source_file_count`.
  - Added status polling endpoint: `GET /api/schedule/upload/{file_id}`.
  - Tool-layer behavior updated: `parse_schedule_image` now returns structured `processing` / `failed` states instead of hard errors when background parse is not ready.
- Added/updated regression coverage:
  - `student-planner/tests/test_schedule_import_api.py`
  - `student-planner/tests/test_schedule_tools.py`
- Verification:
  - `py -3.12 -m pytest tests/test_schedule_import_api.py tests/test_schedule_tools.py -q` (19 passed)
  - `py -3.12 -m pytest tests/test_schedule_upload_cache.py tests/test_schedule_import_api.py tests/test_schedule_tools.py tests/test_schedule_integration.py -q` (23 passed)
  - `py -3.12 -m pytest -q` (178 passed)
  - `npm --prefix frontend test -- src/pages/ChatPage.test.tsx src/stores/chatStore.test.ts` (40 passed)
  - `npm --prefix frontend run build` (PASS)

## Current Focus (after async image parse backend)
- Next priority: frontend polling / WS progress consumption for image parse status, so users can see real backend progress and auto-continue to confirmation without manual retry.

## Session Update (2026-04-20, Calendar Week Filtering + Persistence)
- Completed the previously deferred schedule-import calendar regression fix end-to-end:
  - `frontend/src/stores/calendarStore.ts::eventsForDate` now filters course events by `current_semester_start`, teaching-week index, `week_start/week_end`, and `week_pattern`.
  - `frontend/src/pages/CalendarPage.tsx` month view now uses the same per-date course activation logic, so pre-semester dates and off-parity weeks no longer show course dots.
  - Backend `Course` model/schema/API and agent bulk-import/add-course/list-course paths now persist and return `week_pattern/week_text`.
  - Added Alembic migration `student-planner/alembic/versions/9f3e2d4a1b6c_add_course_week_type.py` to backfill the new course columns into existing environments.
- Added/updated regression coverage:
  - `student-planner/tests/test_courses.py`
  - `student-planner/tests/test_bulk_import.py`
  - `student-planner/frontend/src/stores/calendarStore.test.ts`
  - `student-planner/frontend/src/pages/CalendarPage.test.tsx`
- Verification:
  - `py -3.12 -m pytest tests/test_courses.py tests/test_bulk_import.py -q` (11 passed)
  - `npm --prefix frontend test -- src/stores/calendarStore.test.ts src/pages/CalendarPage.test.tsx` (11 passed)
  - `py -3.12 -m pytest -q` (186 passed)
  - `npm --prefix frontend test` (65 passed)
  - `npm --prefix frontend run build` (PASS)

## Session Update (2026-04-20, Legacy DB Schema Repair)
- Resolved a local runtime regression that appeared immediately after service restart:
  - Calendar page showed `Internal Server Error`.
  - Chat page appeared to hang right after sending a schedule attachment.
- Root cause:
  - The local dev database `student_planner.db` had already been migrated to an older revision `9f3e2d4a1b6c` that created `courses.week_type`.
  - New application code now queries `courses.week_pattern/week_text`, so any course query failed with `sqlite3.OperationalError: no such column: courses.week_pattern`.
  - This broke both calendar course loading and chat system-prompt/context assembly, because chat also reads today's courses before starting the loop.
- Fix:
  - Added compatibility migration `student-planner/alembic/versions/c4c3b8a92f1d_repair_course_week_columns.py`.
  - Migration behavior: detect legacy `week_type`, add missing `week_pattern/week_text`, backfill data, and advance Alembic head.
  - Executed `py -3.12 -m alembic upgrade head` locally.
  - Restarted backend and frontend after migration.
- Verification:
  - Direct SQLAlchemy query against `Course` now succeeds on the local dev DB.
  - `PRAGMA table_info(courses)` confirms `week_pattern` and `week_text` now exist.
  - Backend `/health` returns OK after restart.

## Session Update (2026-04-20, Calendar Desktop Paging Controls)
- Added a temporary desktop-friendly paging entry for calendar verification:
  - top bar now shows previous / next arrow buttons on the calendar page
  - buttons shift by day in day view and by month in month view
  - existing swipe paging remains unchanged for touch devices
- Refactor:
  - moved `shiftMonth` into `student-planner/frontend/src/stores/calendarStore.ts`
  - `student-planner/frontend/src/pages/CalendarPage.tsx` now reuses the shared store paging action
  - `student-planner/frontend/src/components/AppShell.tsx` now owns the desktop paging controls
- Verification:
  - `npm --prefix frontend test -- src/components/AppShell.test.tsx` (6 passed)
  - `npm --prefix frontend test -- src/pages/CalendarPage.test.tsx src/stores/calendarStore.test.ts src/components/AppShell.test.tsx` (17 passed)
  - `npm --prefix frontend run build` (PASS)

## Session Update (2026-04-20, Silent Consecutive ask_user Guardrail)
- Reproduced the user-reported chat regression against the live local backend using the same schedule-image message pattern:
  - after one `ask_user` answer, the model briefly planned another `ask_user` before `save_period_times`
  - the guardrail correctly blocked it, but the backend also emitted the guardrail error event to the frontend
  - result: UI popped “不能连续两次调用 ask_user”，while the agent then continued with valid tools and completed the flow
- Fix:
  - `student-planner/app/agent/guardrails.py` now marks the consecutive-`ask_user` violation as internal-only (`user_visible=False`)
  - `student-planner/app/agent/loop.py` still feeds that violation back into the model as a tool error for self-correction, but no longer forwards it to the user UI
- Regression coverage:
  - added `tests/test_agent_loop.py::test_consecutive_ask_user_violation_is_not_sent_to_user`
- Verification:
  - `py -3.12 -m pytest tests/test_agent_loop.py -q` (7 passed)
  - `py -3.12 -m pytest tests/test_agent_loop.py tests/test_chat_ws.py -q` (11 passed)

## Session Update (2026-04-20, Chat Tool-Preamble Leak + Course-Rename Loop)
- Reproduced the user-reported "infinite loop" on the live local data path:
  - session `78d549b2-8bd1-4467-9ae1-f867fd4ed38c` repeatedly called `list_courses` 9 times from `2026-04-20 09:37:56` through `2026-04-20 09:38:32`
  - the repeated small white bubbles such as "让我先查一下你的课表" were not normal final replies; they were streamed tool-preamble text leaking to the UI before the model switched into a tool call
- Root cause split into two layers:
  - streaming layer bug: `app/agent/loop.py` forwarded `text_delta` chunks immediately, even when the final streamed response actually contained `tool_calls`
  - action-space gap: the agent had `list_courses/add_course/delete_course` but lacked `update_course`, so OCR course-name correction / merge requests could degenerate into repeated `list_courses`
- Fix:
  - `student-planner/app/agent/loop.py` now buffers streamed deltas and only emits them when the final response is a pure text answer; if the final response contains `tool_calls`, the preamble deltas are dropped instead of surfacing to the frontend
  - `student-planner/app/agent/tools.py` added `update_course`
  - `student-planner/app/agent/tool_executor.py` added `_update_course(...)` and registered the handler so existing course records can be renamed / corrected without delete-and-recreate loops
- Regression coverage:
  - added `tests/test_agent_loop.py::test_streaming_preamble_is_not_emitted_when_response_uses_tool_calls`
  - added `tests/test_tool_executor.py::test_update_course_changes_name`
  - updated `tests/test_tools_schema.py` to require `update_course`
- Verification:
  - `py -3.12 -m pytest tests/test_agent_loop.py tests/test_tool_executor.py tests/test_tools_schema.py tests/test_chat_ws.py -q` (20 passed)

## Session Update (2026-04-20, Local Course-Merge Shortcut)
- Follow-up investigation showed that prompt-only guidance was not sufficient for the user-reported "merge duplicate courses into one" path:
  - the old loop could still drift into generic greeting / upload-file guidance instead of operating on the current timetable
  - the problematic path was specifically "current timetable duplicate cleanup", not schedule import
- Fix:
  - `student-planner/app/agent/loop.py` now has a narrow local shortcut for existing-course merge/correction requests
  - when the user says the calendar still shows duplicate courses, the loop now:
    - asks which course names should be merged
    - calls `list_courses` exactly once
    - builds a per-timeslot merge plan
    - asks for final confirmation
    - applies `delete_course` / `update_course` directly without handing this branch back to the LLM
  - merge grouping now preserves distinct `week_pattern/week_start/week_end` variants, so odd/even-week records are not accidentally collapsed into one row
- Prompting support also tightened:
  - `student-planner/Agent.md` now explicitly documents current-timetable correction flows (`list_courses` -> confirm -> `update_course` / `delete_course`)
  - `student-planner/app/agent/tools.py` descriptions now call out existing-course correction use cases
- Regression coverage:
  - added routing-hint tests in `tests/test_agent_loop.py`
  - added `tests/test_agent_loop.py::test_course_merge_shortcut_collapses_duplicate_courses_without_llm`
  - added `tests/test_agent_loop.py::test_course_merge_shortcut_preserves_distinct_week_patterns`
- Verification:
  - `py -3.12 -m pytest tests/test_agent_loop.py -q` (13 passed)
  - `py -3.12 -m pytest tests/test_agent_loop.py tests/test_chat_ws.py tests/test_tool_executor.py tests/test_tools_schema.py -q` (25 passed)
  - live websocket replay against a cloned copy of the real problematic timetable now shows:
    - one initial `ask_user` to identify the duplicate course names
    - exactly one `list_courses`
    - one confirmation step
    - only bounded `delete_course` calls for the matched duplicate records
    - no repeated `list_courses` loop and no leaked tool-preamble bubbles

## Deferred Issue Note (2026-04-20, OCR Review Card Rendering)
- New user-reported frontend regression after uploading schedule images:
  - after image OCR, the assistant bubble rendered a very large mixed block containing the full parsed summary plus inline table-like text
  - the confirmation card below looked malformed / partially desynced from the summary text:
    - summary text said "从图片中识别出的 9 条课程记录" and "去重后共 8 条"
    - the review card header showed `识别课程 8`
    - card content appeared truncated / misaligned, with one item area looking incomplete and the whole interaction visually crowded
  - user screenshot suggests the review payload may be simultaneously rendered in two different formats:
    - once as a long natural-language summary in the assistant bubble
    - once again as the structured `ask_user(type="review")` card
- Status:
  - recorded for next session handoff only; not root-caused or fixed in this session
- Recommended next-session investigation:
  - inspect `frontend/src/pages/ChatPage.tsx` review-card rendering path for schedule-import OCR confirmation
  - compare the actual websocket `ask_user` payload with the assistant text immediately preceding it
  - verify whether OCR confirmation is duplicating both:
    - a human-readable pre-summary message
    - a second structured review dataset containing the same courses
  - confirm whether `count` / displayed card index / deduped course length are derived from the same source object

## Session Update (2026-04-20, OCR Review Card Compaction)
- Resolved the previously deferred schedule-image review card crowding issue on the frontend:
  - `student-planner/frontend/src/pages/ChatPage.tsx` now detects structured schedule review cards that also carry raw OCR table text in `question`
  - when the question includes serialized table markers such as `完整课程列表如下` / `|#|`, the UI now replaces that block with a compact review summary and keeps only the extracted issue note (for example `发现的问题：...`)
  - the structured course cards remain the primary review surface, so the same course list is no longer rendered twice in mixed formats inside one confirmation card
- Styling support:
  - `student-planner/frontend/src/index.css` adds a dedicated compact summary / issue-note block for review cards, with constrained height for long OCR warning text
- Regression coverage:
  - added `frontend/src/pages/ChatPage.test.tsx::hides raw OCR table text when a structured schedule review card is available`
- Verification:
  - `npm --prefix D:\student_time_plan\student-planner\frontend test -- src/pages/ChatPage.test.tsx` (36 passed)
  - `npm --prefix D:\student_time_plan\student-planner\frontend test -- src/pages/ChatPage.test.tsx src/stores/chatStore.test.ts` (46 passed)
  - `npm --prefix D:\student_time_plan\student-planner\frontend run build` (PASS)
