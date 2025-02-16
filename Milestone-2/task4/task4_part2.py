import os
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd

def create_folder(folder_name):
    """Create a folder if it doesn't already exist."""
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

def sanitize_folder_name(folder_name):
    """Sanitize folder names by replacing invalid characters."""
    return re.sub(r'[\\/*?:"<>|]', '_', folder_name).strip()

def write_to_csv(category_folder, category_name, data):
    """Write data to a CSV file."""
    file_name = os.path.join(category_folder, f"{sanitize_folder_name(category_name)}.csv")
    data.to_csv(file_name, mode='a', index=False, encoding='utf-8', header=not os.path.isfile(file_name))

def scrape_data_from_page(soup):
    """Scrape data from a BeautifulSoup object representing a page."""
    data = []
    results = soup.select("[id^=hit-]")  # All IDs that start with "hit-"
    
    for result in results:
        entry = {
            "Title": result.select_one("h3 a").get_text(strip=True) if result.select_one("h3 a") else "N/A",
            "Schedule": result.select_one(".mt-1.mb-3.font-weight-bold").get_text(strip=True) if result.select_one(".mt-1.mb-3.font-weight-bold") else "N/A",
            "Description": result.select_one("div.result-hit-body > div.mb-2, div.mb-2").get_text(strip=True) if result.select_one("div.result-hit-body > div.mb-2, div.mb-2") else "N/A",
            "Address": " ".join([span.get_text(strip=True) for span in result.select(".mb-3.text-muted .comma_split_line")]) if result.select(".mb-3.text-muted .comma_split_line") else "N/A",
            "Phone": result.select_one(".contact-links ul li:nth-child(1) span.comma_split_line.d-none.d-sm-block.text-body").get_text(strip=True) if result.select_one(".contact-links ul li:nth-child(1) span.comma_split_line.d-none.d-sm-block.text-body") else "N/A",
            "Email": result.select_one(".contact-links ul li:nth-child(2) a").get("href").replace("mailto:", "").strip() if result.select_one(".contact-links ul li:nth-child(2) a") else "N/A",
            "Website": result.select_one(".contact-links ul li:nth-child(3) a").get("href").strip() if result.select_one(".contact-links ul li:nth-child(3) a") else "N/A"
        }
        data.append(entry)
    
    return pd.DataFrame(data)

def scrape_category(url, parent_folder):
    """Recursively scrape categories and subcategories from the given URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        category_blocks = soup.find_all(['li', 'div'], class_='category-block')
        if not category_blocks:
            print(f"No category blocks found at {url}")
            return

        for block in category_blocks:
            link = block.find('a')
            if link:
                name = link.find('div', class_='card-body').text.strip()
                href = link['href']

                sanitized_name = sanitize_folder_name(name)
                category_folder = os.path.join(parent_folder, sanitized_name)
                create_folder(category_folder)

                full_url = requests.compat.urljoin(url, href)

                # Scrape the last subcategory page for data with pagination support
                scrape_last_subcategory(full_url, category_folder, sanitized_name)

                # Recursively scrape subcategories
                scrape_category(full_url, category_folder)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")

def scrape_last_subcategory(url, category_folder, category_name):
    """Scrape the last subcategory page with pagination support."""
    try:
        while url:  # Loop through all pages
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Scrape data from the current page
            data = scrape_data_from_page(soup)

            # Write data to CSV file if data is available
            if not data.empty:
                write_to_csv(category_folder, category_name, data)
                print(f"Data scraped and saved to {category_folder}/{category_name}.csv")

            # Find the active page and next page link
            active_page = soup.select_one("nav > ol > li.page-item.active")  # The currently active page

            if active_page:
                next_page = active_page.find_next_sibling("li")  # Look for the next page after the active one
                if next_page and next_page.find("a"):  # Check if there's a valid link
                    url = requests.compat.urljoin(url, next_page.find("a")['href'])  # Get the next page URL
                else:
                    url = None  # No more pages
            else:
                url = None  # No more pages

    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")

if __name__ == "__main__":
    base_url = "https://directory.wigan.gov.uk/kb5/wigan/fsd/home.page"

    main_folder = 'Wigan_Categories_2'
    create_folder(main_folder)

    scrape_category(base_url, main_folder)
