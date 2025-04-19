import requests
from bs4 import BeautifulSoup
import csv
import threading
import time
from queue import Queue

BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"
TOTAL_PAGES = 50
OUTPUT_FILE = "output.csv"

#Thread-safe queue for page numbers
page_queue = Queue()
for i in range(1, TOTAL_PAGES + 1):
    page_queue.put(i)

# Locak for writing to the CSV file
csv_lock = threading.Lock()

# Function to scrape a single page
def scrape_page(page_num):
    url = BASE_URL.format(page_num)

    try:
        print(f"[Thread-{threading.current_thread().name}] Fetching page {page_num}...")
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an error for bad responses
        soup = BeautifulSoup(response.text, 'html.parser')

        books = soup.select('article.product_pod')
        scraped_data = []

        for book in books:
            title = book.h3.a['title']
            price = book.select_one('.price_color').text
            availability = book.select_one('.availability').text.strip()
            scraped_data.append([title, price, availability])
            print(f"[Thread-{threading.current_thread().name}] Scraped: {title}, {price}, {availability}")
     
        # Write to CSV file in a thread-safe manner
        with csv_lock:
            with open(OUTPUT_FILE, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerows(scraped_data)
        
        print(f"[Thread-{threading.current_thread().name}] Done page {page_num}")
        
    except Exception as e:
        print(f"Error on page {page_num}: {e}")

# Function to process pages from the queue - Worker thread
def process_pages():
    while not page_queue.empty():
        page_num = page_queue.get()
        scrape_page(page_num)
        page_queue.task_done()


# Main function to start threads
def main():
    # Write CSV header
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Title', 'Price', 'Availability'])

    threads = []
    num_threads = 5  # Number of threads to use

    for _ in range(num_threads):
        thread = threading.Thread(target=process_pages)
        thread.start()
        threads.append(thread)
    

    # Wait for all threads to finish
    for thread in threads:
        thread.join()
    print("All pages have been scraped.")
    print(f"Data saved to {OUTPUT_FILE}")
if __name__ == "__main__":
    main()
    # Optional: Add a delay between requests to avoid overwhelming the server
    # time.sleep(1)
    # Optional: Implement a retry mechanism for failed requests
    # Optional: Implement a logging mechanism for better error handling
    # Optional: Add a delay between requests to avoid overwhelming the server
    # Optional: Implement a retry mechanism for failed requests
    # Optional: Implement a logging mechanism for better error handling
    # Optional: Use a configuration file for settings