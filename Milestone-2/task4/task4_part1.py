import os
import re
import requests
from bs4 import BeautifulSoup

def create_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

def sanitize_folder_name(folder_name):
    # Replace any invalid characters with an underscore or empty string
    return re.sub(r'[\\/*?:"<>|]', '_', folder_name).strip()

def scrape_category(url, parent_folder):
    try:
        response=requests.get(url)
        response.raise_for_status()
        soup=BeautifulSoup(response.text, 'html.parser')

        category_blocks=soup.find_all(['li', 'div'], class_='category-block')
        if not category_blocks:
            print(f"No category blocks found at {url}")
            return

        for block in category_blocks:
            link=block.find('a')
            if link:
                name=link.find('div', class_='card-body').text.strip()
                href=link['href']

                sanitized_name=sanitize_folder_name(name)

                category_folder=os.path.join(parent_folder, sanitized_name)
                create_folder(category_folder)

                full_url=requests.compat.urljoin(url,href)

                scrape_category(full_url, category_folder)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")

if __name__=="__main__":
    base_url= "https://directory.wigan.gov.uk/kb5/wigan/fsd/home.page"

    main_folder= 'Wigan_Categories_1'
    create_folder(main_folder)

    scrape_category(base_url, main_folder)