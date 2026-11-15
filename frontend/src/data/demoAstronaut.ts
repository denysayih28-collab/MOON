import type { AstronautProfile } from '../types'
import { indicators, recentReadings } from './demoData'

export const demoAstronaut: AstronautProfile = {
  identity: {
    astronautId: 'AST-001',
    fullName: 'Maya Chen',
    age: 34,
    gender: 'Female',
    nationality: 'Canadian',
    role: 'Research astronaut',
  },

  physical: {
    heightCm: 168,
    weightKg: 62,
    bmi: 21.97,
  },

  mission: {
    name: 'Orbital Research',
    durationDays: 38,
    status: 'Active',
    startDate: '2026-11-03',
    missionDay: 12,
    progressPercent: 32,
  },

  healthOverview: {
    indicators,
    recentReadings,
  },
}
