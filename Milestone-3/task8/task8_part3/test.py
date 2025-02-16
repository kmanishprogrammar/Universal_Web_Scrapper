import streamlit as st
from streamlit_tags import st_tags
from selenium import webdriver
import time, os
import json
import google.generativeai as genai
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from markdownify import markdownify as md
import random
from pydantic import create_model
from assets import USER_AGENTS 

response_data = [] 

def sel_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    user_agent = random.choice(USER_AGENTS)
    chrome_options.add_argument(f"user-agent={user_agent}")
    web_driver = webdriver.Chrome(options=chrome_options)
    return web_driver

def pydantic_model(fields):
    field_definitions = {field: (str, ...) for field in fields}
    return create_model("DynamicListingModel", **field_definitions)

def pydantic_container(model):
    return create_model("DynamicListingsContainer", listings=(list[model], ...))

def scrape_data(url):
    driver = sel_driver()
    try:
        driver.get(url)
        time.sleep(2)
        html_content = driver.page_source
        markdown_content = md(html_content)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
        output_path = f"output/scraped_data_{timestamp}.md"
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(markdown_content)
        
    finally:
        driver.quit()

def scrape(fields):
    global response_data 
    if fields:
        dynamic_model = pydantic_model(fields)
        dynamic_listing_container = pydantic_container(dynamic_model)

        genai.configure(api_key="AIzaSyD5zflCCvz5dG6W-A-3SgZ-QSf-DNCdfjw")

        model = genai.GenerativeModel("gemini-1.5-flash", generation_config={
            "response_schema": dynamic_listing_container,
            "response_mime_type": "application/json"} )
        prompt = f"scrape data about these fields{fields} and response should be in {dynamic_listing_container} format"
        response = model.generate_content(prompt)
        response_json = json.loads(response.text) 

        response_data = response_json["listings"]

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_output_path = f"output/scraped_data_{timestamp}.json"
        with open(json_output_path, "w", encoding="utf-8") as json_file:
            json.dump(response_data, json_file, indent=4)

        return response_json

def ui():
    st.set_page_config(layout="wide", page_title="Universal Web Scraper")
    st.markdown("<h1 style='text-align: center;'>Universal Web Scraper 🦑</h1>", unsafe_allow_html=True)
    with st.sidebar:
        st.markdown("### Web Scraper Settings")
        
        model = st.selectbox("Select Model", ["gpt", "gemini flash"])
        
        url = st.text_input("Enter URL")
        
        fields = st_tags(
            label="Enter Fields to Extract:",
            text="Press enter to add more",
            suggestions=["name", "email", "address", "phone"],
            maxtags=10,
            key="1")

        st.divider()
        
        if st.button("Scrape"):
            scrape(fields) 
    if response_data:
        st.success("Data Scraped successfully")
        st.dataframe(response_data) 

ui()
