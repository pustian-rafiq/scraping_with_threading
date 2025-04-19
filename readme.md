# Book Scraper with Multithreading

This project is a Python script that scrapes book data from the website [Books to Scrape](https://books.toscrape.com/) using multithreading to improve performance. The script extracts the title, price, and availability of books and saves the data to a CSV file.

## Features

- **Multithreading**: Utilizes multiple threads to scrape pages concurrently, improving performance.
- **Thread-Safe Operations**: Ensures safe access to shared resources like the CSV file.
- **Customizable**: Easily configurable for the number of threads and total pages to scrape.
- **Error Handling**: Handles HTTP errors and exceptions gracefully.

## Project Structure

- **`scraper.py`**: The main script that performs the scraping.
- **`output.csv`**: The file where the scraped data is saved.
- **`requirements.txt`**: Lists the required Python libraries.

## How It Works

1. **Initialization**:
   - The script initializes a thread-safe queue with page numbers to scrape.
   - A CSV file is created with headers: `Title`, `Price`, and `Availability`.

2. **Scraping**:
   - Each thread fetches a page from the queue, scrapes the book data, and writes it to the CSV file.
   - The scraping process uses the `requests` library to fetch HTML content and `BeautifulSoup` to parse it.

3. **Multithreading**:
   - Multiple threads are started to process pages concurrently.
   - A thread-safe lock ensures that only one thread writes to the CSV file at a time.

4. **Completion**:
   - The script waits for all threads to finish before exiting.
   - The scraped data is saved to `output.csv`.

## Code Overview

### Constants

- `BASE_URL`: The base URL of the website with a placeholder for page numbers.
- `TOTAL_PAGES`: The total number of pages to scrape (default: 50).
- `OUTPUT_FILE`: The name of the output CSV file (default: `output.csv`).

### Functions

- **`scrape_page(page_num)`**:
  - Fetches and parses a single page.
  - Extracts book data (title, price, availability).
  - Writes the data to the CSV file in a thread-safe manner.

- **`process_pages()`**:
  - Worker function for threads.
  - Processes pages from the queue until the queue is empty.

- **`main()`**:
  - Initializes the CSV file with headers.
  - Starts multiple threads to scrape pages.
  - Waits for all threads to complete.

## Usage

### Prerequisites

- Python 3.6 or higher
- Install the required libraries using:

  ```bash
  pip install -r requirements.txt

- Run this script
  ```bash
  python scraper.py