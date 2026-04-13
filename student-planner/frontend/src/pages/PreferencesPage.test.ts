import { describe, expect, it } from 'vitest'

import { parsePeriodSchedule } from './PreferencesPage'

describe('parsePeriodSchedule', () => {
  it('parses one period range per line', () => {
    expect(parsePeriodSchedule('1-2=08:20-10:00\n3-4=10:20-12:00')).toEqual({
      '1-2': { start: '08:20', end: '10:00' },
      '3-4': { start: '10:20', end: '12:00' },
    })
  })
})
