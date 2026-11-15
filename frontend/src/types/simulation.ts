export type SimulationCategory =
  | 'Cardiovascular'
  | 'Sleep & recovery'
  | 'Respiratory'
  | 'Physical activity'

export type SimulationMetricKey =
  | 'heartRate'
  | 'bloodPressure'
  | 'oxygenSaturation'
  | 'bodyTemperature'
  | 'sleepDuration'
  | 'activityMinutes'

export type SimulationMetric = {
  key: SimulationMetricKey
  label: string
  value: number
  unit: string
  baseline: number
  status: 'Within range' | 'Watch' | 'Outside reference'
  description: string
}

export type SimulationScenario = {
  id: string
  title: string
  category: SimulationCategory
  shortDescription: string
  context: string
  durationHours: number
  difficulty: 'Introductory' | 'Intermediate' | 'Advanced'
  accent: 'mint' | 'blue' | 'violet' | 'orange'
  tags: string[]
  metrics: SimulationMetric[]
}

export type SimulationRun = {
  scenarioId: string
  startedAt: string
  durationHours: number
  metrics: SimulationMetric[]
  summary: string
}
