# Chat Schedule Attachments Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make chat schedule attachments usable end to end: select first, send later, support up to three same-type files, and return an import confirmation card.

**Architecture:** Keep the existing HTTP upload endpoint and Agent parsing tools, then add a lightweight attachment-draft layer in the chat composer. The backend expands `/api/schedule/upload` to validate and merge multi-image uploads into a single cached `file_id`, while the frontend uploads only on send and reuses the current WebSocket text-trigger flow.

**Tech Stack:** FastAPI, pytest, httpx, React 18, TypeScript, Zustand, Vitest, Testing Library

---

## File Structure

- Modify: `student-planner/app/routers/schedule_import.py` - accept multiple uploaded files, validate type/count rules, merge multi-image parse results, return one upload payload.
- Modify: `student-planner/tests/test_schedule_import_api.py` - cover multi-image success and invalid mixed/oversized uploads.
- Modify: `student-planner/tests/test_schedule_integration.py` - keep integration coverage aligned with the upload response contract.
- Modify: `student-planner/frontend/src/api/client.ts` - send multiple `file` parts and expose a typed upload response.
- Modify: `student-planner/frontend/src/types/api.ts` - add the schedule upload response type used by the chat page.
- Create: `student-planner/frontend/src/pages/ChatPage.test.tsx` - verify attachment tray behavior, validation, send orchestration, and upload failure retention.
- Modify: `student-planner/frontend/src/pages/ChatPage.tsx` - add local pending-attachment state, tray UI, validation, and send-time upload orchestration.
- Modify: `AGENTS.md` - keep “当前正在执行” aligned with the next task while implementing this plan.

### Task 1: Backend Multi-File Schedule Upload

**Files:**
- Modify: `student-planner/tests/test_schedule_import_api.py`
- Modify: `student-planner/tests/test_schedule_integration.py`
- Modify: `student-planner/app/routers/schedule_import.py`
- Modify: `AGENTS.md`

- [ ] **Step 1: Write the failing backend tests for batched image uploads and invalid combinations**

Add focused cases to `student-planner/tests/test_schedule_import_api.py`:

```python
@pytest.mark.asyncio
async def test_upload_multiple_images_returns_single_file_id(auth_client, monkeypatch) -> None:
    async def fake_parse_schedule_image(file_bytes: bytes, mime_type: str):
        return [RawCourse(name=f"课程-{len(file_bytes)}", teacher=None, location=None, weekday=1, period="1-2", week_start=1, week_end=16)]

    monkeypatch.setattr("app.agent.schedule_ocr.parse_schedule_image", fake_parse_schedule_image)

    response = await auth_client.post(
        "/api/schedule/upload",
        files=[
            ("file", ("a.png", io.BytesIO(b"img-a"), "image/png")),
            ("file", ("b.png", io.BytesIO(b"img-b"), "image/png")),
        ],
    )

    assert response.status_code == 200
    data = response.json()
    assert data["kind"] == "image"
    assert data["source_file_count"] == 2
    assert data["file_id"]
```

Add rejection coverage for:

- mixed image + spreadsheet uploads
- more than 3 image files
- more than 1 spreadsheet file

Update `student-planner/tests/test_schedule_integration.py` only if the response contract assertions need `source_file_count`.

- [ ] **Step 2: Run the backend upload tests to verify they fail**

Run from `D:\student_time_plan\student-planner`:

```bash
py -3.12 -m pytest tests/test_schedule_import_api.py tests/test_schedule_integration.py -v
```

Expected: FAIL because `/api/schedule/upload` currently accepts only a single `UploadFile` and cannot validate or merge batches.

- [ ] **Step 3: Implement the minimal backend batching logic**

Update `student-planner/app/routers/schedule_import.py` to accept `list[UploadFile]` under the existing `file` field name and centralize validation:

```python
@router.post("/upload")
async def upload_schedule(
    file: list[UploadFile],
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    del db
    uploads = list(file)
    if not uploads:
        raise HTTPException(status_code=400, detail="至少上传一个课表文件。")

    kinds = {_classify_upload(upload.content_type or "") for upload in uploads}
    if len(kinds) != 1:
        raise HTTPException(status_code=400, detail="图片和表格不能混合上传。")

    kind = kinds.pop()
    if kind == "image" and len(uploads) > 3:
        raise HTTPException(status_code=400, detail="课表图片最多上传 3 张。")
    if kind == "spreadsheet" and len(uploads) > 1:
        raise HTTPException(status_code=400, detail="课表文件一次只能上传 1 个。")
```

Then parse each upload, merge image results into one `course_dicts` list, and return:

```python
return {
    "file_id": file_id,
    "kind": kind,
    "courses": course_dicts,
    "count": len(course_dicts),
    "source_file_count": len(uploads),
}
```

Keep the cache contract unchanged: one `file_id`, one merged course list.

- [ ] **Step 4: Run the backend upload tests again to verify they pass**

Run:

```bash
py -3.12 -m pytest tests/test_schedule_import_api.py tests/test_schedule_integration.py -v
```

Expected: PASS for single spreadsheet upload, multi-image upload, and all validation cases.

- [ ] **Step 5: Update `AGENTS.md` to point to Task 2 and commit**

Before committing, update `AGENTS.md` “当前正在执行” to indicate frontend chat attachment tray work is next.

```bash
git add AGENTS.md tests/test_schedule_import_api.py tests/test_schedule_integration.py app/routers/schedule_import.py
git commit -m "feat: support batched schedule uploads"
```

### Task 2: Chat Attachment Draft UI And Validation

**Files:**
- Create: `student-planner/frontend/src/pages/ChatPage.test.tsx`
- Modify: `student-planner/frontend/src/pages/ChatPage.tsx`
- Modify: `AGENTS.md`

- [ ] **Step 1: Write the failing chat page tests for attachment drafting**

Create `student-planner/frontend/src/pages/ChatPage.test.tsx` with focused UI tests. Mock `WebSocket`, `api.uploadSchedule`, and stored auth token so the page can render without the full app shell.

Add coverage like:

```tsx
it('shows selected image attachments in the pending tray before send', async () => {
  render(<ChatPage />)

  const input = screen.getByLabelText('上传课表')
  await user.upload(input, [
    new File(['img-a'], 'a.png', { type: 'image/png' }),
    new File(['img-b'], 'b.png', { type: 'image/png' }),
  ])

  expect(screen.getByText('待发送附件 2')).toBeInTheDocument()
  expect(screen.getByText('a.png')).toBeInTheDocument()
  expect(screen.getByText('b.png')).toBeInTheDocument()
})
```

Also add tests for:

- blocking mixed spreadsheet + image selection
- blocking more than 3 images
- removing a selected attachment from the tray

- [ ] **Step 2: Run the frontend chat page test to verify it fails**

Run from `D:\student_time_plan\student-planner\frontend`:

```bash
npm test -- src/pages/ChatPage.test.tsx
```

Expected: FAIL because `ChatPage.tsx` currently uploads immediately and has no pending attachment tray.

- [ ] **Step 3: Implement the minimal attachment draft state and tray UI**

In `student-planner/frontend/src/pages/ChatPage.tsx`, keep attachment state local to the page:

```tsx
type AttachmentKind = 'image' | 'spreadsheet'

interface PendingAttachment {
  id: string
  file: File
  name: string
  kind: AttachmentKind
}

const [pendingAttachments, setPendingAttachments] = useState<PendingAttachment[]>([])
```

Add helpers that:

- classify file type from `file.type` / filename
- reject mixed kinds
- reject more than three images
- reject more than one spreadsheet
- remove individual pending attachments

Render a simple tray above the form controls, for example:

```tsx
{pendingAttachments.length > 0 ? (
  <section aria-label="待发送附件">
    <p>{`待发送附件 ${pendingAttachments.length}`}</p>
    {pendingAttachments.map((attachment) => (
      <button key={attachment.id} type="button" onClick={() => removeAttachment(attachment.id)}>
        {attachment.name} 删除
      </button>
    ))}
  </section>
) : null}
```

Do not call `api.uploadSchedule` in the input `onChange` handler anymore.

- [ ] **Step 4: Run the frontend chat page test again to verify it passes**

Run:

```bash
npm test -- src/pages/ChatPage.test.tsx
```

Expected: PASS for tray rendering, validation, and removal behavior.

- [ ] **Step 5: Update `AGENTS.md` to point to Task 3 and commit**

Before committing, update `AGENTS.md` “当前正在执行” to indicate send-time upload orchestration is next.

```bash
git add AGENTS.md frontend/src/pages/ChatPage.test.tsx frontend/src/pages/ChatPage.tsx
git commit -m "feat: add chat attachment draft tray"
```

### Task 3: Send-Time Upload Orchestration And Chat Trigger

**Files:**
- Modify: `student-planner/frontend/src/pages/ChatPage.test.tsx`
- Modify: `student-planner/frontend/src/pages/ChatPage.tsx`
- Modify: `student-planner/frontend/src/api/client.ts`
- Modify: `student-planner/frontend/src/types/api.ts`
- Modify: `AGENTS.md`

- [ ] **Step 1: Extend the failing chat page tests to cover send orchestration**

Add send-flow tests to `student-planner/frontend/src/pages/ChatPage.test.tsx`:

```tsx
it('uploads pending attachments only when send is pressed and then sends a parse prompt over websocket', async () => {
  api.uploadSchedule = vi.fn().mockResolvedValue({
    file_id: 'file-1',
    kind: 'image',
    count: 6,
    source_file_count: 2,
    courses: [],
  })

  render(<ChatPage />)
  await user.upload(screen.getByLabelText('上传课表'), [
    new File(['img-a'], 'a.png', { type: 'image/png' }),
    new File(['img-b'], 'b.png', { type: 'image/png' }),
  ])
  await user.click(screen.getByRole('button', { name: '发送' }))

  expect(api.uploadSchedule).toHaveBeenCalledTimes(1)
  expect(mockSocket.send).toHaveBeenCalledWith(
    JSON.stringify({ message: '我上传了课表图片 file_id=file-1，请解析并展示确认卡片。' }),
  )
})
```

Add one more test proving upload failure keeps the tray contents intact.

- [ ] **Step 2: Run the send-flow frontend test to verify it fails**

Run:

```bash
npm test -- src/pages/ChatPage.test.tsx
```

Expected: FAIL because the current API client accepts only one `File`, and `submit()` ignores pending attachments.

- [ ] **Step 3: Update the upload client contract**

In `student-planner/frontend/src/types/api.ts`, add a shared response type:

```ts
export interface ScheduleUploadResponse {
  file_id: string
  kind: 'spreadsheet' | 'image'
  count: number
  source_file_count: number
  courses: unknown[]
}
```

In `student-planner/frontend/src/api/client.ts`, change the client to accept multiple files:

```ts
uploadSchedule(files: File[]) {
  const formData = new FormData()
  for (const file of files) {
    formData.append('file', file)
  }
  return request<ScheduleUploadResponse>('/api/schedule/upload', {
    method: 'POST',
    body: formData,
  })
}
```

- [ ] **Step 4: Implement send-time upload and parse prompting in `ChatPage.tsx`**

Refactor `submit()` so it can send text-only messages, attachment-only messages, or both. When attachments exist:

1. call `api.uploadSchedule(pendingAttachments.map((item) => item.file))`
2. append a friendly user message such as `已发送 2 张课表图片`
3. send the stable parse prompt over WebSocket:

```tsx
const prompt =
  result.kind === 'image'
    ? `我上传了课表图片 file_id=${result.file_id}，请解析并展示确认卡片。`
    : `我上传了课表文件 file_id=${result.file_id}，请解析并展示确认卡片。`
sendJson(socketRef, { message: prompt })
```

4. clear `pendingAttachments` only after the upload promise resolves
5. leave attachments untouched and surface an error if the upload request rejects

If text and attachments are both present, send the text message first only if product intent still requires it; otherwise keep this scope tight and block mixed text + attachment sends with a clear message.

- [ ] **Step 5: Run targeted frontend verification**

Run:

```bash
npm test -- src/pages/ChatPage.test.tsx
npm test -- src/stores/chatStore.test.ts
npm run typecheck
```

Expected: PASS, and the chat page compiles with the new upload response type.

- [ ] **Step 6: Update `AGENTS.md` to point to Task 4 and commit**

Before committing, update `AGENTS.md` “当前正在执行” to indicate final regression and manual verification are next.

```bash
git add AGENTS.md frontend/src/pages/ChatPage.test.tsx frontend/src/pages/ChatPage.tsx frontend/src/api/client.ts frontend/src/types/api.ts
git commit -m "feat: send schedule attachments through chat"
```

### Task 4: Final Regression And Handoff

**Files:**
- Modify: `AGENTS.md`

- [ ] **Step 1: Run backend regression for upload and chat-adjacent behavior**

Run from `D:\student_time_plan\student-planner`:

```bash
py -3.12 -m pytest tests/test_schedule_import_api.py tests/test_schedule_integration.py tests/test_chat_ws.py -v
```

Expected: PASS.

- [ ] **Step 2: Run frontend regression and production build**

Run from `D:\student_time_plan\student-planner\frontend`:

```bash
npm test -- src/pages/ChatPage.test.tsx src/stores/chatStore.test.ts
npm run build
```

Expected: PASS.

- [ ] **Step 3: Manually verify the chat attachment flow**

With the backend and frontend running:

1. choose two schedule screenshots and confirm they appear in the pending tray
2. remove one screenshot and confirm the tray updates
3. send a valid attachment batch and verify an `ask_user` confirmation card appears
4. try a mixed image + spreadsheet selection and confirm the UI blocks it before upload

Record any mismatch in `AGENTS.md` “问题记录” instead of changing scope.

- [ ] **Step 4: Update `AGENTS.md` with the next active issue and commit**

Set “当前正在执行” to the next highest-priority unresolved item after attachment upload, then commit the verification state.

```bash
git add AGENTS.md
git commit -m "chore: verify chat attachment import flow"
```
