#!/usr/bin/env python3
"""
Steely's Smart Web Scraper
Multiple strategies to extract product information from shopping sites
"""

import requests
import json
import sys
import time
import random
from urllib.parse import urlparse
from typing import Dict, Optional

class ProductScraper:
    def __init__(self):
        self.session = requests.Session()
        
        # Realistic user agents to bypass basic bot detection
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]
        
        # Common headers to appear more human
        self.base_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
    
    def get_headers(self, url: str) -> Dict[str, str]:
        """Generate appropriate headers for the target site"""
        headers = self.base_headers.copy()
        headers['User-Agent'] = random.choice(self.user_agents)
        
        # Site-specific adjustments
        domain = urlparse(url).netloc.lower()
        
        if 'newbalance.com' in domain:
            headers['Referer'] = 'https://www.newbalance.com/'
            headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            
        elif 'nike.com' in domain:
            headers['Referer'] = 'https://www.nike.com/'
            
        elif 'amazon.com' in domain:
            headers['Referer'] = 'https://www.amazon.com/'
            
        return headers
    
    def attempt_scrape(self, url: str) -> Dict:
        """Try multiple scraping strategies"""
        result = {
            'url': url,
            'success': False,
            'method_used': None,
            'status_code': None,
            'content': None,
            'error': None,
            'extracted_data': {}
        }
        
        strategies = [
            self._basic_request,
            self._delayed_request,
            self._mobile_request
        ]
        
        for i, strategy in enumerate(strategies, 1):
            try:
                print(f"Trying strategy {i}: {strategy.__name__}")
                response = strategy(url)
                
                result['success'] = True
                result['method_used'] = strategy.__name__
                result['status_code'] = response.status_code
                result['content'] = response.text[:2000]  # First 2KB for analysis
                
                # Try to extract structured data
                result['extracted_data'] = self._extract_product_data(response.text, url)
                
                print(f"✅ Success with {strategy.__name__}")
                return result
                
            except Exception as e:
                print(f"❌ {strategy.__name__} failed: {str(e)}")
                result['error'] = str(e)
                continue
        
        result['success'] = False
        return result
    
    def _basic_request(self, url: str) -> requests.Response:
        """Standard request with good headers"""
        headers = self.get_headers(url)
        response = self.session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response
    
    def _delayed_request(self, url: str) -> requests.Response:
        """Request with random delay to appear human"""
        time.sleep(random.uniform(1, 3))
        headers = self.get_headers(url)
        response = self.session.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response
    
    def _mobile_request(self, url: str) -> requests.Response:
        """Try mobile user agent"""
        headers = self.get_headers(url)
        headers['User-Agent'] = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1'
        response = self.session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response
    
    def _extract_product_data(self, html: str, url: str) -> Dict:
        """Extract product information from HTML"""
        data = {
            'title': None,
            'price': None,
            'description': None,
            'availability': None,
            'images': [],
            'specifications': {}
        }
        
        # Basic extraction patterns (would be much more sophisticated)
        import re
        
        # Try to find price patterns
        price_patterns = [
            r'\$[\d,]+\.?\d*',
            r'price["\']?\s*:\s*["\']?\$?[\d,]+\.?\d*',
            r'amount["\']?\s*:\s*["\']?\$?[\d,]+\.?\d*'
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            if matches:
                data['price'] = matches[0]
                break
        
        # Try to find title in common places
        title_patterns = [
            r'<title[^>]*>([^<]+)</title>',
            r'<h1[^>]*>([^<]+)</h1>',
            r'"name"[:\s]*"([^"]+)"'
        ]
        
        for pattern in title_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            if matches:
                data['title'] = matches[0].strip()
                break
        
        return data

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 smart_scraper.py <url>")
        sys.exit(1)
    
    url = sys.argv[1]
    scraper = ProductScraper()
    result = scraper.attempt_scrape(url)
    
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()