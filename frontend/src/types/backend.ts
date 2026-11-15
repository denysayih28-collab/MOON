/**
 * Types correspondant aux réponses réelles de backend_x.
 * Ces types restent distincts des données de démonstration.
 */

export type MissionApiProfile = {
  id: number
  name: string
  description: string
  start_date: string
  planned_days: number
}

export type AstronautApiProfile = {
  id: number
  access_code: string
  first_name: string
  last_name: string
  mission: MissionApiProfile
  mission_day: number | null
}
