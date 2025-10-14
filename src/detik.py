import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
import re

def scrape_detik(query="purbaya", start_date="01/09/2025", end_date="10/10/2025"):

    base_url = "https://www.detik.com/search/searchall"
    results = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    page = 1

    while True:
        print(f"Scraping Detik page {page}...")

        # Build URL with query, date range, and pagination
        url = (
            f"{base_url}?query={query.replace(' ', '%20')}"
            f"&result_type=relevansi"
            f"&fromdatex={start_date}"
            f"&todatex={end_date}"
            f"&site=all"
            f"&sorttime=0"
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
        no_results = soup.find("div", class_="search-not-found")
        if no_results:
            print(f"No more articles found after page {page - 1}. Ending scrape.")
            break

        # Find all article containers
        articles = soup.find_all("article", class_="list-content__item")

        if not articles:
            print(f"No articles found on page {page}. Ending scrape.")
            break

        articles_found = 0
        # Extract data from each article
        for article in articles:
            # Skip video and photo articles (they have different media classes)
            media_div = article.find("div", class_="media")
            if not media_div:
                continue
                
            # Skip if it's video (has icon-play-bg) or photo (has icon-camera-bg)
            media_icon = media_div.find("i", class_=re.compile(r"icon-play-bg|icon-camera-bg"))
            if media_icon:
                continue

            # Find the link element
            link_tag = article.find("a", href=True)
            if not link_tag:
                continue
                
            article_url = link_tag.get("href")
            if not article_url or "detik.com" not in article_url:
                continue

            # Extract title
            title_tag = article.find("h3", class_="media__title")
            if not title_tag:
                continue
            title_link = title_tag.find("a")
            if not title_link:
                continue
            title = title_link.get_text(strip=True)

            # Extract date
            date_tag = article.find("span", attrs={"d-time": True})
            date_text = date_tag.get_text(strip=True) if date_tag else "Date not available"

            # Extract year using regex
            year_match = re.search(r'\b(20\d{2})\b', date_text)
            year = year_match.group(1) if year_match else None

            # Get description if available
            desc_tag = article.find("div", class_="media__desc")
            desc = desc_tag.get_text(strip=True) if desc_tag else "Description not available"

            results.append({
                "media": "detik",
                "title": title,
                "description": desc,
                "url": article_url,
                "date": date_text,
                "year": year
            })
            articles_found += 1

        print(f"Page {page}: found {articles_found} articles.")

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
    df = scrape_detik(
        query="purbaya",
        start_date="01/09/2025",
        end_date="10/10/2025"
    )

    df = validate_scraped_data(df)

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, "data", "detik.csv")

    os.makedirs(os.path.dirname(data_path), exist_ok=True)

    if not df.empty:
        df.to_csv(data_path, index=False, encoding="utf-8-sig")
        print(f"Successfully saved {len(df)} articles to: {data_path}")
    else:
        print("No articles found. Try changing the query or check Detik HTML structure.")