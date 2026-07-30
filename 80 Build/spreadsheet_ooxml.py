"""Small OOXML repairs needed after spreadsheet export."""

from pathlib import PurePosixPath
import re
import xml.etree.ElementTree as ET
from zipfile import ZipFile


MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PACKAGE_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"


def ensure_freeze_panes(workbook_path, sheet_name, frozen_rows, frozen_columns):
    """Ensure a named Excel worksheet has the requested frozen pane."""
    workbook_path = workbook_path.resolve()
    replacement_path = workbook_path.with_name(f".{workbook_path.name}.freeze-panes")
    worksheet_path = _worksheet_path(workbook_path, sheet_name)
    ET.register_namespace("x", MAIN_NS)

    with ZipFile(workbook_path, "r") as source, ZipFile(replacement_path, "w") as target:
        for entry in source.infolist():
            data = source.read(entry.filename)
            if entry.filename == worksheet_path:
                root = ET.fromstring(data)
                sheet_views = root.find(f"{{{MAIN_NS}}}sheetViews")
                if sheet_views is None:
                    raise RuntimeError(f"Generated worksheet {sheet_name} is missing sheetViews.")
                sheet_view = sheet_views.find(f"{{{MAIN_NS}}}sheetView")
                if sheet_view is None:
                    raise RuntimeError(f"Generated worksheet {sheet_name} is missing sheetView.")
                for child in list(sheet_view):
                    if child.tag in {
                        f"{{{MAIN_NS}}}pane",
                        f"{{{MAIN_NS}}}selection",
                    }:
                        sheet_view.remove(child)
                top_left = f"{excel_column(frozen_columns + 1)}{frozen_rows + 1}"
                pane = ET.Element(
                    f"{{{MAIN_NS}}}pane",
                    {
                        "xSplit": str(frozen_columns),
                        "ySplit": str(frozen_rows),
                        "topLeftCell": top_left,
                        "activePane": "bottomRight",
                        "state": "frozen",
                    },
                )
                selection = ET.Element(
                    f"{{{MAIN_NS}}}selection",
                    {
                        "pane": "bottomRight",
                        "activeCell": top_left,
                        "sqref": top_left,
                    },
                )
                sheet_view.insert(0, selection)
                sheet_view.insert(0, pane)
                data = ET.tostring(root, encoding="utf-8", xml_declaration=True)
            target.writestr(entry, data)
    replacement_path.replace(workbook_path)


def ensure_active_sheet(workbook_path, sheet_name):
    """Save the named worksheet as the workbook's active Excel sheet."""
    workbook_path = workbook_path.resolve()
    replacement_path = workbook_path.with_name(f".{workbook_path.name}.active-sheet")
    with ZipFile(workbook_path, "r") as source:
        workbook = ET.fromstring(source.read("xl/workbook.xml"))
        sheets = workbook.findall(f".//{{{MAIN_NS}}}sheet")
        active_index = next(
            (index for index, sheet in enumerate(sheets) if sheet.attrib.get("name") == sheet_name),
            None,
        )
        if active_index is None:
            raise RuntimeError(f"Generated workbook is missing worksheet: {sheet_name}")
        book_views = workbook.find(f"{{{MAIN_NS}}}bookViews")
        if book_views is None:
            book_views = ET.Element(f"{{{MAIN_NS}}}bookViews")
            sheets_element = workbook.find(f"{{{MAIN_NS}}}sheets")
            insertion_index = (
                list(workbook).index(sheets_element)
                if sheets_element is not None
                else 0
            )
            workbook.insert(insertion_index, book_views)
        workbook_view = book_views.find(f"{{{MAIN_NS}}}workbookView")
        if workbook_view is None:
            workbook_view = ET.SubElement(book_views, f"{{{MAIN_NS}}}workbookView")
        workbook_view.set("activeTab", str(active_index))
        workbook_xml = ET.tostring(workbook, encoding="utf-8", xml_declaration=True)

        with ZipFile(replacement_path, "w") as target:
            for entry in source.infolist():
                data = workbook_xml if entry.filename == "xl/workbook.xml" else source.read(entry.filename)
                target.writestr(entry, data)
    replacement_path.replace(workbook_path)


def worksheet_dimensions(workbook_path, sheet_name):
    """Return the maximum used row and column declared by a named worksheet."""
    worksheet_path = _worksheet_path(workbook_path.resolve(), sheet_name)
    with ZipFile(workbook_path, "r") as source:
        root = ET.fromstring(source.read(worksheet_path))
    dimension = root.find(f"{{{MAIN_NS}}}dimension")
    reference = dimension.attrib.get("ref", "") if dimension is not None else ""
    final_cell = reference.split(":")[-1]
    match = re.fullmatch(r"\$?([A-Z]+)\$?(\d+)", final_cell)
    if not match:
        cells = [
            cell.attrib.get("r", "")
            for cell in root.findall(f".//{{{MAIN_NS}}}c")
        ]
        parsed = [
            re.fullmatch(r"\$?([A-Z]+)\$?(\d+)", cell)
            for cell in cells
        ]
        parsed = [item for item in parsed if item]
        if not parsed:
            raise RuntimeError(f"Generated worksheet {sheet_name} has no usable dimension.")
        row = max(int(item.group(2)) for item in parsed)
        column = max(_column_number(item.group(1)) for item in parsed)
        return row, column
    letters, row = match.groups()
    return int(row), _column_number(letters)


def _column_number(letters):
    column = 0
    for character in letters:
        column = column * 26 + ord(character) - 64
    return column


def _worksheet_path(workbook_path, sheet_name):
    with ZipFile(workbook_path, "r") as source:
        workbook = ET.fromstring(source.read("xl/workbook.xml"))
        relationships = ET.fromstring(source.read("xl/_rels/workbook.xml.rels"))
    targets = {
        relationship.attrib["Id"]: relationship.attrib["Target"]
        for relationship in relationships.findall(f"{{{PACKAGE_REL_NS}}}Relationship")
    }
    for sheet in workbook.findall(f".//{{{MAIN_NS}}}sheet"):
        if sheet.attrib.get("name") != sheet_name:
            continue
        relationship_id = sheet.attrib.get(f"{{{REL_NS}}}id")
        target = targets.get(relationship_id)
        if not target:
            break
        normalized = target.lstrip("/")
        if normalized.startswith("xl/"):
            return normalized
        return str(PurePosixPath("xl") / PurePosixPath(normalized))
    raise RuntimeError(f"Generated workbook is missing worksheet: {sheet_name}")


def excel_column(number):
    result = ""
    value = number
    while value:
        value, remainder = divmod(value - 1, 26)
        result = chr(65 + remainder) + result
    return result
