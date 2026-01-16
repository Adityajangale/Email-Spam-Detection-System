import streamlit as st
import pickle
import re
import string
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')

# -----------------------
# Load Model and Vectorizer
# -----------------------
model = pickle.load(open('spam_model.pkl', 'rb'))
vectorizer = pickle.load(open('vectorizer.pkl', 'rb'))

# -----------------------
# Text Cleaning Function
# -----------------------
def clean_text(text):
    text = text.lower()
    text = re.sub(r'\d+', '', text)
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = " ".join([word for word in text.split() if word not in stopwords.words('english')])
    return text

# -----------------------
# Streamlit UI
# -----------------------
st.set_page_config(page_title="Spam Mail Detector", page_icon="📧", layout="centered")

st.title("📩 Spam Mail Detection System")
st.write("Enter an email or SMS message below to detect whether it’s Spam or Not Spam:")

user_input = st.text_area("Enter your message:", height=150)

if st.button("Detect Spam"):
    if user_input.strip() == "":
        st.warning("⚠️ Please enter a message first!")
    else:
        cleaned = clean_text(user_input)
        vectorized = vectorizer.transform([cleaned])
        prediction = model.predict(vectorized)[0]

        if prediction == 1:
            st.error("🚫 This message is **SPAM**!")
        else:
            st.success("✅ This message is **NOT SPAM**!")

st.markdown("---")
st.caption("Built with ❤️ using Python, NLP, and Streamlit")