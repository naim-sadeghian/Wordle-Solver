import requests
import csv
from bs4 import BeautifulSoup


# File to store results
OUTPUT_FILE = "word_list_common.csv"

def scrape_page(url: str) -> list[str]:
    """
    Scrapes a single page and returns a list of words from <li> elements inside <ul>.
    """
    response = requests.get(url)
    
    # Handle request failure
    if response.status_code != 200:
        print(f"Failed to retrieve {url}, status code: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    # print(soup)
    # Find the <ul> containing the words
    ul_element = soup.find("ul", class_="paginated-list-results")
    # print(ul_element)
    if not ul_element:
        print(f"No word list found on {url}. Pagination may have ended.")
        return None  # Stop pagination

    # Extract text from all <li> elements
    words = [li.text.strip() for li in ul_element.find_all("li") if li.text.strip()]
    
    return words

def scrape_all_pages():
    """
    For each letter in alphabet: Loops through paginated pages until no data is found.
    Write all words to a CSV file.
    """
    page = 1
    all_words = []
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']


    for letter in letters:
        page = 1
        while True:
            url = f"https://www.merriam-webster.com/wordfinder/fill-in-blanks/common/5/{letter}____/{page}"
            # url = f"https://www.merriam-webster.com/wordfinder/fill-in-blanks/all/5/{letter}____/{page}" # Uncomment for all words
            # print(url)

            words = scrape_page(url)

            # Stop if no more words are found (pagination limit)
            if words is None or not words:
                break

            all_words.extend(words)
            page += 1  # Move to the next page

        # Save words to CSV
        with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            # writer.writerow(["Words"])  # Header
            for word in all_words:
                writer.writerow([word])
        
# Run scraper
scrape_all_pages()
