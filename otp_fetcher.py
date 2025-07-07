import imaplib
import email
import re
from bs4 import BeautifulSoup

def fetch_otp_from_email(email_address, password):
    try:
        domain = email_address.split('@')[-1]
        imap_server = {
            "yandex.com": "imap.yandex.com",
            "zoho.com": "imap.zoho.com"
        }.get(domain, None)

        if not imap_server:
            return "❌ Unsupported email domain."

        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email_address, password)
        mail.select("inbox")

        result, data = mail.search(None, "ALL")
        mail_ids = data[0].split()
        latest_email_id = mail_ids[-1]

        result, message_data = mail.fetch(latest_email_id, "(RFC822)")
        raw_email = message_data[0][1]
        msg = email.message_from_bytes(raw_email)

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/html":
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = msg.get_payload(decode=True).decode()

        soup = BeautifulSoup(body, "html.parser")
        text = soup.get_text()

        otp_match = re.search(r'\b\d{4,8}\b', text)
        if otp_match:
            return f"✅ Your OTP:\n{otp_match.group()}"
        else:
            return "❌ OTP not found in the email content."

    except Exception as e:
        return f"❌ Error fetching OTP: {str(e)}"