export type MeasurementPoint = {
  time: string
  value: number
}

export type HealthIndicator = {
  name: string
  key: string
  value: string
  unit: string
  status: 'Normal' | 'Monitored' | 'Recorded'
  icon: string
  color: 'mint' | 'blue' | 'violet' | 'orange'
}

export type DemoAlert = {
  title: string
  detail: string
  time: string
  level: 'info' | 'attention'
}

export type RecentReading = {
  indicator: string
  value: string
  time: string
  source: string
}

export type AstronautProfile = {
  identity: {
    astronautId: string
    fullName: string
    age: number
    gender: string
    nationality: string
    role: string
  }

  physical: {
    heightCm: number
    weightKg: number
    bmi: number
  }

  mission: {
    name: string
    durationDays: number
    status: 'Planned' | 'Active' | 'Completed'
    startDate: string
    missionDay: number
    progressPercent: number
  }

  healthOverview: {
    indicators: HealthIndicator[]
    recentReadings: RecentReading[]
  }
}
