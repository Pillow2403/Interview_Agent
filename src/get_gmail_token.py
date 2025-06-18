# get_gmail_token.py
from google_auth_oauthlib.flow import InstalledAppFlow

# Scope chỉ để gửi mail
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def main():
    flow = InstalledAppFlow.from_client_secrets_file('credential.json', SCOPES)
    creds = flow.run_local_server(port=0)
    # Lưu token để tái sử dụng sau này
    with open('token.json', 'w') as f:
        f.write(creds.to_json())
    print("Token OAuth2 đã lưu vào token.json")

if __name__ == '__main__':
    main()
