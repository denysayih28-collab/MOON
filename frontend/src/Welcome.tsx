import { useState, type FormEvent } from 'react'
import moonLogo from './assets/moon-logo.png'
import './Welcome.css'

type WelcomeProps = {
  onEnter: () => void
}

type AstronautAccessProps = {
  onBack: () => void
  onDemoPreview: () => void
}

export function Welcome({ onEnter }: WelcomeProps) {
  return (
    <main className="welcome-screen">
      <div className="welcome-orbit welcome-orbit-one" />
      <div className="welcome-orbit welcome-orbit-two" />

      <header className="welcome-header">
        <span className="welcome-wordmark">M.O.O.N.</span>
        <span className="demo-badge">
          <span className="demo-badge-dot" />
          DEMO ENVIRONMENT
        </span>
      </header>

      <section className="welcome-content">
        <div className="welcome-logo-frame">
          <img
            className="welcome-logo"
            src={moonLogo}
            alt="M.O.O.N. — astronaut health monitoring"
          />
        </div>

        <p className="welcome-eyebrow">HUMAN RESEARCH &amp; HEALTH MONITORING</p>

        <h1>
          Beyond Earth.
          <br />
          <span>Closer to Human.</span>
        </h1>

        <p className="welcome-description">
          A monitoring environment designed to explore astronaut health,
          visualize physiological indicators, and better understand the
          challenges of human spaceflight.
        </p>

        <button className="welcome-enter-button" onClick={onEnter}>
          <span>ENTER MISSION CONTROL</span>
          <span className="welcome-button-arrow" aria-hidden="true">
            →
          </span>
        </button>

        <p className="welcome-disclaimer">
          PROTOTYPE INTERFACE · DEMONSTRATION DATA · NOT FOR MEDICAL USE
        </p>
      </section>

      <footer className="welcome-footer">
        <span>M.O.O.N. PROJECT</span>
        <span>ASTRONAUT HEALTH MONITORING SYSTEM</span>
      </footer>
    </main>
  )
}

export function AstronautAccess({
  onBack,
  onDemoPreview,
}: AstronautAccessProps) {
  const [astronautId, setAstronautId] = useState('')
  const [message, setMessage] = useState('')

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    if (!astronautId.trim()) {
      setMessage('Please enter an astronaut ID.')
      return
    }

    setMessage(
      'Profile verification is not connected yet. Backend integration is required.',
    )
  }

  return (
    <main className="access-screen">
      <div className="access-glow" />

      <header className="access-header">
        <span className="welcome-wordmark">M.O.O.N.</span>
        <span className="demo-badge">
          <span className="demo-badge-dot" />
          DEMO ENVIRONMENT
        </span>
      </header>

      <section className="access-card">
        <p className="access-eyebrow">MISSION CONTROL ACCESS</p>
        <h1>Astronaut identification</h1>
        <p className="access-description">
          Enter your assigned astronaut ID to access your mission health
          profile and monitoring environment.
        </p>

        <form className="access-form" onSubmit={handleSubmit}>
          <label htmlFor="astronaut-id">ASTRONAUT ID</label>
          <input
            id="astronaut-id"
            type="text"
            value={astronautId}
            onChange={(event) => {
              setAstronautId(event.target.value)
              setMessage('')
            }}
            placeholder="e.g. AST-001"
            autoComplete="off"
          />

          <button type="submit" className="welcome-enter-button access-submit">
            <span>VERIFY ASTRONAUT ID</span>
            <span className="welcome-button-arrow" aria-hidden="true">
              →
            </span>
          </button>
        </form>

        {import.meta.env.DEV && (
          <button
            type="button"
            className="demo-preview-button"
            onClick={onDemoPreview}
          >
            OPEN DEMO PREVIEW
            <span aria-hidden="true">→</span>
          </button>
        )}

        {message && (
          <p className="access-message" role="status">
            {message}
          </p>
        )}

        <button className="access-back-button" onClick={onBack}>
          ← BACK TO WELCOME
        </button>
      </section>

      <footer className="welcome-footer">
        <span>SECURE MISSION ACCESS · PROTOTYPE</span>
        <span>IDENTITY VERIFICATION NOT YET CONNECTED</span>
      </footer>
    </main>
  )
}
