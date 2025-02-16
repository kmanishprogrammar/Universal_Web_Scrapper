import random
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify
from datetime import datetime
import os
from assets import USER_AGENTS 

def scrape_and_convert(url):
    try:
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        
        # Fetch HTML content with the selected user agent
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Check if request was successful

        # Clean the HTML with BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")
        for tag in soup(["script", "style"]):
            tag.decompose()

        # Convert HTML to Markdown
        markdown_content = markdownify(str(soup), heading_style="ATX")

        # Save output in 'output' folder with a timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"output/markdown_{timestamp}.md"
        
        if not os.path.exists("output"):
            os.makedirs("output")

        # Write to Markdown file
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(markdown_content)

        return output_path
    except Exception as e:
        print(f"Error during scraping: {e}")
        return None
