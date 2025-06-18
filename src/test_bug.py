# 

#-----------------------------------------------------------------------------------
# #test dns
# import os, socket
# from dotenv import load_dotenv

# # Nạp .env ở thư mục gốc (project root)
# from pathlib import Path
# env_path = Path(__file__).resolve().parent.parent / '.env'
# load_dotenv(dotenv_path=env_path)

# server = os.getenv("SMTP_SERVER")
# print("SMTP_SERVER từ .env:", repr(server))
# if not server:
#     raise RuntimeError("❌ Bien SMTP_SERVER chua duoc thiet lap! Kiem tra lai file .env")

# # Nếu đến đây server không rỗng, mới test DNS lookup
# print("Thử DNS lookup:", server, "→", socket.gethostbyname(server))

#-----------------------------------------------------------------------------------
#test kết nối TCP tới port SMTP và thử login
# src/test_mail.py

import os
import socket
import smtplib
from dotenv import load_dotenv
from pathlib import Path

# 1. Load .env
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

server = os.getenv("SMTP_SERVER")
port   = int(os.getenv("SMTP_PORT", 587))
user   = os.getenv("SMTP_USER")
pwd    = os.getenv("SMTP_PASSWORD")

print("SMTP_SERVER:", repr(server))
print("SMTP_PORT  :", port)
print("SMTP_USER :", user)

# 2. Test TCP connect
print(f"\n→ Thử kết nối TCP đến {server}:{port} …")
sock = socket.socket()
sock.settimeout(5)
try:
    sock.connect((server, port))
    print("✅ TCP connection thành công!")
except Exception as e:
    print("❌ Không kết nối được TCP:", e)
finally:
    sock.close()

# 3. Test SMTP login
print(f"\n→ Thử login SMTP lên {server}:{port} …")
try:
    # Nếu port 587 (STARTTLS)
    smtp = smtplib.SMTP(server, port, timeout=10)
    smtp.ehlo()
    smtp.starttls()
    smtp.login(user, pwd)
    print("✅ SMTP login (TLS) thành công!")
    smtp.quit()
except Exception as e1:
    print("⚠️ Login TLS thất bại:", e1)
    # Thử SSL trên port 465
    try:
        print("→ Thử login SMTP_SSL lên port 465 …")
        smtp_ssl = smtplib.SMTP_SSL(server, 465, timeout=10)
        smtp_ssl.login(user, pwd)
        print("✅ SMTP_SSL login thành công!")
        smtp_ssl.quit()
    except Exception as e2:
        print("❌ SMTP_SSL login cũng thất bại:", e2)
