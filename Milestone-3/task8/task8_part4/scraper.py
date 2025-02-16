from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from markdownify import markdownify as md
import random
import json
import time
from pydantic import create_model
import google.generativeai as genai
from bs4 import BeautifulSoup
from assets import USER_AGENTS

system_prompt = """You are an intelligent text extraction and conversion assistant. Your task is to extract structured information
                        from the given text and convert it into a pure JSON format. The JSON should contain only the structured data extracted from the text,
                        with no additional commentary, explanations, or extraneous information.
                        You could encounter cases where you can't find the data of the fields you have to extract or the data will be in a foreign language.
                        Please process the following text and provide the output in pure JSON format with no words before or after the JSON:"""

user_prompt = f"Extract the following information from the provided text:\nPage content:\n\n"

def sel_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    user_agent = random.choice(USER_AGENTS)
    chrome_options.add_argument(f"user-agent={user_agent}")
    web_driver = webdriver.Chrome(options=chrome_options)
    return web_driver

def clean_raw_data(content):
    soup = BeautifulSoup(content, 'html.parser')
    if soup.header:
        soup.header.decompose()
    if soup.footer:
        soup.footer.decompose()
    return str(soup)

def markdown(url):
    driver = sel_driver()
    try:
        driver.get(url)
        time.sleep(2)
        html_content = driver.page_source
        cleaned_html = clean_raw_data(html_content)
        markdown_content = md(cleaned_html)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(f"output/scraped_data_{timestamp}.md", "w", encoding="utf-8") as file:
            file.write(markdown_content)
    finally:
        driver.quit()
    return markdown_content

def divide_chunks(text, max_tokens):
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        word_length = len(word) + 1 
        if current_length + word_length > max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_length = word_length
        else:
            current_chunk.append(word)
            current_length += word_length

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

def process_chunks(chunks, system_prompt, user_prompt, model):
    responses = []
    for chunk in chunks:
        prompt = f"{system_prompt} \n {user_prompt} {chunk}"
        response = model.generate_content(prompt)
        json_response = json.loads(response.text)
        responses.extend(json_response["listings"])
    return {"listings": responses}

def pydantic_model(fields):
    field_definitions = {field: (str, ...) for field in fields}
    return create_model("DynamicListingModel", **field_definitions)

def pydantic_container(model):
    return create_model("DynamicListingsContainer", listings=(list[model], ...))

def scrape(fields, url):
    if fields:
        dynamic_model = pydantic_model(fields)
        dynamic_listing_container = pydantic_container(dynamic_model)
        genai.configure(api_key="AIzaSyD5zflCCvz5dG6W-A-3SgZ-QSf-DNCdfjw")

        model = genai.GenerativeModel("gemini-1.5-flash", generation_config={
            "response_schema": dynamic_listing_container,
            "response_mime_type": "application/json",
            "temperature": 0,
            "max_output_tokens": 8096})
        raw_data = markdown(url)
        chunks = list(divide_chunks(raw_data, 1800))
        response = process_chunks(chunks, system_prompt, user_prompt, model)
        return response
