/**
 * Canteen Pulse - Procurement & Recipe Matrix Calculator View ("Steam & Ledger")
 */
import { API } from './api.js';

export class ProcurementView {
  constructor(containerEl) {
    this.container = containerEl;
    this.procData = null;
    this.currentBuffer = 5.0;
  }

  async load() {
    this.container.innerHTML = `<div style="padding: 40px; text-align:center; color: var(--text-secondary);">🛒 Calculating Ingredient Ratios & Daily Procurement Ledger...</div>`;
    try {
      this.procData = await API.getProcurement(this.currentBuffer);
      this.render();
    } catch (err) {
      this.container.innerHTML = `<div style="padding: 40px; text-align:center; color: var(--color-crimson);">⚠️ Failed to load procurement: ${err.message}</div>`;
    }
  }

  render() {
    if (!this.procData) return;
    const p = this.procData;

    this.container.innerHTML = `
      <div class="section-header-block">
        <div>
          <h2 class="section-title">
            <i data-lucide="clipboard-list" style="color:var(--accent-copper); width:18px; height:18px;"></i>
            Kitchen Procurement Ledger & Recipe Matrix
          </h2>
          <span style="font-size:12px; color:var(--text-secondary);">
            Translates ~${p.total_meals} forecasted covers into exact raw pantry requisition quantities.
          </span>
        </div>

        <div style="display:flex; gap:10px; align-items:center;">
          <span style="font-size:11.5px; font-weight:600; color:var(--text-secondary);">SAFETY BUFFER:</span>
          <select class="form-control" id="proc-buffer-select" style="padding: 5px 10px; font-size:12px; width:auto;">
            <option value="0" ${this.currentBuffer === 0 ? 'selected' : ''}>+0% (Zero Waste Tight)</option>
            <option value="5" ${this.currentBuffer === 5 ? 'selected' : ''}>+5% (Standard Chef Buffer)</option>
            <option value="10" ${this.currentBuffer === 10 ? 'selected' : ''}>+10% (Rain / Event Buffer)</option>
            <option value="15" ${this.currentBuffer === 15 ? 'selected' : ''}>+15% (Heavy Surge Buffer)</option>
          </select>

          <button class="btn-primary" id="btn-print-prep-sheet" style="padding: 5px 12px; font-size:12px;">
            <i data-lucide="printer" style="width:13px; height:13px;"></i> Print Prep Sheet
          </button>
        </div>
      </div>

      <!-- SUMMARY SCOREBOARD -->
      <div class="metrics-scoreboard">
        <div class="metric-card">
          <div class="metric-header">
            <span>Forecasted Base</span>
            <i data-lucide="utensils" style="color:var(--accent-copper); width:15px; height:15px;"></i>
          </div>
          <div class="metric-value-large">${p.total_meals} Covers</div>
          <div class="metric-sub">Lunch & Dinner: ${p.main_meals_count} covers</div>
        </div>

        <div class="metric-card">
          <div class="metric-header">
            <span>Active Safety Buffer</span>
            <i data-lucide="shield-alert" style="color:var(--accent-copper); width:15px; height:15px;"></i>
          </div>
          <div class="metric-value-large">+${p.safety_buffer_pct}%</div>
          <div class="metric-sub">Pantry walk-in cushion</div>
        </div>

        <div class="metric-card">
          <div class="metric-header">
            <span>Estimated Requisition Value</span>
            <i data-lucide="indian-rupee" style="color:var(--color-sage); width:15px; height:15px;"></i>
          </div>
          <div class="metric-value-large highlight-sage">₹${p.total_estimated_cost.toLocaleString()}</div>
          <div class="metric-sub">Daily ingredient expenditure</div>
        </div>

        <div class="metric-card">
          <div class="metric-header">
            <span>Pantry SKU Items</span>
            <i data-lucide="layers" style="color:var(--color-cool-slate); width:15px; height:15px;"></i>
          </div>
          <div class="metric-value-large">${p.items_count} SKUs</div>
          <div class="metric-sub">Standardized Recipe Ratios</div>
        </div>
      </div>

      <!-- INGREDIENTS TABLE -->
      <div class="data-table-container">
        <table class="canteen-table">
          <thead>
            <tr>
              <th>Ingredient & Category</th>
              <th>Ratio / 100 Covers</th>
              <th>Net Base</th>
              <th>Buffered Requisition Qty</th>
              <th>Unit Rate</th>
              <th>Line Item Cost</th>
              <th>Chef Prep Notes</th>
            </tr>
          </thead>
          <tbody>
            ${p.items.map(item => `
              <tr>
                <td>
                  <div style="font-weight:600; color:var(--text-primary);">${item.ingredient_name}</div>
                  <span class="unit-badge">${item.category.toUpperCase()}</span>
                </td>
                <td style="font-family:var(--font-mono); font-size:12.5px;">${item.qty_per_100_meals} ${item.unit}</td>
                <td style="font-family:var(--font-mono); font-size:12.5px; color:var(--text-secondary);">${item.base_quantity} ${item.unit}</td>
                <td style="font-family:var(--font-mono); font-size:13px; font-weight:600; color:var(--accent-copper);">
                  ${item.buffered_quantity} ${item.unit}
                </td>
                <td style="font-family:var(--font-mono); font-size:12.5px;">₹${item.unit_price} / ${item.unit}</td>
                <td style="font-family:var(--font-mono); font-size:13px; font-weight:600; color:var(--color-sage);">
                  ₹${item.estimated_cost.toLocaleString()}
                </td>
                <td style="font-size:11.5px; color:var(--text-muted);">${item.notes || '—'}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;

    if (window.lucide) window.lucide.createIcons();

    // Buffer select
    this.container.querySelector('#proc-buffer-select')?.addEventListener('change', (e) => {
      this.currentBuffer = parseFloat(e.target.value);
      this.load();
    });

    // Print
    this.container.querySelector('#btn-print-prep-sheet')?.addEventListener('click', () => {
      window.print();
    });
  }
}
