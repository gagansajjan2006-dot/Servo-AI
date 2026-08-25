/**
 * Canteen Pulse - API Client & WebSocket Telemetry
 */

export const API = {
  // REST ENDPOINTS
  async getToday(targetDate = null) {
    const url = targetDate ? `/api/predict/today?target_date=${targetDate}` : '/api/predict/today';
    const res = await fetch(url);
    if (!res.ok) throw new Error(`API error: ${res.statusText}`);
    return res.json();
  },

  async getRange(days = 14) {
    const res = await fetch(`/api/predict/range?days=${days}`);
    if (!res.ok) throw new Error(`API error: ${res.statusText}`);
    return res.json();
  },

  async simulateScenario(params) {
    const res = await fetch('/api/predict/scenario', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    });
    if (!res.ok) throw new Error(`API error: ${res.statusText}`);
    return res.json();
  },

  async getProcurement(bufferPct = 5.0) {
    const res = await fetch(`/api/procurement/today?buffer=${bufferPct}`);
    if (!res.ok) throw new Error(`API error: ${res.statusText}`);
    return res.json();
  },

  async getCalendarHeatmap(weeks = 52) {
    const res = await fetch(`/api/history/calendar?weeks=${weeks}`);
    if (!res.ok) throw new Error(`API error: ${res.statusText}`);
    return res.json();
  },

  async getHistoryMetrics() {
    const res = await fetch('/api/history/metrics');
    if (!res.ok) throw new Error(`API error: ${res.statusText}`);
    return res.json();
  },

  async logActualSales(payload) {
    const res = await fetch('/api/sales/actual', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error(`API error: ${res.statusText}`);
    return res.json();
  },

  async askAssistant(query) {
    const res = await fetch('/api/assistant/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query })
    });
    if (!res.ok) throw new Error(`API error: ${res.statusText}`);
    return res.json();
  },

  // MENU ENDPOINTS
  async getMenuToday(targetDate = null) {
    const url = targetDate ? `/api/menu/today?target_date=${targetDate}` : '/api/menu/today';
    const res = await fetch(url);
    if (!res.ok) throw new Error(`API error: ${res.statusText}`);
    return res.json();
  },

  async updateDishStatus(itemId, status) {
    const res = await fetch(`/api/menu/${itemId}/status`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status })
    });
    if (!res.ok) throw new Error(`API error: ${res.statusText}`);
    return res.json();
  },

  async addMenuItem(payload) {
    const res = await fetch('/api/menu/item', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error(`API error: ${res.statusText}`);
    return res.json();
  },

  async getAcademicEvents() {
    const res = await fetch('/api/admin/academic');
    if (!res.ok) throw new Error(`API error: ${res.statusText}`);
    return res.json();
  },

  async addAcademicEvent(payload) {
    const res = await fetch('/api/admin/academic', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error(`API error: ${res.statusText}`);
    return res.json();
  },

  async retrainModel() {
    const res = await fetch('/api/admin/retrain', { method: 'POST' });
    if (!res.ok) throw new Error(`API error: ${res.statusText}`);
    return res.json();
  },

  async updateWeatherConfig(payload) {
    const res = await fetch('/api/admin/weather-config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error(`API error: ${res.statusText}`);
    return res.json();
  }
};

// WEBSOCKET TELEMETRY
export class TelemetrySocket {
  constructor(onMessage) {
    this.onMessage = onMessage;
    this.ws = null;
    this.connect();
  }

  connect() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/live`;
    
    try {
      this.ws = new WebSocket(wsUrl);
      
      this.ws.onopen = () => {
        console.log('📡 Connected to Servo AI Live Telemetry WebSocket');
      };
      
      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (this.onMessage) this.onMessage(data);
        } catch (err) {
          console.error('WS parse error:', err);
        }
      };
      
      this.ws.onclose = () => {
        // Reconnect after 3s
        setTimeout(() => this.connect(), 3000);
      };
    } catch (e) {
      console.warn('WebSocket connection fallback:', e);
    }
  }
}
