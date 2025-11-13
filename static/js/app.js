// API Base URL
const API_BASE = '';

// State
let currentTab = 'standings';

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    loadStats();
    loadStandings();
    loadMatches();
});

// ==================== Utility Functions ====================

function showLoading() {
    document.getElementById('loadingOverlay').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loadingOverlay').style.display = 'none';
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

async function apiCall(endpoint, method = 'GET', body = null) {
    try {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json'
            }
        };

        if (body) {
            options.body = JSON.stringify(body);
        }

        const response = await fetch(`${API_BASE}${endpoint}`, options);
        const data = await response.json();

        if (!data.success) {
            throw new Error(data.error || 'API request failed');
        }

        return data;
    } catch (error) {
        showToast(error.message, 'error');
        throw error;
    }
}

// ==================== Tab Management ====================

function showTab(tabName) {
    // Update tab buttons
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => tab.classList.remove('active'));
    event.target.classList.add('active');

    // Update tab content
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(content => content.classList.remove('active'));

    const targetTab = document.getElementById(`${tabName}Tab`);
    if (targetTab) {
        targetTab.classList.add('active');
    }

    currentTab = tabName;

    // Load data for the tab
    if (tabName === 'standings') {
        loadStandings();
    } else if (tabName === 'matches') {
        loadMatches();
    } else if (tabName === 'playoffs') {
        loadPlayoffs();
    }
}

// ==================== API Functions ====================

async function initTournament() {
    if (!confirm('This will reset the tournament and all data. Continue?')) {
        return;
    }

    showLoading();
    try {
        const data = await apiCall('/api/init', 'POST');
        showToast(data.message, 'success');
        loadStats();
        loadStandings();
        loadMatches();
        document.getElementById('playoffsContent').innerHTML = '<div class="empty-state"><h3>No playoffs generated yet</h3><p>Complete 8 Swiss rounds first</p></div>';
    } catch (error) {
        console.error('Error initializing tournament:', error);
    } finally {
        hideLoading();
    }
}

async function createPairings() {
    showLoading();
    try {
        const data = await apiCall('/api/pairings/create', 'POST');
        showToast(`Round ${data.round} pairings created: ${data.pairings_created} matches`, 'success');
        loadStats();
        loadMatches();
    } catch (error) {
        console.error('Error creating pairings:', error);
    } finally {
        hideLoading();
    }
}

async function simulateMatches() {
    showLoading();
    try {
        const data = await apiCall('/api/simulate', 'POST');
        showToast(`Simulated ${data.matches_simulated} matches`, 'success');
        loadStats();
        loadStandings();
        loadMatches();
    } catch (error) {
        console.error('Error simulating matches:', error);
    } finally {
        hideLoading();
    }
}

async function generatePlayoffs() {
    showLoading();
    try {
        const data = await apiCall('/api/playoffs/generate', 'POST');
        showToast(data.message, 'success');
        loadPlayoffs();
        showTab('playoffs');
        document.querySelector('[onclick="showTab(\'playoffs\')"]').click();
    } catch (error) {
        console.error('Error generating playoffs:', error);
    } finally {
        hideLoading();
    }
}

async function loadStats() {
    try {
        const data = await apiCall('/api/stats');
        const stats = data.stats;

        document.getElementById('currentRound').textContent = stats.current_round;
        document.getElementById('totalMatches').textContent = stats.total_matches;
        document.getElementById('totalGoals').textContent = stats.total_goals;
        document.getElementById('avgGoals').textContent = stats.avg_goals_per_match;
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

async function loadStandings() {
    try {
        const data = await apiCall('/api/standings');
        const standings = data.standings;

        if (standings.length === 0) {
            document.getElementById('standingsContent').innerHTML = '<div class="empty-state"><h3>No standings yet</h3><p>Initialize tournament first</p></div>';
            return;
        }

        let html = '<table><thead><tr>';
        html += '<th>Pos</th>';
        html += '<th>Team</th>';
        html += '<th>P</th>';
        html += '<th>W</th>';
        html += '<th>D</th>';
        html += '<th>L</th>';
        html += '<th>GF</th>';
        html += '<th>GA</th>';
        html += '<th>GD</th>';
        html += '<th>Pts</th>';
        html += '</tr></thead><tbody>';

        standings.forEach(team => {
            html += `<tr class="team-row" style="border-left-color: ${team.category_color}">`;
            html += `<td class="team-position">${team.position}</td>`;
            html += `<td class="team-name">${team.name}</td>`;
            html += `<td>${team.played}</td>`;
            html += `<td>${team.won}</td>`;
            html += `<td>${team.drawn}</td>`;
            html += `<td>${team.lost}</td>`;
            html += `<td>${team.goals_for}</td>`;
            html += `<td>${team.goals_against}</td>`;
            html += `<td>${team.goal_difference > 0 ? '+' : ''}${team.goal_difference}</td>`;
            html += `<td class="team-stats"><strong>${team.points}</strong></td>`;
            html += '</tr>';
        });

        html += '</tbody></table>';
        document.getElementById('standingsContent').innerHTML = html;
    } catch (error) {
        console.error('Error loading standings:', error);
    }
}

async function loadMatches() {
    try {
        const roundSelector = document.getElementById('roundSelector');
        const selectedRound = roundSelector ? roundSelector.value : '';

        const endpoint = selectedRound ? `/api/pairings?round=${selectedRound}` : '/api/pairings';
        const data = await apiCall(endpoint);
        const pairings = data.pairings;

        if (pairings.length === 0) {
            document.getElementById('matchesContent').innerHTML = '<div class="empty-state"><h3>No matches yet</h3><p>Create pairings first</p></div>';
            return;
        }

        // Group by round
        const rounds = {};
        pairings.forEach(pairing => {
            if (!rounds[pairing.round]) {
                rounds[pairing.round] = [];
            }
            rounds[pairing.round].push(pairing);
        });

        let html = '';
        Object.keys(rounds).sort((a, b) => b - a).forEach(round => {
            html += '<div class="round-group">';
            html += `<div class="round-header">Round ${round}</div>`;

            rounds[round].forEach(match => {
                const simulated = match.simulated === 1;
                const cardClass = simulated ? 'match-card' : 'match-card unsimulated';

                html += `<div class="${cardClass}">`;
                html += '<div class="match-teams">';

                // Team 1
                html += '<div class="match-team">';
                html += `<div class="match-team-name">${match.team1}</div>`;
                html += `<div class="match-ranking">Ranking: ${match.team1_ranking}</div>`;
                html += '</div>';

                // Score
                if (simulated) {
                    html += `<div class="match-score">${match.goals1} - ${match.goals2}</div>`;
                } else {
                    html += '<div class="match-score">- vs -</div>';
                }

                // Team 2
                html += '<div class="match-team">';
                html += `<div class="match-team-name">${match.team2}</div>`;
                html += `<div class="match-ranking">Ranking: ${match.team2_ranking}</div>`;
                html += '</div>';

                html += '</div>';

                // Status
                const statusClass = simulated ? 'match-status' : 'match-status pending';
                const statusText = simulated ? 'Played' : 'Pending';
                html += `<div class="${statusClass}">${statusText}</div>`;

                html += '</div>';
            });

            html += '</div>';
        });

        document.getElementById('matchesContent').innerHTML = html;
    } catch (error) {
        console.error('Error loading matches:', error);
    }
}

async function loadPlayoffs() {
    try {
        const data = await apiCall('/api/playoffs');
        const playoffs = data.playoffs;

        const competitions = [
            { name: 'Champions League', key: 'Champions League', class: 'champions' },
            { name: 'Europa League', key: 'Europa League', class: 'europa' },
            { name: 'Conference League', key: 'Conference League', class: 'conference' }
        ];

        let html = '';
        let hasPlayoffs = false;

        competitions.forEach(comp => {
            const matches = playoffs[comp.key];
            if (matches && matches.length > 0) {
                hasPlayoffs = true;

                html += '<div class="playoffs-competition">';
                html += `<div class="competition-header ${comp.class}">`;
                html += `🏆 ${comp.name} Playoffs`;
                html += '</div>';
                html += '<div class="playoff-matches">';

                matches.forEach(match => {
                    html += '<div class="playoff-match">';

                    // Team 1
                    html += '<div class="playoff-team">';
                    html += `<div class="playoff-position">${match.position1}</div>`;
                    html += '<div class="playoff-team-info">';
                    html += `<div class="playoff-team-name">${match.team1}</div>`;
                    html += `<div class="playoff-team-ranking">Ranking: ${match.team1_ranking}</div>`;
                    html += '</div>';
                    html += '</div>';

                    // VS
                    html += '<div class="playoff-vs">VS</div>';

                    // Team 2
                    html += '<div class="playoff-team">';
                    html += '<div class="playoff-team-info" style="text-align: right;">';
                    html += `<div class="playoff-team-name">${match.team2}</div>`;
                    html += `<div class="playoff-team-ranking">Ranking: ${match.team2_ranking}</div>`;
                    html += '</div>';
                    html += `<div class="playoff-position">${match.position2}</div>`;
                    html += '</div>';

                    html += '</div>';
                });

                html += '</div>';
                html += '</div>';
            }
        });

        if (!hasPlayoffs) {
            html = '<div class="empty-state"><h3>No playoffs generated yet</h3><p>Complete 8 Swiss rounds first</p></div>';
        }

        document.getElementById('playoffsContent').innerHTML = html;
    } catch (error) {
        console.error('Error loading playoffs:', error);
    }
}
