import streamlit as st
from imap import poll_inbox_once

st.set_page_config(page_title="📧 Email Spam Dashboard", layout="wide")
st.title("📬 Live Email Spam Monitor")

if st.button("Fetch Latest Emails"):
    data = poll_inbox_once()

    if data:
        st.dataframe(data, use_container_width=True)
    else:
        st.info("No new unread emails found.")
