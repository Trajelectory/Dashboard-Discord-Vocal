const socket = io();

let currentPeriod = 'today';
let statsData = null;

// ===============================
// CONNEXION
// ===============================

socket.on('connect', () => {
    console.log('✅ Connecté au serveur');
    socket.emit('get_stats', { period: currentPeriod });
});

socket.on('disconnect', () => {
    console.log('❌ Déconnecté du serveur');
});

socket.on('stats_update', (data) => {
    console.log('📊 Stats reçues:', data);
    statsData = data;
    renderStats();
});

// ===============================
// PERIOD TOGGLE
// ===============================

document.querySelectorAll('.period-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.period-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentPeriod = btn.dataset.period;
        socket.emit('get_stats', { period: currentPeriod });
    });
});

// ===============================
// RENDER FUNCTIONS
// ===============================

function renderStats() {
    if (!statsData) return;
    
    renderCurrentSessions(statsData.current_sessions);
    renderRecords(statsData.records);
    renderLeaderboard(statsData.top_users);
    renderDetailedStats(statsData.all_stats);
}

function renderCurrentSessions(sessions) {
    const container = document.getElementById('currentSessions');
    
    if (!sessions || Object.keys(sessions).length === 0) {
        container.innerHTML = '<div class="empty-state">Aucune session active</div>';
        return;
    }
    
    container.innerHTML = '';
    
    for (const [member, session] of Object.entries(sessions)) {
        const card = document.createElement('div');
        card.className = 'session-card';
        
        const duration = formatDuration(session.duration);
        
        card.innerHTML = `
            <div class="session-live">🔴 EN DIRECT</div>
            <div class="session-member">${member}</div>
            <div class="session-channel">📍 ${session.channel}</div>
            <div class="session-duration">${duration}</div>
        `;
        
        container.appendChild(card);
    }
}

function renderRecords(records) {
    if (!records) return;
    
    // Record aujourd'hui
    if (records.longest_session_today && records.longest_session_today.member) {
        document.getElementById('recordToday').textContent = records.longest_session_today.member;
        document.getElementById('recordTodayTime').textContent = formatDuration(records.longest_session_today.duration);
    } else {
        document.getElementById('recordToday').textContent = '-';
        document.getElementById('recordTodayTime').textContent = '-';
    }
    
    // Record semaine
    if (records.longest_session_week && records.longest_session_week.member) {
        document.getElementById('recordWeek').textContent = records.longest_session_week.member;
        document.getElementById('recordWeekTime').textContent = formatDuration(records.longest_session_week.duration);
    } else {
        document.getElementById('recordWeek').textContent = '-';
        document.getElementById('recordWeekTime').textContent = '-';
    }
    
    // Record mois
    if (records.longest_session_month && records.longest_session_month.member) {
        document.getElementById('recordMonth').textContent = records.longest_session_month.member;
        document.getElementById('recordMonthTime').textContent = formatDuration(records.longest_session_month.duration);
    } else {
        document.getElementById('recordMonth').textContent = '-';
        document.getElementById('recordMonthTime').textContent = '-';
    }
    
    // Record all-time
    if (records.longest_session_ever && records.longest_session_ever.member) {
        document.getElementById('recordEver').textContent = records.longest_session_ever.member;
        document.getElementById('recordEverTime').textContent = formatDuration(records.longest_session_ever.duration);
    } else {
        document.getElementById('recordEver').textContent = '-';
        document.getElementById('recordEverTime').textContent = '-';
    }
}

function renderLeaderboard(topUsers) {
    const container = document.getElementById('leaderboard');
    
    if (!topUsers || topUsers.length === 0) {
        container.innerHTML = '<div class="empty-state">Aucune donnée disponible</div>';
        return;
    }
    
    container.innerHTML = '';
    
    topUsers.forEach((user, index) => {
        const item = document.createElement('div');
        item.className = 'leaderboard-item';
        
        let rankEmoji = '';
        if (index === 0) rankEmoji = '🥇';
        else if (index === 1) rankEmoji = '🥈';
        else if (index === 2) rankEmoji = '🥉';
        
        item.innerHTML = `
            <div class="leaderboard-rank">${rankEmoji} #${index + 1}</div>
            <div class="leaderboard-member">${user.member}</div>
            <div class="leaderboard-time">${formatDuration(user.total_time)}</div>
        `;
        
        container.appendChild(item);
    });
}

function renderDetailedStats(allStats) {
    const container = document.getElementById('detailedStats');
    
    if (!allStats || Object.keys(allStats).length === 0) {
        container.innerHTML = '<div class="empty-state">Aucune donnée disponible</div>';
        return;
    }
    
    container.innerHTML = '';
    
    // Trier par temps total décroissant
    const sortedStats = Object.entries(allStats).sort((a, b) => {
        return b[1].total_time - a[1].total_time;
    });
    
    sortedStats.forEach(([member, stats]) => {
        if (stats.total_time === 0) return;
        
        const card = document.createElement('div');
        card.className = 'user-stat-card';
        
        card.innerHTML = `
            <div class="user-stat-name">${member}</div>
            <div class="user-stat-row">
                <span class="user-stat-label">⏱️ Temps total</span>
                <span class="user-stat-value">${formatDuration(stats.total_time)}</span>
            </div>
            <div class="user-stat-row">
                <span class="user-stat-label">🔢 Sessions</span>
                <span class="user-stat-value">${stats.session_count}</span>
            </div>
            <div class="user-stat-row">
                <span class="user-stat-label">⏳ Moyenne/session</span>
                <span class="user-stat-value">${formatDuration(stats.average_session)}</span>
            </div>
            <div class="user-stat-row">
                <span class="user-stat-label">📍 Canaux visités</span>
                <span class="user-stat-value">${stats.channels_visited.length}</span>
            </div>
        `;
        
        container.appendChild(card);
    });
}

// ===============================
// HELPER FUNCTIONS
// ===============================

function formatDuration(seconds) {
    if (!seconds || seconds === 0) return '0m';
    
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    if (hours > 0) {
        return `${hours}h ${minutes}m`;
    } else if (minutes > 0) {
        return `${minutes}m ${secs}s`;
    } else {
        return `${secs}s`;
    }
}

// ===============================
// AUTO-REFRESH
// ===============================

// Rafraîchir toutes les 5 secondes
setInterval(() => {
    socket.emit('get_stats', { period: currentPeriod });
}, 5000);