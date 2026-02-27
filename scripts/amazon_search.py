#!/usr/bin/env python3
"""Search Amazon using headless Chromium."""
import sys, json, subprocess

# Use system chromium
CHROMIUM_PATH = "/usr/bin/chromium"

def search(query):
    from playwright.sync_api import sync_playwright
    
    url = f"https://www.amazon.com/s?k={query.replace(' ', '+')}"
    results = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=CHROMIUM_PATH,
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"]
        )
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page.goto(url, timeout=15000, wait_until="domcontentloaded")
        page.wait_for_timeout(3000)
        
        # Get search results
        items = page.query_selector_all("[data-component-type='s-search-result']")
        
        for item in items[:8]:
            try:
                title_el = item.query_selector("h2 a span")
                link_el = item.query_selector("h2 a")
                price_el = item.query_selector(".a-price .a-offscreen")
                rating_el = item.query_selector(".a-icon-alt")
                reviews_el = item.query_selector("[aria-label*='stars'] + span .a-size-base")
                
                title = title_el.text_content().strip() if title_el else None
                if not title:
                    continue
                    
                href = link_el.get_attribute("href") if link_el else None
                link = f"https://www.amazon.com{href}" if href and href.startswith("/") else href
                price = price_el.text_content().strip() if price_el else "N/A"
                rating = rating_el.text_content().strip() if rating_el else "N/A"
                reviews = reviews_el.text_content().strip() if reviews_el else "N/A"
                
                results.append({
                    "title": title[:120],
                    "price": price,
                    "rating": rating,
                    "reviews": reviews,
                    "link": link
                })
            except:
                continue
        
        browser.close()
    
    return results

if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "tiny gold huggie hoop earrings"
    results = search(query)
    print(json.dumps(results, indent=2))
