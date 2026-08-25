/**
 * Canteen Pulse - Charts & Calendar Heatmap Engine
 */

export function renderCalendarHeatmap(containerEl, data, onSelectDate) {
  if (!containerEl) return;
  containerEl.innerHTML = '';

  const tooltipEl = document.getElementById('heatmap-tooltip') || createTooltip();

  // Create grid
  const grid = document.createElement('div');
  grid.className = 'calendar-heatmap-grid';

  data.forEach((day) => {
    const cell = document.createElement('div');
    cell.className = 'heatmap-cell';
    
    const meals = day.actual_meals !== null ? day.actual_meals : day.predicted_meals;
    
    // Assign color level
    let level = 0;
    if (meals > 0) {
      if (meals < 150) level = 1;
      else if (meals < 280) level = 2;
      else if (meals < 390) level = 3;
      else if (meals < 460) level = 4;
      else level = 5;
    }
    cell.classList.add(`level-${level}`);

    if (day.anomaly_flag) {
      cell.classList.add('is-anomaly');
    }

    // Tooltip events
    cell.addEventListener('mouseenter', (e) => {
      const actText = day.actual_meals !== null ? `<b>${day.actual_meals}</b> meals served` : '<i>Pending actuals</i>';
      const predText = day.predicted_meals ? `Predicted: ${day.predicted_meals}` : '';
      const varText = day.variance_pct ? ` (Var: ${day.variance_pct > 0 ? '+' : ''}${day.variance_pct}%)` : '';
      const eventText = day.holiday_name || day.exam_name || day.fest_name ? `<div style="color: #A855F7; margin-top:4px; font-weight:600;">⭐ ${day.holiday_name || day.exam_name || day.fest_name}</div>` : '';
      const anomalyText = day.anomaly_reason ? `<div style="color: #EF4444; margin-top:4px; font-weight:600;">⚠️ Anomaly: ${day.anomaly_reason}</div>` : '';

      tooltipEl.innerHTML = `
        <div style="font-weight:700; color:#FFA726; margin-bottom:4px;">${day.day_name}, ${day.date}</div>
        <div>${actText}</div>
        <div style="font-size:11px; color:#9CA3AF;">${predText}${varText} • ${day.weather} (${day.temp}°C)</div>
        ${eventText}
        ${anomalyText}
      `;
      tooltipEl.style.display = 'block';
      tooltipEl.style.left = `${e.clientX + 12}px`;
      tooltipEl.style.top = `${e.clientY + 12}px`;
    });

    cell.addEventListener('mousemove', (e) => {
      tooltipEl.style.left = `${e.clientX + 12}px`;
      tooltipEl.style.top = `${e.clientY + 12}px`;
    });

    cell.addEventListener('mouseleave', () => {
      tooltipEl.style.display = 'none';
    });

    cell.addEventListener('click', () => {
      if (onSelectDate) onSelectDate(day);
    });

    grid.appendChild(cell);
  });

  containerEl.appendChild(grid);
}

function createTooltip() {
  const el = document.createElement('div');
  el.id = 'heatmap-tooltip';
  el.className = 'heatmap-tooltip';
  document.body.appendChild(el);
  return el;
}
