from fpdf import FPDF
import datetime
import json
import base64
import io
import openpyxl
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
import pdfkit
from markdown import markdown

# --- PDFKIT CONFIGURATION ---
# This path should be correct for a standard Windows installation.
# def sanitize_text(text):
#     if not isinstance(text, str):
#         text = str(text)
#     return text.encode('latin-1', 'replace').decode('latin-1')

class PDF(FPDF):
    def header(self):
        self.set_fill_color(29, 43, 75)
        self.rect(0, 0, 210, 25, 'F')
        self.set_y(10)
        self.set_font('Arial', 'B', 20)
        self.set_text_color(240, 240, 240)
        self.cell(0, 10, 'Prem TestVerse - Test Report', 0, 1, 'C')
        self.ln(15)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf_report(url, results, filepath):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Arial', '', 12)
    pdf.set_text_color(0, 0, 0)
    
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 8, 'Test Run Summary', 0, 1, 'L')
    pdf.set_font('Arial', '', 11)
    clean_url = sanitize_text(url)
    pdf.cell(0, 6, f'Website Tested: {clean_url}', 0, 1, 'L')
    report_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf.cell(0, 6, f'Report Generated: {report_time}', 0, 1, 'L')
    pdf.ln(5)
    
    final_status = "Success"
    for res in results:
        if res.get('status') not in ['Success', 'New Baseline', 'Visuals Match']:
            final_status = res.get('status')
            break
    
    if final_status == "Success":
        pdf.set_fill_color(40, 167, 69)
        status_text = "TEST PASSED"
    else:
        pdf.set_fill_color(220, 53, 69)
        status_text = f"TEST {final_status.upper()}"

    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 12, status_text, 1, 1, 'C', fill=True)
    pdf.ln(10)
    
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, 'Detailed Steps', 0, 1, 'L')

    for res in results:
        pdf.ln(5)
        step_status = res.get('status', 'N/A')

        if step_status in ['Success', 'Visuals Match']:
            pdf.set_fill_color(230, 245, 233)
        elif step_status in ['Failed', 'Visual Mismatch']:
            pdf.set_fill_color(253, 237, 238)
        else:
            pdf.set_fill_color(230, 240, 252)
            
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, f"Step {res.get('step')} - {step_status}", 1, 1, 'L', fill=True)
        pdf.set_text_color(0, 0, 0)

        line_height = 6
        pdf.set_font('Arial', 'B', 10)
        pdf.write(line_height, "Command:")
        pdf.ln(line_height)
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 5, sanitize_text(res.get('command', '')), border=1, align='L')
        pdf.set_font('Arial', 'B', 10)
        pdf.write(line_height, "Details:")
        pdf.ln(line_height)
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 5, sanitize_text(res.get('details', '')), border=1, align='L')
        
        if 'ai_suggestion' in res and res['ai_suggestion']:
            pdf.ln(2)
            pdf.set_font('Arial', 'B', 10)
            pdf.set_text_color(0, 0, 128)
            pdf.write(line_height, "AI Assistant Suggestion:")
            pdf.ln(line_height)
            pdf.set_font('Arial', 'I', 10)
            pdf.set_fill_color(233, 236, 239)
            pdf.multi_cell(0, 5, sanitize_text(res.get('ai_suggestion', '')), border=1, align='L', fill=True)
            pdf.set_text_color(0, 0, 0)

        if 'screenshot' in res and res['screenshot']:
            try:
                img_data = base64.b64decode(res['screenshot'])
                img_file = io.BytesIO(img_data)
                pdf.ln(3)
                pdf.set_font('Arial', 'B', 10)
                pdf.cell(0, 6, "Screenshot:", 0, 1, 'L')
                if pdf.get_y() + 80 > 297:
                    pdf.add_page()
                pdf.image(img_file, w=180)
                pdf.set_text_color(0, 0, 0)
            except Exception as e:
                pdf.set_font('Arial', 'I', 10)
                pdf.set_text_color(255, 0, 0)
                pdf.multi_cell(0, 5, f"[Could not embed screenshot: {e}]")
                pdf.set_text_color(0, 0, 0)
    pdf.output(filepath)

def generate_excel_report(results, url, user_name, test_run_id):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Test Execution Report"
    ws.merge_cells('A1:G1')
    title_cell = ws['A1']
    title_cell.value = "Test Execution Report"
    title_cell.font = Font(size=20, bold=True)
    title_cell.alignment = Alignment(horizontal='center')
    header_info = {
        "Project Name": "Prem TestVerse",
        "Module Name": "Automated Test Run",
        "Test Run ID": test_run_id,
        "Executed By": user_name,
        "Execution Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "URL Tested": url
    }
    bold_font = Font(bold=True)
    for i, (key, value) in enumerate(header_info.items(), 3):
        key_cell = ws[f'A{i}']
        key_cell.value = key
        key_cell.font = bold_font
        ws.merge_cells(f'B{i}:C{i}')
        value_cell = ws[f'B{i}']
        value_cell.value = value
    ws.append([])
    table_headers = ["Step", "Test Step (Command)", "Status", "Actual Result (Details)", "AI Suggestion"]
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="1D2B4B", end_color="1D2B4B", fill_type="solid")
    thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
    header_row_num = len(header_info) + 4
    for col, title in enumerate(table_headers, 1):
        cell = ws.cell(row=header_row_num, column=col, value=title)
        cell.font = header_font
        cell.fill = header_fill
        cell.border = thin_border
    success_fill = PatternFill(start_color="D4EDDA", end_color="D4EDDA", fill_type="solid")
    fail_fill = PatternFill(start_color="F8D7DA", end_color="F8D7DA", fill_type="solid")
    for row_idx, res in enumerate(results, start=header_row_num + 1):
        ws.cell(row=row_idx, column=1, value=res.get('step')).border = thin_border
        ws.cell(row=row_idx, column=2, value=res.get('command')).border = thin_border
        status_cell = ws.cell(row=row_idx, column=3, value=res.get('status'))
        status_cell.border = thin_border
        ws.cell(row=row_idx, column=4, value=res.get('details')).border = thin_border
        ws.cell(row=row_idx, column=5, value=res.get('ai_suggestion', 'N/A')).border = thin_border
        if 'Success' in res.get('status', '') or 'Match' in res.get('status', '') or 'Baseline' in res.get('status', ''):
            status_cell.fill = success_fill
        else:
            status_cell.fill = fail_fill
    ws.column_dimensions['A'].width = 15
    ws.column_dimensions['B'].width = 50
    ws.column_dimensions['C'].width = 20
    ws.column_dimensions['D'].width = 60
    ws.column_dimensions['E'].width = 60
    virtual_workbook = io.BytesIO()
    wb.save(virtual_workbook)
    return virtual_workbook.getvalue()

def generate_code_analysis_pdf(ai_markdown_output):
    """Generates a PDF from Markdown text using pdfkit, with syntax highlighting."""
    if not config:
        return None 

    html_content = markdown(ai_markdown_output, extensions=['fenced_code', 'codehilite'])
    
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>AI Code Analysis Report</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; background-color: #121a2e; color: #f0f0f0; padding: 1in; font-size: 11pt; }}
            h1, h2, h3 {{ color: #8a9fff; border-bottom: 1px solid rgba(255, 255, 255, 0.2); padding-bottom: 5px; }}
            pre {{ background-color: #282c34; border-radius: 8px; padding: 1em; color: #abb2bf; white-space: pre-wrap; word-wrap: break-word; }}
            code {{ font-family: 'Courier New', monospace; }}
            .header {{ text-align: center; margin-bottom: 1in; }}
            .footer {{ text-align: center; margin-top: 1in; font-size: 9pt; color: #aeb9e1; }}
            
            /* Atom One Dark Theme for Syntax Highlighting in PDF */
            .codehilite .c {{ color: #5c6370; font-style: italic }} /* Comment */
            .codehilite .k {{ color: #c678dd }} /* Keyword */
            .codehilite .kn {{ color: #c678dd }} /* Keyword.Namespace */
            .codehilite .nf {{ color: #61afef }} /* Name.Function */
            .codehilite .nc {{ color: #e5c07b }} /* Name.Class */
            .codehilite .s1, .codehilite .s2, .codehilite .s {{ color: #98c379 }} /* String */
            .codehilite .mi {{ color: #d19a66 }} /* Number.Integer */
            .codehilite .bp {{ color: #56b6c2 }} /* Name.Builtin.Pseudo */
            .codehilite .o {{ color: #56b6c2 }} /* Operator */
            .codehilite .p {{ color: #abb2bf }} /* Punctuation */
            .codehilite .n {{ color: #e06c75 }} /* Name */
        </style>
    </head>
    <body>
        <div class="header">
            <h1>AI Code Analysis Report</h1>
            <p>Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        {html_content}
        <div class="footer">
            <p>Report generated by Prem TestVerse</p>
        </div>
    </body>
    </html>
    """
    
    options = { 'page-size': 'A4', 'margin-top': '0.75in', 'margin-right': '0.75in', 'margin-bottom': '0.75in', 'margin-left': '0.75in', 'encoding': "UTF-8" }
    
    try:
        pdf = pdfkit.from_string(full_html, False, options=options)
        return pdf
    except Exception as e:
        print(f"Error generating PDF with pdfkit: {e}")
        return None