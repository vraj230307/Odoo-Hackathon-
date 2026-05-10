/**
 * Traveloop — search.js
 * Member 3: City Search + Activity Search
 * Handles: API calls, autocomplete, filtering, sorting, trip cart
 */

/* ══════════════════════════════════════════════
   CONFIG
══════════════════════════════════════════════ */
const API_BASE = window.API_BASE || 'http://localhost:5000';

const ENDPOINTS = {
  cities:     `${API_BASE}/api/cities`,
  activities: `${API_BASE}/api/activities`,
};

/* ══════════════════════════════════════════════
   TRIP CART  (localStorage)
══════════════════════════════════════════════ */
const Cart = (() => {
  const KEY = 'traveloop_cart';

  function load()        { try { return JSON.parse(localStorage.getItem(KEY)) || []; } catch { return []; } }
  function save(items)   { localStorage.setItem(KEY, JSON.stringify(items)); }
  function getAll()      { return load(); }
  function add(item)     {
    const items = load();
    if (items.find(i => i.id === item.id && i.type === item.type)) return false;
    items.push(item);
    save(items);
    return true;
  }
  function remove(id, type) {
    const items = load().filter(i => !(i.id === id && i.type === type));
    save(items);
  }
  function total() {
    return load().reduce((s, i) => s + (Number(i.cost) || 0), 0);
  }
  return { getAll, add, remove, total };
})();

/* ══════════════════════════════════════════════
   TOAST
══════════════════════════════════════════════ */
function showToast(message, type = 'success') {
  const container = document.getElementById('toastContainer');
  if (!container) return;
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  const icons = { success: '✅', error: '❌', info: 'ℹ️' };
  t.innerHTML = `<span>${icons[type] || '✅'}</span><span>${message}</span>`;
  container.appendChild(t);
  setTimeout(() => t.remove(), 3200);
}

/* ══════════════════════════════════════════════
   GENERIC FETCH HELPER
══════════════════════════════════════════════ */
async function apiFetch(url, params = {}) {
  const qs = new URLSearchParams(
    Object.fromEntries(Object.entries(params).filter(([, v]) => v !== '' && v !== undefined))
  ).toString();
  const fullUrl = qs ? `${url}?${qs}` : url;
  const res = await fetch(fullUrl);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const json = await res.json();
  if (!json.success) throw new Error(json.message || 'API error');
  return json.data;
}

/* ══════════════════════════════════════════════
   FORMAT HELPERS
══════════════════════════════════════════════ */
function fmt(n)  { return '₹' + Number(n).toLocaleString('en-IN'); }
function stars(r){ return '★'.repeat(Math.round(r)) + '☆'.repeat(5 - Math.round(r)); }

/* ══════════════════════════════════════════════
   DEBOUNCE
══════════════════════════════════════════════ */
function debounce(fn, ms) {
  let t;
  return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
}

/* ══════════════════════════════════════════════
   AUTOCOMPLETE
══════════════════════════════════════════════ */
function setupAutocomplete({ inputEl, listEl, fetchFn, labelFn, onSelect }) {
  const debouncedFetch = debounce(async (q) => {
    if (!q || q.length < 2) { listEl.style.display = 'none'; return; }
    try {
      const results = await fetchFn(q);
      renderAutocomplete(results.slice(0, 6));
    } catch { listEl.style.display = 'none'; }
  }, 280);

  function renderAutocomplete(items) {
    if (!items.length) { listEl.style.display = 'none'; return; }
    listEl.innerHTML = items.map((item, i) => `
      <li class="autocomplete-item" role="option" tabindex="0" data-index="${i}">
        <div class="item-icon">${item.emoji || '📍'}</div>
        <div>
          <div class="item-name">${labelFn(item)}</div>
          <div class="item-meta">${item.country || item.city_name || item.category || ''}</div>
        </div>
        <span class="item-badge">${item.avg_cost_per_day ? fmt(item.avg_cost_per_day) + '/day' : (item.cost ? fmt(item.cost) : '')}</span>
      </li>
    `).join('');
    listEl.style.display = 'block';
    listEl.querySelectorAll('.autocomplete-item').forEach((el, i) => {
      el.addEventListener('click', () => { onSelect(items[i]); listEl.style.display = 'none'; inputEl.value = labelFn(items[i]); });
      el.addEventListener('keydown', e => { if (e.key === 'Enter') el.click(); });
    });
  }

  inputEl.addEventListener('input', e => debouncedFetch(e.target.value.trim()));
  document.addEventListener('click', e => { if (!inputEl.contains(e.target) && !listEl.contains(e.target)) listEl.style.display = 'none'; });
}

/* ══════════════════════════════════════════════
   CART RENDER
══════════════════════════════════════════════ */
function renderCart() {
  const items = Cart.getAll();
  const countEl = document.getElementById('cartCount');
  const bodyEl  = document.getElementById('cartBody');
  const totalEl = document.getElementById('cartTotal');
  if (countEl) countEl.textContent = items.length;
  if (totalEl) totalEl.textContent = fmt(Cart.total());
  if (!bodyEl) return;
  if (!items.length) {
    bodyEl.innerHTML = '<p style="color:var(--text-muted);font-size:13.5px;padding-top:16px;">Nothing added yet.</p>';
    return;
  }
  bodyEl.innerHTML = items.map(item => `
    <div class="cart-item">
      <span class="cart-item-icon">${item.emoji || '📍'}</span>
      <div class="cart-item-info">
        <div class="cart-item-name">${item.name}</div>
        <div class="cart-item-meta">${item.type} · ${fmt(item.cost || 0)}</div>
      </div>
      <button class="cart-item-remove" data-id="${item.id}" data-type="${item.type}" aria-label="Remove">✕</button>
    </div>
  `).join('');
  bodyEl.querySelectorAll('.cart-item-remove').forEach(btn => {
    btn.addEventListener('click', () => {
      Cart.remove(btn.dataset.id, btn.dataset.type);
      renderCart();
      updateAddedButtons();
    });
  });
}

function updateAddedButtons() {
  const cartIds = Cart.getAll().map(i => i.id);
  document.querySelectorAll('.card-add-btn').forEach(btn => {
    const id = btn.closest('[data-id]')?.dataset.id;
    if (id && cartIds.includes(id)) {
      btn.textContent = '✓ Added';
      btn.classList.add('added');
    }
  });
}

/* ══════════════════════════════════════════════
   CART PANEL TOGGLE
══════════════════════════════════════════════ */
function setupCartPanel() {
  const fab     = document.getElementById('cartFab');
  const cart    = document.getElementById('tripCart');
  const closeBtn= document.getElementById('cartClose');
  if (!fab || !cart) return;
  fab.addEventListener('click', () => cart.classList.toggle('open'));
  if (closeBtn) closeBtn.addEventListener('click', () => cart.classList.remove('open'));
}

/* ══════════════════════════════════════════════
   CITY SEARCH PAGE
══════════════════════════════════════════════ */
function initCitySearch() {
  const grid        = document.getElementById('cityGrid');
  const searchInput = document.getElementById('citySearchInput');
  const searchBtn   = document.getElementById('citySearchBtn');
  const autocomplete= document.getElementById('cityAutocomplete');
  const countrySelect= document.getElementById('countrySelect');
  const sortSelect  = document.getElementById('sortSelect');
  const resultCount = document.getElementById('resultCount');

  if (!grid) return;   // not on city page

  let allCities = [];
  let activeRegion = 'all';
  let activeCountry = '';
  let activeSort = 'name';
  let searchQuery = '';

  /* Fetch all cities */
  async function loadCities() {
    grid.innerHTML = '<div class="spinner"></div>';
    try {
      allCities = await apiFetch(ENDPOINTS.cities);
      populateCountrySelect();
      applyFilters();
    } catch (err) {
      grid.innerHTML = `<div class="empty-state"><div class="empty-icon">⚠️</div><h3>Failed to load cities</h3><p>${err.message}</p></div>`;
    }
  }

  function populateCountrySelect() {
    const countries = [...new Set(allCities.map(c => c.country))].sort();
    countrySelect.innerHTML = '<option value="">All Countries</option>' +
      countries.map(c => `<option value="${c}">${c}</option>`).join('');
  }

  /* Filtering + sorting */
  function applyFilters() {
    let filtered = [...allCities];

    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      filtered = filtered.filter(c => c.name.toLowerCase().includes(q) || (c.country || '').toLowerCase().includes(q));
    }
    if (activeRegion !== 'all') filtered = filtered.filter(c => c.region === activeRegion);
    if (activeCountry)          filtered = filtered.filter(c => c.country === activeCountry);

    // Dedup by id
    const seen = new Set();
    filtered = filtered.filter(c => { if (seen.has(c.id)) return false; seen.add(c.id); return true; });

    // Sort
    if (activeSort === 'name')      filtered.sort((a, b) => a.name.localeCompare(b.name));
    if (activeSort === 'cost_asc')  filtered.sort((a, b) => (a.avg_cost_per_day || 0) - (b.avg_cost_per_day || 0));
    if (activeSort === 'cost_desc') filtered.sort((a, b) => (b.avg_cost_per_day || 0) - (a.avg_cost_per_day || 0));
    if (activeSort === 'rating')    filtered.sort((a, b) => (b.rating || 0) - (a.rating || 0));

    renderCityCards(filtered);
    if (resultCount) resultCount.textContent = filtered.length;
  }

  function renderCityCards(cities) {
    if (!cities.length) {
      grid.innerHTML = `<div class="empty-state"><div class="empty-icon">🌍</div><h3>No cities found</h3><p>Try a different search or filter.</p></div>`;
      return;
    }
    const cartIds = Cart.getAll().map(i => i.id);
    grid.innerHTML = cities.map(city => `
      <article class="card" data-id="${city.id}">
        <div class="card-img">${city.emoji || '🏙️'}</div>
        ${city.featured ? '<span class="card-badge">Featured</span>' : ''}
        <div class="card-body">
          <div class="card-category">${city.region || 'Destination'}</div>
          <h2 class="card-title">${city.name}</h2>
          <p class="card-meta">
            <svg width="13" height="13" fill="none" viewBox="0 0 24 24"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z" fill="currentColor"/><circle cx="12" cy="9" r="2.5" fill="#fff"/></svg>
            ${city.country || ''}
          </p>
          <div class="card-footer">
            <div class="card-price">${fmt(city.avg_cost_per_day || 0)} <span>/day</span></div>
            <button class="card-add-btn ${cartIds.includes(city.id) ? 'added' : ''}"
              data-id="${city.id}" data-name="${city.name}"
              data-cost="${city.avg_cost_per_day || 0}" data-emoji="${city.emoji || '🏙️'}">
              ${cartIds.includes(city.id) ? '✓ Added' : '+ Add to Trip'}
            </button>
          </div>
        </div>
      </article>
    `).join('');

    grid.querySelectorAll('.card-add-btn:not(.added)').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const added = Cart.add({ id: btn.dataset.id, name: btn.dataset.name, cost: btn.dataset.cost, emoji: btn.dataset.emoji, type: 'city' });
        if (added) {
          btn.textContent = '✓ Added';
          btn.classList.add('added');
          renderCart();
          showToast(`${btn.dataset.name} added to trip!`);
        } else {
          showToast('Already in your trip.', 'info');
        }
      });
    });
  }

  /* Region chips */
  document.querySelectorAll('#cityFilterBar .filter-chip[data-region]').forEach(chip => {
    chip.addEventListener('click', () => {
      document.querySelectorAll('#cityFilterBar .filter-chip[data-region]').forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      activeRegion = chip.dataset.region;
      applyFilters();
    });
  });

  /* Country select */
  if (countrySelect) countrySelect.addEventListener('change', e => { activeCountry = e.target.value; applyFilters(); });
  if (sortSelect)    sortSelect.addEventListener('change', e => { activeSort = e.target.value; applyFilters(); });

  /* Search button */
  if (searchBtn) searchBtn.addEventListener('click', () => { searchQuery = searchInput.value.trim(); applyFilters(); });
  if (searchInput) {
    searchInput.addEventListener('keydown', e => { if (e.key === 'Enter') { searchQuery = e.target.value.trim(); applyFilters(); } });
  }

  /* Autocomplete */
  if (autocomplete && searchInput) {
    setupAutocomplete({
      inputEl:  searchInput,
      listEl:   autocomplete,
      fetchFn:  (q) => apiFetch(ENDPOINTS.cities, { q }),
      labelFn:  (c) => c.name,
      onSelect: (c) => { searchQuery = c.name; applyFilters(); },
    });
  }

  loadCities();
}

/* ══════════════════════════════════════════════
   ACTIVITY SEARCH PAGE
══════════════════════════════════════════════ */
function initActivitySearch() {
  const grid          = document.getElementById('activityGrid');
  const searchInput   = document.getElementById('activitySearchInput');
  const searchBtn     = document.getElementById('activitySearchBtn');
  const autocomplete  = document.getElementById('activityAutocomplete');
  const cityFilter    = document.getElementById('cityFilterSelect');
  const sortSelect    = document.getElementById('activitySortSelect');
  const resultCount   = document.getElementById('activityResultCount');

  if (!grid) return;   // not on activity page

  let allActivities = [];
  let activeCategory = 'all';
  let activePrice = 'all';
  let activeCity = '';
  let activeSort = 'name';
  let searchQuery = '';

  const PRICE_RANGES = { free: [0, 0], budget: [1, 500], mid: [501, 2000], premium: [2001, Infinity] };

  async function loadActivities() {
    grid.innerHTML = '<div class="spinner"></div>';
    try {
      allActivities = await apiFetch(ENDPOINTS.activities);
      populateCitySelect();
      applyFilters();
    } catch (err) {
      grid.innerHTML = `<div class="empty-state"><div class="empty-icon">⚠️</div><h3>Failed to load activities</h3><p>${err.message}</p></div>`;
    }
  }

  function populateCitySelect() {
    const cities = [...new Set(allActivities.map(a => a.city_name).filter(Boolean))].sort();
    if (cityFilter) {
      cityFilter.innerHTML = '<option value="">All Cities</option>' +
        cities.map(c => `<option value="${c}">${c}</option>`).join('');
    }
  }

  function applyFilters() {
    let filtered = [...allActivities];

    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      filtered = filtered.filter(a => a.name.toLowerCase().includes(q) || (a.description || '').toLowerCase().includes(q));
    }
    if (activeCategory !== 'all') filtered = filtered.filter(a => a.category === activeCategory);
    if (activeCity)               filtered = filtered.filter(a => a.city_name === activeCity);
    if (activePrice !== 'all') {
      const [lo, hi] = PRICE_RANGES[activePrice] || [0, Infinity];
      filtered = filtered.filter(a => (a.cost || 0) >= lo && (a.cost || 0) <= hi);
    }

    // Dedup
    const seen = new Set();
    filtered = filtered.filter(a => { if (seen.has(a.id)) return false; seen.add(a.id); return true; });

    // Sort
    if (activeSort === 'name')      filtered.sort((a, b) => a.name.localeCompare(b.name));
    if (activeSort === 'cost_asc')  filtered.sort((a, b) => (a.cost || 0) - (b.cost || 0));
    if (activeSort === 'cost_desc') filtered.sort((a, b) => (b.cost || 0) - (a.cost || 0));
    if (activeSort === 'rating')    filtered.sort((a, b) => (b.rating || 0) - (a.rating || 0));
    if (activeSort === 'duration')  filtered.sort((a, b) => (a.duration_hours || 0) - (b.duration_hours || 0));

    renderActivityCards(filtered);
    if (resultCount) resultCount.textContent = filtered.length;
  }

  function renderActivityCards(activities) {
    if (!activities.length) {
      grid.innerHTML = `<div class="empty-state"><div class="empty-icon">🎒</div><h3>No activities found</h3><p>Try adjusting your filters.</p></div>`;
      return;
    }
    const cartIds = Cart.getAll().map(i => i.id);
    grid.innerHTML = activities.map(act => `
      <article class="card" data-id="${act.id}">
        <div class="card-img">${act.emoji || '🎯'}</div>
        ${act.featured ? '<span class="card-badge">Popular</span>' : ''}
        <div class="card-body">
          <div class="card-category">${act.category || 'Activity'}</div>
          <h2 class="card-title">${act.name}</h2>
          <p class="card-meta">
            <svg width="13" height="13" fill="none" viewBox="0 0 24 24"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z" fill="currentColor"/><circle cx="12" cy="9" r="2.5" fill="#fff"/></svg>
            ${act.city_name || ''}
            ${act.duration_hours ? ` · ⏱ ${act.duration_hours}h` : ''}
          </p>
          ${act.rating ? `<div class="rating" style="margin-bottom:10px;">
            <span class="stars">${stars(act.rating)}</span>
            <span class="rating-val">${act.rating}</span>
          </div>` : ''}
          <div class="card-footer">
            <div class="card-price">${act.cost === 0 ? '<span style="color:var(--success);font-size:15px;font-weight:700;">Free</span>' : fmt(act.cost || 0)}</div>
            <button class="card-add-btn ${cartIds.includes(act.id) ? 'added' : ''}"
              data-id="${act.id}" data-name="${act.name}"
              data-cost="${act.cost || 0}" data-emoji="${act.emoji || '🎯'}">
              ${cartIds.includes(act.id) ? '✓ Added' : '+ Add'}
            </button>
          </div>
        </div>
      </article>
    `).join('');

    grid.querySelectorAll('.card-add-btn:not(.added)').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const added = Cart.add({ id: btn.dataset.id, name: btn.dataset.name, cost: btn.dataset.cost, emoji: btn.dataset.emoji, type: 'activity' });
        if (added) {
          btn.textContent = '✓ Added';
          btn.classList.add('added');
          renderCart();
          showToast(`${btn.dataset.name} added!`);
        } else {
          showToast('Already in your trip.', 'info');
        }
      });
    });
  }

  /* Category chips */
  document.querySelectorAll('#activityFilterBar .filter-chip[data-category]').forEach(chip => {
    chip.addEventListener('click', () => {
      document.querySelectorAll('#activityFilterBar .filter-chip[data-category]').forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      activeCategory = chip.dataset.category;
      applyFilters();
    });
  });

  /* Price chips */
  document.querySelectorAll('.filter-chip[data-price]').forEach(chip => {
    chip.addEventListener('click', () => {
      document.querySelectorAll('.filter-chip[data-price]').forEach(c => c.classList.remove('active'));
      if (activePrice === chip.dataset.price) { activePrice = 'all'; }
      else { chip.classList.add('active'); activePrice = chip.dataset.price; }
      applyFilters();
    });
  });

  if (cityFilter)  cityFilter.addEventListener('change', e => { activeCity = e.target.value; applyFilters(); });
  if (sortSelect)  sortSelect.addEventListener('change', e => { activeSort = e.target.value; applyFilters(); });

  if (searchBtn) searchBtn.addEventListener('click', () => { searchQuery = searchInput.value.trim(); applyFilters(); });
  if (searchInput) {
    searchInput.addEventListener('keydown', e => { if (e.key === 'Enter') { searchQuery = e.target.value.trim(); applyFilters(); } });
  }

  if (autocomplete && searchInput) {
    setupAutocomplete({
      inputEl:  searchInput,
      listEl:   autocomplete,
      fetchFn:  (q) => apiFetch(ENDPOINTS.activities, { q }),
      labelFn:  (a) => a.name,
      onSelect: (a) => { searchQuery = a.name; applyFilters(); },
    });
  }

  loadActivities();
}

/* ══════════════════════════════════════════════
   INIT
══════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', () => {
  setupCartPanel();
  renderCart();
  initCitySearch();
  initActivitySearch();
});
