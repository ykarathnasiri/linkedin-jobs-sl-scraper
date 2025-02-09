import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import logging
import time
import os
from pathlib import Path

# Configure logging
log_filename = 'linkedin_scraper.log'
try:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, 'a', 'utf-8'),
            logging.StreamHandler()
        ]
    )
except PermissionError:
    temp_log = os.path.join(os.path.expanduser('~'), 'linkedin_scraper.log')
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(temp_log, 'a', 'utf-8'),
            logging.StreamHandler()
        ]
    )

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def create_empty_job_dict():
    """Create a dictionary with all required fields initialized as None"""
    return {
        "job_id": None,
        "title": None,
        "company": None,
        "location": None,
        "experience_level": None,
        "employment_type": None,
        "posted_date": None,
        "job_function": None,
        "industries": None,
        "salary": None,
        "required_skills": None,
        "description": None,
        "company_size": None,
        "company_industry": None,
        "applicant_count": None,
        "job_url": None
    }

def initialize_csv(filename):
    """Initialize CSV file with headers"""
    columns = [
        "job_id", "title", "company", "location", "experience_level",
        "employment_type", "posted_date", "job_function", "industries",
        "salary", "required_skills", "description", "company_size",
        "company_industry", "applicant_count", "job_url"
    ]
    df = pd.DataFrame(columns=columns)
    df.to_csv(filename, index=False, encoding='utf-8', mode='w')
    return filename

def append_to_csv(job_data, filename):
    """Append a single job to the CSV file"""
    try:
        df = pd.DataFrame([job_data])
        df.to_csv(filename, mode='a', header=False, index=False, encoding='utf-8')
        return True
    except Exception as e:
        logger.error(f"Error appending to CSV: {str(e)}")
        return False

def scrape_job_listings():
    """Scrape all job listings from LinkedIn for Sri Lanka"""
    base_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?location=Sri%20Lanka&start={}"
    page = 0
    total_jobs = 0
    consecutive_empty_pages = 0
    max_empty_pages = 3  # Stop after 3 consecutive empty pages
    
    # Initialize CSV file
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = data_dir / f"linkedin_jobs_{timestamp}.csv"
    initialize_csv(csv_filename)
    
    logger.info("Starting to scrape LinkedIn jobs in Sri Lanka")
    print("Starting to scrape LinkedIn jobs in Sri Lanka...")
    
    while consecutive_empty_pages < max_empty_pages:
        try:
            url = base_url.format(page * 25)
            response = requests.get(url, headers=HEADERS)
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch page {page}. Status code: {response.status_code}")
                break
                
            soup = BeautifulSoup(response.text, 'html.parser')
            job_cards = soup.find_all("div", {"class": "base-card"})
            
            if not job_cards:
                consecutive_empty_pages += 1
                if consecutive_empty_pages >= max_empty_pages:
                    logger.info("No more jobs found. Scraping complete.")
                    print(f"\nScraping complete! Total jobs scraped: {total_jobs}")
                    break
                continue
            
            consecutive_empty_pages = 0  # Reset counter when we find jobs
            
            for card in job_cards:
                try:
                    job_data = extract_job_data(card)
                    if job_data:
                        append_to_csv(job_data, csv_filename)
                        total_jobs += 1
                        print(f"\rJobs scraped: {total_jobs}", end="", flush=True)
                        logger.info(f"Scraped job: {job_data['title']} at {job_data['company']}")
                    time.sleep(1)  # Respect rate limits
                    
                except Exception as e:
                    logger.warning(f"Failed to extract data from a job card: {str(e)}")
                    continue
            
            page += 1
            time.sleep(2)  # Respect rate limits between pages
            
        except Exception as e:
            logger.error(f"Error processing page {page}: {str(e)}")
            break
            
    return total_jobs, csv_filename

def extract_job_data(card):
    """Extract data from a job card with exact field structure"""
    try:
        # Initialize with empty structure
        job_data = create_empty_job_dict()
        
        # Get job link and ID
        job_link = card.find("a", {"class": "base-card__full-link"})
        if not job_link:
            return None
        
        job_data.update({
            "job_id": job_link.get('href').split('?')[0].split('-')[-1],
            "title": get_text(card, "h3", "base-search-card__title"),
            "company": get_text(card, "h4", "base-search-card__subtitle"),
            "location": get_text(card, "span", "job-search-card__location"),
            "posted_date": get_date(card),
            "job_url": job_link.get('href')
        })
        
        # Get detailed info
        details = get_job_details(job_data["job_id"])
        job_data.update(details)
        
        return job_data
    except Exception as e:
        logger.error(f"Error extracting job data: {str(e)}")
        return None

def get_text(element, tag, class_name):
    """Safely extract text from an element"""
    found = element.find(tag, {"class": class_name})
    return found.text.strip() if found else None

def get_date(card):
    """Safely extract date from card"""
    time_element = card.find("time")
    return time_element.get("datetime") if time_element else None

def get_job_details(job_id):
    """Get detailed job information with specific field structure"""
    url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            return {}

        soup = BeautifulSoup(response.text, 'html.parser')
        
        details = {
            "experience_level": None,
            "employment_type": None,
            "job_function": None,
            "industries": None,
            "salary": None,
            "required_skills": None,
            "description": None,
            "company_size": None,
            "company_industry": None,
            "applicant_count": None
        }
        
        # Extract description
        desc_element = soup.find("div", {"class": "show-more-less-html__markup"})
        if desc_element:
            details["description"] = desc_element.get_text(strip=True)

        # Extract job criteria
        criteria_list = soup.find("ul", {"class": "description__job-criteria-list"})
        if criteria_list:
            for item in criteria_list.find_all("li"):
                text = item.text.strip()
                if "Seniority level" in text:
                    details["experience_level"] = item.find("span", {"class": "description__job-criteria-text"}).text.strip()
                elif "Employment type" in text:
                    details["employment_type"] = item.find("span", {"class": "description__job-criteria-text"}).text.strip()
                elif "Job function" in text:
                    details["job_function"] = item.find("span", {"class": "description__job-criteria-text"}).text.strip()
                elif "Industries" in text:
                    details["industries"] = item.find("span", {"class": "description__job-criteria-text"}).text.strip()

        # Extract salary if available
        salary_element = soup.find("span", string=lambda text: text and "salary" in text.lower())
        if salary_element:
            details["salary"] = salary_element.get_text(strip=True)

        # Extract skills
        skills_section = soup.find("div", string=lambda text: text and "Skills" in text)
        if skills_section:
            skills_list = skills_section.find_next("ul")
            if skills_list:
                details["required_skills"] = ", ".join([li.text.strip() for li in skills_list.find_all("li")])

        # Extract company info
        company_info = soup.find("div", {"class": "company-details"})
        if company_info:
            size_element = company_info.find("span", string=lambda text: text and "Company size" in text)
            if size_element:
                details["company_size"] = size_element.find_next("span").text.strip()
            
            industry_element = company_info.find("span", string=lambda text: text and "Industry" in text)
            if industry_element:
                details["company_industry"] = industry_element.find_next("span").text.strip()

        # Extract applicant count
        applicants_element = soup.find("span", string=lambda text: text and "applicants" in text.lower())
        if applicants_element:
            details["applicant_count"] = applicants_element.text.strip()

        return details

    except Exception as e:
        logger.error(f"Error fetching details for job {job_id}: {str(e)}")
        return {}

def main():
    try:
        total_jobs, csv_filename = scrape_job_listings()
        print(f"\nAll available jobs in Sri Lanka have been scraped!")
        print(f"Total jobs scraped: {total_jobs}")
        print(f"Data saved to: {csv_filename}")
        
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
        print("Don't worry - all scraped data has been saved to CSV")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print("An error occurred. Check the log file for details.")

if __name__ == "__main__":
    main()