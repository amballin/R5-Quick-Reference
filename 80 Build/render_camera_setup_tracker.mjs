import fs from "node:fs/promises";
import path from "node:path";
import { createRequire } from "node:module";
import { pathToFileURL } from "node:url";


const payloadPath = process.argv[2];
if (!payloadPath) {
  throw new Error("Expected a camera-setup tracker payload path.");
}

const payload = JSON.parse(await fs.readFile(payloadPath, "utf8"));
const runtimeRequire = createRequire(path.join(payload.runtime_dir, "package.json"));
const artifactEntry = runtimeRequire.resolve("@oai/artifact-tool");
const { FileBlob, SpreadsheetFile, Workbook } = await import(pathToFileURL(artifactEntry).href);
const sharp = runtimeRequire("sharp");

const layout = payload.layout;
const shared = payload.shared_layout;
const source = payload.source;
const sheets = layout.sheets;
const colors = shared.colors;
const fontName = shared.font_family;
const migration = payload.migration_source
  ? await readMigration(payload.migration_source, FileBlob, SpreadsheetFile)
  : payload.status
    ? statusMigration(payload.status)
    : emptyMigration();

const workbook = Workbook.create();
const dashboard = workbook.worksheets.add(sheets.dashboard.name);
const checklist = workbook.worksheets.add(sheets.checklist.name);
const registration = workbook.worksheets.add(sheets.registration.name);
const sessions = workbook.worksheets.add(sheets.sessions.name);
const lists = workbook.worksheets.add(sheets.lists.name);
const menu = workbook.worksheets.add(sheets.menu.name);
const metadata = workbook.worksheets.add(sheets.metadata.name);

for (const sheet of workbook.worksheets.items) {
  sheet.showGridLines = false;
}

const tests = source.tests;
const checklistHeaderRow = 5;
const checklistFirstDataRow = checklistHeaderRow + 1;
const checklistLastRow = checklistHeaderRow + tests.length;
const checklistColumns = sheets.checklist.columns;
const checklistLastColumn = columnName(checklistColumns.length);
const menuLastRow = tests.length + 1;
const registrationLastRow = 4 + source.registration.rows.length;
const checklistBannerDataUrl = await compositeBannerDataUrl(
  configuredBannerPanels(),
  layout.banner.width_px,
  sharp,
);

buildLists();
buildMenu();
buildChecklist();
buildRegistration();
buildSessions();
buildDashboard();
buildMetadata();

const checklistInspection = await workbook.inspect({
  kind: "table",
  range: `'${sheets.checklist.name}'!A${checklistHeaderRow}:${checklistLastColumn}${Math.min(checklistLastRow, 12)}`,
  include: "values,formulas",
  tableMaxRows: 12,
  tableMaxCols: checklistColumns.length,
  maxChars: 9000,
});
console.log(checklistInspection.ndjson);
const formulaErrors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 300 },
  summary: "camera-setup tracker formula error scan",
});
console.log(formulaErrors.ndjson);

await fs.mkdir(payload.preview_dir, { recursive: true });
for (const sheet of workbook.worksheets.items) {
  const renderOptions = sheet.name === sheets.checklist.name
    ? {
        sheetName: sheet.name,
        range: `A1:${checklistLastColumn}${checklistLastRow}`,
        scale: 1,
        format: "png",
      }
    : sheet.name === sheets.registration.name
      ? {
          sheetName: sheet.name,
          range: `A1:N${registrationLastRow}`,
          scale: 1,
          format: "png",
        }
      : {
        sheetName: sheet.name,
        autoCrop: "all",
        scale: 1,
        format: "png",
      };
  const preview = await workbook.render(renderOptions);
  const safeName = sheet.name.replaceAll(/[^A-Za-z0-9_-]/g, "_");
  await fs.writeFile(
    path.join(payload.preview_dir, `${safeName}.png`),
    new Uint8Array(await preview.arrayBuffer()),
  );
}
await fs.mkdir(path.dirname(payload.output), { recursive: true });
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(payload.output);


function buildLists() {
  const columns = [
    ["Main Status", ...source.lists.main_status],
    ["Evidence Class", ...source.lists.evidence_class],
    ["Yes / No", ...source.lists.yes_no],
    ["Registration Result", ...source.lists.registration_result],
    ["Comparison Target", "Default Settings", ...source.registration.profiles.map((profile) => profile.heading)],
  ];
  const rowCount = Math.max(...columns.map((column) => column.length));
  const lastColumn = columnName(columns.length);
  const values = Array.from({ length: rowCount }, (_, rowIndex) =>
    columns.map((column) => column[rowIndex] ?? null),
  );
  lists.getRange(`A1:${lastColumn}${rowCount}`).values = values;
  lists.getRange(`A1:${lastColumn}1`).format = headerFormat();
  lists.getRange(`A2:${lastColumn}${rowCount}`).format = {
    font: { name: fontName, size: 11 },
    verticalAlignment: "center",
  };
  lists.getRange(`A:${lastColumn}`).format.columnWidth = 31;
  lists.freezePanes.freezeRows(1);
}


function buildMenu() {
  const columns = sheets.menu.columns;
  const headers = columns.map((column) => column.heading);
  const rows = tests.map((test) => columns.map((column) => test[column.key] ?? ""));
  menu.getRange(`A1:E${menuLastRow}`).values = [headers, ...rows];
  const table = menu.tables.add(`A1:E${menuLastRow}`, true, sheets.menu.table_name);
  table.style = "TableStyleMedium2";
  table.showFilterButton = true;
  table.showBandedRows = true;
  menu.getRange("A1:E1").format = headerFormat();
  menu.getRange(`A2:E${menuLastRow}`).format = {
    font: { name: fontName, size: 11 },
    verticalAlignment: "center",
  };
  columns.forEach((column, index) => {
    const letter = columnName(index + 1);
    menu.getRange(`${letter}:${letter}`).format.columnWidthPx = pointsToPixels(column.width_pt);
    menu.getRange(`${letter}2:${letter}${menuLastRow}`).format = {
      font: { name: fontName, size: 11, bold: column.bold === true },
      horizontalAlignment: column.alignment,
      verticalAlignment: "center",
      wrapText: column.wrap === true,
    };
  });
  menu.getRange(`1:${menuLastRow}`).format.autofitRows();
  menu.freezePanes.freezeRows(sheets.menu.freeze_rows);
  menu.freezePanes.freezeColumns(sheets.menu.freeze_columns);
}


function buildChecklist() {
  checklist.images.add({
    dataUrl: checklistBannerDataUrl,
    anchor: {
      from: { row: 0, col: 0 },
      extent: { widthPx: layout.banner.width_px, heightPx: shared.banner.height_px },
    },
  });

  const headers = checklistColumns.map((column) => column.heading);
  const rows = tests.map((test) => {
    const migrated = migration.checklist.get(test.test_id) || {};
    const blankState = {
      status: test.status || "Not started",
      test_date: "",
      session_id: "",
      evidence_files: "",
      observation: test.observation || "",
      next_action: test.next_action || "",
      evidence_class: test.evidence_class || "Approved target pending verification",
      project_update: test.project_update || "No",
      target_project_files: test.target_project_files || "",
      updated_in_project: test.project_update === "No" ? "Not applicable" : "No",
    };
    const state = { ...blankState, ...migrated };
    return checklistColumns.map((column) => {
      if (["best_access", "menu_location", "menu_detail"].includes(column.key)) {
        return "";
      }
      return state[column.key] ?? test[column.key] ?? "";
    });
  });
  checklist.getRange(`A${checklistHeaderRow}:${checklistLastColumn}${checklistLastRow}`).values = [
    headers,
    ...rows,
  ];

  const table = checklist.tables.add(
    `A${checklistHeaderRow}:${checklistLastColumn}${checklistLastRow}`,
    true,
    sheets.checklist.table_name,
  );
  table.style = "TableStyleMedium2";
  table.showFilterButton = true;
  table.showBandedRows = true;

  const lookupRange = `'${sheets.menu.name}'!$A$2:$E$${menuLastRow}`;
  checklist.getRange(`F${checklistFirstDataRow}`).formulas = [[
    `=IFERROR(VLOOKUP($A${checklistFirstDataRow},${lookupRange},2,FALSE),"")`,
  ]];
  checklist.getRange(`F${checklistFirstDataRow}:F${checklistLastRow}`).fillDown();
  checklist.getRange(`G${checklistFirstDataRow}`).formulas = [[
    `=IFERROR(VLOOKUP($A${checklistFirstDataRow},${lookupRange},3,FALSE),"")`,
  ]];
  checklist.getRange(`G${checklistFirstDataRow}:G${checklistLastRow}`).fillDown();
  checklist.getRange(`H${checklistFirstDataRow}`).formulas = [[
    `=IFERROR(VLOOKUP($A${checklistFirstDataRow},${lookupRange},4,FALSE),"")`,
  ]];
  checklist.getRange(`H${checklistFirstDataRow}:H${checklistLastRow}`).fillDown();

  checklist.getRange(`A${checklistHeaderRow}:${checklistLastColumn}${checklistHeaderRow}`).format = headerFormat();
  checklistColumns.forEach((column, index) => {
    const letter = columnName(index + 1);
    checklist.getRange(`${letter}:${letter}`).format.columnWidthPx = pointsToPixels(column.width_pt);
    checklist.getRange(`${letter}${checklistFirstDataRow}:${letter}${checklistLastRow}`).format = {
      font: { name: fontName, size: 11, bold: column.bold === true },
      horizontalAlignment: column.alignment,
      verticalAlignment: "center",
      wrapText: column.wrap === true,
    };
  });
  checklist.getRange(`J${checklistFirstDataRow}:J${checklistLastRow}`).format.numberFormat = "yyyy-mm-dd";
  checklist.getRange(`I${checklistFirstDataRow}:I${checklistLastRow}`).dataValidation = {
    rule: { type: "list", values: source.lists.main_status },
  };
  checklist.getRange(`O${checklistFirstDataRow}:O${checklistLastRow}`).dataValidation = {
    rule: { type: "list", values: source.lists.evidence_class },
  };
  checklist.getRange(`P${checklistFirstDataRow}:P${checklistLastRow}`).dataValidation = {
    rule: { type: "list", values: source.lists.yes_no },
  };
  checklist.getRange(`R${checklistFirstDataRow}:R${checklistLastRow}`).dataValidation = {
    rule: { type: "list", values: source.lists.yes_no },
  };
  addStatusFormatting(checklist.getRange(`I${checklistFirstDataRow}:I${checklistLastRow}`));

  shared.banner.panels.forEach((panel, index) => {
    checklist.getRange(`${index + 1}:${index + 1}`).format.rowHeightPx = panel.height_px;
  });
  checklist.getRange("4:4").format.rowHeightPx = shared.banner.spacer_height_px;
  checklist.getRange(`${checklistHeaderRow}:${checklistLastRow}`).format.autofitRows();
  checklist.freezePanes.freezeRows(sheets.checklist.excel.freeze_rows);
  checklist.freezePanes.freezeColumns(sheets.checklist.excel.freeze_columns);
}


function buildRegistration() {
  const specification = source.registration;
  const comparisonControls = sheets.registration.comparison_controls;
  registration.getRange("A1:N1").merge();
  registration.getRange("A1").values = [[specification.title]];
  registration.getRange("A2:N2").merge();
  registration.getRange("A2").values = [[specification.instructions]];
  registration.getRange("A1:N1").format = titleBandFormat(16);
  registration.getRange("A2:N2").format = noteBandFormat();
  registration.getRange("3:3").format.rowHeight = 22;

  const headers = ["Setting", "Default Settings"];
  for (const profile of specification.profiles) {
    headers.push(
      `${profile.heading} Target`,
      `${profile.heading.split(" ")[0]} Configured`,
      `${profile.heading.split(" ")[0]} Read-back`,
      `${profile.heading.split(" ")[0]} Notes`,
    );
  }
  const rows = specification.rows.map((row) => {
    const migrated = migration.registration.get(row.setting) || {};
    const values = [row.setting, row.default_value];
    for (const profile of specification.profiles) {
      values.push(
        row[profile.key],
        migrated[`${profile.key}_configured`] || "Not started",
        migrated[`${profile.key}_read_back`] || "Not started",
        migrated[`${profile.key}_notes`] || "",
      );
    }
    return values;
  });
  const lastRow = registrationLastRow;
  const firstDataRow = 5;
  registration.getRange(`A4:N${lastRow}`).values = [headers, ...rows];
  const table = registration.tables.add(`A4:N${lastRow}`, true, "RegistrationTable");
  table.style = "TableStyleMedium2";
  table.showFilterButton = true;
  table.showBandedRows = true;
  registration.getRange("A4:N4").format = headerFormat();
  registration.getRange(`A5:N${lastRow}`).format = {
    font: { name: fontName, size: 11 },
    verticalAlignment: "center",
    wrapText: true,
  };
  for (const [column, alignment] of Object.entries(sheets.registration.column_alignments || {})) {
    registration.getRange(`${column}5:${column}${lastRow}`).format.horizontalAlignment = alignment;
  }
  const widths = [150, 168, 168, 96, 96, 180, 168, 96, 96, 180, 168, 96, 96, 180];
  widths.forEach((width, index) => {
    const letter = columnName(index + 1);
    registration.getRange(`${letter}:${letter}`).format.columnWidthPx = pointsToPixels(width);
  });
  const compareRow = comparisonControls.row;
  const comparisonTargets = Object.entries(comparisonControls.targets).map(
    ([column, targetConfig]) => {
      if (targetConfig.source === "default") {
        return { column, heading: "Default Settings" };
      }
      const profile = specification.profiles.find((item) => item.key === targetConfig.profile);
      if (!profile) {
        throw new Error(`Missing comparison profile: ${targetConfig.profile}`);
      }
      return { column, heading: profile.heading };
    },
  );
  const comparisonHeadings = comparisonTargets.map((target) => target.heading);
  const labelCell = registration.getRange(`${comparisonControls.label_column}${compareRow}`);
  labelCell.values = [["Compare to:"]];
  labelCell.format = {
    fill: colors.pale_warning,
    font: { name: fontName, size: 10, bold: true, color: colors.dark_text },
    horizontalAlignment: "center",
    verticalAlignment: "center",
  };
  for (const [targetColumn, targetConfig] of Object.entries(comparisonControls.targets)) {
    const helperColumn = targetConfig.helper;
    const defaultTarget = comparisonTargets.find((target) => target.column === targetConfig.default);
    if (!defaultTarget) {
      throw new Error(`Missing default comparison target column: ${targetConfig.default}`);
    }
    const controlCell = registration.getRange(`${targetColumn}${compareRow}`);
    controlCell.values = [[defaultTarget.heading]];
    controlCell.dataValidation = { rule: { type: "list", values: comparisonHeadings } };
    controlCell.format = {
      fill: colors.pale_warning,
      font: { name: fontName, size: 10, bold: true, color: colors.dark_text },
      horizontalAlignment: "center",
      verticalAlignment: "center",
    };
    const helperFormulas = Array.from({ length: lastRow - firstDataRow + 1 }, (_, rowOffset) => {
      const rowNumber = firstDataRow + rowOffset;
      const selectorFormula = comparisonTargets.reduceRight(
        (fallback, choice) =>
          `IF($${targetColumn}$${compareRow}="${choice.heading.replaceAll('"', '""')}",${choice.column}${rowNumber},${fallback})`,
        `""`,
      );
      return [`=${selectorFormula}`];
    });
    registration.getRange(`${helperColumn}${firstDataRow}:${helperColumn}${lastRow}`).formulas = helperFormulas;
    registration.getRange(`${targetColumn}${firstDataRow}:${targetColumn}${lastRow}`).conditionalFormats.add(
      "cellIs",
      {
        operator: "notEqual",
        formula: `$${helperColumn}${firstDataRow}`,
        format: {
          fill: colors[comparisonControls.fill],
          font: { color: comparisonControls.font_color },
        },
      },
    );
  }
  const helperColumns = Object.values(comparisonControls.targets).map((target) => target.helper);
  registration.getRange(`${helperColumns[0]}:${helperColumns.at(-1)}`).format.columnWidthPx = 2;
  registration.getRange(`${helperColumns[0]}1:${helperColumns.at(-1)}${lastRow}`).format.font = {
    color: colors.white,
    size: 1,
  };
  const outerBorders = sheets.registration.outer_borders || {};
  for (const range of outerBorders.ranges || []) {
    const borders = {
      top: { style: "thick", weight: outerBorders.weight_pt, color: colors[outerBorders.color] },
      bottom: { style: "thick", weight: outerBorders.weight_pt, color: colors[outerBorders.color] },
      left: { style: "thick", weight: outerBorders.weight_pt, color: colors[outerBorders.color] },
      right: { style: "thick", weight: outerBorders.weight_pt, color: colors[outerBorders.color] },
    };
    registration.getRange(range).format.borders = borders;
    const [startColumn, endColumn] = range.split(":");
    registration.getRange(`${startColumn}1:${endColumn}${lastRow}`).format.borders = borders;
  }
  for (const range of [`D5:E${lastRow}`, `H5:I${lastRow}`, `L5:M${lastRow}`]) {
    registration.getRange(range).dataValidation = {
      rule: { type: "list", values: source.lists.registration_result },
    };
  }
  registration.getRange(`4:${lastRow}`).format.autofitRows();
  registration.freezePanes.freezeRows(sheets.registration.freeze_rows);
  registration.freezePanes.freezeColumns(sheets.registration.freeze_columns);
}


function buildSessions() {
  sessions.getRange("A1:L1").merge();
  sessions.getRange("A1").values = [["Verification Sessions"]];
  sessions.getRange("A2:L2").merge();
  sessions.getRange("A2").values = [[
    "Use one row per camera session. Reference the Session ID from Checklist rows so evidence and observations remain traceable.",
  ]];
  sessions.getRange("A1:L1").format = titleBandFormat(16);
  sessions.getRange("A2:L2").format = noteBandFormat();
  sessions.getRange("3:3").format.rowHeight = 12;
  const headers = [
    "Session ID", "Date", "Goal", "Firmware", "Battery / Charge", "Lens",
    "Flash / Trigger", "Starting Backup", "Image Range", "Outcome", "Next Session", "Notes",
  ];
  const migratedRows = migration.sessions.length ? migration.sessions : [];
  const rowCount = Math.max(20, migratedRows.length);
  const rows = Array.from({ length: rowCount }, (_, index) =>
    migratedRows[index] || Array(headers.length).fill(""),
  );
  sessions.getRange(`A4:L${4 + rowCount}`).values = [headers, ...rows];
  const table = sessions.tables.add(`A4:L${4 + rowCount}`, true, "SessionsTable");
  table.style = "TableStyleMedium2";
  table.showFilterButton = true;
  table.showBandedRows = true;
  sessions.getRange("A4:L4").format = headerFormat();
  sessions.getRange(`A5:L${4 + rowCount}`).format = {
    font: { name: fontName, size: 11 },
    verticalAlignment: "center",
    wrapText: true,
  };
  const widths = [96, 84, 216, 84, 120, 144, 144, 132, 120, 216, 216, 228];
  widths.forEach((width, index) => {
    const letter = columnName(index + 1);
    sessions.getRange(`${letter}:${letter}`).format.columnWidthPx = pointsToPixels(width);
  });
  sessions.getRange(`B5:B${4 + rowCount}`).format.numberFormat = "yyyy-mm-dd";
  sessions.getRange(`4:${4 + rowCount}`).format.autofitRows();
}


function buildDashboard() {
  dashboard.getRange("A1:H2").merge();
  dashboard.getRange("A1").values = [["EOS R5 On-Camera Verification Progress"]];
  dashboard.getRange("A3:H4").merge();
  dashboard.getRange("A3").values = [[payload.status
    ? "Git-synchronized working copy. Import spreadsheet updates into verification status before finishing for the day. Changed definitions require retesting."
    : "Blank master template. Update the Checklist and C1-C3 Registration sheets in a separate working copy. Only Verified, unambiguous results may be promoted to owner-confirmed project status."
  ]];
  dashboard.getRange("A1:H2").format = titleBandFormat(20);
  dashboard.getRange("A3:H4").format = noteBandFormat();

  dashboard.getRange("A6:H6").values = [[
    "Total checklist items", "", "Verified", "", "In progress / pending", "", "Needs attention", "",
  ]];
  dashboard.getRange("A6:H6").format = {
    font: { name: fontName, size: 11, bold: true },
    horizontalAlignment: "center",
    verticalAlignment: "center",
  };
  dashboard.getRange("A6:B6").format.fill = colors.pale_gray;
  dashboard.getRange("C6:D6").format = {
    fill: colors.pale_success,
    font: { name: fontName, size: 11, bold: true, color: colors.success },
    horizontalAlignment: "center",
    verticalAlignment: "center",
  };
  dashboard.getRange("E6:F6").format = {
    fill: colors.pale_warning,
    font: { name: fontName, size: 11, bold: true, color: colors.warning },
    horizontalAlignment: "center",
    verticalAlignment: "center",
  };
  dashboard.getRange("G6:H6").format = {
    fill: colors.pale_danger,
    font: { name: fontName, size: 11, bold: true, color: colors.danger },
    horizontalAlignment: "center",
    verticalAlignment: "center",
  };
  dashboard.getRange("A7").formulas = [[`=COUNTA('${sheets.checklist.name}'!$A$${checklistFirstDataRow}:$A$${checklistLastRow})`]];
  dashboard.getRange("C7").formulas = [[`=COUNTIF('${sheets.checklist.name}'!$I$${checklistFirstDataRow}:$I$${checklistLastRow},"Verified")`]];
  dashboard.getRange("E7").formulas = [[
    `=COUNTIF('${sheets.checklist.name}'!$I$${checklistFirstDataRow}:$I$${checklistLastRow},"In progress")+COUNTIF('${sheets.checklist.name}'!$I$${checklistFirstDataRow}:$I$${checklistLastRow},"Configured—not registered")+COUNTIF('${sheets.checklist.name}'!$I$${checklistFirstDataRow}:$I$${checklistLastRow},"Registered—pending read-back")`,
  ]];
  dashboard.getRange("G7").formulas = [[
    `=COUNTIF('${sheets.checklist.name}'!$I$${checklistFirstDataRow}:$I$${checklistLastRow},"Failed—needs correction")+COUNTIF('${sheets.checklist.name}'!$I$${checklistFirstDataRow}:$I$${checklistLastRow},"Inconclusive—needs retest")+COUNTIF('${sheets.checklist.name}'!$I$${checklistFirstDataRow}:$I$${checklistLastRow},"Blocked")`,
  ]];
  dashboard.getRange("A7:H8").format = {
    font: { name: fontName, size: 16, bold: true },
    horizontalAlignment: "center",
    verticalAlignment: "center",
  };
  dashboard.getRange("A7:B8").format.font = { name: fontName, size: 16, bold: true, color: colors.navy };
  dashboard.getRange("C7:D8").format.font = { name: fontName, size: 16, bold: true, color: colors.success };
  dashboard.getRange("E7:F8").format.font = { name: fontName, size: 16, bold: true, color: colors.warning };
  dashboard.getRange("G7:H8").format.font = { name: fontName, size: 16, bold: true, color: colors.danger };
  dashboard.getRange("C7").conditionalFormats.add("cellIs", {
    operator: "greaterThanOrEqual",
    formula: 0,
    format: { fill: colors.pale_success, font: { color: colors.success, bold: true } },
  });
  dashboard.getRange("E7").conditionalFormats.add("cellIs", {
    operator: "greaterThanOrEqual",
    formula: 0,
    format: { fill: colors.pale_warning, font: { color: colors.warning, bold: true } },
  });
  dashboard.getRange("G7").conditionalFormats.add("cellIs", {
    operator: "greaterThanOrEqual",
    formula: 0,
    format: { fill: colors.pale_danger, font: { color: colors.danger, bold: true } },
  });

  const phases = [...new Set(tests.map((test) => test.phase))];
  const statuses = source.lists.main_status;
  const dashboardRows = Math.max(phases.length, statuses.length);
  const summary = Array.from({ length: dashboardRows }, (_, index) => [
    phases[index] || "",
    "",
    "",
    "",
    "",
    "",
    statuses[index] || "",
    "",
  ]);
  dashboard.getRange(`A11:H${11 + dashboardRows}`).values = [
    ["Phase", "Total", "Verified", "Attention", "Completion", "", "Status", "Count"],
    ...summary,
  ];
  dashboard.getRange("A11:E11").format = headerFormat();
  dashboard.getRange("G11:H11").format = headerFormat();
  for (let index = 0; index < phases.length; index += 1) {
    const row = 12 + index;
    dashboard.getRange(`B${row}`).formulas = [[`=COUNTIF('${sheets.checklist.name}'!$C$${checklistFirstDataRow}:$C$${checklistLastRow},A${row})`]];
    dashboard.getRange(`C${row}`).formulas = [[`=COUNTIFS('${sheets.checklist.name}'!$C$${checklistFirstDataRow}:$C$${checklistLastRow},A${row},'${sheets.checklist.name}'!$I$${checklistFirstDataRow}:$I$${checklistLastRow},"Verified")`]];
    dashboard.getRange(`D${row}`).formulas = [[
      `=COUNTIFS('${sheets.checklist.name}'!$C$${checklistFirstDataRow}:$C$${checklistLastRow},A${row},'${sheets.checklist.name}'!$I$${checklistFirstDataRow}:$I$${checklistLastRow},"Failed—needs correction")+COUNTIFS('${sheets.checklist.name}'!$C$${checklistFirstDataRow}:$C$${checklistLastRow},A${row},'${sheets.checklist.name}'!$I$${checklistFirstDataRow}:$I$${checklistLastRow},"Inconclusive—needs retest")+COUNTIFS('${sheets.checklist.name}'!$C$${checklistFirstDataRow}:$C$${checklistLastRow},A${row},'${sheets.checklist.name}'!$I$${checklistFirstDataRow}:$I$${checklistLastRow},"Blocked")`,
    ]];
    dashboard.getRange(`E${row}`).formulas = [[
      `=IF(B${row}=0,0,(C${row}+COUNTIFS('${sheets.checklist.name}'!$C$${checklistFirstDataRow}:$C$${checklistLastRow},A${row},'${sheets.checklist.name}'!$I$${checklistFirstDataRow}:$I$${checklistLastRow},"Backup-Settings"))/B${row})`,
    ]];
  }
  for (let index = 0; index < statuses.length; index += 1) {
    const row = 12 + index;
    dashboard.getRange(`H${row}`).formulas = [[`=COUNTIF('${sheets.checklist.name}'!$I$${checklistFirstDataRow}:$I$${checklistLastRow},G${row})`]];
  }
  dashboard.getRange(`E12:E${11 + phases.length}`).format.numberFormat = "0%";
  for (const rule of sheets.dashboard.completion_rules || []) {
    const font = {};
    if (rule.font_color) font.color = colors[rule.font_color];
    if (rule.bold === true) font.bold = true;
    if (rule.italic === true) font.italic = true;
    const format = {};
    if (Object.keys(font).length) format.font = font;
    if (rule.fill) format.fill = colors[rule.fill];
    const config = {
      operator: rule.operator,
      formula: rule.values || rule.value,
      format,
    };
    dashboard.getRange(`E12:E${11 + phases.length}`).conditionalFormats.add("cellIs", config);
  }
  for (const column of sheets.dashboard.centered_columns || []) {
    dashboard.getRange(`${column}11:${column}${11 + dashboardRows}`).format.horizontalAlignment = "center";
  }
  dashboard.getRange("A:H").format.columnWidth = 16;
  dashboard.getRange("A:A").format.columnWidth = 22;
  dashboard.getRange("E:E").format.columnWidth = 18;
  dashboard.getRange("G:G").format.columnWidth = 32;
  dashboard.getRange("H:H").format.columnWidth = 12;

  const workflowStart = 13 + dashboardRows;
  dashboard.getRange(`A${workflowStart}:H${workflowStart}`).merge();
  dashboard.getRange(`A${workflowStart}`).values = [["Recommended workflow"]];
  dashboard.getRange(`A${workflowStart}:H${workflowStart}`).format = {
    fill: colors.navy,
    font: { name: fontName, size: 11, bold: true, color: colors.white },
  };
  dashboard.getRange(`A${workflowStart + 1}:H${workflowStart + 5}`).merge();
  dashboard.getRange(`A${workflowStart + 1}`).values = [[
    "1. Save the starting camera configuration and document C1–C3.\n" +
    "2. Disable Auto update, then configure and verify the SWITCH My Menu tab.\n" +
    "3. Save Backup-Settings checkpoints after shared setup/controls and after C1–C3 read-back.\n" +
    "4. Work through Checklist in Sequence order and use one Session ID per camera session.\n" +
    "5. Filter Project Update? = Yes and Status = Verified before changing project evidence states.",
  ]];
  dashboard.getRange(`A${workflowStart + 1}:H${workflowStart + 5}`).format = {
    fill: colors.pale_gray,
    font: { name: fontName, size: 11, color: colors.dark_text },
    wrapText: true,
    verticalAlignment: "top",
  };
}


function buildMetadata() {
  const rows = [
    ["Type", "ID", "Revision"],
    ["workbook_revision", "", String(payload.workbook_revision)],
    ["source_fingerprint", "", payload.source_fingerprint],
    ...Object.entries(payload.definition_fingerprints.tests || {}).map(
      ([id, revision]) => ["test", id, revision],
    ),
    ...Object.entries(payload.definition_fingerprints.registration || {}).map(
      ([id, revision]) => ["registration", id, revision],
    ),
  ];
  metadata.getRange(`A1:C${rows.length}`).values = rows;
  metadata.getRange("A1:C1").format = headerFormat();
  metadata.getRange(`A2:C${rows.length}`).format = {
    font: { name: fontName, size: 10 },
    verticalAlignment: "center",
  };
  metadata.getRange("A:A").format.columnWidth = 24;
  metadata.getRange("B:B").format.columnWidth = 34;
  metadata.getRange("C:C").format.columnWidth = 78;
  metadata.freezePanes.freezeRows(1);
}


function configuredBannerPanels() {
  const textByRole = {
    title: layout.banner.title,
    instructions: layout.banner.instructions,
    note: `${layout.banner.note} ${payload.release_label}.`,
  };
  return shared.banner.panels.map((panel, index) => ({
    row: index,
    heightPx: panel.height_px,
    fill: panel.fill,
    text: textByRole[panel.role],
    textColor: panel.text_color,
    fontSize: panel.font_size,
    fontWeight: panel.font_weight,
    fontStyle: panel.font_style,
  }));
}


function headerFormat() {
  return {
    fill: colors.blue,
    font: { name: fontName, bold: true, color: colors.white, size: 11 },
    wrapText: true,
    verticalAlignment: "center",
    horizontalAlignment: "center",
  };
}


function titleBandFormat(size) {
  return {
    fill: colors.navy,
    font: { name: fontName, size, bold: true, color: colors.white },
    verticalAlignment: "center",
    horizontalAlignment: "left",
  };
}


function noteBandFormat() {
  return {
    fill: colors.pale_blue,
    font: { name: fontName, size: 11, italic: true, color: colors.dark_text },
    wrapText: true,
    verticalAlignment: "center",
  };
}


function addStatusFormatting(range) {
  range.conditionalFormats.add("containsText", {
    text: "Backup-Settings",
    format: { fill: colors.pale_blue, font: { color: colors.blue, bold: true } },
  });
  range.conditionalFormats.add("containsText", {
    text: "Verified",
    format: { fill: colors.pale_success, font: { color: "#315B20", bold: true } },
  });
  range.conditionalFormats.add("containsText", {
    text: "In progress",
    format: { fill: colors.pale_warning, font: { color: "#7F6000", bold: true } },
  });
  range.conditionalFormats.add("containsText", {
    text: "Blocked",
    format: { fill: colors.pale_danger, font: { color: "#9C0006", bold: true } },
  });
  range.conditionalFormats.add("containsText", {
    text: "Failed",
    format: { fill: "#F4CCCC", font: { color: "#9C0006", bold: true } },
  });
}


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


function pointsToPixels(points) {
  return Math.round(points * 4 / 3);
}


function compositeBannerDataUrl(panels, widthPx, sharpRenderer) {
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
  return sharpRenderer(Buffer.from(svg))
    .png()
    .toBuffer()
    .then((png) => `data:image/png;base64,${png.toString("base64")}`);
}


function xmlEscape(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&apos;");
}


function emptyMigration() {
  return {
    checklist: new Map(),
    registration: new Map(),
    sessions: [],
  };
}


function statusMigration(status) {
  const result = emptyMigration();
  for (const [testId, state] of Object.entries(status.tests || {})) {
    result.checklist.set(testId, {
      ...state,
      evidence_files: Array.isArray(state.evidence_files)
        ? state.evidence_files.join("\n")
        : state.evidence_files || "",
    });
  }
  for (const [setting, state] of Object.entries(status.registration || {})) {
    result.registration.set(setting, state);
  }
  const headers = [
    "session_id", "date", "goal", "firmware", "battery_charge", "lens",
    "flash_trigger", "starting_backup", "image_range", "outcome", "next_session", "notes",
  ];
  result.sessions = (status.sessions || []).map((session) =>
    headers.map((header) => session[header] ?? ""),
  );
  return result;
}


async function readMigration(sourcePath, FileBlobClass, SpreadsheetFileClass) {
  const input = await FileBlobClass.load(sourcePath);
  const oldWorkbook = await SpreadsheetFileClass.importXlsx(input);
  const result = emptyMigration();

  const checklistSheet = sheetByNames(oldWorkbook, ["Checklist", "Checklist - Table 1-1"]);
  if (checklistSheet) {
    const values = checklistSheet.getUsedRange(true).values;
    const headerIndex = values.findIndex((row) => row.includes("Test ID"));
    if (headerIndex >= 0) {
      const headers = values[headerIndex];
      const indices = Object.fromEntries(headers.map((header, index) => [String(header || ""), index]));
      const mutable = [
        "Status", "Test Date", "Session ID", "Evidence Files", "Observation",
        "Next Action", "Evidence Class", "Updated in Project",
      ];
      for (const row of values.slice(headerIndex + 1)) {
        const testId = row[indices["Test ID"]];
        if (!testId) continue;
        const record = {};
        for (const heading of mutable) {
          if (indices[heading] === undefined) continue;
          record[toSnakeCase(heading)] = row[indices[heading]] ?? "";
        }
        result.checklist.set(String(testId), record);
      }
    }
  }

  const registrationSheet = sheetByNames(oldWorkbook, ["C1-C3 Registration"]);
  if (registrationSheet) {
    const values = registrationSheet.getUsedRange(true).values;
    const headerIndex = values.findIndex((row) => row.includes("Setting"));
    if (headerIndex >= 0) {
      const headers = values[headerIndex].map((value) => String(value || ""));
      for (const row of values.slice(headerIndex + 1)) {
        const setting = row[0];
        if (!setting) continue;
        const record = {};
        for (const key of ["C1", "C2", "C3"]) {
          const lower = key.toLowerCase();
          const configured = headers.findIndex((heading) => heading === `${key} Configured`);
          const readBack = headers.findIndex((heading) => heading === `${key} Read-back`);
          const notes = headers.findIndex((heading) => heading === `${key} Notes`);
          record[`${lower}_configured`] = configured >= 0 ? row[configured] ?? "" : "";
          record[`${lower}_read_back`] = readBack >= 0 ? row[readBack] ?? "" : "";
          record[`${lower}_notes`] = notes >= 0 ? row[notes] ?? "" : "";
        }
        result.registration.set(String(setting), record);
      }
    }
  }

  const sessionsSheet = sheetByNames(oldWorkbook, ["Sessions"]);
  if (sessionsSheet) {
    const values = sessionsSheet.getUsedRange(true).values;
    const headerIndex = values.findIndex((row) => row.includes("Session ID"));
    if (headerIndex >= 0) {
      result.sessions = values
        .slice(headerIndex + 1)
        .filter((row) => row.some((value) => value !== null && value !== ""))
        .map((row) => row.slice(0, 12));
    }
  }
  return result;
}


function sheetByNames(workbookToSearch, names) {
  for (const name of names) {
    try {
      return workbookToSearch.worksheets.getItem(name);
    } catch {
      // Continue to the next compatible name.
    }
  }
  return null;
}


function toSnakeCase(value) {
  return value.toLowerCase().replaceAll(/[^a-z0-9]+/g, "_").replaceAll(/^_|_$/g, "");
}
