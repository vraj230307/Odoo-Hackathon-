/**
 * Traveloop — budget.js
 * Member 3: Budget Dashboard
 * Handles: Chart.js charts, expense log, budget alerts, AI estimator API
 */

const API_BASE = window.API_BASE || 'http://localhost:5000';

/* ══════════════════════════════════════════════
   STORAGE
══════════════════════════════════════════════ */
const Store = (() => {
  function get(key, def) { try { return JSON.parse(localStorage.getItem(key)) ?? def; } catch { return def; } }
  function set(key, val) { localStorage.setItem(key, JSON.stringify(val)); }
  return { get, set };
})();

/* ══════════════════════════════════════════════
   FORMATTERS
══════════════════════════════════════════════ */
function fmt(n, currency = 'INR') {
  const symbols = { INR: '₹', USD: '$', EUR: '€', GBP: '£', JPY: '¥' };
  const sym = symbols[currency] || '₹';
  return sym + Number(n || 0).toLocaleString('en-IN', { maximumFractionDigits: 0 });
}

/* ══════════════════════════════════════════════
   TOAST
══════════════════════════════════════════════ */
function showToast(msg, type = 'success') {
  const c = document.getElementById('toastContainer');
  if (!c) return;
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  const icons = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' };
  t.innerHTML = `<span>${icons[type]}</span><span>${msg}</span>`;
  c.appendChild(t);
  setTimeout(() => t.remove(), 3500);
}

/* ══════════════════════════════════════════════
   BUDGET ALERT
══════════════════════════════════════════════ */
function renderAlert(type, message) {
  const c = document.getElementById('budgetAlertContainer');
  if (!c) return;
  if (!message) { c.innerHTML = ''; return; }
  c.innerHTML = `
    <div class="budget-alert ${type}">
      <span class="alert-icon">${{info:'ℹ️',warning:'⚠️',danger:'🚨',success:'✅'}[type]}</span>
      <span class="alert-text">${message}</span>
      <button class="alert-dismiss" onclick="this.closest('.budget-alert').remove()">✕</button>
    </div>`;
}

/* ══════════════════════════════════════════════
   CATEGORY CONFIG
══════════════════════════════════════════════ */
const CAT_COLORS = {
  '🍜 Food':          '#FF6B35',
  '🏨 Accommodation': '#0D6EFD',
  '🚌 Transport':     '#8B5CF6',
  '🎭 Activities':    '#12B76A',
  '🛍️ Shopping':      '#F59E0B',
  '🏥 Health':        '#EF4444',
  '📡 Other':         '#94A3B8',
};

function catColor(cat) { return CAT_COLORS[cat] || '#CBD5E1'; }

/* ══════════════════════════════════════════════
   SUMMARY UPDATE
══════════════════════════════════════════════ */
function updateSummary(expenses, budget, days, currency) {
  const total = expenses.reduce((s, e) => s + e.amount, 0);
  const remaining = Math.max(0, budget - total);
  const pct = budget > 0 ? Math.round((total / budget) * 100) : 0;
  const dailyAvg = expenses.length > 0
    ? (total / Math.max(1, [...new Set(expenses.map(e => e.date))].length))
    : 0;

  document.getElementById('totalBudget').textContent    = fmt(budget, currency);
  document.getElementById('totalSpent').textContent     = fmt(total, currency);
  document.getElementById('totalRemaining').textContent = fmt(remaining, currency);
  document.getElementById('dailyAvg').textContent       = fmt(dailyAvg, currency);
  document.getElementById('spentPct').textContent       = `${pct}% of budget`;

  const daysLeft = dailyAvg > 0 ? Math.floor(remaining / dailyAvg) : days;
  document.getElementById('daysRemaining').textContent = `~${daysLeft} day${daysLeft !== 1 ? 's' : ''} remaining`;

  // Budget alert logic
  if (pct >= 100)      renderAlert('danger',  `🚨 Budget exceeded! You've spent ${fmt(total - budget, currency)} over your limit.`);
  else if (pct >= 85)  renderAlert('warning', `⚠️ Heads up! You've used ${pct}% of your budget.`);
  else if (pct >= 60)  renderAlert('info',    `ℹ️ You've used ${pct}% of your budget. Keep an eye on spending.`);
  else if (pct > 0)    renderAlert('success', `✅ Looking good! ${pct}% used — ${fmt(remaining, currency)} remaining.`);
  else                 renderAlert(null, null);
}

/* ══════════════════════════════════════════════
   EXPENSE LIST RENDER
══════════════════════════════════════════════ */
function renderExpenseList(expenses, currency) {
  const el = document.getElementById('expenseList');
  if (!el) return;
  if (!expenses.length) {
    el.innerHTML = '<p style="color:var(--text-muted);font-size:13.5px;padding:16px 0;">No expenses yet. Add one →</p>';
    return;
  }
  el.innerHTML = [...expenses].reverse().map((exp, ri) => {
    const i = expenses.length - 1 - ri;
    return `
    <div class="expense-row">
      <span class="expense-dot" style="background:${catColor(exp.category)}"></span>
      <div class="expense-name">${exp.description}</div>
      <span class="expense-cat">${exp.category}</span>
      <div class="expense-amount">${fmt(exp.amount, currency)}</div>
      <div class="expense-actions">
        <button class="expense-del-btn" data-index="${i}" title="Delete">🗑</button>
      </div>
    </div>`;
  }).join('');

  el.querySelectorAll('.expense-del-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const idx = parseInt(btn.dataset.index);
      const expenses = Store.get('traveloop_expenses', []);
      expenses.splice(idx, 1);
      Store.set('traveloop_expenses', expenses);
      refresh();
      showToast('Expense removed.', 'info');
    });
  });
}

/* ══════════════════════════════════════════════
   CATEGORY BREAKDOWN RENDER
══════════════════════════════════════════════ */
function renderCategoryBreakdown(expenses, currency) {
  const el = document.getElementById('categoryBreakdown');
  if (!el) return;
  if (!expenses.length) {
    el.innerHTML = '<p style="color:var(--text-muted);font-size:13.5px;">No expenses logged yet.</p>';
    return;
  }
  const byCategory = {};
  expenses.forEach(e => {
    byCategory[e.category] = (byCategory[e.category] || 0) + e.amount;
  });
  const total = Object.values(byCategory).reduce((s, v) => s + v, 0);
  const sorted = Object.entries(byCategory).sort((a, b) => b[1] - a[1]);

  el.innerHTML = sorted.map(([cat, amt]) => {
    const pct = total > 0 ? Math.round((amt / total) * 100) : 0;
    return `
    <div class="cat-row">
      <div class="cat-header">
        <div class="cat-name">${cat}</div>
        <div style="display:flex;gap:12px;align-items:center;">
          <span class="cat-amount">${fmt(amt, currency)}</span>
          <span class="cat-pct">${pct}%</span>
        </div>
      </div>
      <div class="progress-bar-track">
        <div class="progress-bar-fill" style="width:${pct}%;background:${catColor(cat)}"></div>
      </div>
    </div>`;
  }).join('');
}

/* ══════════════════════════════════════════════
   CHARTS
══════════════════════════════════════════════ */
let pieChartInst = null, barChartInst = null, dailyChartInst = null;

const chartDefaults = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { labels: { font: { family: "'DM Sans', sans-serif", size: 12 }, color: '#5A6A85' } } }
};

function buildCharts(expenses, budget, currency) {
  buildPie(expenses, currency);
  buildBar(expenses, currency);
  buildDaily(expenses, currency);
}

function buildPie(expenses, currency) {
  const ctx = document.getElementById('pieChart');
  if (!ctx) return;
  const byCategory = {};
  expenses.forEach(e => { byCategory[e.category] = (byCategory[e.category] || 0) + e.amount; });
  const labels = Object.keys(byCategory);
  const data   = Object.values(byCategory);
  const colors = labels.map(catColor);

  if (pieChartInst) pieChartInst.destroy();
  pieChartInst = new Chart(ctx, {
    type: 'doughnut',
    data: { labels, datasets: [{ data, backgroundColor: colors, borderWidth: 3, borderColor: '#fff', hoverOffset: 6 }] },
    options: {
      ...chartDefaults,
      plugins: {
        ...chartDefaults.plugins,
        legend: { ...chartDefaults.plugins.legend, position: 'right' },
        tooltip: { callbacks: { label: (ctx) => ` ${ctx.label}: ${fmt(ctx.raw, currency)} (${Math.round(ctx.parsed / expenses.reduce((s,e)=>s+e.amount,0) * 100)}%)` } }
      },
      cutout: '62%',
    }
  });
}

function buildBar(expenses, currency) {
  const ctx = document.getElementById('barChart');
  if (!ctx) return;
  const byCategory = {};
  expenses.forEach(e => { byCategory[e.category] = (byCategory[e.category] || 0) + e.amount; });
  const labels = Object.keys(byCategory).sort((a,b) => byCategory[b] - byCategory[a]);
  const data   = labels.map(l => byCategory[l]);
  const colors = labels.map(catColor);

  if (barChartInst) barChartInst.destroy();
  barChartInst = new Chart(ctx, {
    type: 'bar',
    data: { labels, datasets: [{ label: 'Spending', data, backgroundColor: colors, borderRadius: 8, borderSkipped: false }] },
    options: {
      ...chartDefaults,
      scales: {
        x: { grid: { display: false }, ticks: { color: '#94A3B8', font: { family: "'DM Sans'" } } },
        y: { grid: { color: '#F1F5FB' }, ticks: { color: '#94A3B8', font: { family: "'DM Sans'" }, callback: (v) => fmt(v, currency) } }
      },
      plugins: { ...chartDefaults.plugins, legend: { display: false } }
    }
  });
}

function buildDaily(expenses, currency) {
  const ctx = document.getElementById('dailyChart');
  if (!ctx) return;
  const byDate = {};
  expenses.forEach(e => { byDate[e.date] = (byDate[e.date] || 0) + e.amount; });
  const sortedDates = Object.keys(byDate).sort();
  const data = sortedDates.map(d => byDate[d]);

  if (dailyChartInst) dailyChartInst.destroy();
  dailyChartInst = new Chart(ctx, {
    type: 'line',
    data: {
      labels: sortedDates,
      datasets: [{
        label: 'Daily Spend',
        data,
        borderColor: '#0D6EFD',
        backgroundColor: 'rgba(13,110,253,0.08)',
        borderWidth: 2.5,
        tension: 0.4,
        fill: true,
        pointBackgroundColor: '#0D6EFD',
        pointRadius: 4,
      }]
    },
    options: {
      ...chartDefaults,
      scales: {
        x: { grid: { display: false }, ticks: { color: '#94A3B8' } },
        y: { grid: { color: '#F1F5FB' }, ticks: { color: '#94A3B8', callback: (v) => fmt(v, currency) } }
      }
    }
  });
}

/* ══════════════════════════════════════════════
   REFRESH — main re-render
══════════════════════════════════════════════ */
function refresh() {
  const expenses = Store.get('traveloop_expenses', []);
  const budget   = Store.get('traveloop_budget',   50000);
  const days     = Store.get('traveloop_days',     7);
  const currency = Store.get('traveloop_currency', 'INR');

  updateSummary(expenses, budget, days, currency);
  renderExpenseList(expenses, currency);
  renderCategoryBreakdown(expenses, currency);
  buildCharts(expenses, budget, currency);
}

/* ══════════════════════════════════════════════
   CHART TABS
══════════════════════════════════════════════ */
function setupChartTabs() {
  document.querySelectorAll('.chart-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.chart-tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.chart-pane').forEach(p => p.classList.remove('active'));
      tab.classList.add('active');
      document.getElementById(`pane-${tab.dataset.chart}`)?.classList.add('active');
    });
  });
}

/* ══════════════════════════════════════════════
   BUDGET SLIDER
══════════════════════════════════════════════ */
function setupBudgetSlider() {
  const slider  = document.getElementById('budgetSlider');
  const display = document.getElementById('sliderDisplay');
  if (!slider) return;

  const saved = Store.get('traveloop_budget', 50000);
  slider.value = saved;
  if (display) display.textContent = '₹' + Number(saved).toLocaleString('en-IN');

  function updateSlider() {
    const val = parseInt(slider.value);
    const pct = ((val - slider.min) / (slider.max - slider.min)) * 100;
    slider.style.setProperty('--pct', `${pct}%`);
    if (display) display.textContent = '₹' + val.toLocaleString('en-IN');
  }
  slider.addEventListener('input', updateSlider);
  updateSlider();

  document.getElementById('saveBudgetBtn')?.addEventListener('click', () => {
    const budget   = parseInt(slider.value);
    const days     = parseInt(document.getElementById('tripDays')?.value) || 7;
    const currency = document.getElementById('tripCurrency')?.value || 'INR';
    Store.set('traveloop_budget', budget);
    Store.set('traveloop_days', days);
    Store.set('traveloop_currency', currency);
    refresh();
    showToast('Budget settings saved!');
  });
}

/* ══════════════════════════════════════════════
   ADD EXPENSE FORM
══════════════════════════════════════════════ */
function setupExpenseForm() {
  const btn = document.getElementById('addExpenseBtn');
  if (!btn) return;

  // Default date = today
  const dateEl = document.getElementById('expDate');
  if (dateEl) dateEl.value = new Date().toISOString().split('T')[0];

  btn.addEventListener('click', () => {
    const description = document.getElementById('expName')?.value.trim();
    const amount      = parseFloat(document.getElementById('expAmount')?.value);
    const category    = document.getElementById('expCategory')?.value;
    const date        = document.getElementById('expDate')?.value || new Date().toISOString().split('T')[0];

    if (!description) { showToast('Please enter a description.', 'error'); return; }
    if (!amount || amount <= 0) { showToast('Please enter a valid amount.', 'error'); return; }

    const expenses = Store.get('traveloop_expenses', []);
    expenses.push({ id: Date.now().toString(), description, amount, category, date });
    Store.set('traveloop_expenses', expenses);

    // Reset
    document.getElementById('expName').value   = '';
    document.getElementById('expAmount').value = '';
    if (dateEl) dateEl.value = new Date().toISOString().split('T')[0];

    refresh();
    showToast(`${description} — ${fmt(amount)} added!`);
  });

  document.getElementById('clearExpenses')?.addEventListener('click', () => {
    if (!confirm('Clear all expenses?')) return;
    Store.set('traveloop_expenses', []);
    refresh();
    showToast('All expenses cleared.', 'info');
  });
}

/* ══════════════════════════════════════════════
   AI ESTIMATOR  — POST /budget/calculate
══════════════════════════════════════════════ */
function setupEstimator() {
  const btn = document.getElementById('estimateBtn');
  const result = document.getElementById('estimateResult');
  if (!btn) return;

  btn.addEventListener('click', async () => {
    const city    = document.getElementById('estCity')?.value.trim();
    const days    = parseInt(document.getElementById('estDays')?.value) || 5;
    const people  = parseInt(document.getElementById('estPeople')?.value) || 1;
    const style   = document.getElementById('estStyle')?.value || 'mid';
    const currency= Store.get('traveloop_currency', 'INR');

    if (!city) { showToast('Enter a destination city.', 'error'); return; }

    btn.disabled = true;
    btn.textContent = '⏳ Estimating…';
    if (result) result.style.display = 'none';

    try {
      const res = await fetch(`${API_BASE}/budget/calculate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ city, days, people, style, currency })
      });
      const json = await res.json();
      if (!json.success) throw new Error(json.message);

      const d = json.data;
      if (result) {
        result.style.display = 'block';
        result.innerHTML = `
          <div style="background:var(--surface-2);border-radius:var(--radius-md);padding:16px;margin-top:8px;">
            <div style="font-size:12px;color:var(--text-muted);margin-bottom:8px;font-weight:600;text-transform:uppercase;letter-spacing:.5px;">Estimate for ${city}</div>
            <div style="font-family:var(--font-display);font-size:24px;font-weight:800;color:var(--primary);margin-bottom:4px;">${fmt(d.total_cost, currency)}</div>
            <div style="font-size:13px;color:var(--text-secondary);">${fmt(d.cost_per_day, currency)}/day · ${days} days · ${people} person${people>1?'s':''}</div>
            ${d.breakdown ? `<div style="margin-top:12px;display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:12.5px;">
              ${Object.entries(d.breakdown).map(([k,v])=>`<div><span style="color:var(--text-muted)">${k}:</span> <strong>${fmt(v, currency)}</strong></div>`).join('')}
            </div>` : ''}
          </div>`;
      }

      // Update day cost estimate card
      const card = document.getElementById('estimateCard');
      const val  = document.getElementById('estimateCostVal');
      if (card && val) { card.style.display = 'flex'; val.textContent = fmt(d.cost_per_day, currency) + '/day'; }

      showToast('Budget estimate ready!');
    } catch (err) {
      showToast(`Estimate failed: ${err.message}`, 'error');
    } finally {
      btn.disabled = false;
      btn.textContent = '✈️ Estimate Budget';
    }
  });
}

/* ══════════════════════════════════════════════
   INIT
══════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', () => {
  // Pre-fill budget slider from storage
  const savedBudget   = Store.get('traveloop_budget', 50000);
  const savedDays     = Store.get('traveloop_days', 7);
  const savedCurrency = Store.get('traveloop_currency', 'INR');
  const daysEl     = document.getElementById('tripDays');
  const currencyEl = document.getElementById('tripCurrency');
  if (daysEl)     daysEl.value     = savedDays;
  if (currencyEl) currencyEl.value = savedCurrency;

  setupChartTabs();
  setupBudgetSlider();
  setupExpenseForm();
  setupEstimator();
  refresh();
});
