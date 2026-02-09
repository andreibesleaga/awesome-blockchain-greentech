#!/usr/bin/env python3
"""
Project discovery script for README.md
Searches GitHub for new blockchain greentech projects similar to existing ones.
"""

import os
import re
import sys
import time
import requests
from pathlib import Path
from collections import defaultdict

# Configuration
GITHUB_API = 'https://api.github.com'
TIMEOUT = 10
USER_AGENT = 'AwesomeBlockchainGreentechBot/1.0'

# Keywords for different categories
SEARCH_QUERIES = {
    'Energy Grid & P2P Trading': [
        'blockchain renewable energy trading',
        'decentralized energy grid',
        'peer-to-peer energy',
        'blockchain solar power'
    ],
    'Digital Carbon Markets': [
        'blockchain carbon credits',
        'tokenized carbon offsets',
        'ReFi regenerative finance',
        'carbon marketplace blockchain'
    ],
    'Digital MRV': [
        'blockchain carbon verification',
        'IoT blockchain environmental monitoring',
        'blockchain forestry monitoring',
        'dMRV measurement reporting verification'
    ],
    'Supply Chain & Circular Economy': [
        'blockchain circular economy',
        'digital product passport blockchain',
        'blockchain supply chain sustainability',
        'blockchain waste management'
    ],
    'Layer 1 Protocols': [
        'green blockchain protocol',
        'energy efficient blockchain',
        'carbon negative blockchain',
        'sustainable blockchain'
    ]
}

def get_github_token():
    """Get GitHub token from environment."""
    return os.environ.get('GITHUB_TOKEN', '')

def extract_existing_repos(content):
    """Extract GitHub repository URLs from README."""
    # Match GitHub URLs, capturing owner and optional repo
    github_pattern = r'https?://github\.com/([^/\s\)]+)(?:/([^/\s\)]+))?'
    matches = re.findall(github_pattern, content)
    
    repos = set()
    orgs = set()
    
    for owner, repo in matches:
        if repo:
            # Clean up repo name (remove trailing chars)
            repo = repo.rstrip('.,;:)')
            repos.add(f"{owner}/{repo}")
        else:
            # Track organizations/profiles that appear as standalone URLs (e.g., github.com/owner without /repo)
            orgs.add(owner)
    
    # Mark all repos from these organizations for exclusion during project discovery
    for org in orgs:
        # Add a pattern to match any repo from this org
        repos.add(f"{org}/*")
    
    return repos

def search_github_repos(query, existing_repos, token='', rate_limit_errors=None):
    """Search GitHub for repositories matching the query."""
    if rate_limit_errors is None:
        rate_limit_errors = []
    
    headers = {
        'User-Agent': USER_AGENT,
        'Accept': 'application/vnd.github.v3+json'
    }
    
    if token:
        headers['Authorization'] = f'token {token}'
    
    # Search for repositories
    search_url = f'{GITHUB_API}/search/repositories'
    params = {
        'q': f'{query} stars:>10 pushed:>2023-01-01',  # Active projects with some traction
        'sort': 'stars',
        'order': 'desc',
        'per_page': 10
    }
    
    try:
        response = requests.get(search_url, headers=headers, params=params, timeout=TIMEOUT)
        
        if response.status_code == 403:
            error_msg = f"Rate limited or forbidden for query: {query}"
            print(f"  ⚠️  {error_msg}")
            rate_limit_errors.append(error_msg)
            return []
        
        if response.status_code != 200:
            print(f"  ❌ Error: HTTP {response.status_code}")
            return []
        
        data = response.json()
        new_repos = []
        
        for item in data.get('items', []):
            full_name = item['full_name']
            
            # Skip if already in README (exact match or org match)
            if full_name in existing_repos:
                continue
            
            # Check if this repo's owner has an org-level entry
            owner = full_name.split('/')[0]
            if f"{owner}/*" in existing_repos:
                continue
            
            # Extract relevant info
            repo_info = {
                'name': item['name'],
                'full_name': full_name,
                'description': item.get('description', 'No description'),
                'stars': item['stargazers_count'],
                'url': item['html_url'],
                'language': item.get('language', 'Unknown'),
                'updated_at': item['updated_at'],
                'topics': item.get('topics', [])
            }
            
            new_repos.append(repo_info)
        
        return new_repos
    
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Request error: {str(e)[:100]}")
        return []
    except Exception as e:
        print(f"  ❌ Error: {str(e)[:100]}")
        return []

def is_relevant_project(repo, category):
    """Check if a repository is relevant based on description and topics."""
    description = (repo.get('description') or '').lower()
    topics = [t.lower() for t in repo.get('topics', [])]
    
    # Define relevance keywords for each category
    relevance_keywords = {
        'Energy Grid & P2P Trading': ['energy', 'grid', 'solar', 'renewable', 'trading', 'power'],
        'Digital Carbon Markets': ['carbon', 'credit', 'offset', 'refi', 'climate', 'emission'],
        'Digital MRV': ['verification', 'monitoring', 'mrv', 'measurement', 'reporting', 'forest'],
        'Supply Chain & Circular Economy': ['supply', 'chain', 'circular', 'waste', 'recycl', 'passport'],
        'Layer 1 Protocols': ['protocol', 'blockchain', 'layer1', 'consensus', 'sustainable']
    }
    
    keywords = relevance_keywords.get(category, [])
    
    # Check if description or topics contain relevant keywords
    text_to_check = description + ' ' + ' '.join(topics)
    
    matches = sum(1 for keyword in keywords if keyword in text_to_check)
    
    # Require at least 2 keyword matches for relevance
    return matches >= 2

def main():
    """Main function to search for new projects."""
    readme_path = Path('README.md')
    
    if not readme_path.exists():
        print("❌ README.md not found!")
        sys.exit(1)
    
    print("📖 Reading README.md...")
    content = readme_path.read_text(encoding='utf-8')
    
    print("🔍 Extracting existing repositories...")
    existing_repos = extract_existing_repos(content)
    print(f"Found {len(existing_repos)} existing repositories\n")
    
    # Get GitHub token
    token = get_github_token()
    if not token:
        print("⚠️  No GitHub token found. Rate limits will be strict.")
    
    # Search for new projects in each category
    all_discoveries = defaultdict(list)
    rate_limit_errors = []
    
    for category, queries in SEARCH_QUERIES.items():
        print(f"\n{'='*60}")
        print(f"🔎 Searching: {category}")
        print('='*60)
        
        for query in queries:
            print(f"\n  Query: {query}")
            repos = search_github_repos(query, existing_repos, token, rate_limit_errors)
            
            # Filter for relevance
            relevant_repos = [r for r in repos if is_relevant_project(r, category)]
            
            print(f"  Found {len(relevant_repos)} relevant new projects")
            
            for repo in relevant_repos:
                # Avoid duplicates
                if not any(r['full_name'] == repo['full_name'] for r in all_discoveries[category]):
                    all_discoveries[category].append(repo)
            
            # Rate limiting
            time.sleep(2)
    
    # Generate report
    print("\n" + "="*60)
    print("📊 PROJECT DISCOVERY REPORT")
    print("="*60)
    
    total_discoveries = sum(len(repos) for repos in all_discoveries.values())
    print(f"Total new projects found: {total_discoveries}\n")
    
    if rate_limit_errors:
        print(f"⚠️  Encountered {len(rate_limit_errors)} rate limit errors")
    
    if total_discoveries > 0 or rate_limit_errors:
        report_path = Path('new_projects_report.md')
        with report_path.open('w', encoding='utf-8') as f:
            f.write("# New Projects Discovery Report\n\n")
            f.write(f"**Date:** {time.strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n")
            f.write(f"**Total discoveries:** {total_discoveries}\n\n")
            
            if rate_limit_errors:
                f.write("## ⚠️ Rate Limit Errors\n\n")
                f.write("The following queries encountered rate limiting or access issues:\n\n")
                for error in rate_limit_errors:
                    f.write(f"- {error}\n")
                f.write("\n")
                f.write("**Note:** Consider running the workflow again later or check the GitHub token permissions.\n\n")
            
            if total_discoveries > 0:
                f.write("## Suggested Additions\n\n")
                f.write("The following projects were discovered and may be relevant to add to the README:\n\n")
            
            for category, repos in all_discoveries.items():
                if repos:
                    f.write(f"### {category}\n\n")
                    
                    for repo in repos:
                        f.write(f"#### [{repo['name']}]({repo['url']}) ⭐ {repo['stars']}\n\n")
                        f.write(f"- **Description:** {repo['description']}\n")
                        f.write(f"- **Language:** {repo['language']}\n")
                        if repo['topics']:
                            f.write(f"- **Topics:** {', '.join(repo['topics'])}\n")
                        f.write(f"- **Last Updated:** {repo['updated_at'][:10]}\n")
                        f.write("\n")
                    
                    f.write("\n")
            
            f.write("---\n\n")
            f.write("**Note:** Please review each project before adding to the README. ")
            f.write("Verify that it is active, open-source, and relevant to blockchain greentech.\n")
        
        print(f"Report saved to: {report_path}")
        print(f"\n✅ Found {total_discoveries} new potential projects!")
    else:
        print("ℹ️  No new projects discovered this week.")
    
    sys.exit(0)

if __name__ == '__main__':
    main()
