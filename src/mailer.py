# src/mailer.py
import os, base64
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.message import EmailMessage
from dotenv import load_dotenv
from pathlib import Path

# Load ENV nếu còn dùng .env (để đọc HR_EMAIL, SMTP_USER)
load_dotenv()
HR_EMAIL = os.getenv('HR_EMAIL')
SENDER_EMAIL = os.getenv('SMTP_USER')  # địa chỉ Gmail dùng gửi

# Đường dẫn đến token và credentials
BASE_DIR = Path(__file__).resolve().parent.parent
TOKEN_PATH = BASE_DIR / 'token.json'
# Nếu muốn chỉ gửi mail, không cần credentials.json nữa

# Scope: gmail.send
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# Khởi tạo Gmail API service
creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
service = build('gmail', 'v1', credentials=creds)


def send_email_report(pdf_path: str, candidate_name: str, position: str):
    # Tạo EmailMessage với PDF đính kèm
    msg = EmailMessage()
    msg['To'] = HR_EMAIL
    msg['From'] = SENDER_EMAIL
    msg['Subject'] = f"[Báo Cáo] {candidate_name} - {position}"
    body = (
        f"Xin chào,\n\n"  
        f"Đính kèm báo cáo phỏng vấn ứng viên {candidate_name} cho vị trí {position}.\n\n"  
        "Trân trọng,\nAI Interviewer Bot"
    )
    msg.set_content(body)

    # Đọc file PDF và attach
    with open(pdf_path, 'rb') as f:
        pdf_data = f.read()
    msg.add_attachment(pdf_data, maintype='application', subtype='pdf', filename=Path(pdf_path).name)

    # Encode message
    raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode()

    # Gửi
    send_body = {'raw': raw_message}
    service.users().messages().send(userId='me', body=send_body).execute()
    print(f"Email báo cáo đã gửi tới {HR_EMAIL}")