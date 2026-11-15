export type AnatomyInfo = {
  key: string
  name: string
  system: string
  description: string
  spaceflightContext: string
  relatedIndicators: string[]
}

export const anatomyInfo: Record<string, AnatomyInfo> = {
  heart: {
    key: 'heart',
    name: 'Heart',
    system: 'Cardiovascular system',
    description:
      'The heart circulates blood throughout the body, delivering oxygen and nutrients to tissues.',
    spaceflightContext:
      'Spaceflight can affect cardiovascular adaptation. The effects depend on mission conditions and individual factors.',
    relatedIndicators: ['heart_rate', 'blood_pressure'],
  },

  lung_l: {
    key: 'lung_l',
    name: 'Left lung',
    system: 'Respiratory system',
    description:
      'The left lung participates in gas exchange, allowing oxygen to enter the blood and carbon dioxide to be removed.',
    spaceflightContext:
      'Respiratory measurements can contribute to astronaut health monitoring, but the available indicators do not directly assess the complete function of a lung.',
    relatedIndicators: ['spo2'],
  },

  lung_r: {
    key: 'lung_r',
    name: 'Right lung',
    system: 'Respiratory system',
    description:
      'The right lung participates in gas exchange, allowing oxygen to enter the blood and carbon dioxide to be removed.',
    spaceflightContext:
      'Respiratory measurements can contribute to astronaut health monitoring, but the available indicators do not directly assess the complete function of a lung.',
    relatedIndicators: ['spo2'],
  },

  brain: {
    key: 'brain',
    name: 'Brain',
    system: 'Nervous system',
    description:
      'The brain processes sensory information and coordinates cognitive, behavioral, and physiological functions.',
    spaceflightContext:
      'Sleep, mood, and other observations can help document astronaut well-being. They do not directly measure brain function.',
    relatedIndicators: ['sleep_duration', 'mood'],
  },

  brainstem: {
    key: 'brainstem',
    name: 'Brainstem',
    system: 'Nervous system',
    description:
      'The brainstem connects major parts of the brain with the spinal cord and participates in essential autonomic functions.',
    spaceflightContext:
      'The current demonstration does not include a measurement that directly evaluates brainstem function.',
    relatedIndicators: [],
  },

  liver: {
    key: 'liver',
    name: 'Liver',
    system: 'Digestive and metabolic systems',
    description:
      'The liver contributes to metabolism, nutrient processing, and the production and processing of various substances in the body.',
    spaceflightContext:
      'The current demonstration does not include a liver-specific measurement.',
    relatedIndicators: [],
  },

  diaphragm: {
    key: 'diaphragm',
    name: 'Diaphragm',
    system: 'Muscular and respiratory systems',
    description:
      'The diaphragm is a major muscle involved in breathing.',
    spaceflightContext:
      'The current demonstration does not directly measure diaphragm activity or respiratory muscle function.',
    relatedIndicators: [],
  },
}
