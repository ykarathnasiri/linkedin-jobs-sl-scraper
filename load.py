import requests
from bs4 import BeautifulSoup
import math
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

def scrape_job_listings(keywords, location="Sri Lanka", total_jobs=100):
    """Scrape job listings from LinkedIn"""
    jobs_data = []
    base_url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={keywords}&location={location}&start={{}}"
    number_of_pages = math.ceil(total_jobs / 25)

    for page in range(number_of_pages):
        try:
            url = base_url.format(page * 25)
            response = requests.get(url, headers=HEADERS)
            if response.status_code != 200:
                logger.error(f"Failed to fetch page {page}. Status code: {response.status_code}")
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            job_cards = soup.find_all("div", {"class": "base-card"})

            for card in job_cards:
                try:
                    job_data = extract_job_data(card)
                    if job_data:
                        jobs_data.append(job_data)
                        logger.info(f"Scraped job: {job_data['title']} at {job_data['company']}")
                    time.sleep(1)

                except Exception as e:
                    logger.warning(f"Failed to extract data from a job card: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"Error processing page {page}: {str(e)}")
            continue

    return jobs_data

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
        
        # Initialize empty details
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

def save_to_csv(jobs_data, base_filename="linkedin_jobs_sri_lanka.csv"):
    """Save data to CSV with specific column order"""
    if not jobs_data:
        logger.error("No data to save")
        return False

    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = data_dir / f"linkedin_jobs_{timestamp}.csv"
    
    try:
        df = pd.DataFrame(jobs_data)
        # Ensure specific column order
        columns = [
            "job_id", "title", "company", "location", "experience_level",
            "employment_type", "posted_date", "job_function", "industries",
            "salary", "required_skills", "description", "company_size",
            "company_industry", "applicant_count", "job_url"
        ]
        df = df.reindex(columns=columns)
        df.to_csv(filename, index=False, encoding='utf-8')
        logger.info(f"Data successfully saved to {filename}")
        return True
    except Exception as e:
        logger.error(f"Error saving data: {str(e)}")
        # Try saving to home directory as backup
        try:
            home_dir = Path.home()
            backup_filename = home_dir / f"linkedin_jobs_{timestamp}.csv"
            df.to_csv(backup_filename, index=False, encoding='utf-8')
            logger.info(f"Data saved to alternative location: {backup_filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to save data to alternative location: {str(e)}")
            return False

def main():
    try:
        # Get user inputs with validation
        while True:
            keywords = input("Enter job keywords (e.g., 'Software Engineer'): ").strip()
            if keywords or input("No keywords entered. Search all jobs? (y/n): ").lower() == 'y':
                break
            
        while True:
            try:
                total_jobs = input("Enter number of jobs to scrape (default 100): ").strip()
                total_jobs = int(total_jobs) if total_jobs else 100
                if total_jobs > 0:
                    break
                print("Please enter a positive number")
            except ValueError:
                print("Please enter a valid number")

        logger.info(f"Starting to scrape {total_jobs} LinkedIn jobs in Sri Lanka for keyword: {keywords}")
        
        # Scrape jobs
        jobs_data = scrape_job_listings(keywords, total_jobs=total_jobs)
        
        # Save data
        if jobs_data:
            if save_to_csv(jobs_data):
                print(f"Successfully scraped {len(jobs_data)} jobs")
            else:
                print("Failed to save data. Check the log file for details.")
        else:
            print("No jobs were scraped. Check the log file for details.")

    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
        if 'jobs_data' in locals() and jobs_data:
            save_to_csv(jobs_data)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print("An error occurred. Check the log file for details.")

if __name__ == "__main__":
    main()