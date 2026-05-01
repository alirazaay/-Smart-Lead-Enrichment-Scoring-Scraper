/**
 * Smart Lead Enrichment — Client-Side Application
 * Handles API calls, result rendering, and CSV export.
 */

const API_BASE = window.location.origin;

// Store last result for CSV export
let lastResult = null;

// ── Event Listeners ─────────────────────────────────────────────────────────

document.getElementById('company-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') analyzeLead();
});

// ── Quick Try ───────────────────────────────────────────────────────────────

function quickTry(domain) {
    document.getElementById('company-input').value = domain;
    analyzeLead();
}

// ── Main Analysis ───────────────────────────────────────────────────────────

async function analyzeLead() {
    const input = document.getElementById('company-input');
    const btn = document.getElementById('analyze-btn');
    const company = input.value.trim();

    if (!company) {
        showError('Please enter a company name or domain.');
        return;
    }

    // UI: loading state
    setLoading(true);
    hideError();
    document.getElementById('results-section').hidden = true;

    try {
        const response = await fetch(`${API_BASE}/api/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ company }),
        });

        const data = await response.json();

        if (!response.ok) {
            showError(data.error || 'Something went wrong. Please try again.');
            return;
        }

        lastResult = data;
        renderResults(data);

    } catch (err) {
        showError('Could not connect to the server. Make sure the backend is running.');
    } finally {
        setLoading(false);
    }
}

// ── Render Results ──────────────────────────────────────────────────────────

function renderResults(data) {
    const section = document.getElementById('results-section');

    // Score & Priority
    const scoreEl = document.getElementById('score-value');
    scoreEl.textContent = data.total_score;
    scoreEl.style.color = data.color;

    const badge = document.getElementById('priority-badge');
    badge.textContent = `${data.emoji} ${data.priority}`;
    badge.className = 'priority-badge ' + data.priority.toLowerCase();

    // Company info
    document.getElementById('company-name').textContent = data.company_name || data.domain;
    document.getElementById('company-domain').textContent = data.domain;

    // Details grid
    document.getElementById('val-industry').textContent = data.industry || '—';
    document.getElementById('val-location').textContent = data.location || '—';
    document.getElementById('val-size').textContent = data.employee_count || '—';

    const sourceLabel = {
        'hunter_io': 'Hunter.io API',
        'database': 'Verified Database',
        'derived': 'Domain Analysis',
        'unknown': 'Limited Data',
    };
    document.getElementById('val-source').textContent = sourceLabel[data.data_source] || data.data_source;

    // Emails
    renderEmails(data.emails || [], data.priority_emails || []);

    // Score breakdown
    renderBreakdown(data.breakdown || {});

    // Recommendation
    document.getElementById('recommendation-text').textContent = data.recommendation || '';

    // Extra info (LinkedIn, description)
    renderExtra(data);

    // Show results
    section.hidden = false;
    section.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ── Render Emails ───────────────────────────────────────────────────────────

function renderEmails(allEmails, priorityEmails) {
    const container = document.getElementById('emails-list');

    if (!allEmails.length) {
        container.innerHTML = '<p class="empty-state">No emails found on this website.</p>';
        return;
    }

    container.innerHTML = allEmails.map(email => {
        const isPriority = priorityEmails.includes(email);
        return `
            <div class="email-item">
                <span>${email}</span>
                ${isPriority ? '<span class="email-type">Priority</span>' : ''}
            </div>
        `;
    }).join('');
}

// ── Render Score Breakdown ──────────────────────────────────────────────────

function renderBreakdown(breakdown) {
    const container = document.getElementById('breakdown-list');
    const entries = Object.entries(breakdown);

    if (!entries.length) {
        container.innerHTML = '<p class="empty-state">No scoring factors matched.</p>';
        return;
    }

    // Find max points for bar scaling
    const maxPts = Math.max(...entries.map(([, v]) => v), 1);

    container.innerHTML = entries.map(([label, points]) => {
        const barWidth = Math.round((points / 30) * 100);  // 30 is max single factor
        return `
            <div class="breakdown-item">
                <span class="breakdown-label">${label}</span>
                <div class="breakdown-bar-bg">
                    <div class="breakdown-bar-fill" style="width: ${barWidth}%"></div>
                </div>
                <span class="breakdown-points">+${points}</span>
            </div>
        `;
    }).join('');
}

// ── Render Extra Info ───────────────────────────────────────────────────────

function renderExtra(data) {
    const card = document.getElementById('extra-card');
    const linkedinRow = document.getElementById('linkedin-row');
    const descRow = document.getElementById('description-row');
    let showCard = false;

    if (data.linkedin) {
        const link = document.getElementById('linkedin-link');
        const fullUrl = data.linkedin.startsWith('http') ? data.linkedin : `https://${data.linkedin}`;
        link.href = fullUrl;
        link.textContent = data.linkedin;
        linkedinRow.hidden = false;
        showCard = true;
    } else {
        linkedinRow.hidden = true;
    }

    if (data.description) {
        document.getElementById('description-text').textContent = data.description;
        descRow.hidden = false;
        showCard = true;
    } else {
        descRow.hidden = true;
    }

    card.hidden = !showCard;
}

// ── CSV Export ───────────────────────────────────────────────────────────────

function exportCSV() {
    if (!lastResult) return;

    const d = lastResult;
    const headers = [
        'Company', 'Domain', 'Industry', 'Location', 'Employees',
        'Emails', 'Score', 'Priority', 'Recommendation', 'Data Source'
    ];
    const values = [
        d.company_name, d.domain, d.industry, d.location, d.employee_count,
        (d.emails || []).join('; '), d.total_score, d.priority,
        d.recommendation, d.data_source
    ];

    // Escape CSV values
    const escape = v => `"${String(v || '').replace(/"/g, '""')}"`;
    const csv = headers.map(escape).join(',') + '\n' + values.map(escape).join(',');

    // Download
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `lead_${d.domain.replace(/\./g, '_')}.csv`;
    a.click();
    URL.revokeObjectURL(url);
}

// ── UI Helpers ──────────────────────────────────────────────────────────────

function setLoading(isLoading) {
    const btn = document.getElementById('analyze-btn');
    const btnText = btn.querySelector('.btn-text');
    const btnLoader = btn.querySelector('.btn-loader');
    btn.disabled = isLoading;
    btnText.hidden = isLoading;
    btnLoader.hidden = !isLoading;
}

function showError(message) {
    const el = document.getElementById('error-message');
    el.textContent = message;
    el.hidden = false;
}

function hideError() {
    document.getElementById('error-message').hidden = true;
}
