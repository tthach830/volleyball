# volleyball

A simple web app that shows volleyball court availability at the Santa Cruz Live Oak / Loch Lomond Community Center (LNCC) by proxying the City of Santa Cruz [WebTrac](https://casantacruzweb.myvscloud.com/webtrac/web/search.html?search=yes&module=FR&location=LNCC) facility reservation system.

## Features

- Fetches real-time volleyball court availability from the City of Santa Cruz WebTrac system
- Clean, responsive UI with color-coded availability status
- Fallback link to the official booking site when data cannot be fetched
- Direct link to make reservations

## Getting Started

```bash
# Install dependencies
npm install

# Start the server
npm start
```

Then open http://localhost:3000 in your browser.

## Usage

1. Click **Check Availability** to fetch the latest court availability
2. Courts are shown with color-coded status (green = available, red = unavailable)
3. Click **Open Booking Site** to go directly to the City of Santa Cruz booking page

## Data Source

Court availability is sourced from:  
https://casantacruzweb.myvscloud.com/webtrac/web/search.html?search=yes&module=FR&location=LNCC
