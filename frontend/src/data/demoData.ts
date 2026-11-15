import type {
  MeasurementPoint,
  HealthIndicator,
  DemoAlert,
  RecentReading,
} from '../types'

export const measurements: MeasurementPoint[] = [
  { time: '06:00', value: 64 },
  { time: '08:00', value: 68 },
  { time: '10:00', value: 72 },
  { time: '12:00', value: 70 },
  { time: '14:00', value: 75 },
  { time: '16:00', value: 71 },
  { time: '18:00', value: 69 },
  { time: '20:00', value: 67 },
]

export const indicators: HealthIndicator[] = [
  { name: 'Heart rate', key: 'heart_rate', value: '72', unit: 'bpm', status: 'Normal', icon: '♡', color: 'mint' },
  { name: 'Blood pressure', key: 'blood_pressure', value: '118/76', unit: 'mmHg', status: 'Normal', icon: '↕', color: 'blue' },
  { name: 'Oxygen saturation', key: 'spo2', value: '98', unit: '%', status: 'Normal', icon: '◉', color: 'violet' },
  { name: 'Body temperature', key: 'body_temperature', value: '36.8', unit: '°C', status: 'Normal', icon: '♨', color: 'orange' },
  { name: 'Sleep duration', key: 'sleep_duration', value: '7.4', unit: 'hours', status: 'Monitored', icon: '☾', color: 'blue' },
  { name: 'Mood', key: 'mood', value: 'Good', unit: 'self-reported', status: 'Recorded', icon: '☺', color: 'mint' },
]

export const alerts: DemoAlert[] = [
  {
    title: 'Sleep duration recorded',
    detail: 'Sleep measurement received for the previous rest period.',
    time: '08:10',
    level: 'info',
  },
  {
    title: 'Daily wellness check',
    detail: 'Mood entry is available for review.',
    time: '07:45',
    level: 'attention',
  },
]

export const recentReadings: RecentReading[] = [
  { indicator: 'Heart rate', value: '72 bpm', time: '10:00', source: 'Simulated' },
  { indicator: 'Oxygen saturation', value: '98%', time: '09:45', source: 'Simulated' },
  { indicator: 'Body temperature', value: '36.8 °C', time: '09:30', source: 'Simulated' },
  { indicator: 'Blood pressure', value: '118/76 mmHg', time: '09:15', source: 'Simulated' },
]