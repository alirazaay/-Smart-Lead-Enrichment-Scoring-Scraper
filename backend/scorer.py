"""
Lead Scoring Module
Scores leads 0-100 based on weighted business value factors.

Scoring Breakdown:
  - Data Quality:          30 points max
  - Industry Fit:          25 points max
  - Geographic Fit:        20 points max
  - Company Size:          15 points max
  - Contact Accessibility: 10 points max
"""


def score_lead(lead):
    """
    Score a lead from 0-100 based on business value factors.

    Args:
        lead: dict with company_name, industry, location, employee_count, emails

    Returns:
        dict with total_score, priority, emoji, color, breakdown, recommendation
    """
    score = 0
    breakdown = {}

    # ── 1. DATA QUALITY (30 points max) ──────────────────────────────────────
    emails = lead.get('emails', [])
    if emails:
        pts = min(15, len(emails) * 5)
        breakdown['Contact emails found'] = pts
        score += pts

    if lead.get('company_name') and lead['company_name'] != 'Unknown':
        breakdown['Company identified'] = 10
        score += 10

    if lead.get('industry') and lead['industry'] != 'Unknown':
        breakdown['Industry data available'] = 5
        score += 5

    # ── 2. INDUSTRY FIT (25 points max) ──────────────────────────────────────
    target_industries = [
        'technology', 'software', 'saas', 'fintech', 'ecommerce',
        'e-commerce', 'ai', 'data', 'cloud', 'cyber', 'digital',
        'marketing', 'automation', 'analytics', 'platform',
        'communication', 'productivity', 'design', 'monitoring',
    ]

    industry_text = str(lead.get('industry', '')).lower()
    if any(kw in industry_text for kw in target_industries):
        breakdown['Target industry match'] = 25
        score += 25
    elif lead.get('industry') and lead['industry'] != 'Unknown':
        breakdown['Industry identified'] = 10
        score += 10

    # ── 3. GEOGRAPHIC FIT (20 points max) ────────────────────────────────────
    priority_locations = [
        'united states', 'usa', 'united kingdom', 'uk', 'canada',
        'australia', 'san francisco', 'new york', 'london', 'toronto',
        'seattle', 'austin', 'boston', 'chicago', 'los angeles',
        'cambridge', 'atlanta', 'sydney', ', ca', ', ny', ', ma',
        ', wa', ', tx', ', il',
    ]

    location_text = str(lead.get('location', '')).lower()
    if any(loc in location_text for loc in priority_locations):
        breakdown['Priority market location'] = 20
        score += 20
    elif lead.get('location') and lead['location'] != 'Unknown':
        breakdown['Location identified'] = 10
        score += 10

    # ── 4. COMPANY SIZE (15 points max) ──────────────────────────────────────
    employee_str = str(lead.get('employee_count', '')).lower().replace(',', '')
    try:
        if '-' in employee_str:
            parts = employee_str.replace('+', '').split('-')
            low = int(parts[0].strip())
            high = int(parts[1].strip())
            avg = (low + high) / 2
        elif '+' in employee_str:
            avg = int(employee_str.replace('+', '').strip())
        else:
            avg = int(employee_str.strip())

        if 100 <= avg <= 5000:
            breakdown['Ideal company size (mid-market)'] = 15
            score += 15
        elif 50 <= avg <= 10000:
            breakdown['Good company size'] = 10
            score += 10
        elif avg > 10000:
            breakdown['Enterprise company'] = 7
            score += 7
    except (ValueError, IndexError):
        pass

    # ── 5. CONTACT ACCESSIBILITY (10 points max) ────────────────────────────
    if len(emails) >= 3:
        breakdown['Multiple contact points'] = 10
        score += 10
    elif len(emails) == 2:
        breakdown['Two contact points'] = 7
        score += 7
    elif len(emails) == 1:
        breakdown['Contact email found'] = 5
        score += 5

    # ── Determine priority level ─────────────────────────────────────────────
    if score >= 70:
        priority, emoji, color = 'HIGH', '🔥', '#22c55e'
    elif score >= 40:
        priority, emoji, color = 'MEDIUM', '⚡', '#f59e0b'
    else:
        priority, emoji, color = 'LOW', '📋', '#ef4444'

    return {
        'total_score': score,
        'max_score': 100,
        'priority': priority,
        'emoji': emoji,
        'color': color,
        'breakdown': breakdown,
        'recommendation': _get_recommendation(score, lead),
    }


def _get_recommendation(score, lead):
    """Generate an actionable sales recommendation."""
    name = lead.get('company_name', 'this company')

    if score >= 70:
        return (
            f'High-value lead. Prioritize immediate outreach to {name}. '
            f'Strong data signals suggest excellent fit for your solution.'
        )
    elif score >= 40:
        return (
            f'Medium potential lead. Consider personalized outreach to {name} '
            f'with tailored messaging based on their industry.'
        )
    else:
        return (
            f'Lower priority lead. {name} may need more research before outreach. '
            f'Focus on higher-scoring leads first.'
        )
