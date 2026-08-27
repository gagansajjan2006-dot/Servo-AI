/**
 * Servo AI - Batch CSV Forecaster & Kitchen Requisition Studio View ("Steam & Ledger")
 * Provides drag-and-drop CSV ingestion, instant ML batch predictions, KPI summaries,
 * interactive requisition matrices, and enriched CSV output downloads.
 */
import { API } from './api.js';

export class BatchCsvView {
  constructor(containerEl, onOpenAssistant) {
    this.container = containerEl;
    this.onOpenAssistant = onOpenAssistant;
    this.selectedFile = null;
    this.batchResults = null;
    this.searchFilter = '';
    this.bufferPct = 5.0;
  }

  async load() {
    this.render();
  }

  render() {
    this.container.innerHTML = `
      <!-- SECTION HEADER -->
      <div class="section-header-block">
        <div>
          <h2 class="section-title">
            <i data-lucide="file-spreadsheet" style="color:var(--accent-copper); width:20px; height:20px;"></i>
            Batch CSV Demand Forecaster & Procurement Studio
          </h2>
          <span style="font-size:12px; color:var(--text-secondary);">
            Ingest custom campus calendar & weather CSV files to generate multi-day meal forecasts, station breakdowns, and grocery requisitions.
          </span>
        </div>

        <div style="display:flex; gap:8px; align-items:center; flex-wrap:wrap;">
          <a href="${API.getSampleCsvUrl()}" class="btn-secondary" id="btn-download-sample-csv" download style="padding: 6px 14px; font-size:12px; display:inline-flex; align-items:center; gap:6px;">
            <i data-lucide="download" style="width:13px; height:13px;"></i> Download Sample CSV Template
          </a>
        </div>
      </div>

      <!-- MAIN INPUT & CONFIGURATION CARD -->
      <div class="hero-prediction-card" style="margin-bottom: 24px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 16px; flex-wrap:wrap; gap:12px;">
          <div>
            <h3 style="font-family:var(--font-display); font-size:16px; font-weight:700; color:var(--text-primary); margin-bottom:2px;">
              1. Upload Campus Forecast CSV Dataset
            </h3>
            <div style="font-size:12px; color:var(--text-secondary);">
              Columns supported: <code style="font-family:var(--font-mono); color:var(--accent-copper); background:var(--bg-chalkboard); padding:2px 6px; border-radius:4px;">date, temperature_c, rainfall_mm, is_holiday, is_exam, is_special, rolling_avg_7d</code>
            </div>
          </div>

          <!-- SAFETY BUFFER SLIDER -->
          <div style="display:flex; align-items:center; gap:10px; background:var(--bg-chalkboard); padding:8px 14px; border-radius:var(--radius-md); border:1px solid var(--border-subtle);">
            <label style="font-size:11.5px; font-weight:600; text-transform:uppercase; color:var(--text-secondary); margin:0;">
              Procurement Safety Buffer:
            </label>
            <input type="range" id="batch-buffer-slider" min="0" max="25" step="1" value="${this.bufferPct}" style="width:90px; cursor:pointer;" />
            <span id="batch-buffer-val" style="font-family:var(--font-mono); font-weight:700; color:var(--accent-copper); font-size:13px; min-width:38px;">
              +${this.bufferPct}%
            </span>
          </div>
        </div>

        <!-- DRAG AND DROP UPLOAD ZONE -->
        <div class="csv-dropzone" id="csv-dropzone">
          <input type="file" id="csv-file-input" accept=".csv,text/csv" style="display:none;" />
          <div class="dropzone-inner">
            <div class="dropzone-icon-wrap">
              <i data-lucide="upload-cloud" style="width:36px; height:36px; color:var(--accent-copper);"></i>
            </div>
            <div style="font-family:var(--font-display); font-size:16px; font-weight:600; color:var(--text-primary); margin-bottom:4px;">
              Drag & Drop your input CSV file here
            </div>
            <div style="font-size:12px; color:var(--text-secondary); margin-bottom:14px;">
              or browse from your local device (.csv format)
            </div>

            <div style="display:flex; gap:10px; justify-content:center; flex-wrap:wrap;">
              <button class="btn-primary" id="btn-browse-file" style="padding:7px 18px; font-size:12.5px;">
                <i data-lucide="folder-open" style="width:14px; height:14px;"></i> Browse CSV File
              </button>

              <button class="btn-secondary" id="btn-load-sample-demo" style="padding:7px 18px; font-size:12.5px;">
                <i data-lucide="sparkles" style="width:14px; height:14px; color:var(--accent-copper);"></i> Load 14-Day Demo Sample
              </button>
            </div>

            <div id="selected-file-info" style="margin-top:14px; display:none;">
              <span class="file-badge" id="file-badge">
                <i data-lucide="file-check" style="width:14px; height:14px; color:var(--color-sage);"></i>
                <span id="file-name-text" style="font-family:var(--font-mono); font-weight:600;">selected_file.csv</span>
                <span id="file-size-text" style="opacity:0.7; font-size:11px;">(12.4 KB)</span>
              </span>
            </div>
          </div>
        </div>

        <!-- ACTION BUTTON BAR -->
        <div style="margin-top:16px; display:flex; justify-content:flex-end; gap:10px;">
          <button class="btn-primary" id="btn-run-batch-forecast" style="padding:9px 24px; font-size:13.5px; font-weight:600;" disabled>
            <i data-lucide="play" style="width:15px; height:15px;"></i> Run Batch ML Forecasting
          </button>
        </div>
      </div>

      <!-- RESULTS CONTAINER (INJECTED DYNAMICALLY) -->
      <div id="batch-results-wrapper">
        ${this.batchResults ? this.renderResultsHTML() : `
          <div style="text-align:center; padding:48px 20px; background:var(--bg-surface); border:1px dashed var(--border-subtle); border-radius:var(--radius-lg); color:var(--text-secondary);">
            <i data-lucide="calculator" style="width:36px; height:36px; color:var(--border-subtle); margin-bottom:12px;"></i>
            <div style="font-family:var(--font-display); font-size:16px; font-weight:600; color:var(--text-primary); margin-bottom:4px;">
              Ready for Ingestion
            </div>
            <div style="font-size:12.5px; max-width:480px; margin:0 auto;">
              Upload a custom forecast CSV or click <b>"Load 14-Day Demo Sample"</b> to run the machine learning model across multiple days simultaneously.
            </div>
          </div>
        `}
      </div>
    `;

    if (window.lucide) window.lucide.createIcons();
    this.attachEventListeners();
  }

  attachEventListeners() {
    const dropzone = this.container.querySelector('#csv-dropzone');
    const fileInput = this.container.querySelector('#csv-file-input');
    const browseBtn = this.container.querySelector('#btn-browse-file');
    const loadSampleBtn = this.container.querySelector('#btn-load-sample-demo');
    const runBtn = this.container.querySelector('#btn-run-batch-forecast');
    const bufferSlider = this.container.querySelector('#batch-buffer-slider');
    const bufferVal = this.container.querySelector('#batch-buffer-val');

    // Buffer Slider
    bufferSlider?.addEventListener('input', () => {
      this.bufferPct = parseFloat(bufferSlider.value);
      if (bufferVal) bufferVal.textContent = `+${this.bufferPct}%`;
    });

    // Browse Button
    browseBtn?.addEventListener('click', () => fileInput?.click());

    // File Input change
    fileInput?.addEventListener('change', (e) => {
      if (e.target.files && e.target.files.length > 0) {
        this.handleFileSelected(e.target.files[0]);
      }
    });

    // Drag & Drop
    ['dragenter', 'dragover'].forEach(eventName => {
      dropzone?.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.add('dragover');
      });
    });

    ['dragleave', 'drop'].forEach(eventName => {
      dropzone?.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.remove('dragover');
      });
    });

    dropzone?.addEventListener('drop', (e) => {
      if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        this.handleFileSelected(e.dataTransfer.files[0]);
      }
    });

    // Load Sample Demo
    loadSampleBtn?.addEventListener('click', async () => {
      loadSampleBtn.innerHTML = `<i data-lucide="loader" style="width:14px; height:14px; animation:spin 1s linear infinite;"></i> Loading Demo...`;
      try {
        const res = await fetch(API.getSampleCsvUrl());
        const sampleText = await res.text();
        const demoFile = new File([sampleText], "sample_canteen_forecast_input.csv", { type: "text/csv" });
        this.handleFileSelected(demoFile);
        if (window.lucide) window.lucide.createIcons();
      } catch (err) {
        alert(`Failed to load sample demo: ${err.message}`);
      }
    });

    // Run Forecast Button
    runBtn?.addEventListener('click', () => this.runForecast());

    // Result Table Filter & Download Handlers (if results are shown)
    if (this.batchResults) {
      this.attachResultsListeners();
    }
  }

  handleFileSelected(file) {
    if (!file.name.toLowerCase().endsWith('.csv')) {
      alert('Please upload a valid .csv file.');
      return;
    }

    this.selectedFile = file;
    const fileInfo = this.container.querySelector('#selected-file-info');
    const fileName = this.container.querySelector('#file-name-text');
    const fileSize = this.container.querySelector('#file-size-text');
    const runBtn = this.container.querySelector('#btn-run-batch-forecast');

    if (fileInfo && fileName && fileSize) {
      fileName.textContent = file.name;
      const kb = (file.size / 1024).toFixed(1);
      fileSize.textContent = `(${kb} KB)`;
      fileInfo.style.display = 'block';
    }

    if (runBtn) {
      runBtn.removeAttribute('disabled');
    }

    if (window.lucide) window.lucide.createIcons();
  }

  async runForecast() {
    if (!this.selectedFile) {
      alert('Please select or drag-and-drop a CSV file first.');
      return;
    }

    const runBtn = this.container.querySelector('#btn-run-batch-forecast');
    const resultsWrapper = this.container.querySelector('#batch-results-wrapper');

    if (runBtn) {
      runBtn.innerHTML = `<i data-lucide="loader" style="width:15px; height:15px; animation:spin 1s linear infinite;"></i> Computing GBDT Predictions...`;
      runBtn.setAttribute('disabled', 'true');
    }

    if (resultsWrapper) {
      resultsWrapper.innerHTML = `
        <div style="text-align:center; padding:40px; background:var(--bg-surface); border-radius:var(--radius-lg); border:1px solid var(--border-subtle);">
          <div class="pulse-spinner" style="margin:0 auto 14px;"></div>
          <div style="font-family:var(--font-display); font-size:15px; font-weight:600; color:var(--text-primary);">
            Executing Machine Learning Quantile Forecaster...
          </div>
          <div style="font-size:12px; color:var(--text-secondary); margin-top:4px;">
            Evaluating weather signals, calendar modifiers, and station portion distributions.
          </div>
        </div>
      `;
    }

    try {
      const response = await API.uploadBatchCsv(this.selectedFile, this.bufferPct);
      this.batchResults = response;
      this.searchFilter = '';
      
      // Update results wrapper
      if (resultsWrapper) {
        resultsWrapper.innerHTML = this.renderResultsHTML();
      }

      if (runBtn) {
        runBtn.innerHTML = `<i data-lucide="play" style="width:15px; height:15px;"></i> Run Batch ML Forecasting`;
        runBtn.removeAttribute('disabled');
      }

      if (window.lucide) window.lucide.createIcons();
      this.attachResultsListeners();

      // Scroll smoothly down to results
      resultsWrapper?.scrollIntoView({ behavior: 'smooth', block: 'start' });

    } catch (err) {
      alert(`Batch forecast failed: ${err.message}`);
      if (runBtn) {
        runBtn.innerHTML = `<i data-lucide="play" style="width:15px; height:15px;"></i> Run Batch ML Forecasting`;
        runBtn.removeAttribute('disabled');
      }
      if (resultsWrapper) {
        resultsWrapper.innerHTML = `
          <div style="padding:24px; background:rgba(217,83,79,0.1); border:1px solid var(--color-crimson); border-radius:var(--radius-md); color:var(--color-crimson); text-align:center;">
            <i data-lucide="alert-triangle" style="width:24px; height:24px; margin-bottom:8px;"></i>
            <div style="font-weight:600;">Prediction Error: ${err.message}</div>
          </div>
        `;
        if (window.lucide) window.lucide.createIcons();
      }
    }
  }

  renderResultsHTML() {
    if (!this.batchResults || !this.batchResults.summary) return '';
    const s = this.batchResults.summary;
    const allPredictions = this.batchResults.predictions || [];

    const filtered = allPredictions.filter(p => {
      if (!this.searchFilter) return true;
      const q = this.searchFilter.toLowerCase();
      return (
        p.date.toLowerCase().includes(q) ||
        p.day_name.toLowerCase().includes(q) ||
        p.primary_reason.toLowerCase().includes(q) ||
        p.trend.toLowerCase().includes(q)
      );
    });

    return `
      <!-- BATCH KPI SUMMARY CARDS -->
      <div style="margin-bottom: 20px;">
        <div class="section-header-block">
          <div>
            <h3 class="section-title" style="font-size:16px;">
              <i data-lucide="check-circle-2" style="color:var(--color-sage); width:18px; height:18px;"></i>
              Batch Forecast & Procurement Ledger
            </h3>
            <span style="font-size:12px; color:var(--text-secondary);">
              Processed <b>${s.total_rows_processed} days</b> • Engine: <b>${s.model_architecture}</b>
            </span>
          </div>

          <div style="display:flex; gap:8px;">
            <button class="btn-primary" id="btn-export-output-csv" style="padding:6px 14px; font-size:12px;">
              <i data-lucide="download" style="width:13px; height:13px;"></i> Download Enriched Output CSV
            </button>
          </div>
        </div>

        <div class="metrics-grid" style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:12px; margin-bottom:20px;">
          <!-- Card 1 -->
          <div class="metric-box" style="background:var(--bg-surface); border:1px solid var(--border-subtle); padding:16px; border-radius:var(--radius-md);">
            <div style="font-size:11px; font-weight:600; text-transform:uppercase; color:var(--text-secondary); margin-bottom:4px;">Processed Horizon</div>
            <div style="font-family:var(--font-display); font-size:26px; font-weight:700; color:var(--text-primary);">${s.total_rows_processed} Days</div>
            <div style="font-size:11px; color:var(--text-secondary); margin-top:2px;">Complete timeline matrix</div>
          </div>

          <!-- Card 2 -->
          <div class="metric-box" style="background:var(--bg-surface); border:1px solid var(--border-subtle); padding:16px; border-radius:var(--radius-md);">
            <div style="font-size:11px; font-weight:600; text-transform:uppercase; color:var(--text-secondary); margin-bottom:4px;">Total Projected Covers</div>
            <div style="font-family:var(--font-display); font-size:26px; font-weight:700; color:var(--accent-copper);">${s.total_predicted_meals.toLocaleString()}</div>
            <div style="font-size:11px; color:var(--text-secondary); margin-top:2px;">Cumulative dining footfall</div>
          </div>

          <!-- Card 3 -->
          <div class="metric-box" style="background:var(--bg-surface); border:1px solid var(--border-subtle); padding:16px; border-radius:var(--radius-md);">
            <div style="font-size:11px; font-weight:600; text-transform:uppercase; color:var(--text-secondary); margin-bottom:4px;">Daily Average Load</div>
            <div style="font-family:var(--font-display); font-size:26px; font-weight:700; color:var(--text-primary);">${s.average_daily_meals}</div>
            <div style="font-size:11px; color:var(--text-secondary); margin-top:2px;">Covers / calendar day</div>
          </div>

          <!-- Card 4 -->
          <div class="metric-box" style="background:var(--bg-surface); border:1px solid var(--border-subtle); padding:16px; border-radius:var(--radius-md);">
            <div style="font-size:11px; font-weight:600; text-transform:uppercase; color:var(--text-secondary); margin-bottom:4px;">Est. Procurement Cost</div>
            <div style="font-family:var(--font-display); font-size:26px; font-weight:700; color:var(--color-sage);">₹${s.total_estimated_procurement_cost.toLocaleString()}</div>
            <div style="font-size:11px; color:var(--text-secondary); margin-top:2px;">Includes +${s.safety_buffer_pct}% safety buffer</div>
          </div>
        </div>
      </div>

      <!-- FILTER & SEARCH BAR -->
      <div class="data-table-container">
        <div style="padding:14px 18px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; border-bottom:1px solid var(--border-subtle);">
          <div style="display:flex; align-items:center; gap:8px;">
            <i data-lucide="search" style="width:14px; height:14px; color:var(--text-secondary);"></i>
            <input type="text" id="batch-table-filter" placeholder="Filter by date, day, trend, reason..." value="${this.searchFilter}" style="background:var(--bg-chalkboard); border:1px solid var(--border-subtle); color:var(--text-primary); padding:6px 12px; border-radius:var(--radius-sm); font-size:12px; width:260px;" />
          </div>

          <div style="font-size:12px; color:var(--text-secondary);">
            Showing <b>${filtered.length}</b> of <b>${allPredictions.length}</b> forecast records
          </div>
        </div>

        <!-- RESPONSIVE ENRICHED TABLE -->
        <div style="overflow-x:auto;">
          <table class="canteen-table" style="width:100%;">
            <thead>
              <tr>
                <th style="width:40px;">#</th>
                <th>Date & Day</th>
                <th>Predicted Demand</th>
                <th>95% Confidence</th>
                <th>Station Breakdown (B | L | S | D)</th>
                <th>Key Grocery Staples (Buffered)</th>
                <th>Est. Cost</th>
                <th>Causal Explainability</th>
              </tr>
            </thead>
            <tbody>
              ${filtered.map(p => `
                <tr>
                  <td style="font-family:var(--font-mono); color:var(--text-secondary);">${p.row_index}</td>
                  <td>
                    <div style="font-family:var(--font-mono); font-weight:700; color:var(--text-primary); font-size:13px;">${p.date}</div>
                    <div style="font-size:11px; color:var(--accent-copper); font-weight:600;">${p.day_name}</div>
                  </td>
                  <td>
                    <span style="font-family:var(--font-display); font-size:18px; font-weight:700; color:var(--text-cream-hero);">
                      ${p.predicted_meals}
                    </span>
                    <span style="font-size:11px; color:var(--text-secondary); margin-left:2px;">covers</span>
                  </td>
                  <td>
                    <span class="unit-badge" style="font-family:var(--font-mono); font-size:11px; padding:3px 6px;">
                      ${p.lower_bound_95ci} – ${p.upper_bound_95ci}
                    </span>
                  </td>
                  <td>
                    <div style="display:flex; gap:4px; font-family:var(--font-mono); font-size:11px;">
                      <span style="background:var(--bg-chalkboard); padding:2px 5px; border-radius:3px; border:1px solid var(--border-subtle);" title="Breakfast">B: ${p.breakfast_covers}</span>
                      <span style="background:var(--bg-chalkboard); padding:2px 5px; border-radius:3px; border:1px solid rgba(201,113,61,0.4); color:var(--accent-copper);" title="Lunch">L: ${p.lunch_covers}</span>
                      <span style="background:var(--bg-chalkboard); padding:2px 5px; border-radius:3px; border:1px solid rgba(201,113,61,0.4); color:var(--accent-copper);" title="Snacks">S: ${p.snacks_covers}</span>
                      <span style="background:var(--bg-chalkboard); padding:2px 5px; border-radius:3px; border:1px solid var(--border-subtle);" title="Dinner">D: ${p.dinner_covers}</span>
                    </div>
                  </td>
                  <td style="font-size:11.5px; font-family:var(--font-mono);">
                    <div>🍚 Rice: <b>${p.rice_staple_kg}</b> • 🥣 Dal: <b>${p.dal_staple_kg}</b></div>
                    <div style="color:var(--text-secondary); font-size:10.5px;">🥦 Veg: ${p.veggies_kg} • 🥛 Milk: ${p.milk_litres}</div>
                  </td>
                  <td style="font-family:var(--font-mono); font-weight:700; color:var(--color-sage);">
                    ₹${p.total_ingredient_cost_inr.toLocaleString()}
                  </td>
                  <td>
                    <span class="reason-chip ${p.primary_reason.includes('Rain') || p.primary_reason.includes('Storm') ? 'weather' : (p.primary_reason.includes('Exam') || p.primary_reason.includes('Fest') ? 'exam' : 'calendar')}" style="font-size:11px; padding:3px 8px;" title="${p.all_reasons}">
                      ${p.primary_reason}
                    </span>
                  </td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;
  }

  attachResultsListeners() {
    // Filter handler
    const filterInput = this.container.querySelector('#batch-table-filter');
    filterInput?.addEventListener('input', (e) => {
      this.searchFilter = e.target.value;
      const wrapper = this.container.querySelector('#batch-results-wrapper');
      if (wrapper) {
        wrapper.innerHTML = this.renderResultsHTML();
        if (window.lucide) window.lucide.createIcons();
        this.attachResultsListeners();
        // Restore focus to filter input
        const newFilter = this.container.querySelector('#batch-table-filter');
        if (newFilter) {
          newFilter.focus();
          newFilter.selectionStart = newFilter.selectionEnd = newFilter.value.length;
        }
      }
    });

    // Export output CSV button
    const exportBtn = this.container.querySelector('#btn-export-output-csv');
    exportBtn?.addEventListener('click', async () => {
      if (!this.selectedFile) return;
      exportBtn.innerHTML = `<i data-lucide="loader" style="width:13px; height:13px; animation:spin 1s linear infinite;"></i> Downloading CSV...`;
      try {
        const blob = await API.downloadBatchCsv(this.selectedFile, this.bufferPct);
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = `predicted_canteen_forecast_output.csv`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(downloadUrl);
        exportBtn.innerHTML = `<i data-lucide="check" style="width:13px; height:13px; color:var(--color-sage);"></i> Downloaded!`;
        setTimeout(() => {
          exportBtn.innerHTML = `<i data-lucide="download" style="width:13px; height:13px;"></i> Download Enriched Output CSV`;
          if (window.lucide) window.lucide.createIcons();
        }, 2500);
      } catch (err) {
        alert(`Export failed: ${err.message}`);
        exportBtn.innerHTML = `<i data-lucide="download" style="width:13px; height:13px;"></i> Download Enriched Output CSV`;
      }
      if (window.lucide) window.lucide.createIcons();
    });
  }
}
