# linkedin-jobs-sl-scraper
# LinkedIn Job Scraper - Sri Lanka

A Python-based web scraper that automatically collects all job listings from LinkedIn in Sri Lanka. The scraper captures detailed job information including job title, company, location, experience level, job description, and more.

## Features

- Scrapes all available LinkedIn jobs in Sri Lanka
- Captures detailed job information including descriptions and requirements
- Real-time progress tracking
- Continuous CSV data saving (no data loss on interruption)
- Comprehensive error handling and logging
- Automatic rate limiting to respect LinkedIn's servers
- Detects when all jobs have been scraped

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/linkedin-jobs-sl-scraper.git
cd linkedin-jobs-sl-scraper
```

2. Create and activate a virtual environment:

On Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

On macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Project Structure

```
linkedin-jobs-sl-scraper/
│
├── data/                  # Directory for scraped data
├── src/                   # Source code
│   └── scraper.py        # Main scraper script
│
├── venv/                  # Virtual environment (auto-generated)
├── .gitignore
├── README.md
├── requirements.txt
└── linkedin_scraper.log  # Log file (auto-generated)
```

## Usage

1. Make sure your virtual environment is activated
2. Run the scraper:
```bash
python src/scraper.py
```

The script will:
- Start scraping all LinkedIn jobs in Sri Lanka
- Show real-time progress
- Save data continuously to a CSV file in the `data` directory
- Create a log file with detailed operation information
- Stop automatically when all available jobs are scraped

## Output

The scraper creates two main outputs:

1. CSV file (in `data` directory) with columns:
   - job_id
   - title
   - company
   - location
   - experience_level
   - employment_type
   - posted_date
   - job_function
   - industries
   - salary
   - required_skills
   - description
   - company_size
   - company_industry
   - applicant_count
   - job_url

2. Log file (`linkedin_scraper.log`) with detailed operation logs

## Error Handling

- The scraper includes comprehensive error handling
- All errors are logged to `linkedin_scraper.log`
- If the main data directory is not accessible, it will save to the user's home directory
- Data is saved continuously, so interruptions won't lose scraped data

## Rate Limiting

The scraper includes built-in delays to respect LinkedIn's servers:
- 1 second delay between individual job scrapes
- 2 seconds delay between pages
- Automatic detection of failed requests

## Contributing

Feel free to open issues or submit pull requests with improvements.

## License

MIT License - feel free to use this code for any purpose.

## Disclaimer

This scraper is for educational purposes only. Make sure to comply with LinkedIn's terms of service and robots.txt when using this tool.
