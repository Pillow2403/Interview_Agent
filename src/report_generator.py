# src/report_generator.py
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime

# Đăng ký font hỗ trợ Unicode (Vietnamese)
root = os.path.dirname(os.path.dirname(__file__))  # project root
font_path = os.path.join(root, 'font', 'dejavu-fonts-ttf-2.37', 'dejavu-fonts-ttf-2.37','ttf', 'DejaVuSans.ttf')
pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))


def generate_pdf_report(candidate_name: str, position: str, domain: str,
                        conversation_history: list, scores: dict) -> str:
    """
    Tạo file PDF với font Unicode, hỗ trợ tiếng Việt có dấu.
    """
    # Đường dẫn lưu file
    root = os.path.dirname(os.path.dirname(__file__))  # project root
    temp_dir = os.path.join(root, 'data', 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(temp_dir, f"Report_{candidate_name.replace(' ', '_')}_{timestamp}.pdf")

    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    # Sử dụng font Unicode
    c.setFont('DejaVuSans', 16)
    c.drawString(40, height - 50, "BÁO CÁO ĐÁNH GIÁ ỨNG VIÊN")
    c.setFont('DejaVuSans', 12)
    c.drawString(40, height - 80, f"Ứng viên: {candidate_name}")
    c.drawString(40, height - 100, f"Vị trí: {position}")
    c.drawString(40, height - 120, f"Lĩnh vực: {domain}")
    c.drawString(40, height - 140, f"Ngày tạo: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    # Điểm trung bình
    avg = scores['averaged']
    c.setFont('DejaVuSans', 14)
    c.drawString(40, height - 180, "Điểm Trung Bình:")
    c.setFont('DejaVuSans', 12)
    c.drawString(60, height - 200, f"Độ trôi chảy (Fluency): {avg['fluency']}/10")
    c.drawString(60, height - 220, f"Kiến thức chuyên môn (Knowledge): {avg['knowledge']}/10")
    c.drawString(60, height - 240, f"Kỹ năng mềm (Soft Skills): {avg['soft_skills']}/10")

    # Chi tiết từng câu hỏi
    y = height - 280
    c.setFont('DejaVuSans', 14)
    c.drawString(40, y, "Chi Tiết Phỏng Vấn:")
    y -= 20

    c.setFont('DejaVuSans', 10)
    for item in scores['detailed']:
        q = item['question']
        a = item['answer']
        f_s = item['fluency']
        k_s = item['knowledge']
        s_s = item['soft_skills']

        # Nếu không đủ chỗ, chuyển trang
        if y < 80:
            c.showPage()
            c.setFont('DejaVuSans', 10)
            y = height - 50

        c.drawString(40, y, f"Q: {q}")
        y -= 14
        c.drawString(60, y, f"A: {a}")
        y -= 14
        c.drawString(60, y, f"Fluency: {f_s}/10   Knowledge: {k_s}/10   Soft Skills: {s_s}/10")
        y -= 20

    c.save()
    return filename
