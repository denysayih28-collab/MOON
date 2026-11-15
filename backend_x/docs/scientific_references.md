# Références scientifiques et limites

Valeurs de référence d'un **adulte au repos, sur Terre**. Elles ne remplacent pas les limites
opérationnelles de la NASA en mission, ni un avis médical. M.O.O.N. n'établit aucun diagnostic.

| Indicateur | Norme utilisée | Source |
|---|---|---|
| Pression artérielle | Normale < 120/80 ; élevée 120–129 et < 80 ; stade 1 : 130–139 ou 80–89 ; stade 2 : ≥ 140 ou ≥ 90 ; crise : > 180 et/ou > 120 | American Heart Association, « Understanding Blood Pressure Readings » (heart.org) |
| Pression basse | 90/60 à 120/80 considéré normal | Cleveland Clinic, « Vital signs » |
| Fréquence cardiaque | 60–100 bpm au repos ; tachycardie > 100 ; bradycardie < 60 (normale chez les sportifs) | AHA, Mayo Clinic |
| SpO2 | Normale 95–100 % ; hypoxémie < 90 % | Références cliniques usuelles (MedicineNet, Yale Medicine) |
| Température | Normale 36,1–37,2 °C ; fièvre ≥ 38 °C ; hypothermie < 35 °C | MedlinePlus, Cleveland Clinic, CDC |
| Sommeil | ≥ 7 h par nuit ; ≤ 6 h jugé insuffisant | AASM/SRS, consensus 2015 (SLEEP 38(6):843) |
| Humeur | Aucune norme médicale : score déclaratif 1–5 | — |

## Seuils choisis par l'équipe (`is_demo = true`)
Ce ne sont pas des normes publiées, mais des paliers d'escalade : HR-02 (< 50 bpm), HR-03 (< 40 bpm),
HR-05 (> 130 bpm), TEMP-03 (≥ 39,5 °C), MOOD-01 et MOOD-02. L'API les signale via `rule_is_team_threshold`.

## Limites
- Les normes terrestres peuvent différer en microgravité et en habitacle spatial.
- Pas de seuil individuel : un même seuil s'applique à tous les astronautes (amélioration future : seuils personnalisés).
- La fréquence cardiaque dépend du contexte (effort, stress) : la persistance (2 mesures) réduit les fausses alertes sans les supprimer.
- Données de démonstration fictives, ne provenant d'aucun astronaute réel.
