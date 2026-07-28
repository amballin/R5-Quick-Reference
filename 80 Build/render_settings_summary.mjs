import fs from "node:fs/promises";
import path from "node:path";
import { createRequire } from "node:module";
import { pathToFileURL } from "node:url";


const payloadPath = process.argv[2];
if (!payloadPath) {
  throw new Error("Expected a subject-settings summary payload path.");
}

const payload = JSON.parse(await fs.readFile(payloadPath, "utf8"));
const runtimeRequire = createRequire(path.join(payload.runtime_dir, "package.json"));
const artifactEntry = runtimeRequire.resolve("@oai/artifact-tool");
const { SpreadsheetFile, Workbook } = await import(pathToFileURL(artifactEntry).href);

const workbook = Workbook.create();
const sheet = workbook.worksheets.add("Subject Settings Summary");
sheet.showGridLines = false;

const profileHeaders = payload.profiles.map((profile) => profile.title);
const headers = [
  "Setting",
  "Best or Quick Access",
  "Menu Location",
  "Default Settings",
  ...profileHeaders,
  "Card Order",
  "Rapid Setup Order",
];
const rows = payload.rows.map((row) => [
  row.setting,
  row.best_access,
  row.menu_location,
  row.default_value,
  ...row.values,
  row.card_order,
  row.rapid_order,
]);
const columnCount = headers.length;
const lastColumn = columnName(columnCount);
const headerRow = 5;
const lastRow = headerRow + rows.length;

sheet.getRange(`A1:${lastColumn}1`).merge();
sheet.getRange("A1").values = [["Subject Settings Summary"]];
sheet.getRange(`A2:${lastColumn}2`).merge();
sheet.getRange("A2").values = [[
  "Sort Rapid Setup Order ascending for efficient camera configuration. Sort Card Order ascending to restore the reference-card sequence.",
]];
sheet.getRange(`A3:${lastColumn}3`).merge();
sheet.getRange("A3").values = [[
  "Amber profile headers are authored but not currently released. “Not Used” marks settings made inapplicable by Manual Focus or the selected AF method.",
]];
sheet.getRange(`A${headerRow}:${lastColumn}${lastRow}`).values = [headers, ...rows];

const table = sheet.tables.add(`A${headerRow}:${lastColumn}${lastRow}`, true, "SubjectSettingsTable");
table.style = "TableStyleMedium2";
table.showFilterButton = true;
table.showBandedRows = true;

sheet.getRange(`A1:${lastColumn}1`).format = {
  fill: "#17324D",
  font: { bold: true, color: "#FFFFFF", size: 18 },
  verticalAlignment: "center",
};
sheet.getRange(`A2:${lastColumn}2`).format = {
  fill: "#DCE8F2",
  font: { color: "#17324D", size: 10 },
  wrapText: true,
  verticalAlignment: "center",
};
sheet.getRange(`A3:${lastColumn}3`).format = {
  fill: "#F2F5F7",
  font: { color: "#52606D", italic: true, size: 9 },
  wrapText: true,
  verticalAlignment: "center",
};
sheet.getRange(`A${headerRow}:${lastColumn}${headerRow}`).format = {
  fill: "#295D82",
  font: { bold: true, color: "#FFFFFF", size: 10 },
  wrapText: true,
  verticalAlignment: "center",
};

for (let index = 0; index < payload.profiles.length; index += 1) {
  if (!payload.profiles[index].release) {
    const col = columnName(5 + index);
    sheet.getRange(`${col}${headerRow}`).format = {
      fill: "#B7791F",
      font: { bold: true, color: "#FFFFFF", size: 10 },
      wrapText: true,
      verticalAlignment: "center",
    };
  }
}

sheet.getRange(`A${headerRow + 1}:C${lastRow}`).format = {
  verticalAlignment: "center",
  wrapText: true,
};
sheet.getRange(`D${headerRow + 1}:${columnName(4 + payload.profiles.length)}${lastRow}`).format = {
  verticalAlignment: "center",
  wrapText: true,
};
sheet.getRange(`${columnName(columnCount - 1)}${headerRow + 1}:${lastColumn}${lastRow}`).format = {
  horizontalAlignment: "center",
  verticalAlignment: "center",
  numberFormat: "0",
};

const profileBody = sheet.getRange(
  `D${headerRow + 1}:${columnName(4 + payload.profiles.length)}${lastRow}`,
);
profileBody.conditionalFormats.add("containsText", {
  text: "Not Used",
  format: {
    fill: "#E7EAED",
    font: { color: "#6B7280", italic: true },
  },
});
profileBody.conditionalFormats.add("cellIs", {
  operator: "equal",
  formula: '"—"',
  format: {
    font: { color: "#9AA4AE", italic: true },
  },
});

sheet.getRange("A:A").format.columnWidth = 23;
sheet.getRange("B:B").format.columnWidth = 31;
sheet.getRange("C:C").format.columnWidth = 39;
sheet.getRange("D:D").format.columnWidth = 20;
for (let index = 0; index < payload.profiles.length; index += 1) {
  const col = columnName(5 + index);
  sheet.getRange(`${col}:${col}`).format.columnWidth = 20;
}
sheet.getRange(`${columnName(columnCount - 1)}:${lastColumn}`).format.columnWidth = 12;
sheet.getRange("1:1").format.rowHeight = 30;
sheet.getRange("2:2").format.rowHeight = 32;
sheet.getRange("3:3").format.rowHeight = 28;
sheet.getRange(`${headerRow}:${headerRow}`).format.rowHeight = 42;
sheet.getRange(`${headerRow + 1}:${lastRow}`).format.rowHeight = 36;

sheet.freezePanes.freezeRows(headerRow);
sheet.freezePanes.freezeColumns(4);

const inspection = await workbook.inspect({
  kind: "table",
  range: `Subject Settings Summary!A1:${lastColumn}10`,
  include: "values,formulas",
  tableMaxRows: 10,
  tableMaxCols: columnCount,
  maxChars: 5000,
});
const inspectionTail = await workbook.inspect({
  kind: "table",
  range: `Subject Settings Summary!A11:${lastColumn}${lastRow}`,
  include: "values,formulas",
  tableMaxRows: 10,
  tableMaxCols: columnCount,
  maxChars: 5000,
});
const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 100 },
  summary: "subject-settings formula error scan",
});
console.log(inspection.ndjson);
console.log(inspectionTail.ndjson);
console.log(errors.ndjson);

await fs.mkdir(path.dirname(payload.output), { recursive: true });
const preview = await workbook.render({
  sheetName: "Subject Settings Summary",
  range: `A1:${lastColumn}${lastRow}`,
  scale: 1,
  format: "png",
});
await fs.writeFile(payload.preview, new Uint8Array(await preview.arrayBuffer()));
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(payload.output);

function columnName(number) {
  let result = "";
  let value = number;
  while (value > 0) {
    const remainder = (value - 1) % 26;
    result = String.fromCharCode(65 + remainder) + result;
    value = Math.floor((value - 1) / 26);
  }
  return result;
}
