const SETTINGS = {
  sheetName: 'Leads',
  secretProperty: 'WEBHOOK_SECRET'
};

function doPost(event) {
  const data = JSON.parse(event.postData.contents || '{}');
  const expected = PropertiesService.getScriptProperties().getProperty(SETTINGS.secretProperty);
  if (expected && data.secret !== expected) {
    return json_({ ok: false, error: 'forbidden' });
  }
  if (!data.name || !data.phone) {
    return json_({ ok: false, error: 'name and phone are required' });
  }

  const book = SpreadsheetApp.getActive();
  let sheet = book.getSheetByName(SETTINGS.sheetName);
  if (!sheet) {
    sheet = book.insertSheet(SETTINGS.sheetName);
    sheet.appendRow(['created_at', 'name', 'phone', 'comment', 'chat_id']);
  }
  sheet.appendRow([
    data.created_at || new Date().toISOString(),
    data.name,
    data.phone,
    data.comment || '',
    data.chat_id || ''
  ]);
  return json_({ ok: true });
}

function json_(value) {
  return ContentService
    .createTextOutput(JSON.stringify(value))
    .setMimeType(ContentService.MimeType.JSON);
}
