import imaplib, email, re
from bs4 import BeautifulSoup

IMAP_SERVERS = {
    "yandex.com": "imap.yandex.com",
    "zoho.com": "imap.zoho.com",
    "zohomail.com": "imap.zoho.com",
    "2k25mail.com": "imap.2k25mail.com"
}

def alias_in_any_header(msg, alias_email):
    alias_lower = alias_email.lower()
    for header in ["To", "Delivered-To", "X-Original-To", "Envelope-To"]:
        v = msg.get(header, "")
        if v and alias_lower in v.lower():
            return True
    return False

def extract_body(msg):
    body = ""
    html_content = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            payload = part.get_payload(decode=True)
            if payload:
                text = payload.decode(errors="ignore")
                if content_type == "text/plain":
                    body += text + "\n"
                elif content_type == "text/html":
                    html_content += text + "\n"
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            body = payload.decode(errors="ignore")
    if html_content:
        soup = BeautifulSoup(html_content, "html.parser")
        html_text = soup.get_text(separator="\n")
        body += "\n" + html_text
    return body

def find_otp(text):
    if not text:
        return None
    match = re.search(r"\b(\d{3})-(\d{3})\b", text)
    if match:
        return match.group(1) + match.group(2)
    match = re.search(r"\b\d{6}\b", text)
    if match:
        return match.group(0)
    match = re.search(r"\b\d{4,8}\b", text)
    if match:
        return match.group(0)
    match = re.search(r"(\d\s){3,7}\d", text)
    if match:
        return match.group(0).replace(" ", "")
    return None

def fetch_otp_from_email(email_address, password):
    try:
        domain = email_address.split("@")[1]
        if domain not in IMAP_SERVERS:
            return "❌ Bot only supports Yandex and Zoho."
        imap_server = IMAP_SERVERS[domain]
        base_email = email_address.split("+")[0] + "@" + domain
        alias_email = email_address
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(base_email, password)
        folders = ["INBOX", "FB-Security", "Spam", "Social networks", "Bulk", "Promotions", "[Gmail]/All Mail"]
        seen_otps = set()
        for folder in folders:
            try:
                select_status, _ = mail.select(folder)
                if select_status != "OK":
                    continue
                result, data = mail.search(None, "ALL")
                if result != "OK":
                    continue
                email_ids = data[0].split()[-20:]
                for eid in reversed(email_ids):
                    result, data = mail.fetch(eid, "(RFC822)")
                    if result != "OK":
                        continue
                    msg = email.message_from_bytes(data[0][1])
                    subject = msg.get("Subject", "")
                    from_email = msg.get("From", "")
                    folder_name = folder
                    to_field = msg.get("To", "")
                    if domain.endswith("yandex.com") and not alias_in_any_header(msg, alias_email):
                        continue
                    body = extract_body(msg)
                    otp = find_otp(body)
                    if not otp:
                        otp = find_otp(subject)
                    if otp and otp not in seen_otps:
                        seen_otps.add(otp)
                        return (
                            f"✅ Your OTP:
"
                            f"🔑 OTP: {otp}\n"
                            f"📩 From: {from_email}\n"
                            f"📝 Subject: {subject}\n"
                            f"📁 Folder: {folder_name}\n"
                            f"📥 To: {to_field}"
                        )
            except Exception:
                continue
        return "❌ No OTP found in the last 20 emails for this alias."
    except Exception as e:
        return f"❌ Error: {e}"
