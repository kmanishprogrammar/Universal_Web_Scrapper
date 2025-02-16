import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

def scrape_libraries_data():
    # Base URL for state library data
    base_url = "https://publiclibraries.com"

    # URL of the main page with the state links
    main_url = "https://publiclibraries.com/state/"

    # Get the content of the main page
    response = requests.get(main_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Create directory to store CSV files
    if not os.path.exists('libraries_data'):
        os.makedirs('libraries_data')

    # Find all state links
    state_links = soup.select('.dropdown-content a')

    # Loop through each state link
    for state_link in state_links:
        state_name = state_link.text.strip()
        state_url = state_link['href']
        
        # Request the state page
        state_response = requests.get(state_url)
        state_soup = BeautifulSoup(state_response.content, 'html.parser')
        
        # Find the table containing the libraries' data
        table = state_soup.find('table')
        
        if table:
            # Extract table headers
            headers = [th.text.strip() for th in table.find_all('th')]
            
            # Extract table rows
            rows = []
            for tr in table.find_all('tr')[1:]:  # Skip header row
                cols = [td.text.strip() for td in tr.find_all('td')]
                rows.append(cols)
            
            # Create a pandas DataFrame
            df = pd.DataFrame(rows, columns=headers)
            
            # Save DataFrame to CSV with state name as the file name
            csv_file_path = f'libraries_data/{state_name}.csv'
            df.to_csv(csv_file_path, index=False)
            
            print(f"Data saved for {state_name} in {csv_file_path}")
        else:
            print(f"No table found for {state_name}")

# Call the function to scrape data
scrape_libraries_data()
