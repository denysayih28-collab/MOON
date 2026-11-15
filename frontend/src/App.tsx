

import type { AstronautProfile } from './types'
import { demoAstronaut } from './data/demoAstronaut'

import {
  Component,
  useEffect,
  useState,
  type ErrorInfo,
  type ReactNode,
} from 'react'


import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { AnatomyViewer } from 'open-anatomy-3d-react'
import 'open-anatomy-3d-react/styles.css'
import './App.css'
import { AstronautAccess, Welcome } from './Welcome'

import {
  measurements,
  indicators,
  alerts,
  recentReadings,
} from './data/demoData'

import { anatomyInfo } from './data/anatomyInfo'

type Page =
  | 'Dashboard'
  | 'Profile'
  | 'Body Explorer'
  | 'Measurements'
  | 'Alerts'

type AnatomyErrorBoundaryProps = {
  children: ReactNode
  fallback: ReactNode
}

type AnatomyErrorBoundaryState = {
  hasError: boolean
}

class AnatomyErrorBoundary extends Component<
  AnatomyErrorBoundaryProps,
  AnatomyErrorBoundaryState
> {
  state: AnatomyErrorBoundaryState = {
    hasError: false,
  }

  static getDerivedStateFromError(): AnatomyErrorBoundaryState {
    return { hasError: true }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('M.O.O.N. — 3D anatomy viewer error:', error, info)
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback
    }

    return this.props.children
  }
}

const navigation: { name: Page; icon: string }[] = [
  { name: 'Dashboard', icon: '▦' },
  { name: 'Profile', icon: '♙' },
  { name: 'Body Explorer', icon: '⌖' },
  { name: 'Measurements', icon: '⌁' },
  { name: 'Alerts', icon: 'bell' },
]

function Sidebar({
  page,
  onNavigate,
  astronaut,
}: {
  page: Page
  onNavigate: (page: Page) => void
  astronaut: AstronautProfile | null
}) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark">
          <span>✳</span>
        </div>
        <div>
          <div className="brand-name">M.O.O.N.</div>
          <div className="brand-caption">HUMAN HEALTH SYSTEMS</div>
        </div>
      </div>

      <div className="workspace-label">WORKSPACE</div>

      <nav className="navigation" aria-label="Main navigation">
        {navigation.map((item) => (
          <button
            key={item.name}
            className={`nav-item ${page === item.name ? 'active' : ''}`}
            onClick={() => onNavigate(item.name)}
            aria-current={page === item.name ? 'page' : undefined}
          >
            <span className="nav-icon">
              {item.icon === 'bell' ? (
                <svg
                  viewBox="0 0 24 24"
                  width="18"
                  height="18"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.8"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  aria-hidden="true"
                >
                  <path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9" />
                  <path d="M10 21h4" />
                </svg>
              ) : (
                item.icon
              )}
            </span>
            <span>{item.name}</span>
            {item.name === 'Alerts' && (
              <span className="nav-count">2</span>
            )}
          </button>
        ))}
      </nav>

      <div className="sidebar-bottom">
  <div className="mission-card">
    <div className="mission-orbit">◉</div>
    <div className="mission-label">ACTIVE MISSION</div>

    <div className="mission-name">
      {astronaut?.mission.name ?? 'No active mission'}
    </div>

    <div className="mission-meta">
      {astronaut ? (
        <>
          <span className="status-dot" />
          Mission day{' '}
          {String(astronaut.mission.missionDay).padStart(3, '0')}
        </>
      ) : (
        'No astronaut selected'
      )}
    </div>

    <div className="mission-progress">
      <span
        style={{
          width: `${astronaut?.mission.progressPercent ?? 0}%`,
        }}
      />
    </div>

    <div className="mission-foot">
      <span>MISSION PROGRESS</span>
      <span>{astronaut?.mission.progressPercent ?? 0}%</span>
    </div>
  </div>

  <div className="profile">
    <div className="profile-avatar">
      {astronaut
        ? astronaut.identity.fullName
            .split(' ')
            .map((part) => part[0])
            .join('')
            .slice(0, 2)
            .toUpperCase()
        : '--'}
    </div>

    <div className="profile-info">
      <strong>
        {astronaut?.identity.fullName ?? 'No profile selected'}
      </strong>
      <span>{astronaut?.identity.role ?? 'Astronaut'}</span>
    </div>

    <span className="profile-menu">···</span>
  </div>
</div>
        <div className="mission-name">
      </div>
    </aside>
  )
}

function Dashboard() {
  return (
    <>
      <section className="welcome-row">
        <div>
          <div className="eyebrow">
            <span className="status-dot" /> MISSION CONTROL / LIVE OVERVIEW
          </div>
          <h1>
            Health overview<span className="title-period">.</span>
          </h1>
          <p className="page-subtitle">
            A clearer picture of crew health, one measurement at a time.
          </p>
        </div>
        <div className="date-chip">
          <span>◷</span> Mission day 012
        </div>
      </section>

      <section className="mission-banner">
        <div className="banner-content">
          <div className="banner-tag">
            <span className="banner-pulse" /> CREW STATUS
          </div>
          <h2>Monitoring in progress.</h2>
          <p>
            Your health indicators and wellness records are gathered in one
            place.
          </p>
          <button
            className="banner-button"
            onClick={() =>
              window.dispatchEvent(
                new CustomEvent('moon-navigate', {
                  detail: 'Body Explorer',
                }),
              )
            }
          >
            Explore body systems <span>↗</span>
          </button>
        </div>

        <div className="orbit-visual" aria-hidden="true">
          <div className="orbit orbit-one" />
          <div className="orbit orbit-two" />
          <div className="orbit orbit-three" />
          <div className="planet">
            <span>✳</span>
          </div>
          <span className="orbit-point point-one" />
          <span className="orbit-point point-two" />
        </div>

        <div className="banner-index">M / 012</div>
      </section>

      <section className="section-heading">
        <div>
          <span className="section-kicker">01 / VITAL SIGNS</span>
          <h2>Health indicators</h2>
        </div>
        <span className="section-note">DEMO DATA · NOT CLINICAL</span>
      </section>

      <section className="indicator-grid">
        {indicators.map((item) => (
          <article className="indicator-card" key={item.key}>
            <div className="indicator-top">
              <span className={`indicator-icon ${item.color}`}>
                {item.icon}
              </span>
              <span className="indicator-status">
                <span className="tiny-dot" />
                {item.status}
              </span>
            </div>

            <div className="indicator-name">{item.name}</div>

            <div className="indicator-value">
              {item.value}
              <span>{item.unit}</span>
            </div>

            <div className="indicator-footer">
              <span>Latest record</span>
              <span className="indicator-arrow">↗</span>
            </div>
          </article>
        ))}
      </section>

      <div className="dashboard-lower">
        <section className="panel chart-panel">
          <div className="panel-header">
            <div>
              <span className="section-kicker">02 / TREND ANALYSIS</span>
              <h2>Heart rate</h2>
            </div>
            <span className="chart-unit">BPM</span>
          </div>

          <div className="chart-summary">
            <strong>
              72 <span>bpm</span>
            </strong>
            <span className="chart-change">Sample measurement</span>
          </div>

          <div className="chart-wrap">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart
                data={measurements}
                margin={{ top: 10, right: 5, left: -22, bottom: 0 }}
              >
                <defs>
                  <linearGradient
                    id="heartGradient"
                    x1="0"
                    y1="0"
                    x2="0"
                    y2="1"
                  >
                    <stop
                      offset="0%"
                      stopColor="#55d6bc"
                      stopOpacity={0.25}
                    />
                    <stop
                      offset="100%"
                      stopColor="#55d6bc"
                      stopOpacity={0}
                    />
                  </linearGradient>
                </defs>

                <CartesianGrid
                  stroke="#24343e"
                  strokeDasharray="3 5"
                  vertical={false}
                />

                <XAxis
                  dataKey="time"
                  tick={{ fill: '#81939d', fontSize: 11 }}
                  axisLine={false}
                  tickLine={false}
                />

                <YAxis
                  domain={[50, 90]}
                  tick={{ fill: '#81939d', fontSize: 11 }}
                  axisLine={false}
                  tickLine={false}
                />

                <Tooltip
                  contentStyle={{
                    background: '#13232c',
                    border: '1px solid #30434d',
                    borderRadius: 10,
                    color: '#f1f7f8',
                  }}
                  labelStyle={{ color: '#a9bbc3' }}
                />

                <Area
                  type="monotone"
                  dataKey="value"
                  stroke="#55d6bc"
                  strokeWidth={2.5}
                  fill="url(#heartGradient)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          <div className="chart-foot">
            <span>
              <i className="legend-dot" /> Simulated heart-rate readings
            </span>
            <span>Sample timeline · 06:00–20:00</span>
          </div>
        </section>

        <section className="panel alerts-panel">
          <div className="panel-header">
            <div>
              <span className="section-kicker">03 / SYSTEM FEED</span>
              <h2>Recent alerts</h2>
            </div>
            <span className="alert-total">02</span>
          </div>

          <div className="alert-list">
            {alerts.map((alert) => (
              <article className="alert-item" key={alert.title}>
                <span className={`alert-symbol ${alert.level}`}>
                  {alert.level === 'info' ? 'i' : '!'}
                </span>
                <div className="alert-copy">
                  <strong>{alert.title}</strong>
                  <p>{alert.detail}</p>
                  <span>{alert.time} · DEMO EVENT</span>
                </div>
              </article>
            ))}
          </div>

          <div className="panel-bottom-note">
            <span className="status-dot" /> No live monitoring connection
          </div>
        </section>
      </div>

      <section className="panel readings-panel">
        <div className="panel-header">
          <div>
            <span className="section-kicker">04 / MEASUREMENT LOG</span>
            <h2>Recent measurements</h2>
          </div>
          <span className="table-count">4 RECORDS</span>
        </div>

        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>INDICATOR</th>
                <th>VALUE</th>
                <th>TIME</th>
                <th>SOURCE</th>
                <th>STATUS</th>
              </tr>
            </thead>
            <tbody>
              {recentReadings.map((reading) => (
                <tr key={reading.indicator}>
                  <td>
                    <span className="table-indicator">
                      {reading.indicator}
                    </span>
                  </td>
                  <td className="table-value">{reading.value}</td>
                  <td>{reading.time}</td>
                  <td>
                    <span className="source-tag">{reading.source}</span>
                  </td>
                  <td>
                    <span className="table-status">
                      <span className="tiny-dot" /> Recorded
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </>
  )
}

function ProfilePage({
  astronaut,
}: {
  astronaut: AstronautProfile
}) {
  const { identity, physical, mission } = astronaut

  return (
    <>
      {/* PAGE HEADER */}
      <section className="welcome-row">
        <div>
          <div className="eyebrow">
            <span className="status-dot" /> CREW DATABASE / ASTRONAUT PROFILE
          </div>

          <h1>
            Astronaut profile<span className="title-period">.</span>
          </h1>

          <p className="page-subtitle">
            Personal information, physical characteristics and mission assignment.
          </p>
        </div>

        <span className="preview-badge">
          DEMO PROFILE · NOT AUTHENTICATED
        </span>
      </section>

      {/* IDENTITY */}
      <section className="section-heading">
        <div>
          <span className="section-kicker">01 / IDENTIFICATION</span>
          <h2>Identity</h2>
        </div>
      </section>

      <section className="panel profile-panel">
        <div className="profile-identity">
          <div className="profile-large-avatar">
            {identity.fullName
              .split(' ')
              .map((part) => part[0])
              .join('')
              .slice(0, 2)
              .toUpperCase()}
          </div>

          <div>
            <h2>{identity.fullName}</h2>
            <p>{identity.role}</p>
            <span className="source-tag">
              ID: {identity.astronautId}
            </span>
          </div>
        </div>

        <div className="profile-fields">
          <div>
            <span>AGE</span>
            <strong>{identity.age} years</strong>
          </div>

          <div>
            <span>GENDER</span>
            <strong>{identity.gender}</strong>
          </div>

          <div>
            <span>NATIONALITY</span>
            <strong>{identity.nationality}</strong>
          </div>
        </div>
      </section>

      {/* PHYSICAL PROFILE */}
      <section className="section-heading">
        <div>
          <span className="section-kicker">02 / BODY METRICS</span>
          <h2>Physical profile</h2>
        </div>
      </section>

      <section className="profile-metrics-grid">
        <article className="indicator-card">
          <div className="indicator-name">Height</div>
          <div className="indicator-value">
            {physical.heightCm}
            <span>cm</span>
          </div>
        </article>

        <article className="indicator-card">
          <div className="indicator-name">Weight</div>
          <div className="indicator-value">
            {physical.weightKg}
            <span>kg</span>
          </div>
        </article>

        <article className="indicator-card">
          <div className="indicator-name">Body Mass Index</div>
          <div className="indicator-value">
            {physical.bmi.toFixed(1)}
            <span>kg/m²</span>
          </div>
        </article>
      </section>

      {/* MISSION INFORMATION */}
      <section className="section-heading">
        <div>
          <span className="section-kicker">03 / FLIGHT RECORD</span>
          <h2>Mission information</h2>
        </div>
      </section>

      <section className="panel profile-panel">
        <div className="panel-header">
          <div>
            <span className="section-kicker">CURRENT MISSION</span>
            <h2>{mission.name}</h2>
          </div>

          <span className="source-tag">{mission.status}</span>
        </div>

        <div className="profile-fields">
          <div>
            <span>MISSION DURATION</span>
            <strong>{mission.durationDays} days</strong>
          </div>

          <div>
            <span>START DATE</span>
            <strong>{mission.startDate}</strong>
          </div>

          <div>
            <span>CURRENT MISSION DAY</span>
            <strong>{mission.missionDay}</strong>
          </div>
        </div>

        <div className="profile-progress-heading">
          <span>MISSION PROGRESS</span>
          <strong>{mission.progressPercent}%</strong>
        </div>

        <div className="mission-progress">
          <span
            style={{
              width: `${mission.progressPercent}%`,
            }}
          />
        </div>
      </section>

    </>
  )
}


function BodyExplorer() {
  const [selectedStructure, setSelectedStructure] = useState<{
    key: string
    label: string
  } | null>(null)
  const [viewerAttempt, setViewerAttempt] = useState(0)

  // La clé utilisée pour chercher une fiche est toujours définie.
  const selectedKey = selectedStructure?.key ?? ''

  // Le cast permet de consulter les clés connues de anatomyInfo
  // sans supposer que toutes les clés du modèle 3D y existent.
  const selectedInfo =
    selectedKey !== ''
      ? anatomyInfo[selectedKey as keyof typeof anatomyInfo]
      : undefined

  // Ne conserver que les indicateurs réellement présents dans demoData.
  const associatedIndicators = (selectedInfo?.relatedIndicators ?? [])
    .map((key) => indicators.find((indicator) => indicator.key === key))
    .filter(
      (indicator): indicator is (typeof indicators)[number] =>
        indicator !== undefined,
    )

  const structureText = [
    selectedStructure?.key ?? '',
    selectedStructure?.label ?? '',
  ]
    .join(' ')
    .toLowerCase()

  const isHeart = /heart|cardiac/.test(structureText)
  const isLung = /lung|pulmonary|bronch/.test(structureText)
  const isBrain = /brain|cerebr|neural/.test(structureText)

  const isBone =
    /humerus|femur|tibia|fibula|radius|ulna|clavicle|scapula|sternum|rib|vertebra|pelvis|pelvic|patella|phalanx|phalanges|metacarpal|metatarsal|carpal|tarsal|mandible|skull|sacrum|coccyx/.test(
      structureText,
    )

  const isMuscle =
    /muscle|quadriceps|hamstring|biceps|triceps|deltoid|pectoral|gluteal|gastrocnemius|soleus|trapezius|latissimus|diaphragm|masseter|sartorius|gracilis|iliopsoas|brachialis|brachioradialis|sternocleidomastoid/.test(
      structureText,
    )

  const selectedIcon = !selectedStructure
    ? '◎'
    : isHeart
      ? '🫀'
      : isLung
        ? '🫁'
        : isBrain
          ? '🧠'
          : isBone
            ? '🦴'
            : isMuscle
              ? '💪'
              : '◇'

  return (
    <>
      <section className="welcome-row">
        <div>
          <div className="eyebrow">
            M.O.O.N. / ANATOMICAL INTERFACE
          </div>
          <h1>
            Body explorer<span className="title-period">.</span>
          </h1>
          <p className="page-subtitle">
            Explore anatomical structures and their associated indicators.
          </p>
        </div>
        <div className="date-chip">INTERACTIVE 3D MODEL</div>
      </section>

      <section className="explorer-layout">
        <div className="panel anatomy-panel">
          <div className="panel-header">
            <div>
              <span className="section-kicker">INTERACTIVE ANATOMY</span>
              <h2>Human body systems</h2>
            </div>
            <span className="anatomy-live-badge">3D MODEL</span>
          </div>

          <div className="anatomy-stage anatomy-stage-3d">
            <AnatomyErrorBoundary
              key={viewerAttempt}
              fallback={
                <div className="anatomy-fallback">
                  <div className="anatomy-fallback-heading">
                    <span className="anatomy-fallback-icon">◇</span>

                    <div>
                      <span className="section-kicker">ALTERNATIVE VIEW</span>
                      <h3>3D visualization unavailable</h3>
                    </div>
                  </div>

                  <p className="anatomy-fallback-description">
                    The anatomical model could not be loaded.
                    You can still explore the available anatomical
                    structures using the list below.
                  </p>

                  <div className="anatomy-fallback-list">
                    {Object.values(anatomyInfo).map((info) => (
                      <button
                        type="button"
                        key={info.key}
                        className={`anatomy-fallback-button ${
                          selectedStructure?.key === info.key ? 'selected' : ''
                        }`}
                        aria-pressed={selectedStructure?.key === info.key}
                        onClick={() => {
                          setSelectedStructure({
                            key: info.key,
                            label: info.name,
                          })
                        }}
                      >
                        <span>{info.name}</span>
                        <span className="anatomy-fallback-arrow">↗</span>
                      </button>
                    ))}
                  </div>

                  <button
                    type="button"
                    className="anatomy-retry-button"
                    onClick={() => setViewerAttempt((attempt) => attempt + 1)}
                  >
                    ↻ Retry 3D viewer
                  </button>
                </div>
              }
            >
              <AnatomyViewer
                defaultSex="male"
                modelUrls={{
                  male: '/models/anatomy-male.glb',
                  female: '/models/anatomy-female.glb',
                }}
                onStructureClick={(key, structure) => {
                  setSelectedStructure({
                    key,
                    label: structure.label,
                  })
                }}
                showSexToggle
                showLayerToggles
                showRotateControl
                showZoomControls
                hoverHint="Click a structure to inspect it"
                className="moon-anatomy-viewer"
              />
            </AnatomyErrorBoundary>
          </div>
          <p className="anatomy-caption">
            Drag to rotate. Use the viewer controls to zoom and explore body
            systems. Select a structure to inspect its available information.
          </p>
        </div>

        <div className="panel region-panel">
          <span className="section-kicker">SELECTED STRUCTURE</span>

          <div className="region-icon" aria-hidden="true">
            {selectedIcon}
          </div>

          <h2>{selectedStructure?.label ?? 'Explore the model'}</h2>

          <p>
            {selectedStructure
              ? `Anatomical structure key: ${selectedStructure.key}`
              : 'Select an anatomical structure in the 3D model to view its details.'}
          </p>

          <div className="region-divider" />

          <span className="section-kicker">ANATOMICAL INFORMATION</span>

          {selectedInfo ? (
            <>
              <div className="region-metric-name">
                {selectedInfo.system}
              </div>

              <p className="region-description">
                {selectedInfo.description}
              </p>

              <div className="region-divider" />

              <span className="section-kicker">SPACEFLIGHT CONTEXT</span>

              <p className="region-description">
                {selectedInfo.spaceflightContext}
              </p>

              <div className="region-divider" />

              <span className="section-kicker">ASSOCIATED INDICATORS</span>

              {associatedIndicators.length > 0 ? (
                associatedIndicators.map((indicator) => (
                  <div
                    className="region-indicator"
                    key={indicator.key}
                  >
                    <div className="region-metric-name">
                      {indicator.name}
                    </div>

                    <div className="region-metric-value">
                      {indicator.value} {indicator.unit}
                    </div>

                    <span className="source-tag">Simulated data</span>
                  </div>
                ))
              ) : (
                <p className="region-description">
                  No directly associated indicator is available in this
                  demonstration.
                </p>
              )}
            </>
          ) : (
            <p className="region-description">
              {selectedStructure
                ? 'No detailed anatomical information is available for this structure yet.'
                : 'Select an anatomical structure in the 3D model to explore its information.'}
            </p>
          )}

          <div className="region-note">
            Demonstration values only. These are not live measurements,
            medical assessments, or clinical recommendations.
          </div>
        </div>
      </section>

      <section className="anatomy-attribution">
        <span className="section-kicker">MODEL ATTRIBUTION</span>
        <p>
          Anatomy models adapted from BodyParts3D © Database Center for Life
          Science (DBCLS), licensed under CC BY 4.0. The female model also
          incorporates Human Reference Atlas organs and a MakeHuman body mesh.
          See the model licenses and full attribution in the project files.
        </p>
      </section>
    </>
  )
}

function MeasurementsPage() {
  return (
    <>
      <section className="welcome-row">
        <div>
          <div className="eyebrow">M.O.O.N. / DATA RECORDS</div>
          <h1>
            Measurements<span className="title-period">.</span>
          </h1>
          <p className="page-subtitle">
            Review recorded indicators and their data provenance.
          </p>
        </div>
        <span className="date-chip">DEMO DATASET</span>
      </section>

      <section className="panel readings-panel standalone-panel">
        <div className="panel-header">
          <div>
            <span className="section-kicker">MEASUREMENT HISTORY</span>
            <h2>Latest records</h2>
          </div>
          <span className="table-count">
            {recentReadings.length} RECORDS
          </span>
        </div>

        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>INDICATOR</th>
                <th>VALUE</th>
                <th>TIME</th>
                <th>SOURCE</th>
                <th>STATUS</th>
              </tr>
            </thead>
            <tbody>
              {recentReadings.map((reading) => (
                <tr key={reading.indicator}>
                  <td>
                    <span className="table-indicator">
                      {reading.indicator}
                    </span>
                  </td>
                  <td className="table-value">{reading.value}</td>
                  <td>{reading.time}</td>
                  <td>
                    <span className="source-tag">{reading.source}</span>
                  </td>
                  <td>
                    <span className="table-status">
                      <span className="tiny-dot" /> Recorded
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <p className="data-disclaimer">
          These records are static demonstration data. They are not connected
          to a live sensor or medical device.
        </p>
      </section>
    </>
  )
}

function AlertsPage() {
  return (
    <>
      <section className="welcome-row">
        <div>
          <div className="eyebrow">M.O.O.N. / RULE-BASED EVENTS</div>
          <h1>
            Alerts<span className="title-period">.</span>
          </h1>
          <p className="page-subtitle">
            Review system messages and their origin.
          </p>
        </div>
        <span className="date-chip">2 DEMO EVENTS</span>
      </section>

      <section className="panel alerts-page-panel">
        <div className="panel-header">
          <div>
            <span className="section-kicker">SYSTEM FEED</span>
            <h2>Recent events</h2>
          </div>
          <span className="preview-badge">DEMONSTRATION</span>
        </div>

        {alerts.map((alert) => (
          <article
            className="alert-item alert-page-item"
            key={alert.title}
          >
            <span className={`alert-symbol ${alert.level}`}>
              {alert.level === 'info' ? 'i' : '!'}
            </span>

            <div className="alert-copy">
              <strong>{alert.title}</strong>
              <p>{alert.detail}</p>
              <span>
                {alert.time} · DEMO EVENT · SOURCE: SIMULATED
              </span>
            </div>

            <span className="source-tag">
              {alert.level === 'info' ? 'Information' : 'Attention'}
            </span>
          </article>
        ))}

        <p className="data-disclaimer">
          These are illustrative interface events, not outputs from the
          backend alert engine. Thresholds and recommendations must be
          validated and documented before use.
        </p>
      </section>
    </>
  )
}

function App() {
  const [entryStage, setEntryStage] = useState<'welcome' | 'access' | 'app'>('welcome')
  const [isDemoPreview, setIsDemoPreview] = useState(false)
  const [page, setPage] = useState<Page>('Dashboard')
  const [selectedAstronaut, setSelectedAstronaut] =
  useState<AstronautProfile | null>(null)

  useEffect(() => {
    const handleNavigation = (event: Event) => {
      const requested = (event as CustomEvent<Page>).detail

      if (navigation.some((item) => item.name === requested)) {
        setPage(requested)
      }
    }

    window.addEventListener('moon-navigate', handleNavigation)

    return () => {
      window.removeEventListener('moon-navigate', handleNavigation)
    }
  }, [])

  if (entryStage === 'welcome') {
    return <Welcome onEnter={() => setEntryStage('access')} />
  }

  if (entryStage === 'access') {
    return (
      <AstronautAccess
        onBack={() => setEntryStage('welcome')}
        onDemoPreview={() => {
          if (import.meta.env.DEV) {
            setSelectedAstronaut(demoAstronaut)
            setIsDemoPreview(true)
            setPage('Dashboard')
            setEntryStage('app')
          }
        }}
      />
    )
  }

  return (
    <div className="app-shell">
      <Sidebar
  page={page}
  onNavigate={setPage}
  astronaut={selectedAstronaut}
/>

      <main className="main-area">
        <header className="topbar">
          <div className="breadcrumb">
            <span>M.O.O.N.</span>
            <span className="breadcrumb-separator">/</span>
            <span>{page}</span>
          </div>

          <div className="topbar-right">
            <span className="sandbox-pill">
              <span className="tiny-dot" />
              {isDemoPreview
                ? 'DEMO PREVIEW · NOT AUTHENTICATED'
                : 'SIMULATION ENVIRONMENT'}
            </span>

            <div className="topbar-divider" />

            <button
              className="icon-button"
              aria-label="Notifications"
              onClick={() => setPage('Alerts')}
            >
              <svg
                viewBox="0 0 24 24"
                width="20"
                height="20"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.8"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                <path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9" />
                <path d="M10 21h4" />
              </svg>
              <span className="notification-dot" />
            </button>
          </div>
        </header>

        <div key={page} className="page-content page-transition">
          {page === 'Dashboard' && <Dashboard />}
          {page === 'Profile' &&
            (selectedAstronaut ? (
              <ProfilePage astronaut={selectedAstronaut} />
            ) : (
              <section className="panel standalone-panel">
                <p>No astronaut profile is currently selected.</p>
              </section>
            ))}
          {page === 'Body Explorer' && <BodyExplorer />}
          {page === 'Measurements' && <MeasurementsPage />}
          {page === 'Alerts' && <AlertsPage />}

          <footer className="app-footer">
            <span>
              M.O.O.N. <span className="footer-separator">/</span> CREW
              HEALTH MONITORING PROTOTYPE
            </span>
            <span>SIMULATED DATA · NOT FOR CLINICAL USE</span>
          </footer>
        </div>
      </main>
    </div>
  )
}

export default App