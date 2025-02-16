import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
from io import BytesIO

# Function to get the main state links and their URLs
def get_state_links(main_url):
    response = requests.get(main_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    state_links = soup.select('.dropdown-content a')
    state_options = {state_link.text.strip(): state_link['href'] for state_link in state_links}
    return state_options

# Function to scrape library data for a specific state
def scrape_state_data(state_url):
    state_response = requests.get(state_url)
    state_soup = BeautifulSoup(state_response.content, 'html.parser')
    
    # Find the table containing the libraries' data
    table = state_soup.find('table')
    if not table:
        return None

    # Extract table headers
    headers = [th.text.strip() for th in table.find_all('th')]

    # Extract table rows
    rows = []
    for tr in table.find_all('tr')[1:]:  # Skip header row
        cols = [td.text.strip() for td in tr.find_all('td')]
        rows.append(cols)

    # Create and return a pandas DataFrame
    return pd.DataFrame(rows, columns=headers)

# Function to provide download options for CSV, Excel, and JSON
def download_data(df, state_name):
    st.write("Download the data:")
    
    # Create three columns for the buttons
    col1, col2, col3 = st.columns(3)

    # CSV Download
    csv_data = df.to_csv(index=False).encode('utf-8')
    with col1:
        st.download_button(label="Download as CSV", data=csv_data, file_name=f'{state_name}_libraries.csv', mime='text/csv')

    # Excel Download (using BytesIO)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    excel_data = output.getvalue()
    with col2:
        st.download_button(label="Download as Excel", data=excel_data, file_name=f'{state_name}_libraries.xlsx', mime='application/vnd.ms-excel')

    # JSON Download
    json_data = df.to_json(orient='records')
    with col3:
        st.download_button(label="Download as JSON", data=json_data, file_name=f'{state_name}_libraries.json', mime='application/json')

# Base URL for state library data
base_url = "https://publiclibraries.com"
main_url = "https://publiclibraries.com/state/"

# Get the state options using the function
state_options = get_state_links(main_url)

# Streamlit app title
st.title("Public Libraries Information by State")

# Dropdown to select the state
selected_state = st.selectbox("Select a state to view library information:", list(state_options.keys()))

# Get the selected state's URL
state_url = state_options[selected_state]

# Scrape the data for the selected state
df = scrape_state_data(state_url)

if df is not None:
    # Display the data in Streamlit
    st.write(f"Libraries Information for {selected_state}")
    st.dataframe(df)
    
    # Provide download options using the function
    download_data(df, selected_state)
else:
    st.write(f"No libraries data available for {selected_state}.")
