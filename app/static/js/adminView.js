/**
 * Canteen Pulse - Admin & ML Retrain Workbench View ("Steam & Ledger")
 */
import { API } from './api.js';

export class AdminView {
  constructor(containerEl, onRefreshTelemetry) {
    this.container = containerEl;
    this.onRefreshTelemetry = onRefreshTelemetry;
    this.events = [];
    this.metrics = null;
  }

  async load() {
    this.container.innerHTML = `<div style="padding: 40px; text-align:center; color: var(--text-secondary);">⚙️ Loading Model Ledger & Training Logs...</div>`;
    try {
      const [ev, met] = await Promise.all([
        API.getAcademicEvents(),
        API.getHistoryMetrics()
      ]);
      this.events = ev;
      this.metrics = met;
      this.render();
    } catch (err) {
      this.container.innerHTML = `<div style="padding: 40px; text-align:center; color: var(--color-crimson);">⚠️ Failed to load admin workbench: ${err.message}</div>`;
    }
  }

  render() {
    if (!this.metrics) return;
    const m = this.metrics;
    const featImps = m.feature_importances || {};

    this.container.innerHTML = `
      <div class="section-header-block">
        <div>
          <h2 class="section-title">
            <i data-lucide="sliders-horizontal" style="color:var(--accent-copper); width:18px; height:18px;"></i>
            Model Retrain Workbench & System Ledger
          </h2>
          <span style="font-size:12px; color:var(--text-secondary);">
            Manage training datasets, feature weights, academic calendar modifiers, and live weather feeds.
          </span>
        </div>

        <div style="display:flex; gap:8px;">
          <a href="/api/admin/export-csv" class="btn-secondary" style="padding: 6px 14px; font-size:12px;" download>
            <i data-lucide="download" style="width:13px; height:13px;"></i> Export Historical CSV
          </a>
        </div>
      </div>

      <!-- RETRAIN BANNER & TWO-TONE BUTTON -->
      <div class="retrain-banner">
        <div>
          <div style="font-family:var(--font-display); font-size:16px; font-weight:700; color:var(--text-primary); margin-bottom:2px;">
            Gradient Boosted Decision Tree Forecaster (${m.model_version})
          </div>
          <div style="font-size:12px; color:var(--text-secondary);">
            Last Calibrated: <span style="font-family:var(--font-mono); color:var(--text-primary);">${new Date(m.last_trained_at).toLocaleString()}</span> • Corpus: <b>${m.total_samples} Days</b> • R² Fit: <b>${m.r2_score}</b>
          </div>
        </div>

        <button class="btn-primary" id="btn-trigger-retrain">
          <i data-lucide="refresh-cw" style="width:14px; height:14px;"></i> Retrain Model on Latest Actuals
        </button>
      </div>

      <!-- FEATURE IMPORTANCE PANEL (THIN 6PX COPPER BARS + MONOSPACE PERCENTAGE) -->
      <div class="hero-prediction-card" style="margin-bottom: 24px;">
        <h3 class="section-title" style="font-size:15px; margin-bottom: 16px;">
          <i data-lucide="bar-chart-2" style="color:var(--accent-copper); width:16px; height:16px;"></i>
          SHAP-Surrogate Feature Importance Distribution
        </h3>

        <div style="display:flex; flex-direction:column; gap:12px;">
          ${Object.entries(featImps).map(([feat, weight]) => {
            const pct = Math.round(weight * 100);
            return `
              <div>
                <div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:4px;">
                  <span style="font-family:var(--font-mono); color:var(--text-primary); font-weight:500;">${feat}</span>
                  <span style="font-family:var(--font-mono); font-weight:600; color:var(--accent-copper);">${pct}%</span>
                </div>
                <div class="progress-track">
                  <div class="progress-fill" style="width: ${pct}%;"></div>
                </div>
              </div>
            `;
          }).join('')}
        </div>
      </div>

      <!-- WEATHER SCENARIO CONFIGURATION -->
      <div class="whatif-lab-card" style="margin-bottom: 24px;">
        <h3 class="section-title" style="font-size:15px; margin-bottom: 12px;">
          <i data-lucide="cloud-sun" style="color:var(--accent-copper); width:16px; height:16px;"></i>
          Live Weather Station & Scenario Modifiers
        </h3>

        <div class="whatif-form-grid">
          <div class="form-group">
            <label>Live Campus Weather Preset</label>
            <select class="form-control" id="weather-preset-select">
              <option value="Monsoon Shower">🌧️ Monsoon Season (Rain Showers + Chai Surge)</option>
              <option value="Sunny Summer">☀️ Peak Summer (35°C Heatwave)</option>
              <option value="Crisp Winter">❄️ Winter Mornings (19°C Cool Breeze)</option>
              <option value="Overcast Cool">🌤️ Pleasant Overcast Mild</option>
            </select>
          </div>

          <div class="form-group">
            <label>OpenWeather API Key (Optional Real-World Hook)</label>
            <input type="password" class="form-control" id="openweather-api-key" placeholder="Enter OpenWeather API Key" />
          </div>
        </div>

        <div style="display:flex; justify-content:flex-end;">
          <button class="btn-secondary" id="btn-save-weather-cfg">
            <i data-lucide="save" style="width:13px; height:13px;"></i> Save Weather Feed
          </button>
        </div>
      </div>

      <!-- ACADEMIC CALENDAR MANAGER -->
      <div class="data-table-container">
        <div class="section-header-block" style="padding: 16px 20px; margin-bottom: 0;">
          <h3 class="section-title" style="font-size:15px;">
            <i data-lucide="calendar" style="color:var(--accent-copper); width:16px; height:16px;"></i>
            Academic Calendar & Campus Event Modifiers
          </h3>
        </div>

        <table class="canteen-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Event Title</th>
              <th>Category</th>
              <th>Footfall Multiplier</th>
              <th>Operational Context</th>
            </tr>
          </thead>
          <tbody>
            ${this.events.map(e => `
              <tr>
                <td style="font-family:var(--font-mono); font-weight:600;">${e.event_date}</td>
                <td style="font-weight:600; color:var(--text-primary);">${e.title}</td>
                <td><span class="unit-badge">${e.event_type.toUpperCase()}</span></td>
                <td style="font-family:var(--font-mono); font-weight:600; color:${e.impact_multiplier > 1.0 ? 'var(--accent-copper)' : 'var(--color-cool-slate)'};">
                  ${e.impact_multiplier}x
                </td>
                <td style="font-size:12px; color:var(--text-secondary);">${e.description || '—'}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;

    if (window.lucide) window.lucide.createIcons();

    // Trigger Retrain button
    const retrainBtn = this.container.querySelector('#btn-trigger-retrain');
    retrainBtn?.addEventListener('click', async () => {
      retrainBtn.innerHTML = `<i data-lucide="loader" style="width:14px; height:14px; animation:spin 1s linear infinite;"></i> Retraining GBDT Ensemble...`;
      try {
        const res = await API.retrainModel();
        alert(`🎉 Model successfully retrained!\n\nMAE: ±${res.metrics.mae} covers\nR² Score: ${res.metrics.r2_score}\nSamples: ${res.metrics.sample_count} days`);
        this.load();
        if (this.onRefreshTelemetry) this.onRefreshTelemetry();
      } catch (err) {
        alert(`Retrain error: ${err.message}`);
      }
    });

    // Save Weather Config
    this.container.querySelector('#btn-save-weather-cfg')?.addEventListener('click', async () => {
      const preset = this.container.querySelector('#weather-preset-select').value;
      const key = this.container.querySelector('#openweather-api-key').value;
      try {
        await API.updateWeatherConfig({ scenario: preset, api_key: key || null });
        alert(`🌤️ Weather scenario updated to: ${preset}`);
        if (this.onRefreshTelemetry) this.onRefreshTelemetry();
      } catch (err) {
        alert(`Weather update error: ${err.message}`);
      }
    });
  }
}
