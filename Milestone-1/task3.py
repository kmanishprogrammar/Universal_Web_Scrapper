import csv
from playwright.sync_api import sync_playwright
import time

# Define the URL template
url_template = "https://directory.wigan.gov.uk/kb5/wigan/fsd/results.page?healthchannel=6&sr={}"

# Define the function to scrape data
def scrape_data(page, csv_writer):
    results = page.query_selector_all("[id^=hit-]")  # All IDs that start with "hit-"
    print(f"Found {len(results)} results on this page.")

    for result in results:
        try:
            # Extract title
            title_selector = "div.result_hit_header h3 a"
            title_element = result.query_selector(title_selector)
            title = title_element.inner_text().strip() if title_element else "N/A"

            # Extract schedule (timing)
            schedule_selector = "div.result_hit_header .clearfix.mt-1.mb-3.font-weight-bold"
            schedule_element = result.query_selector(schedule_selector)
            schedule = schedule_element.inner_text().strip() if schedule_element else "N/A"

            # Extract address
            address_selector = "div.result-hit-body > div.d-flex.w-100 > div > div"
            address_element = result.query_selector(address_selector)
            address = address_element.inner_text().strip() if address_element else "N/A"

            # Extract phone
            phone_selector = "div.contact-links ul li:nth-child(1) span.comma_split_line.d-none.d-sm-block.text-body"
            phone_element = result.query_selector(phone_selector)
            phone = phone_element.inner_text().strip() if phone_element else "N/A"

            # Extract email
            email_selector = "div.contact-links ul li:nth-child(2) a"
            email_element = result.query_selector(email_selector)
            email = email_element.get_attribute("href").replace("mailto:", "").strip() if email_element else "N/A"

            # Extract website
            website_selector = "div.contact-links ul li:nth-child(3) a"
            website_element = result.query_selector(website_selector)
            website = website_element.get_attribute("href").strip() if website_element else "N/A"

            # Extract description (event details)
            description_selector = "div.result-hit-body > div.mb-2"
            description_element = result.query_selector(description_selector)
            description = description_element.inner_text().strip() if description_element else "N/A"

            # Write the extracted data to the CSV file
            csv_writer.writerow([title, schedule, address, phone, email, website, description])

        except Exception as e:
            print(f"Error extracting data: {e}")

# Main function
def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Launch browser in headless mode
        page = browser.new_page()

        # Open the CSV file for writing
        with open('scraped_data.csv', mode='w', newline='', encoding='utf-8') as file:
            csv_writer = csv.writer(file)
            # Write the CSV headers
            csv_writer.writerow(["Title", "Schedule", "Address", "Phone", "Email", "Website", "Description"])

            # Loop through all pages (assuming 10 results per page)
            for i in range(0, 287, 10):
                url = url_template.format(i)
                print(f"Scraping URL: {url}")
                page.goto(url)

                try:
                    # Wait for at least one result to be visible on the page
                    page.wait_for_selector("[id^=hit-]", timeout=60000)  # Increased timeout for slow loading pages
                    time.sleep(3)  # Optional: extra time for page content to load fully
                except Exception as e:
                    print(f"Error waiting for selector: {e}")
                    print("Page content:")
                    print(page.content())  # Debug: print the page content for inspection
                    continue

                # Call the scrape_data function
                scrape_data(page, csv_writer)

        browser.close()

if __name__ == "__main__":
    main()
