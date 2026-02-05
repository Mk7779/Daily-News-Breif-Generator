import streamlit as st
import feedparser
import requests
import os
from datetime import date

# ---------------- CONFIG ---------------- #
HF_API_KEY = os.getenv("HF_API_KEY")

SUMMARIZER_API = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}

# ---------------- RSS SOURCES ---------------- #
NEWS_SOURCES = {
    "Technology": [
        "https://feeds.bbci.co.uk/news/technology/rss.xml",
        "https://www.theverge.com/rss/index.xml"
    ],
    "Business": [
        "https://feeds.bbci.co.uk/news/business/rss.xml",
        "https://www.reuters.com/rssFeed/businessNews"
    ],
    "Sports": [
        "https://feeds.bbci.co.uk/sport/rss.xml"
    ],
    "Health": [
        "https://feeds.bbci.co.uk/news/health/rss.xml"
    ],
    "Entertainment": [
        "https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml"
    ],
    "Politics": [
        "https://feeds.bbci.co.uk/news/politics/rss.xml"
    ]
}

# ---------------- FUNCTIONS ---------------- #

def fetch_articles(category, limit=5):
    articles = []
    for feed_url in NEWS_SOURCES.get(category, []):
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:limit]:
            articles.append({
                "title": entry.title,
                "summary": entry.get("summary", ""),
                "source": feed.feed.get("title", "Unknown")
            })
    return articles


def summarize_text(text):
    if len(text.strip()) < 50:
        return text

    payload = {
        "inputs": text,
        "parameters": {"max_length": 60, "min_length": 25}
    }

    response = requests.post(
        SUMMARIZER_API,
        headers=HEADERS,
        json=payload
    )

    if response.status_code == 200:
        return response.json()[0]["summary_text"]

    return "Summary not available."


# ---------------- STREAMLIT UI ---------------- #

st.set_page_config(page_title="Daily News Brief Generator", layout="wide")

st.title("📰 AI Daily News Brief Generator")

st.sidebar.header("Preferences")

selected_categories = st.sidebar.multiselect(
    "Select News Segments",
    list(NEWS_SOURCES.keys()),
    default=["Technology"]
)

selected_date = st.sidebar.date_input(
    "Select Date",
    value=date.today()
)

reading_style = st.sidebar.selectbox(
    "Reading Preference",
    ["Short", "Detailed"]
)

st.markdown(
    f"### Your Personalized News Brief — {selected_date.strftime('%d %b %Y')}"
)

if not selected_categories:
    st.warning("Please select at least one category.")
else:
    for category in selected_categories:
        st.subheader(f"🔹 {category}")

        articles = fetch_articles(category)

        if not articles:
            st.write("No articles found.")
            continue

        for article in articles:
            summary = summarize_text(article["summary"])
            st.markdown(f"**• {summary}**")
            st.caption(f"Source: {article['source']}")

        st.divider()
