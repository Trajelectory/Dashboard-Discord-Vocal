const socket = io();
const channelsGrid = document.getElementById('channelsGrid');
const statusDot = document.getElementById('statusDot');
const statusText = document.getElementById('statusText');
const logsEntries = document.getElementById('logsEntries');

let healthPanelCollapsed = false;
let logsPanelCollapsed = true;
let lastPingTime = Date.now();
let connectionLost = false;

// ===============================
// CONNEXION
// ===============================

socket.on('connect', () => {
    console.log('✅ Connecté au serveur');
    statusDot.className = 'status-dot connected';
    statusText.textContent = 'Connexion en temps réel établie';
    
    socket.emit('get_logs', { limit: 50 });
    
    if (connectionLost) {
        removeAlert();
        showAlert('✅ Connexion rétablie !');
        setTimeout(removeAlert, 3000);
        connectionLost = false;
    }
});

socket.on('disconnect', () => {
    console.log('❌ Déconnecté du serveur');
    statusDot.className = 'status-dot disconnected';
    statusText.textContent = 'Connexion perdue - Reconnexion...';
});

socket.on('voice_update', (data) => {
    console.log('📡 Mise à jour reçue:', data);
    renderChannels(data);
});

// ===============================
// RENDER CHANNELS
// ===============================

function renderChannels(voiceData) {
    channelsGrid.innerHTML = '';
    
    for (const [channelName, channelData] of Object.entries(voiceData)) {
        const channelCard = document.createElement('div');
        channelCard.className = 'channel-card';
        
        const header = document.createElement('div');
        header.className = 'channel-header';
        header.innerHTML = `
            <div class="channel-name">${channelName}</div>
            <div class="member-count">${channelData.count} 👤</div>
        `;
        channelCard.appendChild(header);
        
        if (channelData.members.length > 0) {
            const membersList = document.createElement('ul');
            membersList.className = 'members-list';
            
            channelData.members.forEach(member => {
                const memberItem = document.createElement('li');
                memberItem.className = 'member-item';
                
                let avatarClass = 'avatar-wrapper';
                if (member.stream) {
                    avatarClass += ' live';
                } else if (member.webcam) {
                    avatarClass += ' cam';
                }
                
                let voiceIndicators = '';
                if (member.muted || member.server_muted) {
                    const iconClass = member.server_muted ? 'voice-indicator muted server-action' : 'voice-indicator muted';
                    voiceIndicators += `<span class="${iconClass}" title="${member.server_muted ? 'Muté par le serveur' : 'Micro coupé'}">🔇</span>`;
                }
                if (member.deafened || member.server_deafened) {
                    const iconClass = member.server_deafened ? 'voice-indicator deafened server-action' : 'voice-indicator deafened';
                    voiceIndicators += `<span class="${iconClass}" title="${member.server_deafened ? 'Sourdine serveur' : 'Casque débranché'}">🔕</span>`;
                }
                
                let badges = '';
                if (member.stream || member.webcam) {
                    badges = '<div class="activity-badges">';
                    if (member.stream) {
                        badges += '<span class="activity-badge badge-stream">📡 STREAM</span>';
                    }
                    if (member.webcam) {
                        badges += '<span class="activity-badge badge-webcam">📹 WEBCAM</span>';
                    }
                    badges += '</div>';
                }
                
                memberItem.innerHTML = `
                    <div class="${avatarClass}">
                        <img src="${member.avatar}" alt="${member.name}" class="member-avatar">
                    </div>
                    <div class="member-info">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div class="member-name">${member.name}</div>
                            <div class="voice-indicators">${voiceIndicators}</div>
                        </div>
                        <div class="member-status">
                            <span class="status-indicator status-${member.status}"></span>
                            ${member.status}
                        </div>
                        ${badges}
                    </div>
                `;
                
                membersList.appendChild(memberItem);
            });
            
            channelCard.appendChild(membersList);
        } else {
            const emptyDiv = document.createElement('div');
            emptyDiv.className = 'empty-channel';
            emptyDiv.textContent = 'Aucun membre dans ce salon';
            channelCard.appendChild(emptyDiv);
        }
        
        channelsGrid.appendChild(channelCard);
    }
}

// ===============================
// HEALTH PANEL
// ===============================

function toggleHealthPanel() {
    const panel = document.getElementById('healthPanel');
    const content = document.getElementById('healthContent');
    healthPanelCollapsed = !healthPanelCollapsed;
    
    if (healthPanelCollapsed) {
        panel.classList.add('collapsed');
        content.style.display = 'none';
    } else {
        panel.classList.remove('collapsed');
        content.style.display = 'block';
    }
}

function formatUptime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
}

function formatTime(isoString) {
    if (!isoString) return 'Jamais';
    const date = new Date(isoString);
    const now = new Date();
    const diff = Math.floor((now - date) / 1000);
    
    if (diff < 60) return `${diff}s`;
    if (diff < 3600) return `${Math.floor(diff / 60)}min`;
    return `${Math.floor(diff / 3600)}h`;
}

function showAlert(message) {
    const oldAlert = document.querySelector('.alert-banner');
    if (oldAlert) oldAlert.remove();
    
    const alert = document.createElement('div');
    alert.className = 'alert-banner';
    alert.textContent = message;
    document.body.prepend(alert);
    
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 10000);
}

function removeAlert() {
    const alert = document.querySelector('.alert-banner');
    if (alert) alert.remove();
}

socket.on('health_status', (status) => {
    const statusDotHealth = document.getElementById('overallStatus');
    const statusTextHealth = document.getElementById('overallStatusText');
    
    if (status.status === 'healthy') {
        statusDotHealth.className = 'health-status healthy';
        statusTextHealth.textContent = 'Sain';
        if (connectionLost) {
            removeAlert();
            connectionLost = false;
        }
    } else {
        statusDotHealth.className = 'health-status degraded';
        statusTextHealth.textContent = 'Dégradé';
        if (!connectionLost) {
            showAlert('⚠️ Connexion au bot instable');
            connectionLost = true;
        }
    }
    
    document.getElementById('botStatus').textContent = 
        status.bot.alive ? '✅ En ligne' : '❌ Hors ligne';
    document.getElementById('clientCount').textContent = 
        status.web.connected_clients;
    document.getElementById('uptime').textContent = 
        formatUptime(status.uptime_seconds);
    document.getElementById('lastUpdate').textContent = 
        formatTime(status.bot.last_update);
});

setInterval(() => {
    const pingStart = Date.now();
    socket.emit('ping');
    
    socket.once('pong', () => {
        const ping = Date.now() - pingStart;
        document.getElementById('pingDisplay').textContent = `Ping: ${ping}ms`;
        lastPingTime = Date.now();
    });
    
    setTimeout(() => {
        const timeSinceLastPing = Date.now() - lastPingTime;
        if (timeSinceLastPing > 5000 && !connectionLost) {
            connectionLost = true;
        }
    }, 5000);
}, 5000);

// ===============================
// LOGS PANEL
// ===============================

function toggleLogsPanel() {
    const panel = document.getElementById('logsPanel');
    const content = document.getElementById('logsContent');
    logsPanelCollapsed = !logsPanelCollapsed;
    
    if (logsPanelCollapsed) {
        panel.classList.add('collapsed');
        content.style.display = 'none';
    } else {
        panel.classList.remove('collapsed');
        content.style.display = 'block';
    }
}

function addLogEntry(log) {
    const entry = document.createElement('div');
    entry.className = `log-entry ${log.type}`;
    
    let text = '';
    if (log.type === 'join') {
        text = `<span class="log-time">${log.time_str}</span><span class="log-member">${log.member}</span> <span class="log-action">a rejoint</span> <span class="log-channel">${log.channel}</span>`;
    } else if (log.type === 'leave') {
        text = `<span class="log-time">${log.time_str}</span><span class="log-member">${log.member}</span> <span class="log-action">a quitté</span> <span class="log-channel">${log.channel}</span>`;
    } else if (log.type === 'move') {
        text = `<span class="log-time">${log.time_str}</span><span class="log-member">${log.member}</span> <span class="log-action">est passé de</span> <span class="log-channel">${log.from_channel}</span> <span class="log-action">à</span> <span class="log-channel">${log.to_channel}</span>`;
    }
    
    entry.innerHTML = text;
    logsEntries.prepend(entry);
    
    while (logsEntries.children.length > 50) {
        logsEntries.removeChild(logsEntries.lastChild);
    }
}

function clearLogs() {
    if (confirm('Effacer tout ?')) {
        logsEntries.innerHTML = '';
    }
}

socket.on('activity_log', (log) => {
    console.log('📋 New activity log:', log);
    addLogEntry(log);
});

socket.on('logs_history', (data) => {
    console.log('📋 Logs history received:', data.logs.length);
    data.logs.forEach(log => addLogEntry(log));
});