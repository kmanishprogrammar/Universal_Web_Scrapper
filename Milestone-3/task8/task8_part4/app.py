import streamlit as st
from streamlit_tags import st_tags
import pandas as pd
from scraper import scrape
import io

def download_options(df):
    csv = df.to_csv(index=False).encode("utf-8")
    excel = io.BytesIO()
    df.to_excel(excel, index=False, engine="xlsxwriter")
    excel.seek(0)
    json_data = df.to_json(orient="records")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button("Download as CSV", csv, "records.csv", "text/csv")
    with col2:
        st.download_button("Download as Excel", excel, "records.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    with col3:
        st.download_button("Download as JSON", json_data, "records.json", "application/json")

def ui():
    st.set_page_config(layout="wide", page_title="Universal Web Scraper")
    st.markdown("<h1 style='text-align: center;'>Universal Web Scraper 🦑</h1>", unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("### Web Scraper Settings")
        model = st.selectbox("Select Model", ["gemini flash", "gpt-4-mini", "gpt-3.5-turbo"])
        url = st.text_input("Enter URL")
        fields = st_tags(
            label="Enter Fields to Extract:",
            text="Press enter to add more",
            suggestions=["name", "email", "address", "phone"],
            maxtags=10,
            key="1"
        )
        st.divider()
        if st.button("Scrape"):
            response = scrape(fields, url)
            st.session_state['response'] = response

    if 'response' in st.session_state:
        st.success("Data Scraped successfully")
        df = pd.DataFrame(st.session_state['response']["listings"])
        st.dataframe(df)
        download_options(df)

if __name__ == "__main__":
    ui()
