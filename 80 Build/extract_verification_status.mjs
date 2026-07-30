import fs from "node:fs/promises";
import path from "node:path";
import { createRequire } from "node:module";
import { pathToFileURL } from "node:url";


const [sourcePath, outputPath, runtimeDir] = process.argv.slice(2);
if (!sourcePath || !outputPath || !runtimeDir) {
  throw new Error("Expected workbook, output JSON, and runtime directory paths.");
}
const runtimeRequire = createRequire(path.join(runtimeDir, "package.json"));
const artifactEntry = runtimeRequire.resolve("@oai/artifact-tool");
const { FileBlob, SpreadsheetFile } = await import(pathToFileURL(artifactEntry).href);
const input = await FileBlob.load(sourcePath);
const workbook = await SpreadsheetFile.importXlsx(input);

const checklistValues = usedValues("Checklist", ["Checklist - Table 1-1"]);
const registrationValues = usedValues("C1-C3 Registration");
const sessionValues = usedValues("Sessions");
const metadataValues = usedValues("Metadata");

const output = {
  checklist: rowObjects(checklistValues, "Test ID").map((row) => ({
    test_id: row["Test ID"],
    status: row["Status"],
    test_date: row["Test Date"],
    session_id: row["Session ID"],
    evidence_files: row["Evidence Files"],
    observation: row["Observation"],
    next_action: row["Next Action"],
    evidence_class: row["Evidence Class"],
    updated_in_project: row["Updated in Project"],
  })),
  registration: registrationObjects(registrationValues),
  sessions: rowObjects(sessionValues, "Session ID").map((row) => ({
    session_id: row["Session ID"],
    date: row["Date"],
    goal: row["Goal"],
    firmware: row["Firmware"],
    battery_charge: row["Battery / Charge"],
    lens: row["Lens"],
    flash_trigger: row["Flash / Trigger"],
    starting_backup: row["Starting Backup"],
    image_range: row["Image Range"],
    outcome: row["Outcome"],
    next_session: row["Next Session"],
    notes: row["Notes"],
  })),
  metadata: metadataObjects(metadataValues),
};
await fs.writeFile(outputPath, JSON.stringify(output, null, 2), "utf8");


function usedValues(primary, aliases = []) {
  for (const name of [primary, ...aliases]) {
    try {
      return workbook.worksheets.getItem(name).getUsedRange(true).values;
    } catch {
      // Try the next supported sheet name.
    }
  }
  return [];
}


function rowObjects(values, identifier) {
  const headerIndex = values.findIndex((row) => row.includes(identifier));
  if (headerIndex < 0) return [];
  const headers = values[headerIndex].map((value) => String(value || ""));
  return values.slice(headerIndex + 1)
    .filter((row) => row.some((value) => value !== null && value !== ""))
    .map((row) => Object.fromEntries(headers.map((header, index) => [header, row[index] ?? ""])));
}


function registrationObjects(values) {
  const rows = rowObjects(values, "Setting");
  return Object.fromEntries(rows.filter((row) => row.Setting).map((row) => [
    String(row.Setting),
    {
      c1_configured: row["C1 Configured"] ?? "",
      c1_read_back: row["C1 Read-back"] ?? "",
      c1_notes: row["C1 Notes"] ?? "",
      c2_configured: row["C2 Configured"] ?? "",
      c2_read_back: row["C2 Read-back"] ?? "",
      c2_notes: row["C2 Notes"] ?? "",
      c3_configured: row["C3 Configured"] ?? "",
      c3_read_back: row["C3 Read-back"] ?? "",
      c3_notes: row["C3 Notes"] ?? "",
    },
  ]));
}


function metadataObjects(values) {
  const result = { tests: {}, registration: {} };
  for (const row of values.slice(1)) {
    const type = String(row[0] || "");
    const id = String(row[1] || "");
    const value = String(row[2] || "");
    if (type === "test" && id) result.tests[id] = value;
    else if (type === "registration" && id) result.registration[id] = value;
    else if (type && !id) result[type] = value;
  }
  return result;
}
