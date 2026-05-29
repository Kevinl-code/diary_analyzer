import streamlit as st
import pandas as pd
import plotly.express as px
from textblob import TextBlob
from collections import Counter
import re
import nltk
from nltk.corpus import stopwords

st.set_page_config(
    page_title="MindTrack",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "df" not in st.session_state:
    st.session_state.df = None

if "analyzed" not in st.session_state:
    st.session_state.analyzed = False

if "filename" not in st.session_state:
    st.session_state.filename = ""

try:
    stop_words = set(stopwords.words("english"))
except:
    nltk.download("stopwords")
    stop_words = set(stopwords.words("english"))

st.markdown("""
<style>

/* =========================================================
GOOGLE FONTS
========================================================= */

@import url('https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;600;700&family=Poppins:wght@400;500;600;700&display=swap');

/* =========================================================
ROOT VARIABLES
========================================================= */

:root {

    --primary-bg: rgba(255,255,255,0.04);
    --border-color: rgba(120,120,120,0.15);
    --card-radius: 18px;

}

/* =========================================================
GLOBAL
========================================================= */

html, body, .stApp {

    font-family: 'Poppins', sans-serif;
}

/* =========================================================
HEADINGS
========================================================= */

h1, h2, h3, h4, h5 {

    font-family: 'Figtree', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: -0.5px;
}

/* =========================================================
MAIN CONTAINER
========================================================= */

.block-container {

    padding-top: 1.2rem;
    padding-bottom: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

/* =========================================================
SIDEBAR
========================================================= */

section[data-testid="stSidebar"] {

    background: rgba(255,255,255,0.02);
    border-right: 1px solid var(--border-color);
}

section[data-testid="stSidebar"] * {

    font-family: 'Poppins', sans-serif !important;
}

/* =========================================================
RADIO BUTTONS
========================================================= */

.stRadio label {

    font-size: 15px !important;
    font-weight: 500 !important;
}

/* =========================================================
METRIC CARDS
========================================================= */

[data-testid="metric-container"] {

    background: var(--primary-bg);
    border: 1px solid var(--border-color);

    padding: 18px;

    border-radius: var(--card-radius);

    backdrop-filter: blur(12px);

    transition: 0.3s ease;
}

[data-testid="metric-container"]:hover {

    transform: translateY(-2px);
}

/* =========================================================
BUTTONS
========================================================= */

.stButton button {

    width: 100%;

    border-radius: 14px;

    border: 1px solid var(--border-color);

    padding: 0.7rem 1rem;

    font-weight: 600;

    transition: 0.3s ease;
}

.stButton button:hover {

    transform: translateY(-2px);
}

/* =========================================================
UPLOAD BOX
========================================================= */

[data-testid="stFileUploaderDropzone"] {

    border-radius: 16px;

    border: 2px dashed rgba(120,120,120,0.3);

    padding: 1.5rem;

    background: rgba(255,255,255,0.02);
}

/* =========================================================
DATAFRAME
========================================================= */

[data-testid="stDataFrame"] {

    border-radius: 16px;

    overflow: hidden;

    border: 1px solid var(--border-color);
}

/* =========================================================
ALERTS
========================================================= */

.stAlert {

    border-radius: 14px;
}

/* =========================================================
PLOTLY CHARTS
========================================================= */

.js-plotly-plot {

    border-radius: 18px;

    overflow: hidden;

    border: 1px solid var(--border-color);

    padding: 10px;

    background: rgba(255,255,255,0.02);
}

/* =========================================================
SCROLLBAR
========================================================= */

::-webkit-scrollbar {

    width: 8px;
}

::-webkit-scrollbar-thumb {

    background: rgba(120,120,120,0.3);

    border-radius: 10px;
}

/* =========================================================
REMOVE STREAMLIT BRANDING
========================================================= */

#MainMenu {

    visibility: hidden;
}

footer {

    visibility: hidden;
}

header {

    visibility: hidden;
}

/* =========================================================
MOBILE RESPONSIVE
========================================================= */

@media screen and (max-width: 768px) {

    .block-container {

        padding-left: 1rem;
        padding-right: 1rem;
    }

    h1 {

        font-size: 2rem !important;
    }
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("🧭 Navigation")

page = st.sidebar.radio(
    "Go To",
    [
        "Home",
        "Diary Analysis",
        "Insights",
        "Suggestions"
    ]
)
st.sidebar.markdown("---")

if st.session_state.get("analyzed"):
    st.sidebar.success("Analysis Ready")

    st.sidebar.write(
        f"📄 {st.session_state.get('filename')}"
    )
    
    if st.sidebar.button("🗑 Clear Analysis"):
    
        st.session_state.df = None
        st.session_state.analyzed = False
        st.session_state.filename = ""
    
        st.rerun()

else:

    st.sidebar.info("No diary analyzed yet")

if page == "Home":

    st.title("🧠 MindTrack")

    st.subheader("Mental Health Analyzer")

    st.write("""
    Upload your personal diary entries and discover emotional trends,
    recurring stress patterns, and wellness insights through lightweight NLP.
    """)
    st.subheader("📁 Upload Diary Entries as CSV")

    uploaded_file = st.file_uploader(
        "Choose CSV File",
        type=["csv"]
    )

    st.info("""
    Required CSV Columns:
    - date
    - entry
    """)
    
    analyze_btn = st.button("🔍 Analyze Diary")
    if uploaded_file is not None and analyze_btn:
        try:
            with st.spinner("Analyzing diary entries..."):
                df = pd.read_csv(uploaded_file)

                if df.empty:
    
                    st.error("CSV file contains no data.")
                    st.stop()
    
                df.columns = df.columns.str.lower().str.strip()
                required_columns = ["date", "entry"]
    
                for col in required_columns:
    
                    if col not in df.columns:
    
                        st.error(
                            f"Missing required column: {col}"
                        )
    
                        st.stop()
                        
                df = df.dropna(subset=["entry"])
                df["entry"] = df["entry"].astype(str)
                df = df[df["entry"].str.strip() != ""]
                df["date"] = pd.to_datetime(
                    df["date"],
                    errors="coerce"
                )
                df = df.dropna(subset=["date"])
    
                df["date"] = df["date"].dt.strftime(
                    "%Y-%m-%d"
                )
                if len(df) > 500:
    
                    st.warning(
                        "Large dataset detected. Using first 500 rows."
                    )
    
                    df = df.head(500)

    
                def clean_text(text):
    
                    text = text.lower()
    
                    text = re.sub(
                        r"[^a-zA-Z ]",
                        "",
                        text
                    )
    
                    words = text.split()
    
                    words = [
                        word for word in words
                        if word not in stop_words
                    ]
    
                    return " ".join(words)
    
                df["cleaned"] = df["entry"].apply(
                    clean_text
                )
    
                def get_sentiment(text):
    
                    polarity = TextBlob(
                        text
                    ).sentiment.polarity
    
                    if polarity > 0:
    
                        return "Positive"
    
                    elif polarity < 0:
    
                        return "Negative"
    
                    else:
    
                        return "Neutral"
    
                df["sentiment"] = df["entry"].apply(
                    get_sentiment
                )
    
                df["score"] = df["entry"].apply(
                    lambda x:
                    TextBlob(x).sentiment.polarity
                )

    
                df = df.sort_values("date")
    
    
                st.session_state.df = df
                st.session_state.analyzed = True
                st.session_state.filename = uploaded_file.name
                st.success(
                    "Diary analysis completed successfully!"
                )
    
        except pd.errors.EmptyDataError:
    
            st.error(
                "Uploaded CSV file is empty."
            )
    
        except UnicodeDecodeError:
    
            st.error(
                "Encoding issue. Save CSV as UTF-8."
            )
    
        except Exception as e:
    
            st.error(
                f"Error processing file: {e}"
            )

if st.session_state.analyzed:

    st.markdown("---")

    st.success(
        f"Current Analysis Loaded: {st.session_state.filename}"
    )

df = st.session_state.get("df")

if page == "Diary Analysis":
    st.title("📄 Diary Analysis")

    if df is None:
        st.warning("Please upload a CSV file in Home page.")
    else:
        st.subheader("Uploaded Diary Data")
        st.dataframe(
            df[["date", "entry", "sentiment"]],
            use_container_width=True
        )
        st.markdown("---")
        total_entries = len(df)
        positive_count = len(
            df[df["sentiment"] == "Positive"]
        )
        negative_count = len(
            df[df["sentiment"] == "Negative"]
        )
        neutral_count = len(
            df[df["sentiment"] == "Neutral"]
        )
        mental_energy = round(
            (positive_count / total_entries) * 100,
            2
        )
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Entries", total_entries)
        col2.metric("Positive", positive_count)
        col3.metric("Negative", negative_count)
        col4.metric("Neutral", neutral_count)
        col5.metric("Mental Energy",f"{mental_energy}%")
        
if page == "Insights":
    st.title("📊 Emotional Insights")
    if df is None:
        st.warning("Please upload a CSV file in Home page.")
    else:
        st.subheader("📈 Mood Trend")

        line_fig = px.line(
            df,
            x="date",
            y="score",
            markers=True
        )

        line_fig.update_layout(
            template="plotly",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )

        st.plotly_chart(
            line_fig,
            use_container_width=True
        )

        st.subheader("🥧 Emotion Distribution")

        pie_data = df["sentiment"].value_counts()

        pie_fig = px.pie(
            names=pie_data.index,
            values=pie_data.values
        )

        pie_fig.update_layout(
            template="plotly",
            paper_bgcolor="rgba(0,0,0,0)"
        )

        st.plotly_chart(
            pie_fig,
            use_container_width=True
        )

        st.subheader("🔍 Common Emotional Words")

        all_words = " ".join(df["cleaned"]).split()

        common_words = Counter(all_words).most_common(10)

        word_df = pd.DataFrame(
            common_words,
            columns=["Word", "Count"]
        )

        bar_fig = px.bar(
            word_df,
            x="Word",
            y="Count"
        )

        bar_fig.update_layout(
            template="plotly",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )

        st.plotly_chart(
            bar_fig,
            use_container_width=True
        )

if page == "Suggestions":

    st.title("💡 Wellness Suggestions")

    if df is None:

        st.warning("Please upload a CSV file in Home page.")

    else:

        text_data = " ".join(df["cleaned"])

        suggestions = []

        if "stress" in text_data:

            suggestions.append(
                "Try taking small breaks and reducing continuous workload pressure."
            )

        if "anxious" in text_data:

            suggestions.append(
                "Practice mindfulness or breathing exercises regularly."
            )

        if "tired" in text_data:

            suggestions.append(
                "Improve sleep schedule and hydration habits."
            )

        if "lonely" in text_data:

            suggestions.append(
                "Spend time with supportive friends or family."
            )

        if "sad" in text_data:

            suggestions.append(
                "Engage in activities you enjoy and avoid isolation."
            )

    
        positive_count = len(
            df[df["sentiment"] == "Positive"]
        )

        mental_energy = round(
            (positive_count / len(df)) * 100,
            2
        )

        st.metric(
            "Mental Energy Score",
            f"{mental_energy}%"
        )

        st.markdown("---")

        if mental_energy > 70:

            st.success(
                "Your emotional trend appears healthy and stable."
            )

        elif mental_energy > 40:

            st.warning(
                "Your emotional state shows moderate fluctuations."
            )

        else:

            st.error(
                "Your diary indicates emotional strain and stress."
            )

        st.markdown("---")

        st.subheader("🌿 Personalized Suggestions")

        if len(suggestions) == 0:

            st.info(
                "Maintain healthy routines and continue journaling consistently."
            )

        else:

            for suggestion in suggestions:

                st.success(suggestion)

st.markdown("---")

st.caption(
    "MindTrack • Lightweight Mental Health NLP Analyzer"
)
