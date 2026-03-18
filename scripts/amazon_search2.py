#!/usr/bin/env python3
"""Search Amazon using headless Chromium — debug version."""
import sys, json

CHROMIUM_PATH = "/usr/bin/chromium"

def search(query):
    from playwright.sync_api import sync_playwright
    
    url = f"https://www.amazon.com/s?k={query.replace(' ', '+')}"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=CHROMIUM_PATH,
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"]
        )
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page.goto(url, timeout=[REDACTED_CLIENT_ID], wait_until="domcontentloaded")
        page.wait_for_timeout(5000)
        
        # Debug: get page title and some content
        title = page.title()
        content = page.content()[:2000]
        
        # Try different selectors
        results = []
        
        # Method 1
        items = page.query_selector_all("[data-component-type='s-search-result']")
        print(f"Method 1 (s-search-result): {len(items)} items", file=sys.stderr)
        
        # Method 2
        items2 = page.query_selector_all(".s-result-item")
        print(f"Method 2 (s-result-item): {len(items2)} items", file=sys.stderr)
        
        # Method 3: just get all links with prices
        items3 = page.query_selector_all(".a-price")
        print(f"Method 3 (a-price): {len(items3)} items", file=sys.stderr)
        
        print(f"Page title: {title}", file=sys.stderr)
        
        # If we got items, parse them
        for item in (items or items2)[:8]:
            try:
                text = item.text_content()[:300]
                results.append(text)
            except:
                pass
        
        browser.close()
        return results

if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "tiny gold huggie hoop earrings"
    results = search(query)
    for i, r in enumerate(results):
        print(f"\n--- Result {i+1} ---")
        print(r)
