import streamlit as st
import pandas as pd
import plotly.express as px
from collections import Counter
from textblob import TextBlob
import re
import nltk
from nltk.corpus import stopwords

st.set_page_config(
    page_title="MindTrack",
    page_icon="diary_analyzer/assets/logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "df" not in st.session_state:
    st.session_state.df = None
if "analyzed" not in st.session_state:
    st.session_state.analyzed = False
if "filename" not in st.session_state:
    st.session_state.filename = ""
if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

try:
    stop_words = set(stopwords.words("english"))
except:
    nltk.download("stopwords")
    stop_words = set(stopwords.words("english"))

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;600;700&family=Poppins:wght@400;500;600;700&display=swap');

:root {
    --primary-bg: rgba(255,255,255,0.04);
    --border-color: rgba(120,120,120,0.15);
    --card-radius: 18px;
}

html, body, .stApp {
    font-family: 'Poppins', sans-serif;
}

h1, h2, h3, h4, h5 {
    font-family: 'Figtree', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: -0.5px;
}

.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

section[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.02);
    border-right: 1px solid var(--border-color);
}

.stRadio label {
    font-size: 15px !important;
    font-weight: 500 !important;
}

[data-testid="metric-container"] {
    background: var(--primary-bg);
    border: 1px solid var(--border-color);
    padding: 18px;
    border-radius: var(--card-radius);
    backdrop-filter: blur(12px);
}

.stButton button {
    width: 100%;
    border-radius: 14px;
    border: 1px solid var(--border-color);
    padding: 0.7rem 1rem;
    font-weight: 600;
}

[data-testid="stFileUploaderDropzone"] {
    border-radius: 16px;
    border: 2px dashed rgba(120,120,120,0.3);
    padding: 1.5rem;
}

#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

@media screen and (max-width: 768px) {
    .block-container { padding-left: 1rem; padding-right: 1rem; }
    h1 { font-size: 2rem !important; }
}
</style>
""", unsafe_allow_html=True)

st.sidebar.title("🧭 Navigation")
st.sidebar.write("Upload your personal diary entries to discover emotional trends.")

st.sidebar.subheader("📁 Upload Diary CSV")
uploaded_file = st.sidebar.file_uploader(
    "Choose CSV File",
    type=["csv"],
    label_visibility="collapsed"
)

st.sidebar.info("Required columns: **date**, **entry**")

if uploaded_file is not None:
    if st.sidebar.button("🔍 Analyze Diary", use_container_width=True):
        try:
            with st.spinner("Analyzing diary entries..."):
                df = pd.read_csv(uploaded_file)
                
                if df.empty:
                    st.error("CSV file contains no data.")
                    st.stop()

                df.columns = df.columns.str.lower().str.strip()
                if "date" not in df.columns or "entry" not in df.columns:
                    st.error("Missing required columns: date, entry")
                    st.stop()

                df = df.dropna(subset=["entry"])
                df["entry"] = df["entry"].astype(str)
                df["date"] = pd.to_datetime(df["date"], errors="coerce")
                df = df.dropna(subset=["date"])
                df["date"] = df["date"].dt.strftime("%Y-%m-%d")

                def clean_text(text):
                    text = text.lower()
                    text = re.sub(r"[^a-zA-Z ]", "", text)
                    return " ".join([w for w in text.split() if w not in stop_words])

                def get_sentiment(text):
                    polarity = TextBlob(text).sentiment.polarity
                    return "Positive" if polarity > 0 else ("Negative" if polarity < 0 else "Neutral")

                df["cleaned"] = df["entry"].apply(clean_text)
                df["sentiment"] = df["entry"].apply(get_sentiment)
                df["score"] = df["entry"].apply(lambda x: TextBlob(x).sentiment.polarity)
                df = df.sort_values("date")

                st.session_state.df = df
                st.session_state.analyzed = True
                st.session_state.filename = uploaded_file.name
                
                st.session_state.current_page = "Diary Analysis"
                st.rerun()

        except Exception as e:
            st.sidebar.error(f"Error processing file: {e}")

page_options = ["Home", "Diary Analysis", "Insights", "Suggestions"]

if "navigation_radio" not in st.session_state:
    st.session_state["navigation_radio"] = st.session_state.current_page

selected_page = st.sidebar.radio(
    "Go To",
    page_options,
    key="navigation_radio"
)
st.session_state.current_page = selected_page

st.sidebar.markdown("---")

if st.session_state.analyzed:
    st.sidebar.success(f"📄 Active: {st.session_state.filename}")
    if st.sidebar.button("🗑 Clear Analysis", use_container_width=True):
        st.session_state.df = None
        st.session_state.analyzed = False
        st.session_state.filename = ""
        st.session_state.current_page = "Home"
        st.session_state["navigation_radio"] = "Home"
        st.rerun()

df = st.session_state.df

if st.session_state.current_page == "Home":
    st.title("🧠 MindTrack")
    st.subheader("Mental Health Diary NLP Analyzer")
    st.write("Please use the sidebar on the left to upload your diary file and begin your journey.")
    
    st.markdown("---")
    st.subheader("📄 Example CSV Format Required")
    sample_df = pd.DataFrame({
        "date": ["2026-05-01", "2026-05-02"],
        "entry": ["Feeling stressed because of workload", "Today was peaceful and relaxing"]
    })
    st.dataframe(sample_df, use_container_width=True)

elif st.session_state.current_page == "Diary Analysis":
    st.title("📄 Diary Analysis")
    if df is None:
        st.warning("Please upload a CSV file in the Sidebar to unpack analysis data.")
    else:
        st.subheader("Uploaded Diary Matrix Data")
        st.dataframe(df[["date", "entry", "sentiment"]], use_container_width=True)

        st.markdown("---")
        total_entries = len(df)
        positive_count = len(df[df["sentiment"] == "Positive"])
        negative_count = len(df[df["sentiment"] == "Negative"])
        neutral_count = len(df[df["sentiment"] == "Neutral"])
        mental_energy = round((positive_count / total_entries) * 100, 2) if total_entries > 0 else 0

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Entries", total_entries)
        col2.metric("Positive", positive_count)
        col3.metric("Negative", negative_count)
        col4.metric("Neutral", neutral_count)
        col5.metric("Mental Energy", f"{mental_energy}%")

elif st.session_state.current_page == "Insights":
    st.title("📊 Emotional Insights & Visualizations")
    if df is None:
        st.warning("Please upload a CSV file in the Sidebar to map trends.")
    else:
        st.subheader("📈 Mood Polarity Trend Across Time")
        line_fig = px.line(df, x="date", y="score", markers=True)
        line_fig.update_layout(template="plotly", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(line_fig, use_container_width=True)

        st.subheader("🥧 Overall Metric Sentiment Breakdown")
        pie_data = df["sentiment"].value_counts()
        pie_fig = px.pie(names=pie_data.index, values=pie_data.values)
        st.plotly_chart(pie_fig, use_container_width=True)

        st.subheader("🔍 Context Keyword Occurrences")
        all_words = " ".join(df["cleaned"].dropna()).split()
        if all_words:
            common_words = Counter(all_words).most_common(10)
            word_df = pd.DataFrame(common_words, columns=["Word", "Count"])
            bar_fig = px.bar(word_df, x="Word", y="Count")
            st.plotly_chart(bar_fig, use_container_width=True)

elif st.session_state.current_page == "Suggestions":
    st.title("💡 Wellness Suggestions")
    if df is None:
        st.warning("Please upload a CSV file in the Sidebar.")
    else:
        text_data = " ".join(df["cleaned"].dropna())
        suggestions = []

        if "stress" in text_data: suggestions.append("Try taking small structural breaks during work cycles.")
        if "anxious" in text_data: suggestions.append("Practice box-breathing exercises regularly.")
        if "tired" in text_data: suggestions.append("Prioritize checking your hydration metrics and circadian routine.")

        positive_count = len(df[df["sentiment"] == "Positive"])
        mental_energy = round((positive_count / len(df)) * 100, 2) if len(df) > 0 else 0

        st.metric("Aggregate Mental Energy Score", f"{mental_energy}%")
        st.markdown("---")
        
        if len(suggestions) == 0:
            st.info("No negative stressors detected! Continue keeping up your current routine.")
        else:
            for suggestion in suggestions:
                st.success(suggestion)

st.markdown("---")
st.caption("MindTrack • Lightweight Mental Health NLP Analyzer")
