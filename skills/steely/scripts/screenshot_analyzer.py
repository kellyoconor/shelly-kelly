#!/usr/bin/env python3
"""
Steely's Screenshot Analysis Tool
Analyze product pages from screenshots when scraping fails
"""

import json
import sys
import os
import base64
from typing import Dict

def analyze_screenshot(image_path: str, product_url: str = None) -> Dict:
    """
    Analyze a product page screenshot to extract shopping information
    """
    
    if not os.path.exists(image_path):
        return {
            'success': False,
            'error': f'Image file not found: {image_path}',
            'analysis': None
        }
    
    # Read and encode the image
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    # Prepare the analysis prompt
    analysis_prompt = f"""
    Analyze this product page screenshot for shopping intelligence.

    Extract ALL visible information including:

    **Product Details:**
    - Product name/title
    - Price (exact amount)
    - Brand
    - Model/SKU
    - Size/color options
    - Availability/stock status
    
    **Product Features:**
    - Key selling points listed
    - Technical specifications
    - Materials mentioned
    - Use case descriptions
    
    **Shopping Context:**
    - Return policy details
    - Shipping information
    - Reviews/ratings if visible
    - Sale/discount information
    - Comparison with other products
    
    **Visual Assessment:**
    - Product images quality
    - Marketing language tone
    - Target audience indicators
    - Trust signals (certifications, guarantees)

    Be extremely specific about what you can see vs what you're inferring.
    Quote exact text when possible.
    
    If this is a shopping/product page: {product_url}
    """
    
    return {
        'success': True,
        'image_path': image_path,
        'product_url': product_url,
        'analysis_prompt': analysis_prompt,
        'image_data': f'data:image/png;base64,{image_data}' if image_path.endswith('.png') else f'data:image/jpeg;base64,{image_data}',
        'extracted_info': {
            'method': 'screenshot_analysis',
            'source': 'visual_extraction',
            'reliability': 'medium'  # Screenshots can miss dynamic content
        }
    }

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 screenshot_analyzer.py <image_path> [product_url]")
        print("  Analyzes a product page screenshot for shopping intelligence")
        sys.exit(1)
    
    image_path = sys.argv[1]
    product_url = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = analyze_screenshot(image_path, product_url)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()