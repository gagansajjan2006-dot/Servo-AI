/**
 * Canteen Pulse - Live Today Screen ("Steam & Ledger" Kitchen Command)
 */
import { API } from './api.js';

export class TodayView {
  constructor(containerEl, onOpenAssistant) {
    this.container = containerEl;
    this.onOpenAssistant = onOpenAssistant;
    this.data = null;
  }

  async load() {
    this.container.innerHTML = `<div style="padding: 40px; text-align:center; color: var(--text-secondary);">📖 Loading Kitchen Service Ledger...</div>`;
    try {
      this.data = await API.getToday();
      this.render();
    } catch (err) {
      this.container.innerHTML = `<div style="padding: 40px; text-align:center; color: var(--color-crimson);">⚠️ Failed to load today's forecast: ${err.message}</div>`;
    }
  }

  render() {
    if (!this.data) return;
    const d = this.data;
    const hero = d.hero;
    const weather = d.weather;

    const trendClass = hero.trend === 'surging' ? 'trending-surging' : (hero.trend === 'cooling' ? 'trending-cooling' : 'trending-steady');
    const trendIcon = hero.trend === 'surging' ? '🔥' : (hero.trend === 'cooling' ? '❄️' : '⚖️');
    const trendLabel = hero.trend === 'surging' ? 'Service Surge (+8%)' : (hero.trend === 'cooling' ? 'Calm Load' : 'Balanced Pace');

    this.container.innerHTML = `
      <!-- HERO PREDICTION BOARD (LEDGER HEADLINE) -->
      <div class="hero-prediction-card ${trendClass}">
        <!-- Top header row -->
        <div class="hero-header-row">
          <div class="hero-date-badge">
            <span class="date-pill">${d.day_name.toUpperCase()}, ${d.formatted_date}</span>
            <span class="shift-status-pill active">● ACTIVE SERVICE</span>
          </div>

          <!-- Weather impact chip -->
          <div class="weather-impact-chip">
            <div class="weather-icon-badge">
              <i data-lucide="${weather.icon}"></i>
            </div>
            <div>
              <span>${weather.condition}, ${weather.temperature_c}°C</span>
              <span class="weather-causal-tag" style="margin-left: 6px;">• ${weather.canteen_impact}</span>
            </div>
          </div>
        </div>

        <!-- Giant Number & Metrics Column -->
        <div class="hero-body-grid">
          <div class="hero-number-column">
            <div class="hero-label">
              <i data-lucide="sparkles" style="width:13px; height:13px; color:var(--accent-copper);"></i>
              Projected Meal Demand
            </div>

            <div class="hero-number-wrapper">
              <!-- Steam emitter for micro-animation -->
              <div class="steam-emitter">
                <div class="steam-particle"></div>
                <div class="steam-particle"></div>
                <div class="steam-particle"></div>
              </div>

              <div class="hero-giant-number" id="hero-pred-number">~${hero.predicted_count}</div>
              <div class="hero-unit-label">covers</div>
            </div>

            <!-- Confidence Interval & Trend -->
            <div class="confidence-band-bar">
              <div class="ci-range-text">
                <span class="ci-tag">95% CONFIDENCE:</span>
                <span>${hero.confidence_lower} – ${hero.confidence_upper} covers</span>
              </div>
              <div class="trend-badge ${hero.trend}">
                ${trendIcon} ${trendLabel}
              </div>
            </div>
          </div>

          <!-- Right Column: Capacity & Utilization -->
          <div class="hero-gauges-column">
            <div class="gauge-row">
              <span class="gauge-label">Campus Population</span>
              <span class="gauge-val">4,650 Students & Staff</span>
            </div>
            <div class="gauge-row">
              <span class="gauge-label">Seating Capacity</span>
              <span class="gauge-val">600 Seats</span>
            </div>
            <div>
              <div class="gauge-row" style="margin-bottom: 6px;">
                <span class="gauge-label">Peak Seat Utilization</span>
                <span class="gauge-val" style="color: var(--accent-copper); font-family:var(--font-mono);">${hero.capacity_utilization_pct}%</span>
              </div>
              <div class="progress-track">
                <div class="progress-fill" style="width: ${Math.min(100, hero.capacity_utilization_pct)}%;"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Explainability Reason Chips Strip -->
        <div class="explainability-section">
          <div class="reason-strip-title">
            <i data-lucide="cpu" style="width:12px; height:12px; color:var(--accent-copper);"></i>
            Causal Attribution & Model Explainability
          </div>
          <div class="reason-chips-container">
            ${d.reason_chips.map(chip => `
              <div class="reason-chip ${chip.type}">
                <i data-lucide="${chip.icon}" style="width:13px; height:13px;"></i>
                <span>${chip.text}</span>
              </div>
            `).join('')}
          </div>
        </div>
      </div>

      <!-- QUICK ASK AI SEARCH BAR -->
      <div class="quick-ai-bar">
        <div class="quick-ai-icon">
          <i data-lucide="message-square" style="width:16px; height:16px;"></i>
        </div>
        <input type="text" class="quick-ai-input" id="quick-ai-input" placeholder="Ask Logbook Assistant: 'Why is today higher?', 'Rain prep advice', 'Rice requirement'..." />
        <div class="quick-prompts-row">
          <button class="quick-prompt-pill" data-prompt="Why is today higher than usual?">💡 Why is today higher?</button>
          <button class="quick-prompt-pill" data-prompt="What should we prep for the rain?">🌧️ Rain Prep Advice</button>
          <button class="quick-prompt-pill" data-prompt="How much rice and dal should we order today?">🍚 Rice & Dal Requirement</button>
        </div>
      </div>

      <!-- SERVICE TIMELINE (STATION CARDS) -->
      <div class="section-header-block">
        <h2 class="section-title">
          <i data-lucide="utensils" style="color:var(--accent-copper); width:18px; height:18px;"></i>
          Station Portion Ledger
        </h2>
        <span style="font-size:12px; color:var(--text-secondary);">Portion projections by kitchen line</span>
      </div>

      <div class="stations-grid">
        ${d.stations.map(st => `
          <div class="station-card">
            <div class="station-top-row">
              <div class="station-icon-title">
                <div class="station-icon-circle">
                  <i data-lucide="${st.icon}"></i>
                </div>
                <div>
                  <div class="station-name">${st.name}</div>
                  <div class="station-hours">${st.time_slot}</div>
                </div>
              </div>
              <span class="shift-status-pill active" style="font-size:10px;">${st.status}</span>
            </div>

            <div class="station-count-display">
              <div class="station-number">${st.predicted_count}</div>
              <div class="station-share-tag">${st.percentage_of_day}% load</div>
            </div>

            <div class="station-details-list">
              <div class="station-detail-item">
                <span>Peak Rush Window:</span>
                <span class="highlight" style="font-family:var(--font-mono); font-size:11.5px;">${st.peak_window}</span>
              </div>
              <div class="station-detail-item">
                <span>Core Menu Items:</span>
                <span class="highlight">${st.key_items.slice(0, 2).join(', ')}</span>
              </div>
            </div>

            <div class="station-prep-note">
              <b>Chef Log:</b> ${st.prep_note}
            </div>
          </div>
        `).join('')}
      </div>

      <!-- DAILY INGREDIENT GLANCE -->
      <div class="procurement-summary-card">
        <div class="section-header-block" style="margin-bottom: 0;">
          <h3 class="section-title" style="font-size:16px;">
            <i data-lucide="clipboard-check" style="color:var(--accent-copper); width:16px; height:16px;"></i>
            Daily Pantry Requisition Preview (~${hero.predicted_count} Covers + 5% Buffer)
          </h3>
          <button class="btn-secondary" id="btn-view-full-procurement" style="font-size:11.5px; padding:5px 12px;">
            Open Requisition Sheet →
          </button>
        </div>

        <div class="procurement-chips-grid">
          <div class="ingredient-chip-card">
            <div class="ingredient-chip-name">🍚 Basmati Rice</div>
            <div class="ingredient-chip-qty">${Math.round(hero.predicted_count * 0.14 * 1.05)} kg</div>
          </div>
          <div class="ingredient-chip-card">
            <div class="ingredient-chip-name">🍲 Pulses & Toor Dal</div>
            <div class="ingredient-chip-qty">${Math.round(hero.predicted_count * 0.055 * 1.05)} kg</div>
          </div>
          <div class="ingredient-chip-card">
            <div class="ingredient-chip-name">🥦 Fresh Mixed Veg</div>
            <div class="ingredient-chip-qty">${Math.round(hero.predicted_count * 0.12 * 1.05)} kg</div>
          </div>
          <div class="ingredient-chip-card">
            <div class="ingredient-chip-name">🥛 Dairy Milk (Chai/Curd)</div>
            <div class="ingredient-chip-qty">${Math.round(hero.predicted_count * 0.145 * 1.05)} L</div>
          </div>
          <div class="ingredient-chip-card">
            <div class="ingredient-chip-name">🥟 Hot Snacks (Samosa)</div>
            <div class="ingredient-chip-qty">${Math.round(d.raw_station_counts.snacks * 1.15)} units</div>
          </div>
        </div>
      </div>
    `;

    if (window.lucide) window.lucide.createIcons();

    // Attach event listeners
    const aiInput = this.container.querySelector('#quick-ai-input');
    if (aiInput) {
      aiInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && aiInput.value.trim()) {
          this.onOpenAssistant(aiInput.value.trim());
          aiInput.value = '';
        }
      });
    }

    this.container.querySelectorAll('.quick-prompt-pill').forEach(btn => {
      btn.addEventListener('click', () => {
        const p = btn.getAttribute('data-prompt');
        this.onOpenAssistant(p);
      });
    });

    const fullProcBtn = this.container.querySelector('#btn-view-full-procurement');
    if (fullProcBtn) {
      fullProcBtn.addEventListener('click', () => {
        document.querySelector('[data-view="procurement"]').click();
      });
    }
  }
}
