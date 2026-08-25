/**
 * Canteen Pulse - Forecast Outlook Screen & What-If Simulator Lab ("Steam & Ledger")
 */
import { API } from './api.js';

export class ForecastView {
  constructor(containerEl, onOpenAssistant) {
    this.container = containerEl;
    this.onOpenAssistant = onOpenAssistant;
    this.rangeData = [];
    this.selectedDay = null;
    this.daysCount = 14;
  }

  async load() {
    this.container.innerHTML = `<div style="padding: 40px; text-align:center; color: var(--text-secondary);">⏳ Loading 14-Day Demand Ledger & Academic Feeds...</div>`;
    try {
      this.rangeData = await API.getRange(this.daysCount);
      this.selectedDay = this.rangeData[0];
      this.render();
    } catch (err) {
      this.container.innerHTML = `<div style="padding: 40px; text-align:center; color: var(--color-crimson);">⚠️ Failed to load forecast range: ${err.message}</div>`;
    }
  }

  render() {
    if (!this.rangeData.length) return;

    this.container.innerHTML = `
      <!-- TOP HEADER -->
      <div class="section-header-block">
        <div>
          <h2 class="section-title">
            <i data-lucide="calendar" style="color:var(--accent-copper); width:18px; height:18px;"></i>
            14-Day Demand Forecast Timeline
          </h2>
          <span style="font-size:12px; color:var(--text-secondary);">
            Grounded in academic calendars, weather forecasts, and historical rolling trends.
          </span>
        </div>

        <div style="display:flex; gap:6px;">
          <button class="nav-tab-btn ${this.daysCount === 7 ? 'active' : ''}" id="btn-range-7" style="padding: 4px 10px; font-size:12px;">7 Days</button>
          <button class="nav-tab-btn ${this.daysCount === 14 ? 'active' : ''}" id="btn-range-14" style="padding: 4px 10px; font-size:12px;">14 Days</button>
        </div>
      </div>

      <!-- TIMELINE STRIP OF UPCOMING DAYS -->
      <div class="forecast-strip-container" id="forecast-strip">
        ${this.rangeData.map((d, idx) => `
          <div class="forecast-mini-card ${this.selectedDay && this.selectedDay.date === d.date ? 'active' : ''}" data-idx="${idx}">
            <div class="mini-day-title">${d.day_name}</div>
            <div class="mini-date-sub">${d.formatted_date}</div>
            
            <div class="mini-weather-row">
              <i data-lucide="${d.weather_icon}" style="width:13px; height:13px;"></i>
              <span>${d.weather_temp}°C</span>
            </div>

            <div class="mini-predicted-num">~${d.predicted_meals}</div>

            ${d.event && d.event.has_event ? `
              <div class="mini-event-badge" title="${d.event.title}">
                ⭐ ${d.event.title}
              </div>
            ` : `<div style="height: 16px;"></div>`}
          </div>
        `).join('')}
      </div>

      <!-- EXPANDED DETAIL INSPECTOR CARD -->
      <div class="hero-prediction-card" id="forecast-day-detail" style="margin-bottom: 24px;">
        <!-- Injected dynamically on day select -->
      </div>

      <!-- WHAT-IF SCENARIO SIMULATOR LAB -->
      <div class="whatif-lab-card">
        <div class="section-header-block">
          <div>
            <h3 class="section-title" style="font-size:16px;">
              <i data-lucide="sliders" style="color:var(--accent-copper); width:16px; height:16px;"></i>
              Interactive Scenario Simulator ("What-If" Lab)
            </h3>
            <span style="font-size:12px; color:var(--text-secondary);">
              Simulate operational conditions, weather shocks, and campus events to test model behavior in real-time.
            </span>
          </div>
          <button class="btn-primary" id="btn-run-sim" style="font-size:12px; padding:6px 14px;">
            <i data-lucide="play" style="width:13px; height:13px;"></i> Run Simulation
          </button>
        </div>

        <div class="whatif-form-grid">
          <!-- Day of week -->
          <div class="form-group">
            <label>Day of Week</label>
            <select class="form-control" id="sim-dow">
              <option value="0">Monday (Peak Baseline)</option>
              <option value="1">Tuesday</option>
              <option value="2">Wednesday</option>
              <option value="3">Thursday</option>
              <option value="4">Friday</option>
              <option value="5">Saturday (Hostel Mode)</option>
              <option value="6">Sunday (Brunch Mode)</option>
            </select>
          </div>

          <!-- Weather Scenario -->
          <div class="form-group">
            <label>Weather Condition</label>
            <select class="form-control" id="sim-weather">
              <option value="Rainy">🌧️ Heavy Monsoon Rain</option>
              <option value="Sunny">☀️ Hot Summer Day (35°C)</option>
              <option value="Clear">🌤️ Mild & Pleasant</option>
              <option value="Cold">❄️ Cold Winter Morning (17°C)</option>
            </select>
          </div>

          <!-- Rainfall Slider -->
          <div class="form-group">
            <label>Rainfall: <span id="sim-rain-val" style="color:var(--accent-copper); font-family:var(--font-mono);">25 mm</span></label>
            <input type="range" class="form-control" id="sim-rain" min="0" max="60" value="25" step="1" />
          </div>

          <!-- Temperature Slider -->
          <div class="form-group">
            <label>Temperature: <span id="sim-temp-val" style="color:var(--accent-copper); font-family:var(--font-mono);">24°C</span></label>
            <input type="range" class="form-control" id="sim-temp" min="15" max="42" value="24" step="1" />
          </div>
        </div>

        <!-- Event Toggles -->
        <div style="margin-top: 10px;">
          <label style="font-size:11.5px; font-weight:600; text-transform:uppercase; color:var(--text-secondary); margin-bottom:6px; display:block;">
            Academic & Campus Event Modifiers
          </label>
          <div class="toggle-pills-row">
            <button class="toggle-pill" id="sim-tog-holiday" data-active="false">🎉 Campus Holiday (-75%)</button>
            <button class="toggle-pill" id="sim-tog-exam" data-active="false">📚 Midterm Examination (+16%)</button>
            <button class="toggle-pill" id="sim-tog-fest" data-active="true" class="active">⭐ Tech Fest / Hackathon (+30%)</button>
          </div>
        </div>

        <!-- Simulation Result Board -->
        <div id="sim-result-box" style="margin-top: 18px; padding: 16px; background: var(--bg-chalkboard); border: 1px solid var(--border-subtle); border-radius: var(--radius-md);">
          <!-- Injected dynamically -->
        </div>
      </div>
    `;

    if (window.lucide) window.lucide.createIcons();

    // Render inspector for selected day
    this.renderDayInspector(this.selectedDay || this.rangeData[0]);

    // Attach timeline click listeners
    this.container.querySelectorAll('.forecast-mini-card').forEach(card => {
      card.addEventListener('click', () => {
        const idx = parseInt(card.getAttribute('data-idx'));
        this.selectedDay = this.rangeData[idx];
        this.container.querySelectorAll('.forecast-mini-card').forEach(c => c.classList.remove('active'));
        card.classList.add('active');
        this.renderDayInspector(this.selectedDay);
      });
    });

    // 7 vs 14 days buttons
    this.container.querySelector('#btn-range-7')?.addEventListener('click', () => {
      this.daysCount = 7;
      this.load();
    });
    this.container.querySelector('#btn-range-14')?.addEventListener('click', () => {
      this.daysCount = 14;
      this.load();
    });

    // Simulator events
    const rainInput = this.container.querySelector('#sim-rain');
    const rainVal = this.container.querySelector('#sim-rain-val');
    rainInput?.addEventListener('input', () => {
      rainVal.textContent = `${rainInput.value} mm`;
    });

    const tempInput = this.container.querySelector('#sim-temp');
    const tempVal = this.container.querySelector('#sim-temp-val');
    tempInput?.addEventListener('input', () => {
      tempVal.textContent = `${tempInput.value}°C`;
    });

    // Toggle buttons
    ['sim-tog-holiday', 'sim-tog-exam', 'sim-tog-fest'].forEach(id => {
      const btn = this.container.querySelector(`#${id}`);
      btn?.addEventListener('click', () => {
        const isActive = btn.classList.contains('active');
        if (isActive) {
          btn.classList.remove('active');
        } else {
          btn.classList.add('active');
        }
        this.runSimulation();
      });
    });

    this.container.querySelector('#btn-run-sim')?.addEventListener('click', () => this.runSimulation());

    // Initial simulation run
    this.runSimulation();
  }

  async renderDayInspector(dayData) {
    const box = this.container.querySelector('#forecast-day-detail');
    if (!box) return;

    box.innerHTML = `
      <div class="hero-header-row">
        <div class="hero-date-badge">
          <span class="date-pill">${dayData.day_name.toUpperCase()}, ${dayData.formatted_date}</span>
          <span class="shift-status-pill active">OUTLOOK DETAIL</span>
        </div>
        <div class="weather-impact-chip">
          <div class="weather-icon-badge"><i data-lucide="${dayData.weather_icon}"></i></div>
          <div>${dayData.weather_cond}, ${dayData.weather_temp}°C</div>
        </div>
      </div>

      <div class="hero-body-grid">
        <div>
          <div class="hero-label">Projected Demand</div>
          <div class="hero-number-wrapper">
            <div class="hero-giant-number">~${dayData.predicted_meals}</div>
            <div class="hero-unit-label">covers</div>
          </div>
          <div class="confidence-band-bar">
            <div class="ci-range-text">95% Range: ${dayData.confidence_lower} – ${dayData.confidence_upper} covers</div>
          </div>
        </div>

        <div>
          <div style="font-size:11.5px; font-weight:600; text-transform:uppercase; color:var(--text-secondary); margin-bottom:8px;">
            Station Portion Allocation
          </div>
          <div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px;">
            <div style="background:var(--bg-chalkboard); padding:10px; border-radius:6px; border:1px solid var(--border-subtle);">
              <span style="font-size:11px; color:var(--text-secondary);">Breakfast:</span>
              <div style="font-family:var(--font-mono); font-weight:600; font-size:15px;">${dayData.station_counts.breakfast}</div>
            </div>
            <div style="background:var(--bg-chalkboard); padding:10px; border-radius:6px; border:1px solid var(--border-subtle);">
              <span style="font-size:11px; color:var(--text-secondary);">Lunch:</span>
              <div style="font-family:var(--font-mono); font-weight:600; font-size:15px; color:var(--accent-copper);">${dayData.station_counts.lunch}</div>
            </div>
            <div style="background:var(--bg-chalkboard); padding:10px; border-radius:6px; border:1px solid var(--border-subtle);">
              <span style="font-size:11px; color:var(--text-secondary);">Snacks:</span>
              <div style="font-family:var(--font-mono); font-weight:600; font-size:15px; color:var(--accent-copper);">${dayData.station_counts.snacks}</div>
            </div>
            <div style="background:var(--bg-chalkboard); padding:10px; border-radius:6px; border:1px solid var(--border-subtle);">
              <span style="font-size:11px; color:var(--text-secondary);">Dinner:</span>
              <div style="font-family:var(--font-mono); font-weight:600; font-size:15px;">${dayData.station_counts.dinner}</div>
            </div>
          </div>
        </div>
      </div>

      ${dayData.event && dayData.event.has_event ? `
        <div style="margin-top:14px; padding:10px 14px; background:var(--accent-copper-subtle); border:1px solid rgba(201,113,61,0.3); border-radius:6px; display:flex; align-items:center; gap:8px;">
          <i data-lucide="sparkles" style="color:var(--accent-copper); width:16px; height:16px;"></i>
          <div style="font-size:12.5px;">
            <b>Academic Calendar Flag:</b> ${dayData.event.title}
          </div>
        </div>
      ` : ''}
    `;

    if (window.lucide) window.lucide.createIcons();
  }

  async runSimulation() {
    const dow = parseInt(this.container.querySelector('#sim-dow')?.value || '0');
    const weather = this.container.querySelector('#sim-weather')?.value || 'Rainy';
    const rain = parseFloat(this.container.querySelector('#sim-rain')?.value || '25');
    const temp = parseFloat(this.container.querySelector('#sim-temp')?.value || '24');
    
    const isHoliday = this.container.querySelector('#sim-tog-holiday')?.classList.contains('active') || false;
    const isExam = this.container.querySelector('#sim-tog-exam')?.classList.contains('active') || false;
    const isFest = this.container.querySelector('#sim-tog-fest')?.classList.contains('active') || false;

    const resBox = this.container.querySelector('#sim-result-box');
    if (!resBox) return;

    resBox.innerHTML = `<div style="text-align:center; color:var(--text-secondary);">Calibrating scenario prediction...</div>`;

    try {
      const res = await API.simulateScenario({
        day_of_week: dow,
        weather_condition: weather,
        temperature_c: temp,
        rainfall_mm: rain,
        is_holiday: isHoliday,
        is_exam: isExam,
        is_fest: isFest
      });

      resBox.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;">
          <div>
            <div style="font-size:11px; font-weight:600; color:var(--text-secondary); text-transform:uppercase;">Simulated Demand</div>
            <div style="display:flex; align-items:baseline; gap:10px;">
              <span style="font-family:var(--font-display); font-size:46px; font-weight:700; color:var(--text-cream-hero);">~${res.predicted_meals}</span>
              <span style="font-family:var(--font-mono); font-size:12px; color:var(--accent-copper);">COVERS (95% CI: ${res.confidence_lower} – ${res.confidence_upper})</span>
            </div>
          </div>

          <div style="display:flex; gap:10px; font-family:var(--font-mono); font-size:12.5px;">
            <div style="background:var(--bg-surface); padding:6px 10px; border-radius:4px; border:1px solid var(--border-subtle);">Breakfast: <b>${res.stations.breakfast}</b></div>
            <div style="background:var(--bg-surface); padding:6px 10px; border-radius:4px; border:1px solid var(--border-subtle); color:var(--accent-copper);">Lunch: <b>${res.stations.lunch}</b></div>
            <div style="background:var(--bg-surface); padding:6px 10px; border-radius:4px; border:1px solid var(--border-subtle); color:var(--accent-copper);">Snacks: <b>${res.stations.snacks}</b></div>
            <div style="background:var(--bg-surface); padding:6px 10px; border-radius:4px; border:1px solid var(--border-subtle);">Dinner: <b>${res.stations.dinner}</b></div>
          </div>
        </div>

        <div style="margin-top:12px; display:flex; gap:6px; flex-wrap:wrap;">
          ${res.reason_chips.map(chip => `
            <span class="reason-chip ${chip.type}" style="font-size:11px; padding:3px 8px;">
              ${chip.text}
            </span>
          `).join('')}
        </div>
      `;
    } catch (e) {
      resBox.innerHTML = `<div style="color:var(--color-crimson);">Simulation error: ${e.message}</div>`;
    }
  }
}
