import streamlit as st
from streamlit_tags import st_tags_sidebar

st.set_page_config(
    page_title="Web Scraper Settings",
    page_icon="🦑",
    layout="wide"
)

# Title and logo
st.title("Universal Web Scraper 🦑")

# Model selection
st.sidebar.header("Web Scraper Settings")
model_options = ["gpt-4o-mini", "gemini-1.5-flash", "gpt-3.5-turbo"]
selected_model = st.sidebar.selectbox("Select Model", model_options)

# URL input
url_input = st.sidebar.text_input("Enter URL", "")

# Custom sidebar for tags (using st_tags_sidebar)
st.sidebar.header("Enter Fields to Extract:")

# Create the tags input box inside sidebar using st_tags_sidebar
fields_to_extract = st_tags_sidebar(
    value=[],  # Start with an empty list of tags
    suggestions=[],  # Optional: add any suggestions if needed
    label="",  # No label for input
    text="Press enter to add fields",  # Instructions for the user
    maxtags=100,  # Set a reasonable max if needed
    key="fields",  # Unique key for Streamlit state management
)

st.sidebar.markdown("---")
# Scrape button
scrape_button = st.sidebar.button("Scrape")

# Display extracted data (placeholder)
if scrape_button:
    st.write("**Extracted Data:**")
    for field in fields_to_extract:
        st.write(f"{field.capitalize()}: ...")

# Style the sidebar
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
