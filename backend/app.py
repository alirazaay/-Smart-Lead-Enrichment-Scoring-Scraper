"""
Smart Lead Enrichment & Scoring API
Flask server that orchestrates scraping, enrichment, and scoring.
Also serves the frontend static files.
"""

import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

from scraper import scrape_emails
from enrichment import enrich_company
from scorer import score_lead

# Load environment variables
load_dotenv()

# Flask app — serves frontend from ../frontend
app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)


# ── Static file serving ─────────────────────────────────────────────────────

@app.route('/')
def index():
    """Serve the frontend."""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:path>')
def static_files(path):
    """Serve static assets (CSS, JS)."""
    return send_from_directory(app.static_folder, path)


# ── API endpoints ────────────────────────────────────────────────────────────

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'message': 'Smart Lead Enrichment API is running',
        'hunter_api': 'configured' if os.getenv('HUNTER_API_KEY') else 'not configured (using fallback data)',
    })


@app.route('/api/analyze', methods=['POST'])
def analyze_lead():
    """
    Main analysis endpoint.
    Accepts: { "company": "stripe.com" }
    Returns: Full enriched + scored lead profile.
    """
    try:
        data = request.json
        company_input = data.get('company', '').strip()

        if not company_input:
            return jsonify({'error': 'Please provide a company name or domain.'}), 400

        # Clean input to extract domain
        domain = company_input.lower()
        domain = domain.replace('https://', '').replace('http://', '').replace('www.', '')
        domain = domain.split('/')[0]

        # Add .com if no TLD present
        if '.' not in domain:
            domain = f'{domain}.com'

        # ── Step 1: Scrape emails from website ───────────────────────────
        email_data = scrape_emails(domain)

        # ── Step 2: Enrich company data ──────────────────────────────────
        company_data = enrich_company(domain)

        # ── Step 3: Merge emails from both sources ───────────────────────
        all_emails = list(set(email_data.get('all_emails', [])))

        # Add Hunter.io emails if available
        for he in company_data.get('hunter_emails', []):
            email_addr = he.get('email', '')
            if email_addr and email_addr not in all_emails:
                all_emails.append(email_addr)

        priority_emails = email_data.get('priority_emails', [])

        # ── Step 4: Build lead profile ───────────────────────────────────
        lead = {
            'domain': domain,
            'company_name': company_data.get('company_name', domain.split('.')[0].title()),
            'industry': company_data.get('industry', 'Unknown'),
            'employee_count': company_data.get('employee_count', 'Unknown'),
            'location': company_data.get('location', 'Unknown'),
            'linkedin': company_data.get('linkedin', ''),
            'description': company_data.get('description', ''),
            'emails': all_emails[:5],
            'priority_emails': priority_emails[:3],
            'page_title': email_data.get('page_title', ''),
            'data_source': company_data.get('source', 'unknown'),
            'scrape_success': email_data.get('success', False),
        }

        # ── Step 5: Score the lead ───────────────────────────────────────
        score_data = score_lead(lead)

        # Combine everything into final result
        result = {**lead, **score_data}
        return jsonify(result)

    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print()
    print('=' * 55)
    print('  🎯  Smart Lead Enrichment & Scoring API')
    print('=' * 55)
    print(f'  Server:   http://localhost:{port}')
    print(f'  API:      http://localhost:{port}/api/analyze')
    print(f'  Health:   http://localhost:{port}/api/health')

    if os.getenv('HUNTER_API_KEY'):
        print('  Hunter:   ✅ API key configured')
    else:
        print('  Hunter:   ⚠️  No API key — using fallback dataset')

    print('=' * 55)
    print()
    app.run(debug=True, port=port)
