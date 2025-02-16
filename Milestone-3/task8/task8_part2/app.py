import streamlit as st
from streamlit_tags import st_tags_sidebar
from scraper import scrape_and_convert 

st.set_page_config(
    page_title="Web Scraper Settings",
    page_icon="🦑",
    layout="wide"
)

st.title("Universal Web Scraper 🦑")

st.sidebar.header("Web Scraper Settings")
model_options = ["gpt-4o-mini", "gemini-1.5-flash", "gpt-3.5-turbo"]
selected_model = st.sidebar.selectbox("Select Model", model_options)

url_input = st.sidebar.text_input("Enter URL", "")

st.sidebar.header("Enter Fields to Extract:")

fields_to_extract = st_tags_sidebar(
    value=[],  
    suggestions=[], 
    label="", 
    text="Press enter to add fields",  
    maxtags=100, 
    key="fields"  
)

st.sidebar.markdown("---")

scrape_button = st.sidebar.button("Scrape")

if scrape_button:
    if url_input:
        output_file = scrape_and_convert(url_input)
        if output_file:
            st.success(f"Scraping complete! Markdown saved to: {output_file}")
        else:
            st.error("Failed to scrape the URL. Please try again.")
    else:
        st.warning("Please enter a URL to scrape.")

st.sidebar.markdown("""
<style>
.sidebar .sidebar-content {
    background-color: #222;
    color: #fff;
}
.sidebar input, .sidebar select {
    background-color: #333;
    color: #fff;
    border: 1px solid #555;
}
.sidebar button {
    background-color: #444;
    color: #fff;
    border: 1px solid #555;
}
</style>
""", unsafe_allow_html=True)
