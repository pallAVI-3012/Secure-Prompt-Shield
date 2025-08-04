document.addEventListener('DOMContentLoaded', () => {
    document.querySelector('[data-tab="dashboard"]').addEventListener('click', loadFlaggedPrompts);
    document.getElementById('refresh-dash').addEventListener('click', loadFlaggedPrompts);
    document.getElementById('clear-logs').addEventListener('click', clearLogs);
    
    const thresholdSlider = document.getElementById('risk-threshold');
    const thresholdValue = document.getElementById('threshold-value');
    
    thresholdSlider.addEventListener('input', () => {
        thresholdValue.textContent = thresholdSlider.value;
    });
    
    // Load flagged prompts when dashboard tab is first opened
    loadFlaggedPrompts();
});

async function loadFlaggedPrompts() {
    const container = document.getElementById('flagged-prompts-container');
    container.innerHTML = '<div class="scan-line"></div><p class="placeholder-text">LOADING_FLAGGED_PROMPTS...</p>';

    try {
        const response = await fetch('/api/flagged');
        if (!response.ok) {
            throw new Error('Failed to load flagged prompts');
        }

        const flaggedPrompts = await response.json();
        displayFlaggedPrompts(flaggedPrompts);
    } catch (error) {
        container.innerHTML = `
            <div class="scan-line"></div>
            <div class="blocked-message">
                ⚠️ LOAD_ERROR: ${error.message}
            </div>
        `;
    }
}

function displayFlaggedPrompts(prompts) {
    const container = document.getElementById('flagged-prompts-container');
    container.innerHTML = '<div class="scan-line"></div>';

    if (prompts.length === 0) {
        container.innerHTML += '<p class="placeholder-text">NO_FLAGGED_PROMPTS_FOUND</p>';
        return;
    }

    prompts.forEach(prompt => {
        const promptElem = document.createElement('div');
        promptElem.className = 'flagged-prompt';
        
        const riskScoreClass = prompt.analysis.riskScore > 70 ? 'risk-high' : 
                              prompt.analysis.riskScore > 30 ? 'risk-medium' : 'risk-low';
        
        let risksHTML = prompt.analysis.risks.map(risk => {
            const riskClass = risk.severity === 'high' ? 'risk-high' : 
                             risk.severity === 'medium' ? 'risk-medium' : 'risk-low';
            return `<span class="flagged-prompt-risk ${riskClass}">${risk.type}</span>`;
        }).join('');

        promptElem.innerHTML = `
            <div class="flagged-prompt-header">
                <span>FLAGGED_PROMPT</span>
                <span class="flagged-prompt-risk ${riskScoreClass}">SCORE: ${prompt.analysis.riskScore}</span>
            </div>
            <div class="flagged-prompt-text">${escapeHtml(prompt.originalPrompt)}</div>
            <div>${risksHTML}</div>
            <div class="flagged-prompt-meta">
                ${new Date(prompt.timestamp).toLocaleString()}
                • ${prompt.analysis.blocked ? 'BLOCKED' : 'SANITIZED'}
                ${prompt.analysis.sanitizedPrompt !== prompt.originalPrompt ? 
                  `<br><span class="sanitized-text">Sanitized: ${escapeHtml(prompt.analysis.sanitizedPrompt)}</span>` : ''}
            </div>
            ${prompt.analysis.reasoning ? 
              `<div class="flagged-prompt-meta"><strong>Reasoning:</strong> ${escapeHtml(prompt.analysis.reasoning)}</div>` : ''}
        `;
        
        container.appendChild(promptElem);
    });
}

async function clearLogs() {
    if (!confirm('Are you sure you want to clear all flagged prompts? This cannot be undone.')) {
        return;
    }

    try {
        const response = await fetch('/api/flagged', {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error('Failed to clear logs');
        }
        
        await loadFlaggedPrompts();
    } catch (error) {
        alert(`Error clearing logs: ${error.message}`);
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
