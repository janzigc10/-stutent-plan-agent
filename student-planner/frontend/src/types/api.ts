export interface User {
  id: string
  username: string
  preferences: Record<string, unknown> | null
  current_semester_start: string | null
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface Course {
  id: string
  user_id: string
  name: string
  teacher: string | null
  location: string | null
  weekday: number
  start_time: string
  end_time: string
  week_start: number
  week_end: number
  week_pattern?: 'all' | 'odd' | 'even'
  week_text?: string | null
}

export interface Task {
  id: string
  user_id: string
  exam_id: string | null
  title: string
  description: string | null
  scheduled_date: string
  start_time: string
  end_time: string
  status: 'pending' | 'completed' | 'skipped'
}

export interface ScheduleUploadResponse {
  file_id: string
  kind: 'spreadsheet' | 'image'
  status?: 'processing' | 'parsed'
  count: number
  source_file_count: number
  courses: unknown[]
}

export interface ScheduleUploadStatusResponse {
  file_id: string
  kind: 'spreadsheet' | 'image'
  status: 'QUEUED' | 'PARSING' | 'PARSED' | 'FAILED' | 'READY' | 'NEED_PERIOD_TIMES'
  progress: number
  error: string | null
  courses: unknown[]
  count: number
  missing_periods: string[]
  missing_semester_fields?: string[]
  source_file_count: number
}
