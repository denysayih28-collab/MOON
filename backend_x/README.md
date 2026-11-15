# M.O.O.N. — Backend

FastAPI + SQLAlchemy + SQLite. Données de démonstration **fictives** (source `simulated`).

## Lancer
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload        # crée moon.db et le remplit au premier démarrage
python -m pytest                     # tests
python -m app.seed                   # (optionnel) affiche les 5 identifiants fictifs
```
Documentation interactive de l'API : http://localhost:8000/docs

## Accès astronaute
Pas de mot de passe : `POST /api/access {"code": "AST-4K7Q2X"}` renvoie le profil.
Les autres routes prennent `astronaut_code` en paramètre et ne renvoient que les données de cet astronaute.

## Endpoints
| Méthode | Route | Rôle |
|---|---|---|
| GET | /api/health | Vérifier le backend |
| POST | /api/access | Entrer avec son ID |
| GET | /api/indicators | Catalogue (unité, plage normale, source de la norme) |
| GET | /api/measurements/latest?astronaut_code= | Dernière valeur de chaque indicateur |
| GET | /api/measurements?astronaut_code=&indicator=&since=&until= | Historique |
| POST | /api/measurements | Enregistrer → `{measurement, alerts[]}` |
| GET | /api/alerts?astronaut_code=&status=&level= | Historique des alertes |
| GET/PATCH | /api/alerts/{id}?astronaut_code= | Détail / changer l'état |

## Simulation (mode opérateur)
En-tête obligatoire `X-Operator-Key` (défaut `moon-operator`, variable `MOON_OPERATOR_KEY`).

| Méthode | Route | Rôle |
|---|---|---|
| GET | /api/simulation/astronauts | Liste des astronautes et de leurs ID |
| GET | /api/simulation/scenarios | 10 scénarios prédéfinis |
| POST | /api/simulation/scenarios/{nom} `{astronaut_code}` | Lance un scénario |
| POST | /api/simulation/measurements `{astronaut_code, indicator, value, repeat}` | Valeur libre |
| POST | /api/simulation/reset `{astronaut_code?}` | Retire les mesures et alertes simulées |

Une alerte active n'est pas recréée pour la même règle : faire un `reset` avant de rejouer un scénario.

## Alertes
- Règles stockées en base (`alert_rules`), définies dans `app/catalog.py`.
- Niveaux : `information`, `attention`, `high_priority` (catégories du prototype, pas des niveaux médicaux).
- Persistance : les règles « attention » exigent 2 mesures consécutives, les « priorité élevée » 1 seule.
- Sources et limites : `docs/scientific_references.md`.
