# imap.py
import imaplib
import email
import re
import string
import os
import nltk
from email.header import decode_header
from bs4 import BeautifulSoup
import pickle
from dotenv import load_dotenv
from nltk.corpus import stopwords
from datetime import datetime, timedelta


# -------------------------------------------------
# Load environment variables
# -------------------------------------------------
load_dotenv()
IMAP_HOST = os.getenv("IMAP_HOST", "imap.gmail.com")
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

# -------------------------------------------------
# Load model & vectorizer (portable paths)
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL = pickle.load(open(os.path.join(BASE_DIR, "spam_model.pkl"), "rb"))
VECT  = pickle.load(open(os.path.join(BASE_DIR, "vectorizer.pkl"), "rb"))

import nltk
from nltk.corpus import stopwords

try:
    STOPWORDS = set(stopwords.words("english"))
except LookupError:
    nltk.download("stopwords")
    STOPWORDS = set(stopwords.words("english"))


# -------------------------------------------------
# Text cleaning helpers
# -------------------------------------------------
def clean_text(text):
    text = text or ""
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\d+", "", text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    return " ".join([w for w in text.split() if w not in STOPWORDS])

def html_to_text(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator=" ", strip=True)

def decode_mime_words(s):
    if not s:
        return ""
    decoded = ""
    for part, enc in decode_header(s):
        if isinstance(part, bytes):
            decoded += part.decode(enc or "utf-8", errors="ignore")
        else:
            decoded += part
    return decoded

# -------------------------------------------------
# Extract subject & body
# -------------------------------------------------
def extract_subject_and_body(msg):
    subject = decode_mime_words(msg.get("Subject", ""))
    body = ""

    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            disp = str(part.get("Content-Disposition"))

            if ctype == "text/plain" and "attachment" not in disp:
                body = part.get_payload(decode=True).decode(errors="ignore")
                break

            elif ctype == "text/html" and not body:
                html = part.get_payload(decode=True).decode(errors="ignore")
                body = html_to_text(html)
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            body = payload.decode(errors="ignore")

    return subject, body

# -------------------------------------------------
# Spam prediction
# -------------------------------------------------
def is_spam_text(text):
    cleaned = clean_text(text)
    vect = VECT.transform([cleaned])
    pred = MODEL.predict(vect)[0]
    proba = MODEL.predict_proba(vect)[0] if hasattr(MODEL, "predict_proba") else None
    return bool(pred), proba

# -------------------------------------------------
# MAIN FUNCTION (USED BY STREAMLIT UI)
# -------------------------------------------------
def poll_inbox_once():
    results = []

    # Last 30 days filter (dynamic & future-proof)
    since_date = (datetime.now() - timedelta(days=30)).strftime("%d-%b-%Y")

    M = imaplib.IMAP4_SSL(IMAP_HOST)
    M.login(EMAIL, PASSWORD)
    M.select("INBOX")

    status, data = M.search(None, f'(UNSEEN SINCE "{since_date}")')
    if status != "OK":
        M.logout()
        return results

    for num in data[0].split():
        _, msg_data = M.fetch(num, "(RFC822)")
        raw = msg_data[0][1]
        msg = email.message_from_bytes(raw)

        subject, body = extract_subject_and_body(msg)
        full_text = f"{subject}\n{body}"

        spam_flag, proba = is_spam_text(full_text)

        results.append({
            "Subject": subject,
            "Spam": spam_flag,
            "Spam_Probability": float(proba[1]) if proba is not None else None
        })

        # Gmail actions (SAFE)
        if spam_flag:
            M.store(num, "+X-GM-LABELS", "\\Spam")

    M.close()
    M.logout()

    return results

# -------------------------------------------------
# Direct run (backend / debug)
# -------------------------------------------------
if __name__ == "__main__":
    data = poll_inbox_once()
    for row in data:
        print(row)
