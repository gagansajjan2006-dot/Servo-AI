/**
 * Servo AI - Main Application Entrypoint & Mobile-Responsive Coordinator
 */
import { TelemetrySocket } from './api.js';
import { TodayView } from './todayView.js';
import { MenuView } from './menuView.js';
import { ForecastView } from './forecastView.js';
import { BatchCsvView } from './batchCsvView.js';
import { TimetableFoodView } from './timetableFoodView.js';
import { HistoryView } from './historyView.js';
import { ProcurementView } from './procurementView.js';
import { AdminView } from './adminView.js';
import { AssistantDrawer } from './assistantDrawer.js';

class ServoAIApp {
  constructor() {
    this.currentView = 'today';
    this.views = {};
    this.assistantDrawer = null;
    this.telemetry = null;

    this.init();
  }

  init() {
    // 1. Assistant Drawer setup
    const drawerEl = document.getElementById('ai-assistant-drawer');
    const backdropEl = document.getElementById('drawer-backdrop');
    this.assistantDrawer = new AssistantDrawer(drawerEl, backdropEl);

    // 2. Initialize Views
    const todayEl = document.getElementById('view-today');
    const menuEl = document.getElementById('view-menu');
    const forecastEl = document.getElementById('view-forecast');
    const batchEl = document.getElementById('view-batch');
    const ttEl = document.getElementById('view-timetable');
    const historyEl = document.getElementById('view-history');
    const procEl = document.getElementById('view-procurement');
    const adminEl = document.getElementById('view-admin');

    this.views.today = new TodayView(todayEl, (prompt) => this.assistantDrawer.open(prompt));
    this.views.menu = new MenuView(menuEl, (prompt) => this.assistantDrawer.open(prompt));
    this.views.forecast = new ForecastView(forecastEl, (prompt) => this.assistantDrawer.open(prompt));
    this.views.batch = new BatchCsvView(batchEl, (prompt) => this.assistantDrawer.open(prompt));
    this.views.timetable = new TimetableFoodView(ttEl, (prompt) => this.assistantDrawer.open(prompt));
    this.views.history = new HistoryView(historyEl, () => this.views.today.load());
    this.views.procurement = new ProcurementView(procEl);
    this.views.admin = new AdminView(adminEl, () => {
      this.views.today.load();
      this.views.menu.load();
      this.views.history.load();
    });

    // 3. Setup Nav Tab Handlers (Desktop Top Bar + Mobile Bottom Bar)
    document.querySelectorAll('.nav-tab-btn, .mobile-nav-item').forEach(btn => {
      btn.addEventListener('click', () => {
        const target = btn.getAttribute('data-view');
        if (target) {
          this.switchView(target);
        }
      });
    });

    // 4. Mobile Bottom Nav AI Chat Button
    document.getElementById('mob-nav-assistant')?.addEventListener('click', () => {
      this.assistantDrawer.open();
    });

    // 5. Header Actions
    document.getElementById('btn-toggle-assistant')?.addEventListener('click', () => {
      this.assistantDrawer.open();
    });

    document.getElementById('btn-toggle-kitchen-mode')?.addEventListener('click', () => {
      document.body.classList.toggle('ambient-kitchen-mode');
      const isAmbient = document.body.classList.contains('ambient-kitchen-mode');
      const btn = document.getElementById('btn-toggle-kitchen-mode');
      if (btn) {
        btn.innerHTML = isAmbient 
          ? `<i data-lucide="minimize-2" style="width:15px; height:15px;"></i><span>Exit Board</span>`
          : `<i data-lucide="tv" style="width:15px; height:15px;"></i><span>Board View</span>`;
      }
      if (window.lucide) window.lucide.createIcons();
    });

    // 6. Connect WebSocket Telemetry
    this.telemetry = new TelemetrySocket((msg) => this.handleTelemetryMessage(msg));

    // 7. Load initial view
    this.switchView('today');

    if (window.lucide) window.lucide.createIcons();
  }

  switchView(viewName) {
    this.currentView = viewName;

    // Update desktop tab styles
    document.querySelectorAll('.nav-tab-btn').forEach(btn => {
      if (btn.getAttribute('data-view') === viewName) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });

    // Update mobile bottom nav styles
    document.querySelectorAll('.mobile-nav-item').forEach(btn => {
      if (btn.getAttribute('data-view') === viewName) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });

    // Update container visibility
    document.querySelectorAll('.view-section').forEach(sec => {
      if (sec.id === `view-${viewName}`) {
        sec.classList.add('active');
      } else {
        sec.classList.remove('active');
      }
    });

    // Scroll smoothly to top on view change
    window.scrollTo({ top: 0, behavior: 'smooth' });

    // Load active view data
    if (this.views[viewName]) {
      this.views[viewName].load();
    }
  }

  handleTelemetryMessage(msg) {
    if (msg.event === 'actual_logged') {
      this.showToast(`📝 Actuals recorded: ${msg.actual_meals} covers for ${msg.date}`);
    } else if (msg.event === 'model_retrained') {
      this.showToast(`⚡ Model calibrated with R² ${msg.metrics.r2_score}`);
    } else if (msg.event === 'weather_scenario_updated') {
      this.showToast(`🌧️ Weather scenario: ${msg.scenario}`);
      if (this.currentView === 'today') this.views.today.load();
      if (this.currentView === 'menu') this.views.menu.load();
    } else if (msg.event === 'menu_status_updated') {
      this.showToast(`🍲 Dish status updated: ${msg.dish_name} → ${msg.status.toUpperCase()}`);
    } else if (msg.event === 'menu_item_added') {
      this.showToast(`✨ New dish added: ${msg.dish_name} to ${msg.shift.toUpperCase()}!`);
      if (this.currentView === 'menu') this.views.menu.load();
    }
  }

  showToast(text) {
    const toast = document.createElement('div');
    toast.style.cssText = `
      position: fixed;
      bottom: max(75px, calc(70px + env(safe-area-inset-bottom, 0px)));
      right: 16px;
      left: 16px;
      max-width: 400px;
      margin: 0 auto;
      background: var(--bg-surface-elevated);
      color: var(--text-primary);
      border: 1px solid var(--accent-copper);
      border-radius: 8px;
      padding: 10px 16px;
      font-size: 12.5px;
      font-weight: 500;
      box-shadow: 0 8px 24px rgba(0,0,0,0.7);
      z-index: 999;
      animation: fadeInView 0.25s ease-out;
      text-align: center;
    `;
    toast.textContent = text;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3500);
  }
}

// Bootstrap on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  window.app = new ServoAIApp();
});
