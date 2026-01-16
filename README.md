# 📧 Live Email Spam Detection System

An end-to-end email spam detection system using Machine Learning and NLP.
The system integrates with Gmail using IMAP, detects spam emails in real time,
and safely moves only confirmed spam emails to the Spam folder.

##  Features
- NLP-based spam detection (TF-IDF + Naive Bayes)
- Gmail IMAP integration (Unread + Last 30 days filter)
- Streamlit dashboard for live monitoring
- Safe design: non-spam emails remain unread
- Production-ready architecture

##  Tech Stack
- Python
- Scikit-learn
- NLTK
- Streamlit
- IMAP (Gmail)

##  Project Structure
- `imap.py` → Backend IMAP spam scanner
- `imap_ui.py` → Streamlit live dashboard
- `app.py` → Manual spam testing UI

##  How to Run Locally
```bash
pip install -r requirements.txt
streamlit run imap_ui.py
