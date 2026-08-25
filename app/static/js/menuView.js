/**
 * Servo AI - Dedicated Menu Section & Dynamic Portioning Planner ("Steam & Ledger")
 */
import { API } from './api.js';

export class MenuView {
  constructor(containerEl, onOpenAssistant) {
    this.container = containerEl;
    this.onOpenAssistant = onOpenAssistant;
    this.menuData = null;
    this.activeShiftFilter = 'all'; // 'all', 'breakfast', 'lunch', 'snacks', 'dinner'
  }

  async load() {
    this.container.innerHTML = `<div style="padding: 40px; text-align:center; color: var(--text-secondary);">🍽️ Loading Daily Menu Catalog & AI Dish Portions...</div>`;
    try {
      this.menuData = await API.getMenuToday();
      this.render();
    } catch (err) {
      this.container.innerHTML = `<div style="padding: 40px; text-align:center; color: var(--color-crimson);">⚠️ Failed to load menu: ${err.message}</div>`;
    }
  }

  render() {
    if (!this.menuData) return;
    const m = this.menuData;

    this.container.innerHTML = `
      <!-- TOP HEADER BLOCK -->
      <div class="section-header-block">
        <div>
          <h2 class="section-title">
            <i data-lucide="utensils-crossed" style="color:var(--accent-copper); width:20px; height:20px;"></i>
            Daily Kitchen Menu & Portioning Board
          </h2>
          <span style="font-size:12px; color:var(--text-secondary);">
            Dynamic station dish allocations calibrated against today's ~${m.total_daily_covers} forecasted covers.
          </span>
        </div>

        <div style="display:flex; gap:8px; align-items:center; flex-wrap:wrap;">
          <button class="btn-secondary" id="btn-add-dish-toggle" style="padding: 6px 12px; font-size:12px;">
            <i data-lucide="plus" style="width:14px; height:14px; color:var(--accent-copper);"></i> Add Daily Special
          </button>
          <button class="btn-primary" id="btn-print-menu-sheet" style="padding: 6px 14px; font-size:12px;">
            <i data-lucide="printer" style="width:13px; height:13px;"></i> Print Menu Sheet
          </button>
        </div>
      </div>

      <!-- KITCHEN MENU SCOREBOARD -->
      <div class="metrics-scoreboard">
        <div class="metric-card">
          <div class="metric-header">
            <span>Menu SKUs Active</span>
            <i data-lucide="layers" style="color:var(--accent-copper); width:15px; height:15px;"></i>
          </div>
          <div class="metric-value-large">${m.total_menu_items} Dishes</div>
          <div class="metric-sub">Across 4 Service Shifts</div>
        </div>

        <div class="metric-card">
          <div class="metric-header">
            <span>Projected Kitchen Gross</span>
            <i data-lucide="indian-rupee" style="color:var(--color-sage); width:15px; height:15px;"></i>
          </div>
          <div class="metric-value-large highlight-sage">₹${m.total_estimated_revenue.toLocaleString()}</div>
          <div class="metric-sub">Estimated Daily Dining Revenue</div>
        </div>

        <div class="metric-card">
          <div class="metric-header">
            <span>Ingredient Requisition Cost</span>
            <i data-lucide="receipt" style="color:var(--accent-brass); width:15px; height:15px;"></i>
          </div>
          <div class="metric-value-large">₹${m.total_estimated_cost.toLocaleString()}</div>
          <div class="metric-sub">Pantry Ingredient Expenditure</div>
        </div>

        <div class="metric-card">
          <div class="metric-header">
            <span>Estimated Kitchen Margin</span>
            <i data-lucide="trending-up" style="color:var(--color-sage); width:15px; height:15px;"></i>
          </div>
          <div class="metric-value-large highlight-sage">${m.overall_gross_margin_pct}%</div>
          <div class="metric-sub">Target Margin Band: > 60%</div>
        </div>
      </div>

      <!-- SHIFT FILTER TABS STRIP -->
      <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:18px; border-bottom:1px solid var(--border-subtle); padding-bottom:8px; flex-wrap:wrap; gap:8px;">
        <div class="toggle-pills-row">
          <button class="toggle-pill ${this.activeShiftFilter === 'all' ? 'active' : ''}" data-shift="all">
            All Shifts (${m.total_menu_items})
          </button>
          <button class="toggle-pill ${this.activeShiftFilter === 'breakfast' ? 'active' : ''}" data-shift="breakfast">
            🌅 Breakfast (${m.shifts.breakfast.items.length})
          </button>
          <button class="toggle-pill ${this.activeShiftFilter === 'lunch' ? 'active' : ''}" data-shift="lunch">
            ☀️ Lunch (${m.shifts.lunch.items.length})
          </button>
          <button class="toggle-pill ${this.activeShiftFilter === 'snacks' ? 'active' : ''}" data-shift="snacks">
            ☕ Snacks (${m.shifts.snacks.items.length})
          </button>
          <button class="toggle-pill ${this.activeShiftFilter === 'dinner' ? 'active' : ''}" data-shift="dinner">
            🌙 Dinner (${m.shifts.dinner.items.length})
          </button>
        </div>

        <span style="font-size:11.5px; color:var(--text-secondary); font-family:var(--font-mono);">
          Live Status Sync: Active
        </span>
      </div>

      <!-- ADD NEW DISH FORM (COLLAPSIBLE) -->
      <div id="add-dish-form-wrapper" style="display:none; background:var(--bg-surface); border:1px solid var(--accent-copper); border-radius:var(--radius-lg); padding:18px 20px; margin-bottom:24px; animation:fadeInView 0.2s ease-out;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
          <h3 style="font-family:var(--font-display); font-size:16px; color:var(--text-primary); display:flex; align-items:center; gap:6px;">
            <i data-lucide="sparkles" style="width:16px; height:16px; color:var(--accent-copper);"></i>
            Add Chef Special / Daily Menu Item
          </h3>
          <button id="btn-close-add-dish" style="color:var(--text-secondary); padding:4px;"><i data-lucide="x" style="width:16px; height:16px;"></i></button>
        </div>

        <form id="form-create-dish">
          <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr)); gap:12px;">
            <div class="form-group">
              <label>Dish Name</label>
              <input type="text" class="form-control" id="new-dish-name" placeholder="e.g. Malai Kofta Curry" required />
            </div>

            <div class="form-group">
              <label>Service Shift</label>
              <select class="form-control" id="new-dish-shift">
                <option value="breakfast">Breakfast (07:30 - 10:00)</option>
                <option value="lunch" selected>Midday Lunch (12:00 - 14:30)</option>
                <option value="snacks">Evening Tea & Snacks (16:00 - 18:00)</option>
                <option value="dinner">Hostel Dinner (19:30 - 22:00)</option>
              </select>
            </div>

            <div class="form-group">
              <label>Chef Station</label>
              <input type="text" class="form-control" id="new-dish-station" placeholder="e.g. Curry & Steam Line" value="Curry & Steam Line" />
            </div>

            <div class="form-group">
              <label>Selling Price (₹)</label>
              <input type="number" step="1" class="form-control" id="new-dish-price" placeholder="e.g. 80" required />
            </div>

            <div class="form-group">
              <label>Ingredient Cost / Portion (₹)</label>
              <input type="number" step="0.5" class="form-control" id="new-dish-cost" placeholder="e.g. 28" required />
            </div>

            <div class="form-group">
              <label>Estimated Diner Share %</label>
              <input type="number" step="1" min="5" max="100" class="form-control" id="new-dish-share" value="30" required />
            </div>

            <div class="form-group">
              <label>Dietary Tag</label>
              <select class="form-control" id="new-dish-dietary">
                <option value="Veg">🟢 Vegetarian</option>
                <option value="Non-Veg">🔴 Non-Vegetarian</option>
                <option value="Jain">🟡 Jain Option</option>
                <option value="High Protein">⚡ High Protein</option>
              </select>
            </div>

            <div class="form-group">
              <label>Allergens / Info</label>
              <input type="text" class="form-control" id="new-dish-allergens" placeholder="e.g. Dairy, Gluten" value="Dairy" />
            </div>
          </div>

          <div style="display:flex; justify-content:flex-end; margin-top:14px; gap:8px;">
            <button type="submit" class="btn-primary" id="btn-submit-new-dish">
              <i data-lucide="check" style="width:14px; height:14px;"></i> Save Dish to Menu
            </button>
          </div>
        </form>
      </div>

      <!-- DISH SECTIONS PER SHIFT -->
      <div id="shifts-container">
        ${this.renderShifts(m.shifts)}
      </div>
    `;

    if (window.lucide) window.lucide.createIcons();
    this.attachEventListeners();
  }

  renderShifts(shifts) {
    const shiftKeys = Object.keys(shifts);
    let html = '';

    shiftKeys.forEach(shiftKey => {
      if (this.activeShiftFilter !== 'all' && this.activeShiftFilter !== shiftKey) {
        return;
      }

      const s = shifts[shiftKey];
      html += `
        <div class="menu-shift-section">
          <div class="menu-shift-header">
            <div style="display:flex; align-items:center; gap:10px;">
              <h3 style="font-family:var(--font-display); font-size:18px; font-weight:700; color:var(--text-primary); margin:0;">
                ${s.name}
              </h3>
              <span style="font-family:var(--font-mono); font-size:11.5px; color:var(--text-secondary); background:var(--bg-chalkboard); padding:3px 9px; border-radius:4px; border:1px solid var(--border-subtle);">
                ${s.time_slot}
              </span>
            </div>

            <div style="font-family:var(--font-mono); font-size:12.5px; color:var(--accent-copper);">
              Shift Projected Covers: <b>~${s.predicted_covers} diners</b>
            </div>
          </div>

          <div class="dishes-grid">
            ${s.items.map(dish => this.renderDishCard(dish)).join('')}
          </div>
        </div>
      `;
    });

    return html;
  }

  renderDishCard(dish) {
    const isVeg = dish.dietary.toLowerCase().includes('veg') && !dish.dietary.toLowerCase().includes('non');
    const statusMap = {
      ready: { label: '🟢 Ready / Active Service', class: 'status-ready' },
      preparing: { label: '🟡 Prep in Progress', class: 'status-prep' },
      low_stock: { label: '🟠 Low Stock (< 10 Left)', class: 'status-low' },
      sold_out: { label: '🔴 Sold Out', class: 'status-soldout' }
    };
    const st = statusMap[dish.status] || statusMap.ready;

    return `
      <div class="dish-card" data-id="${dish.id}">
        <div>
          <!-- TOP ROW: TITLE & DIETARY BADGE -->
          <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:8px; margin-bottom:4px;">
            <h4 style="font-family:var(--font-display); font-size:15px; font-weight:700; color:var(--text-primary); line-height:1.2; margin:0;">
              ${dish.dish_name}
            </h4>
            <span style="font-size:10px; font-weight:600; padding:2px 6px; border-radius:3px; border:1px solid ${isVeg ? 'rgba(143,163,131,0.4)' : 'rgba(201,113,61,0.4)'}; color:${isVeg ? 'var(--color-sage)' : 'var(--accent-copper)'}; background:var(--bg-chalkboard); white-space:nowrap;">
              ${dish.dietary}
            </span>
          </div>

          <!-- CATEGORY & STATION -->
          <div style="font-size:11px; color:var(--text-secondary); margin-bottom:8px;">
            <span style="color:var(--text-muted);">${dish.category}</span> • <span>${dish.chef_station}</span>
          </div>

          <!-- PORTIONING & DEMAND STATS -->
          <div style="background:var(--bg-chalkboard); border:1px solid var(--border-subtle); border-radius:var(--radius-sm); padding:10px 12px; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center;">
            <div>
              <span style="font-size:10.5px; font-weight:600; text-transform:uppercase; color:var(--text-secondary); display:block;">AI Demand Forecast</span>
              <div style="display:flex; align-items:baseline; gap:4px;">
                <span style="font-family:var(--font-display); font-size:26px; font-weight:700; color:var(--text-cream-hero); line-height:1;">~${dish.predicted_portions}</span>
                <span style="font-size:11px; color:var(--accent-copper); font-family:var(--font-mono);">portions</span>
              </div>
            </div>

            <div style="text-align:right;">
              <span style="font-size:10.5px; color:var(--text-secondary); display:block;">Take Rate</span>
              <span style="font-family:var(--font-mono); font-size:13px; font-weight:600; color:var(--color-sage);">${dish.portion_share_pct}%</span>
            </div>
          </div>

          <!-- FINANCIALS ROW -->
          <div style="display:flex; justify-content:space-between; font-size:11.5px; font-family:var(--font-mono); color:var(--text-secondary); margin-bottom:8px;">
            <span>Rate: <b>₹${dish.price}</b></span>
            <span>Cost: ₹${dish.cost_per_portion}</span>
            <span style="color:var(--color-sage);">Margin: <b>${dish.margin_pct}%</b></span>
          </div>

          <!-- ALLERGENS -->
          <div style="font-size:10.5px; color:var(--text-muted);">
            Allergens: ${dish.allergens} • ${dish.calories} kcal
          </div>
        </div>

        <!-- BOTTOM STATUS SELECTOR -->
        <div style="border-top:1px solid var(--border-subtle); padding-top:8px; display:flex; align-items:center; justify-content:space-between;">
          <span style="font-size:10.5px; font-weight:600; color:var(--text-secondary);">KITCHEN STATUS:</span>
          <select class="form-control dish-status-select" data-id="${dish.id}" style="padding:3px 8px; font-size:11px; width:auto;">
            <option value="ready" ${dish.status === 'ready' ? 'selected' : ''}>🟢 Ready</option>
            <option value="preparing" ${dish.status === 'preparing' ? 'selected' : ''}>🟡 Prep Mode</option>
            <option value="low_stock" ${dish.status === 'low_stock' ? 'selected' : ''}>🟠 Low Stock</option>
            <option value="sold_out" ${dish.status === 'sold_out' ? 'selected' : ''}>🔴 Sold Out</option>
          </select>
        </div>
      </div>
    `;
  }

  attachEventListeners() {
    // Shift filter buttons
    this.container.querySelectorAll('.toggle-pill[data-shift]').forEach(btn => {
      btn.addEventListener('click', () => {
        this.activeShiftFilter = btn.getAttribute('data-shift');
        this.render();
      });
    });

    // Toggle add dish form
    const addDishWrap = this.container.querySelector('#add-dish-form-wrapper');
    this.container.querySelector('#btn-add-dish-toggle')?.addEventListener('click', () => {
      if (addDishWrap) {
        addDishWrap.style.display = addDishWrap.style.display === 'none' ? 'block' : 'none';
        if (addDishWrap.style.display === 'block') {
          addDishWrap.scrollIntoView({ behavior: 'smooth' });
        }
      }
    });

    this.container.querySelector('#btn-close-add-dish')?.addEventListener('click', () => {
      if (addDishWrap) addDishWrap.style.display = 'none';
    });

    // Form submit for new dish
    const form = this.container.querySelector('#form-create-dish');
    form?.addEventListener('submit', async (e) => {
      e.preventDefault();
      const dishName = this.container.querySelector('#new-dish-name').value;
      const shift = this.container.querySelector('#new-dish-shift').value;
      const station = this.container.querySelector('#new-dish-station').value;
      const price = parseFloat(this.container.querySelector('#new-dish-price').value);
      const cost = parseFloat(this.container.querySelector('#new-dish-cost').value);
      const share = parseFloat(this.container.querySelector('#new-dish-share').value) / 100.0;
      const dietary = this.container.querySelector('#new-dish-dietary').value;
      const allergens = this.container.querySelector('#new-dish-allergens').value;

      try {
        await API.addMenuItem({
          dish_name: dishName,
          shift,
          chef_station: station,
          price,
          cost_per_portion: cost,
          portion_share_pct: share,
          dietary,
          allergens,
          status: 'ready'
        });

        alert(`✅ "${dishName}" added to the ${shift.toUpperCase()} menu catalog!`);
        this.load();
      } catch (err) {
        alert(`Error adding dish: ${err.message}`);
      }
    });

    // Status change listener
    this.container.querySelectorAll('.dish-status-select').forEach(sel => {
      sel.addEventListener('change', async (e) => {
        const dishId = parseInt(e.target.getAttribute('data-id'));
        const newStatus = e.target.value;
        try {
          await API.updateDishStatus(dishId, newStatus);
        } catch (err) {
          alert(`Error updating dish status: ${err.message}`);
        }
      });
    });

    // Print
    this.container.querySelector('#btn-print-menu-sheet')?.addEventListener('click', () => {
      window.print();
    });
  }
}
