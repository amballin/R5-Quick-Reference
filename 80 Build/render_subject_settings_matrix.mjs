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
const sharp = runtimeRequire("sharp");

const workbook = Workbook.create();
const layout = payload.layout;
const sharedLayout = payload.shared_layout;
const sheet = workbook.worksheets.add(layout.worksheet);
sheet.showGridLines = false;

const profileHeaders = payload.profiles.map((profile) => profile.title);
const headers = [
  layout.columns.menu_location.heading,
  layout.columns.best_access.heading,
  layout.columns.setting.heading,
  layout.columns.default.heading,
  ...profileHeaders,
  "Card Order",
  "Rapid Setup Order",
];
const rows = payload.rows.map((row) => [
  row.menu_location,
  row.best_access,
  row.setting,
  row.default_value,
  ...row.values,
  row.card_order,
  row.rapid_order,
]);
const columnCount = headers.length;
const visibleLastColumn = columnName(columnCount);
const headerRow = 5;
const firstDataRow = headerRow + 1;
const lastRow = headerRow + rows.length;
const comparisonControls = layout.comparison_controls;
const targetCount = 1 + payload.profiles.length;
const firstTargetColumnNumber = 4;
const firstHelperColumnNumber = columnCount + 1;
const helperLastColumn = columnName(firstHelperColumnNumber + targetCount - 1);

const bannerWidthPx = layout.banner.width_px;
const bannerTexts = {
  title: layout.banner.title,
  instructions: layout.banner.instructions,
  note: `${layout.banner.note} ${payload.release_label}.`,
};
const bannerPanels = sharedLayout.banner.panels.map((panel, index) => ({
  row: index,
  heightPx: panel.height_px,
  fill: panel.fill,
  text: bannerTexts[panel.role],
  textColor: panel.text_color,
  fontSize: panel.font_size,
  fontWeight: panel.font_weight,
  fontStyle: panel.font_style,
}));
const bannerHeightPx = bannerPanels.reduce((total, panel) => total + panel.heightPx, 0);
const bannerDataUrl = await compositeBannerDataUrl(bannerPanels, bannerWidthPx, sharp);
sheet.images.add({
  dataUrl: bannerDataUrl,
  anchor: {
    from: { row: 0, col: 0 },
    extent: { widthPx: bannerWidthPx, heightPx: bannerHeightPx },
  },
});
sheet.getRange(`A${headerRow}:${visibleLastColumn}${lastRow}`).values = [headers, ...rows];

const table = sheet.tables.add(`A${headerRow}:${visibleLastColumn}${lastRow}`, true, layout.table_name);
table.style = "TableStyleMedium2";
table.showFilterButton = true;
table.showBandedRows = true;

sheet.getRange(`A${headerRow}:${visibleLastColumn}${headerRow}`).format = {
  fill: "#295D82",
  font: { bold: true, color: "#FFFFFF", size: 10 },
  wrapText: true,
  verticalAlignment: "center",
};
sheet.getRange(`A${headerRow}:A${headerRow}`).format.horizontalAlignment = "left";
sheet.getRange(`B${headerRow}:B${headerRow}`).format.horizontalAlignment = "center";
sheet.getRange(`C${headerRow}:C${headerRow}`).format.horizontalAlignment = "right";
sheet.getRange(`D${headerRow}:${visibleLastColumn}${headerRow}`).format.horizontalAlignment = "center";

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
sheet.getRange(`A${headerRow + 1}:A${lastRow}`).format.font = {
  bold: false,
};
sheet.getRange(`A${headerRow + 1}:A${lastRow}`).format.horizontalAlignment = "left";
sheet.getRange(`B${headerRow + 1}:C${lastRow}`).format.font = {
  bold: true,
};
sheet.getRange(`B${headerRow + 1}:B${lastRow}`).format.horizontalAlignment = "center";
sheet.getRange(`C${headerRow + 1}:C${lastRow}`).format.horizontalAlignment = "right";
sheet.getRange(`D${headerRow + 1}:${columnName(4 + payload.profiles.length)}${lastRow}`).format = {
  horizontalAlignment: "center",
  verticalAlignment: "center",
  wrapText: true,
};
sheet.getRange(`${columnName(columnCount - 1)}${headerRow + 1}:${visibleLastColumn}${lastRow}`).format = {
  horizontalAlignment: "center",
  verticalAlignment: "center",
  numberFormat: "0",
};

const profileBody = sheet.getRange(
  `D${headerRow + 1}:${columnName(4 + payload.profiles.length)}${lastRow}`,
);
const comparisonTargets = Array.from({ length: targetCount }, (_, index) => ({
  column: columnName(firstTargetColumnNumber + index),
  heading: headers[firstTargetColumnNumber - 1 + index],
}));
const comparisonHeadings = comparisonTargets.map((target) => target.heading);
const compareRow = comparisonControls.row;
sheet.getRange(`${comparisonControls.label_column}${compareRow}`).values = [["Compare to:"]];
sheet.getRange(`${comparisonControls.label_column}${compareRow}`).format = {
  fill: sharedLayout.colors.pale_warning,
  font: { bold: true, color: sharedLayout.colors.dark_text, size: 10 },
  horizontalAlignment: "center",
  verticalAlignment: "center",
};
for (let index = 0; index < comparisonTargets.length; index += 1) {
  const target = comparisonTargets[index];
  const helperColumn = columnName(firstHelperColumnNumber + index);
  const defaultHeading = index === 0 ? target.heading : comparisonControls.default_target;
  const selectorCell = sheet.getRange(`${target.column}${compareRow}`);
  selectorCell.values = [[defaultHeading]];
  selectorCell.dataValidation = { rule: { type: "list", values: comparisonHeadings } };
  selectorCell.format = {
    fill: sharedLayout.colors.pale_warning,
    font: { bold: true, color: comparisonControls.font_color, size: 10 },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    wrapText: true,
  };
  const helperFormulas = Array.from({ length: rows.length }, (_, rowOffset) => {
    const rowNumber = firstDataRow + rowOffset;
    const selectorFormula = comparisonTargets.reduceRight(
      (fallback, choice) =>
        `IF($${target.column}$${compareRow}="${choice.heading.replaceAll('"', '""')}",${choice.column}${rowNumber},${fallback})`,
      `""`,
    );
    return [`=${selectorFormula}`];
  });
  sheet.getRange(`${helperColumn}${firstDataRow}:${helperColumn}${lastRow}`).formulas = helperFormulas;
  sheet.getRange(`${target.column}${firstDataRow}:${target.column}${lastRow}`).conditionalFormats.add(
    "cellIs",
    {
      operator: "notEqual",
      formula: `$${helperColumn}${firstDataRow}`,
      format: {
        fill: sharedLayout.colors[comparisonControls.fill],
        font: { color: comparisonControls.font_color },
      },
    },
  );
}
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
sheet.getRange(`${columnName(firstHelperColumnNumber)}:${helperLastColumn}`).format.columnWidthPx =
  comparisonControls.helper_width_px;
sheet.getRange(`${columnName(firstHelperColumnNumber)}1:${helperLastColumn}${lastRow}`).format.font = {
  color: sharedLayout.colors.white,
  size: 1,
};

sheet.getRange("A:A").format.columnWidthPx = layout.columns.menu_location.width_px;
sheet.getRange("B:B").format.columnWidthPx = layout.columns.best_access.width_px;
sheet.getRange("C:C").format.columnWidthPx = layout.columns.setting.width_px;
sheet.getRange("D:D").format.columnWidth = layout.columns.default.width;
for (let index = 0; index < payload.profiles.length; index += 1) {
  const col = columnName(5 + index);
  sheet.getRange(`${col}:${col}`).format.columnWidth = layout.columns.profile.width;
}
sheet.getRange(`${columnName(columnCount - 1)}:${visibleLastColumn}`).format.columnWidth = layout.columns.order.width;
sharedLayout.banner.panels.forEach((panel, index) => {
  sheet.getRange(`${index + 1}:${index + 1}`).format.rowHeightPx = panel.height_px;
});
sheet.getRange("4:4").format.rowHeight = 22;
sheet.getRange(`${headerRow}:${lastRow}`).format.autofitRows();

sheet.freezePanes.freezeRows(headerRow);
sheet.freezePanes.freezeColumns(3);

const inspection = await workbook.inspect({
  kind: "table",
  range: `'${layout.worksheet}'!A${compareRow}:${visibleLastColumn}10`,
  include: "values,formulas",
  tableMaxRows: 10,
  tableMaxCols: columnCount,
  maxChars: 5000,
});
const inspectionTail = await workbook.inspect({
  kind: "table",
  range: `'${layout.worksheet}'!A11:${visibleLastColumn}${lastRow}`,
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
  sheetName: layout.worksheet,
  range: `A1:${visibleLastColumn}${lastRow}`,
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

async function compositeBannerDataUrl(panels, widthPx, sharpRenderer) {
  const heightPx = panels.reduce((total, panel) => total + panel.heightPx, 0);
  let offsetY = 0;
  const panelMarkup = panels.map((panel) => {
    const verticalCenter = offsetY + Math.round(panel.heightPx / 2);
    const markup = `
      <rect x="0" y="${offsetY}" width="100%" height="${panel.heightPx}" fill="${panel.fill}"/>
      <text
        x="10"
        y="${verticalCenter}"
        fill="${panel.textColor}"
        font-family="Arial, Helvetica, sans-serif"
        font-size="${panel.fontSize}px"
        font-weight="${panel.fontWeight}"
        font-style="${panel.fontStyle || "normal"}"
        dominant-baseline="middle"
      >${xmlEscape(panel.text)}</text>`;
    offsetY += panel.heightPx;
    return markup;
  }).join("");
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="${widthPx}" height="${heightPx}">
      ${panelMarkup}
    </svg>`;
  const png = await sharpRenderer(Buffer.from(svg)).png().toBuffer();
  return `data:image/png;base64,${png.toString("base64")}`;
}

function xmlEscape(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&apos;");
}
