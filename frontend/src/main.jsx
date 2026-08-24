import React from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';

const emptyStatus = {
  collector: 'loading',
  backend: '-',
  records: 0,
  last_scan_at: null,
  latest_presence: null,
  last_error: null,
};

function formatTime(value) {
  if (!value) {
    return 'never';
  }
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? value
    : date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

function formatPercent(value) {
  return typeof value === 'number' ? `${Math.round(value * 100)}%` : '-';
}

function formatScore(value) {
  return typeof value === 'number' ? value.toFixed(2) : 'No score yet';
}

function metricValue(value) {
  return value || value === 0 ? value : '-';
}

function App() {
  const [status, setStatus] = React.useState(emptyStatus);
  const [recent, setRecent] = React.useState([]);
  const [updatedAt, setUpdatedAt] = React.useState(null);
  const [error, setError] = React.useState('');
  const presence = status.latest_presence || {};
  const state = presence.state || 'unknown';
  const isRunning = status.collector === 'running';
  const readings = recent.filter((item) => item.state).slice(-5).reverse();

  async function refresh() {
    try {
      const [statusResponse, recentResponse] = await Promise.all([
        fetch('/api/status'),
        fetch('/api/recent?limit=40'),
      ]);
      const nextStatus = await statusResponse.json();
      const nextRecent = await recentResponse.json();
      setStatus(nextStatus);
      setRecent(nextRecent.records || []);
      setUpdatedAt(new Date());
      setError(nextStatus.last_error || '');
    } catch (requestError) {
      setError(requestError.message);
    }
  }

  async function control(action) {
    await fetch(`/api/collector/${action}`, { method: 'POST' });
    refresh();
  }

  React.useEffect(() => {
    refresh();
    const timer = window.setInterval(refresh, 3000);
    return () => window.clearInterval(timer);
  }, []);

  return (
    <main>
      <div className="shell">
        <section className="hero">
          <div className="surface mast">
            <div className="eyebrow">Local presence telemetry</div>
            <h1>WiFi Sense</h1>
            <div className={`status-row state-${state} collector-${status.collector}`}>
              <span className="state-pill">
                <span className="pulse" />
                <span>{state}</span>
              </span>
              <div className="actions">
                <button className="action" type="button" onClick={() => control('start')} disabled={isRunning}>
                  <Icon name="play" />
                  Start collector
                </button>
                <button className="action secondary" type="button" onClick={() => control('stop')} disabled={!isRunning}>
                  <Icon name="stop" />
                  Stop collector
                </button>
              </div>
            </div>
          </div>
          <aside className="surface summary">
            <p className="summary-title">Collector</p>
            <div className="summary-value">{status.collector}</div>
            <p className="summary-copy">{presence.explanation || 'Start the collector to build a quiet baseline.'}</p>
          </aside>
        </section>

        <section className="grid" aria-label="Status metrics">
          <Metric icon={<Icon name="wifi" />} label="Backend" value={metricValue(status.backend)} />
          <Metric icon={<Icon name="radio" />} label="Last scan" value={formatTime(status.last_scan_at)} />
          <Metric icon={<Icon name="database" />} label="Records" value={metricValue(status.records)} />
          <Metric icon={<Icon name="activity" />} label="Confidence" value={formatPercent(presence.confidence)} />
        </section>

        <section className="content">
          <div className="surface panel">
            <div className="panel-head">
              <div>
                <h2>Activity signal</h2>
                <div className="stamp">
                  {typeof presence.activity_score === 'number' ? `Activity score ${formatScore(presence.activity_score)}` : 'No score yet'}
                </div>
              </div>
              <div className="stamp">{updatedAt ? `Updated ${formatTime(updatedAt)}` : 'Updating every 3s'}</div>
            </div>
            <div className="signal">
              <svg viewBox="0 0 640 190" preserveAspectRatio="none" aria-hidden="true">
                <path className="baseline" d="M0 122 C95 122 132 122 190 122 S304 122 378 122 511 122 640 122" />
                <path className="wave" d="M0 122 C80 86 132 158 210 112 S338 86 420 126 540 150 640 92" />
              </svg>
            </div>
          </div>

          <aside className="surface panel">
            <div className="panel-head">
              <h2>Recent readings</h2>
              <div className="stamp">{readings.length} shown</div>
            </div>
            <div className="readings">
              {readings.length ? readings.map((item) => (
                <div className="reading" key={`${item.timestamp}-${item.state}`}>
                  <strong>{item.state}</strong>
                  <span>{formatTime(item.timestamp)}</span>
                  <span>{item.explanation || 'RSSI reading'}</span>
                  <span>{formatPercent(item.confidence)}</span>
                </div>
              )) : <div className="empty">No readings captured yet.</div>}
            </div>
          </aside>
        </section>

        {error ? <div className="error">{error}</div> : null}
      </div>
    </main>
  );
}

function Metric({ icon, label, value }) {
  return (
    <div className="metric">
      <div className="label">{icon}<span>{label}</span></div>
      <div className="value">{value}</div>
    </div>
  );
}

function Icon({ name }) {
  const paths = {
    play: <path d="M8 5v14l11-7z" />,
    stop: <path d="M7 7h10v10H7z" />,
    wifi: <><path d="M5 12.5a10 10 0 0 1 14 0" /><path d="M8.5 16a5 5 0 0 1 7 0" /><path d="M12 20h.01" /></>,
    radio: <><circle cx="12" cy="12" r="2" /><path d="M7.8 7.8a6 6 0 0 0 0 8.4" /><path d="M16.2 7.8a6 6 0 0 1 0 8.4" /></>,
    database: <><ellipse cx="12" cy="6" rx="7" ry="3" /><path d="M5 6v12c0 1.7 3.1 3 7 3s7-1.3 7-3V6" /><path d="M5 12c0 1.7 3.1 3 7 3s7-1.3 7-3" /></>,
    activity: <path d="M4 13h4l2-7 4 12 2-5h4" />,
  };
  return (
    <svg className="icon" viewBox="0 0 24 24" aria-hidden="true">
      {paths[name]}
    </svg>
  );
}

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);