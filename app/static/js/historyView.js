/**
 * Canteen Pulse - History & Accuracy Screen ("Steam & Ledger")
 */
import { API } from './api.js';
import { renderCalendarHeatmap } from './charts.js';

export class HistoryView {
  constructor(containerEl, onRefreshTelemetry) {
    this.container = containerEl;
    this.onRefreshTelemetry = onRefreshTelemetry;
    this.heatmapData = [];
    this.metrics = null;
  }

  async load() {
    this.container.innerHTML = `<div style="padding: 40px; text-align:center; color: var(--text-secondary);">📊 Loading 52-Week Historical Ledger & Accuracy Metrics...</div>`;
    try {
      const [hm, met] = await Promise.all([
        API.getCalendarHeatmap(52),
        API.getHistoryMetrics()
      ]);
      this.heatmapData = hm;
      this.metrics = met;
      this.render();
    } catch (err) {
      this.container.innerHTML = `<div style="padding: 40px; text-align:center; color: var(--color-crimson);">⚠️ Failed to load history: ${err.message}</div>`;
    }
  }

  render() {
    if (!this.metrics) return;
    const m = this.metrics;

    this.container.innerHTML = `
      <!-- ACCURACY TRUST SCOREBOARD -->
      <div class="metrics-scoreboard">
        <div class="metric-card">
          <div class="metric-header">
            <span>Model Trust Score</span>
            <i data-lucide="shield-check" style="color:var(--color-sage); width:16px; height:16px;"></i>
          </div>
          <div class="metric-value-large highlight-sage">${m.monthly_accuracy_pct}%</div>
          <div class="metric-sub">Rolling 30-Day Operational Accuracy</div>
        </div>

        <div class="metric-card">
          <div class="metric-header">
            <span>Mean Absolute Error</span>
            <i data-lucide="target" style="color:var(--accent-copper); width:16px; height:16px;"></i>
          </div>
          <div class="metric-value-large">±${m.monthly_mae}</div>
          <div class="metric-sub">Average variance in meals per day</div>
        </div>

        <div class="metric-card">
          <div class="metric-header">
            <span>Variance Explained (R²)</span>
            <i data-lucide="line-chart" style="color:var(--accent-brass); width:16px; height:16px;"></i>
          </div>
          <div class="metric-value-large">${m.r2_score}</div>
          <div class="metric-sub">Correlation with campus footfall</div>
        </div>

        <div class="metric-card">
          <div class="metric-header">
            <span>Training Corpus</span>
            <i data-lucide="database" style="color:var(--color-cool-slate); width:16px; height:16px;"></i>
          </div>
          <div class="metric-value-large">${m.total_samples} Days</div>
          <div class="metric-sub">Engine: ${m.model_version}</div>
        </div>
      </div>

      <!-- 52-WEEK CALENDAR HEATMAP (COPPER-TONED) -->
      <div class="calendar-heatmap-card">
        <div class="heatmap-controls-row">
          <div>
            <h3 class="section-title" style="font-size:16px;">
              <i data-lucide="flame" style="color:var(--accent-copper); width:16px; height:16px;"></i>
              52-Week Historical Demand Heatmap
            </h3>
            <span style="font-size:12px; color:var(--text-secondary);">
              Color intensity represents daily meals served. Red hairline borders highlight flagged operational anomalies.
            </span>
          </div>
          <div style="font-size:11.5px; color:var(--text-secondary);">
            Click any cell to log or review actual sales.
          </div>
        </div>

        <div class="heatmap-scroll-wrapper">
          <div id="calendar-heatmap-mount"></div>
        </div>

        <div class="heatmap-legend">
          <span>Fewer Covers</span>
          <div class="legend-squares">
            <div class="legend-square level-0" style="background:#221F1B;"></div>
            <div class="legend-square level-1" style="background:#362E27;"></div>
            <div class="legend-square level-2" style="background:#5A4232;"></div>
            <div class="legend-square level-3" style="background:#865737;"></div>
            <div class="legend-square level-4" style="background:#A86134;"></div>
            <div class="legend-square level-5" style="background:#C9713D;"></div>
          </div>
          <span>Peak Surge</span>
          <span style="margin-left:14px; display:inline-flex; align-items:center; gap:4px;">
            <span style="width:10px; height:10px; border:1.5px solid var(--color-crimson); border-radius:2px; display:inline-block;"></span>
            Flagged Anomaly
          </span>
        </div>
      </div>

      <!-- END-OF-DAY ACTUALS LOGGER -->
      <div class="log-actuals-section">
        <div class="section-header-block">
          <div>
            <h3 class="section-title" style="font-size:16px;">
              <i data-lucide="edit-3" style="color:var(--accent-copper); width:16px; height:16px;"></i>
              Canteen Manager Actuals Logger & Calibration Feed
            </h3>
            <span style="font-size:12px; color:var(--text-secondary);">
              Log actual counts at the close of service. When actuals deviate significantly (>15%), tag root causes to improve retraining.
            </span>
          </div>
        </div>

        <form id="form-log-actuals">
          <div class="form-grid-actuals">
            <div class="form-group">
              <label>Service Date</label>
              <input type="date" class="form-control" id="actual-date" value="${new Date().toISOString().split('T')[0]}" required />
            </div>

            <div class="form-group">
              <label>Total Actual Meals Served</label>
              <input type="number" class="form-control" id="actual-total-meals" placeholder="e.g. 418" required />
            </div>

            <div class="form-group">
              <label>Breakfast Count</label>
              <input type="number" class="form-control" id="actual-breakfast" placeholder="e.g. 88" />
            </div>

            <div class="form-group">
              <label>Lunch Count</label>
              <input type="number" class="form-control" id="actual-lunch" placeholder="e.g. 182" />
            </div>

            <div class="form-group">
              <label>Evening Snacks Count</label>
              <input type="number" class="form-control" id="actual-snacks" placeholder="e.g. 78" />
            </div>

            <div class="form-group">
              <label>Dinner Count</label>
              <input type="number" class="form-control" id="actual-dinner" placeholder="e.g. 70" />
            </div>
          </div>

          <div style="margin: 14px 0;">
            <div class="form-group">
              <label>Chef Shift Notes / Observations</label>
              <input type="text" class="form-control" id="actual-notes" placeholder="e.g. Heavy afternoon rain boosted evening samosa sales by 25%" />
            </div>
          </div>

          <div style="background:var(--bg-chalkboard); padding:14px; border-radius:var(--radius-sm); border:1px solid var(--border-subtle); margin-bottom:18px;">
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">
              <input type="checkbox" id="actual-anomaly-check" style="width:15px; height:15px; accent-color:var(--accent-copper);" />
              <label for="actual-anomaly-check" style="font-weight:600; color:var(--text-primary); font-size:12.5px; cursor:pointer;">
                Tag as Unforeseen Operational Anomaly (Root Cause Analysis Flag)
              </label>
            </div>
            <div id="anomaly-reason-wrap" style="display:none; margin-top:8px;">
              <input type="text" class="form-control" id="actual-anomaly-reason" placeholder="Explain root cause: e.g. Surprise hostel power cut, Flash monsoon storm, Sudden sports fest" />
            </div>
          </div>

          <div style="display:flex; justify-content:flex-end;">
            <button type="submit" class="btn-primary" id="btn-submit-actuals">
              <i data-lucide="check" style="width:14px; height:14px;"></i> Log Actuals & Calibrate Model
            </button>
          </div>
        </form>
      </div>
    `;

    if (window.lucide) window.lucide.createIcons();

    // Render calendar heatmap
    const hmContainer = this.container.querySelector('#calendar-heatmap-mount');
    renderCalendarHeatmap(hmContainer, this.heatmapData, (day) => {
      this.populateActualsForm(day);
    });

    // Anomaly checkbox toggle
    const anomalyCheck = this.container.querySelector('#actual-anomaly-check');
    const anomalyWrap = this.container.querySelector('#anomaly-reason-wrap');
    anomalyCheck?.addEventListener('change', () => {
      anomalyWrap.style.display = anomalyCheck.checked ? 'block' : 'none';
    });

    // Form submit
    const form = this.container.querySelector('#form-log-actuals');
    form?.addEventListener('submit', async (e) => {
      e.preventDefault();
      const dateVal = this.container.querySelector('#actual-date').value;
      const totalVal = parseInt(this.container.querySelector('#actual-total-meals').value);
      const bVal = parseInt(this.container.querySelector('#actual-breakfast').value || '0');
      const lVal = parseInt(this.container.querySelector('#actual-lunch').value || '0');
      const sVal = parseInt(this.container.querySelector('#actual-snacks').value || '0');
      const dVal = parseInt(this.container.querySelector('#actual-dinner').value || '0');
      const notesVal = this.container.querySelector('#actual-notes').value;
      const isAnomaly = anomalyCheck.checked;
      const anomalyReason = this.container.querySelector('#actual-anomaly-reason').value;

      try {
        await API.logActualSales({
          record_date: dateVal,
          actual_meals: totalVal,
          actual_breakfast: bVal || null,
          actual_lunch: lVal || null,
          actual_snacks: sVal || null,
          actual_dinner: dVal || null,
          manager_notes: notesVal,
          anomaly_flag: isAnomaly,
          anomaly_reason: isAnomaly ? anomalyReason : null
        });

        alert(`✅ Successfully recorded actual count of ${totalVal} meals for ${dateVal}!`);
        this.load();
        if (this.onRefreshTelemetry) this.onRefreshTelemetry();
      } catch (err) {
        alert(`Error logging actuals: ${err.message}`);
      }
    });
  }

  populateActualsForm(day) {
    const dateInput = this.container.querySelector('#actual-date');
    const totalInput = this.container.querySelector('#actual-total-meals');
    const notesInput = this.container.querySelector('#actual-notes');
    const anomalyCheck = this.container.querySelector('#actual-anomaly-check');
    const anomalyReason = this.container.querySelector('#actual-anomaly-reason');
    const anomalyWrap = this.container.querySelector('#anomaly-reason-wrap');

    if (dateInput) dateInput.value = day.date;
    if (totalInput) totalInput.value = day.actual_meals !== null ? day.actual_meals : day.predicted_meals;
    if (notesInput) notesInput.value = day.anomaly_reason || '';
    if (anomalyCheck) {
      anomalyCheck.checked = day.anomaly_flag || false;
      if (anomalyWrap) anomalyWrap.style.display = anomalyCheck.checked ? 'block' : 'none';
      if (anomalyReason) anomalyReason.value = day.anomaly_reason || '';
    }

    this.container.querySelector('.log-actuals-section')?.scrollIntoView({ behavior: 'smooth' });
  }
}
