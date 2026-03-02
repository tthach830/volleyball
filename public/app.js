const BOOKING_URL =
  'https://casantacruzweb.myvscloud.com/webtrac/web/search.html?search=yes&module=FR&location=LNCC';

async function loadAvailability() {
  const btn = document.getElementById('refreshBtn');
  const statusEl = document.getElementById('status');
  const resultsEl = document.getElementById('results');
  const fallbackEl = document.getElementById('fallback');

  btn.disabled = true;
  btn.textContent = 'Loading…';

  // Show loading state
  statusEl.className = 'status-bar loading';
  statusEl.textContent = '⏳ Fetching latest court availability…';
  statusEl.hidden = false;
  resultsEl.hidden = true;
  fallbackEl.hidden = true;

  try {
    const resp = await fetch('/api/availability');

    if (!resp.ok) {
      throw new Error(`Server error: ${resp.status}`);
    }

    const data = await resp.json();

    if (data.error) {
      throw new Error(data.error);
    }

    statusEl.hidden = true;

    // Populate heading
    document.getElementById('resultsHeading').textContent =
      data.heading || 'Volleyball Court Availability';

    // Format fetched timestamp
    const ts = data.fetchedAt ? new Date(data.fetchedAt).toLocaleString() : '';
    document.getElementById('fetchedAt').textContent = ts
      ? `Last updated: ${ts}`
      : '';

    const grid = document.getElementById('courtsGrid');
    grid.innerHTML = '';

    if (data.courts && data.courts.length > 0) {
      data.courts.forEach((court) => {
        const card = document.createElement('div');
        card.className = 'court-card';

        const statusClass = classifyStatus(court.status);

        card.innerHTML = `
          <p class="court-name">${escHtml(court.name)}</p>
          <span class="court-status ${statusClass}">${escHtml(court.status)}</span>
        `;
        grid.appendChild(card);
      });
    } else {
      grid.innerHTML = `
        <p style="color: var(--muted); grid-column: 1/-1;">
          No court data found. Visit the
          <a href="${BOOKING_URL}" target="_blank" rel="noopener noreferrer">booking site</a>
          directly for full details.
        </p>`;
    }

    resultsEl.hidden = false;
  } catch (err) {
    statusEl.className = 'status-bar error';
    statusEl.textContent = `⚠️ Could not load court data: ${err.message}`;
    statusEl.hidden = false;
    fallbackEl.hidden = false;
  } finally {
    btn.disabled = false;
    btn.textContent = 'Refresh Availability';
  }
}

/** Classify a status string into a CSS class. */
function classifyStatus(status) {
  if (!status) return 'unknown';
  const s = status.toLowerCase();
  if (s.includes('avail') || s.includes('open') || s.includes('free')) return 'available';
  if (
    s.includes('not avail') ||
    s.includes('unavail') ||
    s.includes('closed') ||
    s.includes('full') ||
    s.includes('booked')
  )
    return 'unavailable';
  return 'unknown';
}

/** Escape HTML special characters. */
function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
