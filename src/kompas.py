import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
import re

def scrape_kompas(query="purbaya"):

    base_url = "https://search.kompas.com/search"
    results = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    page = 1

    while True:
        print(f"Scraping Kompas page {page}...")

        # Build URL with query, and pagination
        url = (
            f"{base_url}?q={query.replace(' ', '+')}"
            f"&site_id=all"
            f"&page={page}"
        )

        try:
            r = requests.get(url, headers=headers, timeout=10)
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page {page}: {e}")
            break

        soup = BeautifulSoup(r.text, "html.parser")

        # Check if "no results" message appears
        no_results = soup.find("div", class_="search-result-empty")
        if no_results:
            print(f"No more articles found after page {page - 1}. Ending scrape.")
            break

        # Find all article links
        article_links = soup.find_all("a", class_="article-link")

        if not article_links:
            print(f"No articles found on page {page}. Ending scrape.")
            break

        # Extract data from each article
        for link_tag in article_links:
            article_url = link_tag.get("href")
            if not article_url or "kompas.com" not in article_url:
                continue

            wrap_div = link_tag.find("div", class_="articleItem-wrap")
            if not wrap_div:
                continue

            # Extract title
            title_tag = wrap_div.find("h2", class_="articleTitle")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)

            # Extract date
            date_tag = wrap_div.find("div", class_="articlePost-date")
            date_text = date_tag.get_text(strip=True) if date_tag else "Date not available"

            # Extract year using regex
            year_match = re.search(r'\b(20\d{2})\b', date_text)
            year = year_match.group(1) if year_match else None

            # Extract description in <p> tag if available
            desc = wrap_div.find("p")
            desc = desc.get_text(strip=True) if desc else "Description not available"

            results.append({
                "media": "kompas",
                "title": title,
                "description": desc,
                "url": article_url,
                "date": date_text,
                "year": year
            })

        print(f"Page {page}: found {len(article_links)} articles.")

        # Be respectful — wait between requests
        time.sleep(1)

        page += 1

    return pd.DataFrame(results)

# Add validation
def validate_scraped_data(df):
    if df.empty:
        print("No data scraped")
        return df
        
    print(f"Total articles scraped: {len(df)}")
    print(f"Articles by year:")
    print(df['year'].value_counts().sort_index())
    
    # Remove duplicates
    initial_count = len(df)
    df = df.drop_duplicates(subset=['url'])
    print(f"Removed {initial_count - len(df)} duplicate articles")
    
    return df

if __name__ == "__main__":
    # Scrape with specified query
    df = scrape_kompas(
        query="purbaya",
    )

    df = validate_scraped_data(df)

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, "data", "kompas.csv")

    os.makedirs(os.path.dirname(data_path), exist_ok=True)

    if not df.empty:
        df.to_csv(data_path, index=False, encoding="utf-8-sig")
        print(f"Successfully saved {len(df)} articles to: {data_path}")
    else:
        print("No articles found. Try changing the query or check Kompas HTML structure.")