"""
Company Enrichment Module
Fetches company data from Hunter.io API with a built-in fallback dataset
for reliable demos.
"""

import requests
import os


# ── Built-in company database for reliable fallback ──────────────────────────
COMPANY_DATABASE = {
    'stripe.com': {
        'company_name': 'Stripe, Inc.',
        'industry': 'Financial Technology (FinTech)',
        'employee_count': '5000-10000',
        'location': 'San Francisco, CA, USA',
        'linkedin': 'linkedin.com/company/stripe',
        'description': 'Online payment processing platform for internet businesses',
    },
    'shopify.com': {
        'company_name': 'Shopify Inc.',
        'industry': 'E-Commerce / SaaS',
        'employee_count': '10000+',
        'location': 'Ottawa, Ontario, Canada',
        'linkedin': 'linkedin.com/company/shopify',
        'description': 'E-commerce platform for online stores and retail POS systems',
    },
    'slack.com': {
        'company_name': 'Slack Technologies (Salesforce)',
        'industry': 'Enterprise Software / SaaS',
        'employee_count': '2000-5000',
        'location': 'San Francisco, CA, USA',
        'linkedin': 'linkedin.com/company/slack',
        'description': 'Business communication and collaboration platform',
    },
    'hubspot.com': {
        'company_name': 'HubSpot, Inc.',
        'industry': 'Marketing Technology / SaaS',
        'employee_count': '5000-10000',
        'location': 'Cambridge, MA, USA',
        'linkedin': 'linkedin.com/company/hubspot',
        'description': 'CRM, marketing, sales, and service software platform',
    },
    'notion.so': {
        'company_name': 'Notion Labs, Inc.',
        'industry': 'Productivity Software / SaaS',
        'employee_count': '500-1000',
        'location': 'San Francisco, CA, USA',
        'linkedin': 'linkedin.com/company/notion-hq',
        'description': 'All-in-one workspace for notes, docs, and project management',
    },
    'figma.com': {
        'company_name': 'Figma, Inc.',
        'industry': 'Design Software / SaaS',
        'employee_count': '1000-2000',
        'location': 'San Francisco, CA, USA',
        'linkedin': 'linkedin.com/company/figma',
        'description': 'Collaborative interface design tool',
    },
    'intercom.com': {
        'company_name': 'Intercom, Inc.',
        'industry': 'Customer Communication / SaaS',
        'employee_count': '500-1000',
        'location': 'San Francisco, CA, USA',
        'linkedin': 'linkedin.com/company/intercom',
        'description': 'Customer messaging platform for sales, marketing, and support',
    },
    'dropbox.com': {
        'company_name': 'Dropbox, Inc.',
        'industry': 'Cloud Storage / SaaS',
        'employee_count': '2000-5000',
        'location': 'San Francisco, CA, USA',
        'linkedin': 'linkedin.com/company/dropbox',
        'description': 'Cloud storage and file synchronization service',
    },
    'twilio.com': {
        'company_name': 'Twilio Inc.',
        'industry': 'Cloud Communications / SaaS',
        'employee_count': '5000-10000',
        'location': 'San Francisco, CA, USA',
        'linkedin': 'linkedin.com/company/twilio',
        'description': 'Cloud communications platform for SMS, voice, and messaging',
    },
    'mailchimp.com': {
        'company_name': 'Mailchimp (Intuit)',
        'industry': 'Email Marketing / SaaS',
        'employee_count': '1000-2000',
        'location': 'Atlanta, GA, USA',
        'linkedin': 'linkedin.com/company/mailchimp',
        'description': 'Marketing automation and email marketing platform',
    },
    'zendesk.com': {
        'company_name': 'Zendesk, Inc.',
        'industry': 'Customer Service Software / SaaS',
        'employee_count': '5000-10000',
        'location': 'San Francisco, CA, USA',
        'linkedin': 'linkedin.com/company/zendesk',
        'description': 'Customer service and engagement platform',
    },
    'asana.com': {
        'company_name': 'Asana, Inc.',
        'industry': 'Project Management / SaaS',
        'employee_count': '1000-2000',
        'location': 'San Francisco, CA, USA',
        'linkedin': 'linkedin.com/company/asana',
        'description': 'Work management platform for teams',
    },
    'datadog.com': {
        'company_name': 'Datadog, Inc.',
        'industry': 'Cloud Monitoring / SaaS',
        'employee_count': '5000-10000',
        'location': 'New York, NY, USA',
        'linkedin': 'linkedin.com/company/datadog',
        'description': 'Cloud-scale monitoring and analytics platform',
    },
    'airtable.com': {
        'company_name': 'Airtable, Inc.',
        'industry': 'Productivity Software / SaaS',
        'employee_count': '500-1000',
        'location': 'San Francisco, CA, USA',
        'linkedin': 'linkedin.com/company/airtable',
        'description': 'Low-code platform for building collaborative apps',
    },
    'canva.com': {
        'company_name': 'Canva Pty Ltd',
        'industry': 'Design Software / SaaS',
        'employee_count': '2000-5000',
        'location': 'Sydney, Australia',
        'linkedin': 'linkedin.com/company/canva',
        'description': 'Online graphic design and visual communication platform',
    },
}


def enrich_company(domain):
    """
    Enrich company data. Tries Hunter.io API first, then falls back
    to built-in dataset.

    Args:
        domain: Company domain (e.g., 'stripe.com')

    Returns:
        dict with company_name, industry, employee_count, location, etc.
    """
    # Clean domain
    domain = (
        domain.lower()
        .replace('https://', '')
        .replace('http://', '')
        .replace('www.', '')
        .split('/')[0]
    )

    # Try Hunter.io API first (if key is available)
    api_key = os.getenv('HUNTER_API_KEY', '')
    if api_key:
        hunter_data = _try_hunter_io(domain, api_key)
        if hunter_data and hunter_data.get('success'):
            return hunter_data

    # Fallback to built-in dataset
    if domain in COMPANY_DATABASE:
        data = COMPANY_DATABASE[domain].copy()
        data['success'] = True
        data['source'] = 'database'
        return data

    # Last resort: derive from domain name
    name_part = domain.split('.')[0]
    company_name = name_part.replace('-', ' ').replace('_', ' ').title()

    return {
        'company_name': company_name,
        'industry': 'Unknown',
        'employee_count': 'Unknown',
        'location': 'Unknown',
        'linkedin': '',
        'description': '',
        'success': False,
        'source': 'derived',
        'note': 'Limited data available. Try a well-known domain for full enrichment.',
    }


def _try_hunter_io(domain, api_key):
    """Attempt to fetch data from Hunter.io domain-search API."""
    try:
        url = f'https://api.hunter.io/v2/domain-search?domain={domain}&api_key={api_key}'
        response = requests.get(url, timeout=10)
        data = response.json()

        if data.get('data'):
            cd = data['data']

            # Extract top emails from Hunter
            hunter_emails = []
            for email_info in cd.get('emails', [])[:5]:
                hunter_emails.append({
                    'email': email_info.get('value', ''),
                    'type': email_info.get('type', ''),
                    'confidence': email_info.get('confidence', 0),
                })

            return {
                'company_name': cd.get('organization', domain.split('.')[0].title()),
                'industry': cd.get('industry', 'Unknown'),
                'employee_count': str(cd.get('employee_count', 'Unknown')),
                'location': cd.get('country', 'Unknown'),
                'linkedin': cd.get('linkedin', ''),
                'description': cd.get('description', ''),
                'hunter_emails': hunter_emails,
                'success': True,
                'source': 'hunter_io',
            }
    except Exception:
        pass

    return None
