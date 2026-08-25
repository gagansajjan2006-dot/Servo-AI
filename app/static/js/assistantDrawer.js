/**
 * Canteen Pulse - AI Kitchen Assistant Drawer
 */
import { API } from './api.js';

export class AssistantDrawer {
  constructor(drawerEl, backdropEl) {
    this.drawer = drawerEl;
    this.backdrop = backdropEl;
    this.messagesContainer = this.drawer.querySelector('#drawer-messages');
    this.inputBox = this.drawer.querySelector('#drawer-input');
    this.sendBtn = this.drawer.querySelector('#drawer-send-btn');
    this.closeBtn = this.drawer.querySelector('#drawer-close-btn');
    this.isOpen = false;

    this.init();
  }

  init() {
    this.closeBtn?.addEventListener('click', () => this.close());
    this.backdrop?.addEventListener('click', () => this.close());

    this.sendBtn?.addEventListener('click', () => this.handleSend());
    this.inputBox?.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') this.handleSend();
    });

    // Suggestion pills
    this.drawer.querySelectorAll('.drawer-pill').forEach(pill => {
      pill.addEventListener('click', () => {
        const text = pill.textContent.replace(/^[^\w]+/, '').trim();
        this.ask(text);
      });
    });

    // Initial greeting
    this.addAssistantMessage(`
      ### 🧑‍🍳 Kitchen AI Assistant Ready
      Hello Chef! I am continuously monitoring student attendance patterns, exam schedules, and weather forecasts.
      
      Ask me questions like:
      - *"Why is today higher than usual?"*
      - *"What should we prep for the rain tomorrow?"*
      - *"How much rice & dal should we boil today?"*
    `);
  }

  open(initialQuery = null) {
    this.isOpen = true;
    this.drawer.classList.add('open');
    this.backdrop.classList.add('open');
    if (initialQuery) {
      this.ask(initialQuery);
    } else {
      setTimeout(() => this.inputBox?.focus(), 200);
    }
  }

  close() {
    this.isOpen = false;
    this.drawer.classList.remove('open');
    this.backdrop.classList.remove('open');
  }

  async handleSend() {
    const q = this.inputBox?.value.trim();
    if (!q) return;
    this.inputBox.value = '';
    await this.ask(q);
  }

  async ask(query) {
    if (!this.isOpen) this.open();
    
    // Add user bubble
    this.addUserMessage(query);

    // Add loading placeholder
    const loadingId = 'loading-' + Date.now();
    const loadingEl = document.createElement('div');
    loadingEl.className = 'chat-bubble assistant';
    loadingEl.id = loadingId;
    loadingEl.innerHTML = `<i data-lucide="loader" style="width:14px; height:14px; animation:spin 1s linear infinite;"></i> Analyzing footfall signals & pantry matrix...`;
    this.messagesContainer.appendChild(loadingEl);
    this.scrollToBottom();
    if (window.lucide) window.lucide.createIcons();

    try {
      const res = await API.askAssistant(query);
      const target = document.getElementById(loadingId);
      if (target) {
        target.innerHTML = this.formatMarkdown(res.reply);
      }
    } catch (err) {
      const target = document.getElementById(loadingId);
      if (target) {
        target.innerHTML = `<div style="color:var(--color-crimson);">⚠️ Failed to get AI response: ${err.message}</div>`;
      }
    }
    this.scrollToBottom();
    if (window.lucide) window.lucide.createIcons();
  }

  addUserMessage(text) {
    const el = document.createElement('div');
    el.className = 'chat-bubble user';
    el.textContent = text;
    this.messagesContainer.appendChild(el);
    this.scrollToBottom();
  }

  addAssistantMessage(markdownText) {
    const el = document.createElement('div');
    el.className = 'chat-bubble assistant';
    el.innerHTML = this.formatMarkdown(markdownText);
    this.messagesContainer.appendChild(el);
    this.scrollToBottom();
    if (window.lucide) window.lucide.createIcons();
  }

  formatMarkdown(text) {
    // Lightweight markdown formatter
    let html = text
      .replace(/^### (.*$)/gim, '<h3>$1</h3>')
      .replace(/^## (.*$)/gim, '<h2>$1</h2>')
      .replace(/\*\*(.*?)\*\*/gim, '<b>$1</b>')
      .replace(/\*(.*?)\*/gim, '<i>$1</i>')
      .replace(/^\- (.*$)/gim, '<li>$1</li>')
      .replace(/\n\n/gim, '<br/><br/>');

    // Wrap li elements in ul
    if (html.includes('<li>')) {
      html = html.replace(/(<li>.*<\/li>)/gis, '<ul>$1</ul>');
    }
    return html;
  }

  scrollToBottom() {
    if (this.messagesContainer) {
      this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }
  }
}
