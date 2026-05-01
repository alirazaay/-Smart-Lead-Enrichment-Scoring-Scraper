"""
Email Scraper Module
Extracts email addresses from a company's website homepage.
"""

import requests
from bs4 import BeautifulSoup
import re


def scrape_emails(url):
    """
    Extract emails from a website's homepage.
    
    Args:
        url: Company domain or full URL (e.g., 'stripe.com' or 'https://stripe.com')
    
    Returns:
        dict with all_emails, priority_emails, page_title, success, source
    """
    try:
        # Normalize URL
        if not url.startswith('http'):
            url = f'https://{url}'

        # Request the page
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract page title
        page_title = ''
        if soup.title and soup.title.string:
            page_title = soup.title.string.strip()

        # Find emails using regex
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        raw_emails = re.findall(email_pattern, response.text)

        # Filter out asset/fake emails
        exclude_patterns = [
            '.png', '.jpg', '.jpeg', '.svg', '.gif', '.css', '.js',
            '.woff', '.ttf', '.eot', 'example.com', 'email.com',
            'domain.com', 'yourcompany', 'sentry.io', 'webpack'
        ]
        emails = list(set([
            e.lower() for e in raw_emails
            if not any(x in e.lower() for x in exclude_patterns)
        ]))

        # Separate priority emails (contact/sales/support)
        priority_keywords = [
            'contact', 'info', 'sales', 'support', 'hello',
            'team', 'partnerships', 'business', 'press', 'media'
        ]
        priority_emails = [
            e for e in emails
            if any(k in e.lower() for k in priority_keywords)
        ]
        other_emails = [e for e in emails if e not in priority_emails]

        return {
            'all_emails': priority_emails + other_emails,
            'priority_emails': priority_emails,
            'page_title': page_title,
            'success': True,
            'source': 'live_scrape'
        }

    except requests.exceptions.SSLError:
        # Try HTTP fallback
        try:
            http_url = url.replace('https://', 'http://')
            response = requests.get(http_url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
            })
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            raw_emails = re.findall(email_pattern, response.text)
            emails = list(set([e.lower() for e in raw_emails]))
            return {
                'all_emails': emails[:10],
                'priority_emails': [],
                'page_title': '',
                'success': True,
                'source': 'live_scrape_http'
            }
        except Exception:
            pass

        return _empty_result('SSL error - site may not be accessible')

    except Exception as e:
        return _empty_result(str(e))


def _empty_result(error_msg=''):
    """Return an empty result structure."""
    return {
        'all_emails': [],
        'priority_emails': [],
        'page_title': '',
        'success': False,
        'error': error_msg,
        'source': 'failed'
    }
