const cheerio = require('cheerio');

/**
 * Parse the WebTrac search results HTML and return structured court data.
 * @param {string} html - Raw HTML from the WebTrac facility search page
 * @returns {{ heading: string, courts: Array<{name: string, status: string}> }}
 */
function parseAvailability(html) {
  const $ = cheerio.load(html);
  const courts = [];

  // WebTrac renders facility results as divs with class "subnavrow" or table rows.
  // Try multiple known selectors used across WebTrac versions.
  const rows = $('.fr-facility-row, .rgRow, .rgAltRow, tr.searchresult, .facility-result, .list-item');

  if (rows.length > 0) {
    rows.each((_, el) => {
      const name = $(el).find('.facility-name, .name, td:first-child').first().text().trim();
      const status = $(el).find('.availability, .status, td.available').first().text().trim();
      if (name) {
        courts.push({ name, status: status || 'See site for details' });
      }
    });
  }

  // Fallback: parse any table that looks like it has facility/court data
  if (courts.length === 0) {
    $('table').each((_, table) => {
      const headers = [];
      $(table)
        .find('th')
        .each((_, th) => headers.push($(th).text().trim().toLowerCase()));

      if (
        headers.some((h) => h.includes('facility') || h.includes('court') || h.includes('location'))
      ) {
        $(table)
          .find('tr')
          .slice(1)
          .each((_, row) => {
            const cells = [];
            $(row)
              .find('td')
              .each((_, td) => cells.push($(td).text().trim()));
            if (cells.length > 0 && cells[0]) {
              courts.push({
                name: cells[0],
                status: cells[1] || 'See site for details',
              });
            }
          });
      }
    });
  }

  // Extract page title / heading for context
  const heading =
    $('h1, h2, .page-title, .results-heading').first().text().trim() ||
    'Volleyball Court Availability';

  return { heading, courts };
}

module.exports = { parseAvailability };
