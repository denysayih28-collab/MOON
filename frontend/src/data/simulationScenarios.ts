import type { SimulationScenario } from '../types/simulation'

// Educational demo scenarios only.
// These values are illustrative, not clinical thresholds or real astronaut data.
export const simulationScenarios: SimulationScenario[] = [
  {
    id: 'microgravity-adaptation',
    title: 'Microgravity adaptation',
    category: 'Cardiovascular',
    shortDescription: 'Explore how a mission environment can influence cardiovascular observations.',
    context: 'A crew member is adapting to the first days of a long-duration mission in microgravity.',
    durationHours: 24,
    difficulty: 'Intermediate',
    accent: 'mint',
    tags: ['Microgravity', 'Heart rate', 'Adaptation'],
    metrics: [
      { key: 'heartRate', label: 'Heart rate', value: 76, unit: 'bpm', baseline: 68, status: 'Watch', description: 'Illustrative change in resting heart rate.' },
      { key: 'bloodPressure', label: 'Blood pressure', value: 116, unit: 'mmHg systolic', baseline: 118, status: 'Within range', description: 'Systolic value used for this simplified demonstration.' },
      { key: 'oxygenSaturation', label: 'Blood oxygen', value: 98, unit: '%', baseline: 98, status: 'Within range', description: 'Illustrative peripheral oxygen saturation.' },
      { key: 'bodyTemperature', label: 'Body temperature', value: 36.8, unit: '°C', baseline: 36.7, status: 'Within range', description: 'Illustrative body temperature.' },
    ],
  },
  {
    id: 'sleep-restriction',
    title: 'Sleep restriction',
    category: 'Sleep & recovery',
    shortDescription: 'Examine a hypothetical reduction in sleep during a demanding mission schedule.',
    context: 'A crew member has experienced several nights of shortened sleep during a busy operational period.',
    durationHours: 72,
    difficulty: 'Introductory',
    accent: 'violet',
    tags: ['Sleep', 'Recovery', 'Fatigue'],
    metrics: [
      { key: 'sleepDuration', label: 'Sleep duration', value: 5.2, unit: 'hours', baseline: 7.5, status: 'Outside reference', description: 'Illustrative average sleep duration per 24-hour period.' },
      { key: 'heartRate', label: 'Heart rate', value: 74, unit: 'bpm', baseline: 68, status: 'Watch', description: 'Illustrative resting heart rate observation.' },
      { key: 'activityMinutes', label: 'Physical activity', value: 38, unit: 'min/day', baseline: 60, status: 'Watch', description: 'Illustrative daily activity duration.' },
    ],
  },
  {
    id: 'reduced-oxygen-observation',
    title: 'Oxygen level observation',
    category: 'Respiratory',
    shortDescription: 'Follow a hypothetical change in a respiratory monitoring indicator.',
    context: 'The monitoring team reviews a simulated oxygen-saturation trend and its associated observations.',
    durationHours: 12,
    difficulty: 'Advanced',
    accent: 'blue',
    tags: ['SpO₂', 'Monitoring', 'Trend'],
    metrics: [
      { key: 'oxygenSaturation', label: 'Blood oxygen', value: 95, unit: '%', baseline: 98, status: 'Watch', description: 'Illustrative oxygen-saturation value; not a diagnostic threshold.' },
      { key: 'heartRate', label: 'Heart rate', value: 78, unit: 'bpm', baseline: 68, status: 'Watch', description: 'Illustrative heart rate observation.' },
      { key: 'bodyTemperature', label: 'Body temperature', value: 36.9, unit: '°C', baseline: 36.7, status: 'Within range', description: 'Illustrative body temperature.' },
    ],
  },
  {
    id: 'exercise-routine',
    title: 'Exercise routine adjustment',
    category: 'Physical activity',
    shortDescription: 'Explore how a modified exercise routine changes activity observations.',
    context: 'A crew member follows an adjusted exercise schedule as part of a simulated countermeasure plan.',
    durationHours: 48,
    difficulty: 'Intermediate',
    accent: 'orange',
    tags: ['Exercise', 'Countermeasures', 'Activity'],
    metrics: [
      { key: 'activityMinutes', label: 'Physical activity', value: 82, unit: 'min/day', baseline: 60, status: 'Within range', description: 'Illustrative daily activity duration.' },
      { key: 'heartRate', label: 'Heart rate', value: 70, unit: 'bpm', baseline: 68, status: 'Within range', description: 'Illustrative resting heart rate observation.' },
      { key: 'sleepDuration', label: 'Sleep duration', value: 7.1, unit: 'hours', baseline: 7.5, status: 'Within range', description: 'Illustrative average sleep duration per 24-hour period.' },
    ],
  },
]
