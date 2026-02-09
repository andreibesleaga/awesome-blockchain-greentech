#!/usr/bin/env python3
"""
Link checker for README.md
Verifies all links in the README are accessible and returns valid status codes.
"""

import re
import sys
import requests
from pathlib import Path
import time
from urllib.parse import urlparse

# Configuration
TIMEOUT = 10
MAX_RETRIES = 2
RETRY_DELAY = 2
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# Domains that aggressively block bot requests
SKIP_DOMAINS = [
    'researchgate.net',
    'reddit.com',
    'medium.com',
    'substack.com',
    'mdpi.com',
]

def is_skip_domain(url):
    """Check if a URL's domain matches any skip domain."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        # Remove 'www.' prefix if present
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Check if domain matches or is a subdomain of any skip domain
        for skip_domain in SKIP_DOMAINS:
            if domain == skip_domain or domain.endswith('.' + skip_domain):
                return True
        return False
    except Exception:
        return False

def extract_links_from_markdown(content):
    """Extract all URLs from markdown content."""
    # Match markdown links [text](url) and bare URLs
    markdown_links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', content)
    bare_urls = re.findall(r'(?<!\()\bhttps?://[^\s\)]+', content)
    
    links = []
    for text, url in markdown_links:
        links.append({'text': text, 'url': url, 'type': 'markdown'})
    
    for url in bare_urls:
        # Skip if already captured in markdown links
        if not any(link['url'] == url for link in links):
            links.append({'text': url, 'url': url, 'type': 'bare'})
    
    return links

def check_url(url, retries=MAX_RETRIES):
    """Check if a URL is accessible."""
    headers = {
        'User-Agent': USER_AGENT,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    for attempt in range(retries + 1):
        try:
            # Use HEAD request first for efficiency
            response = requests.head(url, headers=headers, timeout=TIMEOUT, allow_redirects=True)
            
            # Some servers don't support HEAD, fallback to GET
            if response.status_code == 405 or response.status_code == 403:
                response = requests.get(url, headers=headers, timeout=TIMEOUT, allow_redirects=True)
            
            if response.status_code < 400:
                return {
                    'status': 'success',
                    'status_code': response.status_code,
                    'final_url': response.url
                }
            else:
                return {
                    'status': 'error',
                    'status_code': response.status_code,
                    'error': f'HTTP {response.status_code}'
                }
        
        except requests.exceptions.Timeout:
            if attempt < retries:
                time.sleep(RETRY_DELAY)
                continue
            return {'status': 'error', 'error': 'Timeout'}
        
        except requests.exceptions.ConnectionError as e:
            if attempt < retries:
                time.sleep(RETRY_DELAY)
                continue
            return {'status': 'error', 'error': f'Connection error: {str(e)[:100]}'}
        
        except requests.exceptions.RequestException as e:
            return {'status': 'error', 'error': f'Request error: {str(e)[:100]}'}
        
        except Exception as e:
            return {'status': 'error', 'error': f'Unexpected error: {str(e)[:100]}'}
    
    return {'status': 'error', 'error': 'Max retries exceeded'}

def main():
    """Main function to check all links in README.md."""
    readme_path = Path('README.md')
    
    if not readme_path.exists():
        print("❌ README.md not found!")
        sys.exit(1)
    
    print("📖 Reading README.md...")
    content = readme_path.read_text(encoding='utf-8')
    
    print("🔍 Extracting links...")
    links = extract_links_from_markdown(content)
    
    print(f"Found {len(links)} links")
    
    # Deduplicate links by URL (keep first occurrence)
    seen_urls = set()
    unique_links = []
    for link in links:
        if link['url'] not in seen_urls:
            seen_urls.add(link['url'])
            unique_links.append(link)
    
    if len(unique_links) < len(links):
        print(f"Deduplicated to {len(unique_links)} unique URLs\n")
    else:
        print()
    
    results = {
        'success': [],
        'failed': [],
        'skipped_anchor': 0,
        'skipped_bot_protected': 0
    }
    
    # Check each link
    for i, link in enumerate(unique_links, 1):
        url = link['url']
        
        # Skip anchors and relative links
        if url.startswith('#') or not url.startswith('http'):
            print(f"[{i}/{len(unique_links)}] ⏭️  Skipping: {url}")
            results['skipped_anchor'] += 1
            continue
        
        # Skip bot-protected domains
        if is_skip_domain(url):
            print(f"[{i}/{len(unique_links)}] ⏭️  Skipping (bot-protected): {url}")
            results['skipped_bot_protected'] += 1
            continue
        
        print(f"[{i}/{len(unique_links)}] Checking: {url}")
        result = check_url(url)
        
        if result['status'] == 'success':
            print(f"  ✅ OK (HTTP {result['status_code']})")
            results['success'].append({'link': link, 'result': result})
        else:
            print(f"  ❌ FAILED: {result.get('error', 'Unknown error')}")
            results['failed'].append({'link': link, 'result': result})
        
        # Rate limiting
        time.sleep(0.5)
    
    # Generate report
    total_checked = len(results['success']) + len(results['failed'])
    total_skipped = results['skipped_anchor'] + results['skipped_bot_protected']
    print("\n" + "="*60)
    print("📊 LINK CHECK REPORT")
    print("="*60)
    print(f"Total links found: {len(links)}")
    print(f"Unique URLs: {len(unique_links)}")
    print(f"Links checked: {total_checked}")
    print(f"Links skipped (total): {total_skipped}")
    print(f"  - Anchors/relative: {results['skipped_anchor']}")
    print(f"  - Bot-protected: {results['skipped_bot_protected']}")
    print(f"✅ Successful: {len(results['success'])}")
    print(f"❌ Failed: {len(results['failed'])}")
    print()
    
    if results['failed']:
        report_path = Path('link_check_report.md')
        with report_path.open('w', encoding='utf-8') as f:
            f.write("# Link Check Report\n\n")
            f.write(f"**Date:** {time.strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n")
            f.write(f"## Summary\n\n")
            f.write(f"- Total links found: {len(links)}\n")
            f.write(f"- Unique URLs: {len(unique_links)}\n")
            f.write(f"- Links checked: {total_checked}\n")
            f.write(f"- Links skipped (total): {total_skipped}\n")
            f.write(f"  - Anchors/relative: {results['skipped_anchor']}\n")
            f.write(f"  - Bot-protected: {results['skipped_bot_protected']}\n")
            f.write(f"- ✅ Successful: {len(results['success'])}\n")
            f.write(f"- ❌ Failed: {len(results['failed'])}\n\n")
            
            if results['failed']:
                f.write("## Failed Links\n\n")
                for item in results['failed']:
                    link = item['link']
                    result = item['result']
                    f.write(f"### [{link['text']}]({link['url']})\n\n")
                    f.write(f"- **Error:** {result.get('error', 'Unknown')}\n")
                    if 'status_code' in result:
                        f.write(f"- **Status Code:** {result['status_code']}\n")
                    f.write("\n")
        
        print(f"Report saved to: {report_path}")
        print("\n⚠️  Some links are broken!")
        sys.exit(0)  # Don't fail the workflow, just report
    else:
        print("✅ All links are working!")
        sys.exit(0)

if __name__ == '__main__':
    main()
