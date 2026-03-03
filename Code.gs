function doPost(e) {
  // Allow cross-origin requests from any domain (your website)
  var headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Content-Type": "application/json"
  };

  try {
    // Attempt to parse the incoming request data
    var data = JSON.parse(e.postData.contents);
    var courtName = data.courtName;
    var timeSlot = data.timeSlot;
    var newStatus = data.newStatus || "unavailable";
    
    // Open the Google Sheet by its exact ID to ensure it finds it
    var spreadsheet = SpreadsheetApp.openById("1bPhadhGcRUMPp-xsKcWx5M9LFQ_sheHoYbtZJEPMQ0g");
    var sheet = spreadsheet.getSheets()[0]; // Always targets the first tab
    if (!sheet) {
      return ContentService.createTextOutput(JSON.stringify({
        "status": "error",
        "message": "First sheet not found"
      })).setMimeType(ContentService.MimeType.JSON);
    }
    
    // Find the current data range
    var range = sheet.getDataRange();
    var values = range.getValues();
    
    // Find row index (Court Name)
    // Court names are in column A (index 0), starting from row 2 (index 1)
    var rowIndex = -1;
    for (var i = 1; i < values.length; i++) {
      if (String(values[i][0]).trim() === courtName) {
        rowIndex = i;
        break;
      }
    }
    
    // Find column index (Time Slot)
    // Time slots are in row 1 (index 0), starting from column B (index 1)
    var colIndex = -1;
    for (var j = 1; j < values[0].length; j++) {
      if (String(values[0][j]).trim() === timeSlot) {
        colIndex = j;
        break;
      }
    }
    
    // If we found both the court and the time slot
    if (rowIndex !== -1 && colIndex !== -1) {
      // Arrays are 0-indexed, but getRange is 1-indexed
      var cell = sheet.getRange(rowIndex + 1, colIndex + 1);
      
      // Update the cell value
      cell.setValue(newStatus);
      
      // Add a note/comment with the timestamp
      var now = new Date();
      // Format timestamp nicely to match doGet
      var timestamp = now.toLocaleString("en-US", {
        timeZone: "America/Los_Angeles",
        month: "short",
        day: "numeric",
        hour: "numeric",
        minute: "2-digit",
        hour12: true
      });
      cell.setNote("Status manually changed to " + newStatus + " via website at: " + timestamp);
      
      // Also write the timestamp to the "LastUpdated" or "Timestamp" column if it exists
      var lastUpdatedColIndex = -1;
      for (var k = 0; k < values[0].length; k++) {
        var headerName = String(values[0][k]).trim().toLowerCase();
        if (headerName === "lastupdated" || headerName === "timestamp") {
          lastUpdatedColIndex = k;
          break;
        }
      }
      
      if (lastUpdatedColIndex !== -1) {
        var lastUpdatedCell = sheet.getRange(rowIndex + 1, lastUpdatedColIndex + 1);
        lastUpdatedCell.setValue(timestamp);
      }
      
      return ContentService.createTextOutput(JSON.stringify({
        "status": "success",
        "message": "Successfully updated " + courtName + " at " + timeSlot,
        "timestamp": timestamp
      })).setMimeType(ContentService.MimeType.JSON);
      
    } else {
      return ContentService.createTextOutput(JSON.stringify({
        "status": "error",
        "message": "Could not find court '" + courtName + "' or time slot '" + timeSlot + "'"
      })).setMimeType(ContentService.MimeType.JSON);
    }
    
  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({
        "status": "error",
        "message": error.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

// Handle preflight OPTIONS requests required by browsers (CORS)
function doOptions(e) {
  var headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "86400"
  };
  
  var response = ContentService.createTextOutput("")
    .setMimeType(ContentService.MimeType.TEXT);
    
  // Append headers directly to the response object if possible,
  return response;
}

// Return table data using GET
function doGet(e) {
  try {
    var spreadsheet = SpreadsheetApp.openById("1bPhadhGcRUMPp-xsKcWx5M9LFQ_sheHoYbtZJEPMQ0g");
    var sheet = spreadsheet.getSheets()[0];
    if (!sheet) {
      return ContentService.createTextOutput(JSON.stringify({
        "status": "error",
        "message": "First sheet not found"
      })).setMimeType(ContentService.MimeType.JSON);
    }
    
    var range = sheet.getDataRange();
    var values = range.getDisplayValues();
    
    // Get file's last updated time natively without DriveApp if possible, 
    // or fallback to simply letting the frontend know it loaded successfully without a global timestamp
    // since the table tracks individual 'LastUpdated' cells anyway.
    
    // Format a simple generated timestamp to avoid OAuth permission crashes
    var now = new Date();
    var timestamp = now.toLocaleString("en-US", {
      timeZone: "America/Los_Angeles",
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
      hour12: true
    }) + " (Loaded)";
    
    return ContentService.createTextOutput(JSON.stringify({
      "status": "success",
      "data": values,
      "lastUpdated": timestamp
    })).setMimeType(ContentService.MimeType.JSON);
    
  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({
      "status": "error",
      "message": error.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}
