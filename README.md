# LinkedIn Job Scraper

## Overview
This LinkedIn Job Scraper is a Python-based tool that scrapes job listings from LinkedIn using web scraping techniques. It collects job details, including the title, company, location, experience level, employment type, posted date, job function, industries, salary, required skills, description, company size, company industry, applicant count, job URL, sort method, and time filter.

## Features
- **Scrapes job listings from LinkedIn**
- **Extracts detailed job information, including company details and job descriptions**
- **Saves data to a CSV file with structured columns**
- **Logs errors and warnings for debugging purposes**
- **User-friendly console interface for job keyword input and number of jobs to scrape**

## Prerequisites
Ensure you have Python installed (version 3.7 or later). You can check your Python version with:
```sh
python --version
```

## Installation
1. **Clone the repository**
```sh
git clone https://github.com/ykarathnasiri/linkedin-jobs-sl-scraper.git
cd linkedin-jobs-sl-scraper
```
2. **Install dependencies**
```sh
pip install -r requirements.txt
```

## Usage
Run the script with:
```sh
python linkedin_scraper.py
```

### How It Works:
1. The script prompts the user to enter job keywords (e.g., "Software Engineer").
2. The user can specify the number of jobs to scrape.
3. The scraper fetches job listings from LinkedIn.
4. The extracted data is stored in a CSV file inside the `data/` directory.
5. A log file (`linkedin_scraper.log`) records errors and actions for debugging.

## File Structure
```
linkedin-job-scraper/
├── linkedin_scraper.py        # Main script
├── requirements.txt           # Dependencies
├── README.md                  # Documentation
├── data/                      # Output CSV files
└── linkedin_scraper.log        # Log file
```

## Output
The scraper generates a CSV file with the following columns:
- `job_id`
- `title`
- `company`
- `location`
- `experience_level`
- `employment_type`
- `posted_date`
- `job_function`
- `industries`
- `salary`
- `required_skills`
- `description`
- `company_size`
- `company_industry`
- `applicant_count`
- `job_url`

## Example Output
| job_id | title | company | location | experience_level | employment_type | posted_date | job_function | industries | salary | required_skills | description | company_size | company_industry | applicant_count | job_url |
|--------|-------|---------|----------|------------------|-----------------|-------------|--------------|------------|--------|-----------------|-------------|--------------|------------------|-----------------|---------|
| 12345  | Data Scientist | ABC Corp | Colombo, Sri Lanka | Mid-Level | Full-Time | 2024-02-17 | Analytics | Tech | $5000/month | Python, SQL, ML | AI development role | 500-1000 | IT & Services | 45 | [Job URL] |

## Error Handling
- The script logs errors if a webpage fails to load or data cannot be extracted.
- If an error occurs while saving, the script attempts to save the CSV file in the user's home directory as a backup.

## Limitations
- LinkedIn may block frequent scraping requests.
- Some job details may not be fully extracted due to website structure changes.

## Contributing
Feel free to contribute by submitting issues or pull requests.

## License
This project is licensed under the MIT License.
