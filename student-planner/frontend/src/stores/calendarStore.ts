import { create } from 'zustand'

import { api } from '../api/client'
import type { Course, Task } from '../types/api'

export type CalendarEvent =
  | { kind: 'course'; id: string; title: string; detail: string; start_time: string; end_time: string; source: Course }
  | { kind: 'task'; id: string; title: string; detail: string; start_time: string; end_time: string; source: Task }

export type CalendarViewMode = 'day' | 'month'

function weekdayForDate(date: string) {
  const day = new Date(`${date}T00:00:00`).getDay()
  return day === 0 ? 7 : day
}

function parseDate(date: string | null | undefined) {
  if (!date) {
    return null
  }
  const parsed = new Date(`${date}T00:00:00`)
  return Number.isNaN(parsed.getTime()) ? null : parsed
}

function teachingWeekForDate(date: string, semesterStart: string | null | undefined) {
  const currentDate = parseDate(date)
  const semesterStartDate = parseDate(semesterStart)
  if (!currentDate || !semesterStartDate) {
    return semesterStartDate ? null : undefined
  }
  const millisecondsPerDay = 24 * 60 * 60 * 1000
  const diffDays = Math.floor((currentDate.getTime() - semesterStartDate.getTime()) / millisecondsPerDay)
  if (diffDays < 0) {
    return null
  }
  return Math.floor(diffDays / 7) + 1
}

export function courseOccursOnDate(course: Course, date: string, semesterStart?: string | null) {
  if (course.weekday !== weekdayForDate(date)) {
    return false
  }

  const teachingWeek = teachingWeekForDate(date, semesterStart)
  if (teachingWeek === null) {
    return false
  }
  if (typeof teachingWeek === 'number') {
    if (teachingWeek < course.week_start || teachingWeek > course.week_end) {
      return false
    }
    if (course.week_pattern === 'odd' && teachingWeek % 2 === 0) {
      return false
    }
    if (course.week_pattern === 'even' && teachingWeek % 2 !== 0) {
      return false
    }
  }

  return true
}

export function eventsForDate(
  date: string,
  courses: Course[],
  tasks: Task[],
  semesterStart?: string | null,
): CalendarEvent[] {
  const weekday = weekdayForDate(date)
  return [
    ...courses
      .filter((course) => course.weekday === weekday && courseOccursOnDate(course, date, semesterStart))
      .map((course) => ({
        kind: 'course' as const,
        id: course.id,
        title: course.name,
        detail: course.location ?? course.teacher ?? '',
        start_time: course.start_time,
        end_time: course.end_time,
        source: course,
      })),
    ...tasks
      .filter((task) => task.scheduled_date === date)
      .map((task) => ({
        kind: 'task' as const,
        id: task.id,
        title: task.title,
        detail: task.description ?? task.status,
        start_time: task.start_time,
        end_time: task.end_time,
        source: task,
      })),
  ].sort((left, right) => left.start_time.localeCompare(right.start_time))
}

function toDateString(date: Date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

interface CalendarStore {
  currentDate: string
  viewMode: CalendarViewMode
  courses: Course[]
  tasks: Task[]
  isLoading: boolean
  error: string | null
  setViewMode: (mode: CalendarViewMode) => void
  setCurrentDate: (date: string) => void
  shiftDate: (days: number) => void
  shiftMonth: (months: number) => void
  load: () => Promise<void>
  completeTask: (taskId: string) => Promise<void>
  createTask: (body: Parameters<typeof api.createTask>[0]) => Promise<void>
}

export const useCalendarStore = create<CalendarStore>((set, get) => ({
  currentDate: toDateString(new Date()),
  viewMode: 'day',
  courses: [],
  tasks: [],
  isLoading: false,
  error: null,
  setViewMode(mode) {
    set({ viewMode: mode })
  },
  setCurrentDate(date) {
    set({ currentDate: date })
  },
  shiftDate(days) {
    const next = new Date(`${get().currentDate}T00:00:00`)
    next.setDate(next.getDate() + days)
    set({ currentDate: toDateString(next) })
    void get().load()
  },
  shiftMonth(months) {
    const [year, month, day] = get().currentDate.split('-').map((value) => Number(value))
    if (!Number.isFinite(year) || !Number.isFinite(month) || !Number.isFinite(day)) {
      return
    }
    const target = new Date(year, month - 1 + months, 1)
    const targetYear = target.getFullYear()
    const targetMonth = target.getMonth()
    const daysInTargetMonth = new Date(targetYear, targetMonth + 1, 0).getDate()
    const nextDay = Math.min(day, daysInTargetMonth)
    set({ currentDate: toDateString(new Date(targetYear, targetMonth, nextDay)) })
    void get().load()
  },
  async load() {
    set({ isLoading: true, error: null })
    try {
      const { currentDate } = get()
      const [courses, tasks] = await Promise.all([api.listCourses(), api.listTasks(currentDate, currentDate)])
      set({ courses, tasks, isLoading: false })
    } catch (error) {
      set({ error: error instanceof Error ? error.message : '加载日历失败', isLoading: false })
    }
  },
  async completeTask(taskId) {
    const updated = await api.updateTask(taskId, { status: 'completed' })
    set((state) => ({ tasks: state.tasks.map((task) => (task.id === taskId ? updated : task)) }))
  },
  async createTask(body) {
    try {
      const task = await api.createTask(body)
      set((state) => ({ tasks: [...state.tasks, task], error: null }))
    } catch (error) {
      set({ error: error instanceof Error ? error.message : '新增任务失败' })
    }
  },
}))
