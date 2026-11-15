import { useMemo, useState } from 'react'
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import { simulationScenarios } from '../data/simulationScenarios'
import type {
  SimulationMetric,
  SimulationScenario,
} from '../types/simulation'

import './SimulationLab.css'

const formatValue = (metric: SimulationMetric) =>
  `${metric.value} ${metric.unit}`

function buildTimeline(scenario: SimulationScenario) {
  const points = 8

  return Array.from({ length: points }, (_, index) => {
    const progress = index / (points - 1)
    const point: Record<string, string | number> = {
      time: `${Math.round(progress * scenario.durationHours)}h`,
    }

    scenario.metrics.forEach((metric) => {
      const variation = (metric.value - metric.baseline) * progress
      point[metric.key] = Number((metric.baseline + variation).toFixed(1))
    })

    return point
  })
}

function MetricCard({ metric }: { metric: SimulationMetric }) {
  const statusClass =
    metric.status === 'Within range'
      ? 'metric-status-normal'
      : metric.status === 'Watch'
        ? 'metric-status-watch'
        : 'metric-status-outside'

  return (
    <article className="sim-metric-card">
      <div className="sim-metric-top">
        <span>{metric.label}</span>
        <span className={`sim-metric-status ${statusClass}`}>
          {metric.status}
        </span>
      </div>

      <strong className="sim-metric-value">
        {formatValue(metric)}
      </strong>

      <div className="sim-metric-baseline">
        Reference value: {metric.baseline} {metric.unit}
      </div>

      <p>{metric.description}</p>
    </article>
  )
}

export function SimulationLab() {
  const [selectedId, setSelectedId] = useState(
    simulationScenarios[0].id,
  )
  const [hasRun, setHasRun] = useState(false)

  const selectedScenario = simulationScenarios.find(
    (scenario) => scenario.id === selectedId,
  ) ?? simulationScenarios[0]

  const timeline = useMemo(
    () => buildTimeline(selectedScenario),
    [selectedScenario],
  )

  const primaryMetric = selectedScenario.metrics[0]

  const handleScenarioChange = (scenarioId: string) => {
    setSelectedId(scenarioId)
    setHasRun(false)
  }

  return (
    <div className="simulation-page">
      <section className="sim-hero">
        <div>
          <div className="section-kicker">RESEARCH ENVIRONMENT / 01</div>
          <h1>Simulation Lab</h1>
          <p>
            Explore hypothetical mission conditions and observe how
            astronaut health indicators may evolve over time.
          </p>
        </div>

        <div className="sim-environment-badge">
          <span className="tiny-dot" />
          SIMULATION ENVIRONMENT
        </div>
      </section>

      <section className="sim-disclaimer">
        <span className="sim-disclaimer-icon">i</span>
        <p>
          <strong>Educational prototype.</strong> All values and outcomes
          displayed here are illustrative simulations, not real astronaut
          measurements, medical advice, or validated clinical thresholds.
        </p>
      </section>

      <section className="sim-section">
        <div className="sim-section-heading">
          <div>
            <div className="section-kicker">SCENARIO LIBRARY</div>
            <h2>Select a mission scenario</h2>
          </div>
          <span className="sim-count">
            {simulationScenarios.length} SCENARIOS
          </span>
        </div>

        <div className="sim-scenario-grid">
          {simulationScenarios.map((scenario) => (
            <button
              type="button"
              key={scenario.id}
              className={`sim-scenario-card accent-${scenario.accent} ${
                selectedId === scenario.id ? 'is-selected' : ''
              }`}
              onClick={() => handleScenarioChange(scenario.id)}
              aria-pressed={selectedId === scenario.id}
            >
              <div className="sim-card-topline">
                <span className="sim-category">{scenario.category}</span>
                <span className="sim-card-arrow">↗</span>
              </div>

              <h3>{scenario.title}</h3>
              <p>{scenario.shortDescription}</p>

              <div className="sim-card-footer">
                <span>{scenario.durationHours} HOURS</span>
                <span>{scenario.difficulty.toUpperCase()}</span>
              </div>
            </button>
          ))}
        </div>
      </section>

      <section className="sim-workspace">
        <div className="sim-section-heading">
          <div>
            <div className="section-kicker">CONFIGURATION</div>
            <h2>Scenario overview</h2>
          </div>
          <span className="sim-selected-label">SELECTED SCENARIO</span>
        </div>

        <div className="sim-overview-grid">
          <article className="panel sim-context-panel">
            <div className="sim-panel-heading">
              <span className="sim-panel-icon">◈</span>
              <span>MISSION CONTEXT</span>
            </div>

            <h3>{selectedScenario.title}</h3>
            <p className="sim-context-description">
              {selectedScenario.context}
            </p>

            <div className="sim-tag-list">
              {selectedScenario.tags.map((tag) => (
                <span key={tag}>{tag}</span>
              ))}
            </div>

            <div className="sim-context-meta">
              <div>
                <span>Duration</span>
                <strong>{selectedScenario.durationHours} hours</strong>
              </div>
              <div>
                <span>Complexity</span>
                <strong>{selectedScenario.difficulty}</strong>
              </div>
            </div>

            <button
              type="button"
              className="sim-run-button"
              onClick={() => setHasRun(true)}
            >
              <span>▶</span>
              Run simulation
            </button>

            <p className="sim-run-note">
              Local demonstration · No external engine connected
            </p>
          </article>

          <article className="panel sim-metrics-panel">
            <div className="sim-panel-heading">
              <span className="sim-panel-icon">⌁</span>
              <span>MONITORED INDICATORS</span>
              <span className="sim-indicator-count">
                {selectedScenario.metrics.length}
              </span>
            </div>

            <div className="sim-metric-list">
              {selectedScenario.metrics.map((metric) => (
                <MetricCard key={metric.key} metric={metric} />
              ))}
            </div>
          </article>
        </div>
      </section>

      <section className="sim-results-section">
        <div className="sim-section-heading">
          <div>
            <div className="section-kicker">OUTPUT / ANALYSIS</div>
            <h2>Simulation results</h2>
          </div>
          <span className={`sim-result-state ${hasRun ? 'is-complete' : ''}`}>
            <span className="tiny-dot" />
            {hasRun ? 'DEMO COMPLETED' : 'AWAITING EXECUTION'}
          </span>
        </div>

        <article className="panel sim-chart-panel">
          <div className="sim-chart-heading">
            <div>
              <h3>{primaryMetric.label} evolution</h3>
              <p>
                Illustrative progression over {selectedScenario.durationHours}{' '}
                hours
              </p>
            </div>
            <div className="sim-chart-current">
              <strong>{formatValue(primaryMetric)}</strong>
              <span>SCENARIO VALUE</span>
            </div>
          </div>

          <div className="sim-chart">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart
                data={timeline}
                margin={{ top: 12, right: 12, left: -16, bottom: 0 }}
              >
                <defs>
                  <linearGradient
                    id="simulationGradient"
                    x1="0"
                    y1="0"
                    x2="0"
                    y2="1"
                  >
                    <stop
                      offset="0%"
                      stopColor="#55d6bc"
                      stopOpacity={0.28}
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
                  stroke="#82959e"
                  tickLine={false}
                  axisLine={false}
                  tick={{ fontSize: 11 }}
                />

                <YAxis
                  stroke="#82959e"
                  tickLine={false}
                  axisLine={false}
                  tick={{ fontSize: 11 }}
                  domain={['auto', 'auto']}
                />

                <Tooltip
                  contentStyle={{
                    background: '#101b23',
                    border: '1px solid #24343e',
                    borderRadius: '10px',
                    color: '#e8f0f0',
                  }}
                  labelStyle={{ color: '#82959e' }}
                />

                <Area
                  type="monotone"
                  dataKey={primaryMetric.key}
                  stroke="#55d6bc"
                  strokeWidth={2.5}
                  fill="url(#simulationGradient)"
                  activeDot={{ r: 5, fill: '#55d6bc' }}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          <div className="sim-chart-caption">
            <span>
              <span className="sim-legend-dot" />
              {primaryMetric.label}
            </span>
            <span>
              {hasRun
                ? 'Demonstration run generated locally'
                : 'Preview data · Run the scenario to mark it as executed'}
            </span>
          </div>
        </article>

        <div className="sim-bottom-note">
          <span>ⓘ</span>
          <p>
            This visualization uses a simplified interpolation between
            illustrative reference and scenario values. It does not represent
            a physiological prediction.
          </p>
        </div>
      </section>
    </div>
  )
}
