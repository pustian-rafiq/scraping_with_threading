import requests
from bs4 import BeautifulSoup
import csv
import threading
import time
from queue import Queue
import ipdb
import os


BASE_URL = "https://books.toscrape.com/"
# BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"
TOTAL_PAGES = 50
OUTPUT_FILE = "output.csv"

#Thread-safe queue for page numbers
page_queue = Queue()
page_queue_categories = Queue()

for i in range(1, TOTAL_PAGES + 1):
    page_queue.put(i)

# Lock for writing to the CSV file
csv_lock = threading.Lock()
csv_lock_for_category = threading.Lock()

# Function to scrape a single page
def scrape_page(page_num):
    url = BASE_URL + "catalogue/page-" + str(page_num) + ".html"

    try:
        print(f"[Thread-{threading.current_thread().name}] Fetching page {page_num}...")
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an error for bad responses
        soup = BeautifulSoup(response.text, 'html.parser')

        books = soup.select('article.product_pod')
        scraped_data = []
        # ipdb.set_trace()
        for book in books:
            title = book.h3.a['title']
            price = book.select_one('.price_color').text
            availability = book.select_one('.availability').text.strip()
            scraped_data.append([title, price, availability])
            # ipdb.set_trace()

            # print(f"[Thread-{threading.current_thread().name}] Scraped: {title}, {price}, {availability}")
     
        # Write to CSV file in a thread-safe manner
        with csv_lock:
            with open(OUTPUT_FILE, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerows(scraped_data)
        
        print(f"[Thread-{threading.current_thread().name}] Done page {page_num}")
        
    except Exception as e:
        print(f"Error on page {page_num}: {e}")


def scrape_books_by_category(category_url, CSV_FILE_PATH):

    url = BASE_URL + category_url
    # CSV_FILE_NAME = os.path.join('categories', category_name.tolower() + ".csv")
    try:
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
            print(f"Scraped: {title}, {price}, {availability}")
        # Write to CSV file in a thread-safe manner
        with csv_lock_for_category:
            with open(CSV_FILE_PATH, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerows(scraped_data)
    except Exception as e:
        print(f"Error fetching category {category_url}: {e}")


# Function to scrape all categories links
def scrape_all_categories_links():
    url = BASE_URL + "index.html"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an error for bad responses
        soup = BeautifulSoup(response.text, 'html.parser')
        categories = soup.select('ul.nav-list li ul li a')
        category_links = []
        for category in categories:
            category_name = category.text.strip()
            category_url = category['href']
            category_links.append((category_name, category_url))
            # print(f"Category: {category_name}, URL: {category_url}")
        return category_links
    except Exception as e:
        print(f"Error fetching categories: {e}")
        return []

# Function to process pages from the queue - Worker thread
def process_pages():
    while not page_queue.empty():
        page_num = page_queue.get()
        scrape_page(page_num)
        page_queue.task_done()

# Function to process categories from the queue - Worker thread
def process_categories(categories):
    while not page_queue_categories.empty():   
        for category in categories:
            category_name, category_url = category
            category_name = category_name.replace(" ", "_")
            
            CSV_FILE_PATH = os.path.join('categories', category_name.lower() + ".csv")
            write_csv_header(CSV_FILE_PATH)
            scrape_books_by_category(category_url, CSV_FILE_PATH)
        page_queue.task_done()

def write_csv_header(file_name):
    with open(file_name, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Title', 'Price', 'Availability'])

# Main function to start threads
def main():

    # Optional: Scrape all categories links
    categories = scrape_all_categories_links()
    if categories:
        for i in range(1, len(categories) + 1):
            page_queue_categories.put(i)
        print("Categories scraped successfully.")
        # print("Categories:")
        # for name, url in categories:
        #     print(f"{name}: {url}")
    else:
        print("Failed to scrape categories.")
    
    # Write CSV header
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Title', 'Price', 'Availability'])

    threads_all_books = []
    threads_category_books = []
    num_threads = 5  # Number of threads to use

    for _ in range(num_threads):
        thread_for_all_books = threading.Thread(target=process_pages)
        thread_for_category_wise_book = threading.Thread(target=process_categories, args=(categories,))


        thread_for_all_books.start()
        thread_for_category_wise_book.start()
        threads_all_books.append(thread_for_all_books)
        threads_category_books.append(thread_for_category_wise_book)

        # Start threads for scraping pages
        # thread.start()
        # threads.append(thread)
    

    # Wait for all threads to finish
    for thread in threads_all_books:
        thread.join()

    for thread in threads_category_books:
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