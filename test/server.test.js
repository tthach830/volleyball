const { test, describe } = require('node:test');
const assert = require('node:assert/strict');
const { parseAvailability } = require('../lib/parser');

describe('parseAvailability', () => {
  test('returns default heading when HTML has no headings', () => {
    const result = parseAvailability('<html><body></body></html>');
    assert.equal(result.heading, 'Volleyball Court Availability');
    assert.deepEqual(result.courts, []);
  });

  test('extracts heading from h1 element', () => {
    const html = '<html><body><h1>Court Schedule</h1></body></html>';
    const result = parseAvailability(html);
    assert.equal(result.heading, 'Court Schedule');
  });

  test('parses .facility-result rows', () => {
    const html = `
      <div class="facility-result">
        <span class="name">Beach Court 1</span>
        <span class="status">Available</span>
      </div>
      <div class="facility-result">
        <span class="name">Beach Court 2</span>
        <span class="status">Unavailable</span>
      </div>`;
    const result = parseAvailability(html);
    assert.equal(result.courts.length, 2);
    assert.equal(result.courts[0].name, 'Beach Court 1');
    assert.equal(result.courts[0].status, 'Available');
    assert.equal(result.courts[1].name, 'Beach Court 2');
    assert.equal(result.courts[1].status, 'Unavailable');
  });

  test('falls back to table parsing when known selectors absent', () => {
    const html = `
      <table>
        <tr><th>Facility</th><th>Status</th></tr>
        <tr><td>Court A</td><td>Open</td></tr>
        <tr><td>Court B</td><td>Booked</td></tr>
      </table>`;
    const result = parseAvailability(html);
    assert.equal(result.courts.length, 2);
    assert.equal(result.courts[0].name, 'Court A');
    assert.equal(result.courts[0].status, 'Open');
  });

  test('uses "See site for details" when status cell is empty', () => {
    const html = `
      <div class="facility-result">
        <span class="name">Sand Court</span>
      </div>`;
    const result = parseAvailability(html);
    assert.equal(result.courts[0].status, 'See site for details');
  });
});
