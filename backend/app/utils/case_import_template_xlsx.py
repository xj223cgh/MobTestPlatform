"""用例导入 Excel 模板：仅用标准库打包 OOXML，无需 openpyxl。"""
from __future__ import annotations

import io
import zipfile
from xml.sax.saxutils import escape


def _col_letter(col_1based: int) -> str:
    n = col_1based
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def _t_cell_xml(text: str) -> str:
    esc = escape(text)
    if "\n" in text or (text and (text[0].isspace() or text[-1].isspace())):
        return f'<t xml:space="preserve">{esc}</t>'
    return f"<t>{esc}</t>"


def build_case_import_template_xlsx() -> io.BytesIO:
    """生成 .xlsx（两表：数据模板 + 填写说明）。"""
    sheet_main = [
        ["用例名称", "优先级", "前置条件", "操作步骤", "预期结果", "测试数据"],
        [
            "登录成功验证",
            "P0",
            "用户已注册且状态正常",
            "1.打开登录页\n2.输入用户名和密码\n3.点击登录",
            "登录成功，跳转到首页",
            "用户名:Tester 密码:123321",
        ],
    ]
    sheet_notes = [
        ["字段", "必填", "说明"],
        ["用例名称", "是", "测试用例名称，不可为空"],
        ["优先级", "否", "可选值：P0/P1/P2/P3/P4，默认 P1"],
        ["前置条件", "否", "执行用例前需要满足的条件"],
        ["操作步骤", "否", "具体操作步骤，多步骤换行书写"],
        ["预期结果", "否", "操作后的预期结果"],
        ["测试数据", "否", "测试所需的数据"],
    ]

    str_index: dict[str, int] = {}
    strings: list[str] = []
    ref_count = 0

    def si(val: str) -> int:
        nonlocal ref_count
        ref_count += 1
        if val not in str_index:
            str_index[val] = len(strings)
            strings.append(val)
        return str_index[val]

    def sheet_xml(rows: list[list[str]]) -> str:
        row_chunks: list[str] = []
        for r_idx, row in enumerate(rows, 1):
            cells = []
            for c_idx, val in enumerate(row, 1):
                if val is None or val == "":
                    continue
                ref = f"{_col_letter(c_idx)}{r_idx}"
                idx = si(val)
                cells.append(f'<c r="{ref}" t="s"><v>{idx}</v></c>')
            row_chunks.append(f'<row r="{r_idx}">{"".join(cells)}</row>')
        inner = "<sheetData>" + "".join(row_chunks) + "</sheetData>"
        return (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            f"{inner}"
            "</worksheet>"
        )

    xml_sheet1 = sheet_xml(sheet_main)
    xml_sheet2 = sheet_xml(sheet_notes)

    unique_count = len(strings)
    si_elems = "".join(f"<si>{_t_cell_xml(s)}</si>" for s in strings)
    xml_sst = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        f'count="{ref_count}" uniqueCount="{unique_count}">'
        f"{si_elems}</sst>"
    )

    xml_styles = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<fonts count="1"><font><sz val="11"/><color theme="1"/><name val="Calibri"/>'
        '<family val="2"/><scheme val="minor"/></font></fonts>'
        '<fills count="2"><fill><patternFill patternType="none"/></fill>'
        '<fill><patternFill patternType="gray125"/></fill></fills>'
        '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
        '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
        '<cellXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/></cellXfs>'
        "</styleSheet>"
    )

    xml_workbook = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        "<sheets>"
        '<sheet name="用例导入模板" sheetId="1" r:id="rId1"/>'
        '<sheet name="填写说明" sheetId="2" r:id="rId2"/>'
        "</sheets></workbook>"
    )

    xml_workbook_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
        'Target="worksheets/sheet1.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
        'Target="worksheets/sheet2.xml"/>'
        '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" '
        'Target="styles.xml"/>'
        '<Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/sharedStrings" '
        'Target="sharedStrings.xml"/>'
        "</Relationships>"
    )

    xml_root_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="xl/workbook.xml"/>'
        "</Relationships>"
    )

    xml_ct = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" '
        'ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/worksheets/sheet1.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        '<Override PartName="/xl/worksheets/sheet2.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        '<Override PartName="/xl/sharedStrings.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"/>'
        '<Override PartName="/xl/styles.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
        "</Types>"
    )

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", xml_ct.encode("utf-8"))
        zf.writestr("_rels/.rels", xml_root_rels.encode("utf-8"))
        zf.writestr("xl/workbook.xml", xml_workbook.encode("utf-8"))
        zf.writestr("xl/_rels/workbook.xml.rels", xml_workbook_rels.encode("utf-8"))
        zf.writestr("xl/worksheets/sheet1.xml", xml_sheet1.encode("utf-8"))
        zf.writestr("xl/worksheets/sheet2.xml", xml_sheet2.encode("utf-8"))
        zf.writestr("xl/sharedStrings.xml", xml_sst.encode("utf-8"))
        zf.writestr("xl/styles.xml", xml_styles.encode("utf-8"))
    buf.seek(0)
    return buf
