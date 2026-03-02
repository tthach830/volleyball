const express = require('express');
const fetch = require('node-fetch');
const cheerio = require('cheerio');
const path = require('path');
const { parseAvailability } = require('./lib/parser');

const app = express();
const PORT = process.env.PORT || 3000;

const WEBTRAC_BASE = 'https://casantacruzweb.myvscloud.com';
const SEARCH_URL = `${WEBTRAC_BASE}/webtrac/web/search.html?search=yes&module=FR&location=LNCC`;

app.use(express.static(path.join(__dirname, 'public')));

/**
 * Fetch a fresh CSRF token by loading the WebTrac page.
 */
async function fetchCsrfToken() {
  const resp = await fetch(`${WEBTRAC_BASE}/webtrac/web/search.html?module=FR&location=LNCC`, {
    headers: { 'User-Agent': 'Mozilla/5.0' },
  });
  const html = await resp.text();
  const $ = cheerio.load(html);
  const token =
    $('input[name="_csrf_token"]').val() ||
    $('meta[name="csrf-token"]').attr('content') ||
    (html.match(/_csrf_token['"]\s*:\s*['"]([^'"]+)['"]/) || [])[1];
  const cookies = resp.headers.get('set-cookie') || '';
  return { token, cookies };
}

app.get('/api/availability', async (req, res) => {
  try {
    const { token, cookies } = await fetchCsrfToken();

    const searchUrl = token
      ? `${SEARCH_URL}&_csrf_token=${encodeURIComponent(token)}`
      : SEARCH_URL;

    const fetchOpts = {
      headers: {
        'User-Agent': 'Mozilla/5.0',
        ...(cookies ? { Cookie: cookies } : {}),
      },
    };

    const resp = await fetch(searchUrl, fetchOpts);

    if (!resp.ok) {
      return res.status(502).json({ error: `WebTrac returned status ${resp.status}` });
    }

    const html = await resp.text();
    const data = parseAvailability(html);

    res.json({
      ...data,
      url: SEARCH_URL,
      fetchedAt: new Date().toISOString(),
    });
  } catch (err) {
    res.status(502).json({ error: err.message });
  }
});

app.listen(PORT, () => {
  console.log(`Volleyball courts server running on http://localhost:${PORT}`);
});
