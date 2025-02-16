from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time

url = "https://www.behance.net/joblist?tracking_source=nav20"

def get_jobs(limit, url):
    driver = webdriver.Chrome()
    driver.get(url)
    roles, companies, locations, descriptions, links = [], [], [], [], []
    job_details = {"Job Role": [], "Company": [], "Location": [], "Description": [], "Job Link": []}
    jobs = []
    curr = 0
    prev = 0
    scrolls = 0
    
    while len(jobs) < limit and scrolls <= 3:
        jobs = driver.find_elements(By.CSS_SELECTOR, "div.JobCard-jobCard-mzZ")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        prev = curr
        curr = len(jobs)
        if prev == curr:
            scrolls += 1
    
    if jobs:
        for job in jobs:
            role = job.find_element(By.CSS_SELECTOR, "h3.JobCard-jobTitle-LS4").text
            company = job.find_element(By.CSS_SELECTOR, "p.JobCard-company-GQS").text
            location = job.find_element(By.CSS_SELECTOR, "p.JobCard-jobLocation-sjd").text
            link = job.find_element(By.CSS_SELECTOR, "a.JobCard-jobCardLink-Ywm").get_attribute("href")  
            description = job.find_element(By.CSS_SELECTOR, "p.JobCard-jobDescription-SYp").text
            
            roles.append(role) if role else roles.append("Not Mentioned")
            companies.append(company) if company else companies.append("Not Mentioned")
            locations.append(location) if location else locations.append("Not Mentioned")
            descriptions.append(description) if description else descriptions.append("Not Mentioned")
            links.append(link) if link else links.append("Not Mentioned")
        
        job_details["Job Role"].extend(roles[0:limit])
        job_details["Company"].extend(companies[0:limit])
        job_details['Location'].extend(locations[0:limit])
        job_details["Description"].extend(descriptions[0:limit])
        job_details["Job Link"].extend(links[0:limit])
    
    driver.quit()
    return job_details

# Main execution
dataframe = pd.DataFrame(get_jobs(100, url))
dataframe.to_csv("behance_jobs.csv", index=False)  # Saves data to "behance_jobs.csv" in the current directory

print("Data saved to behance_jobs.csv")
