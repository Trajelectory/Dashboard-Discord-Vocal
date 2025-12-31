async function tryEndpoint(endpoint, responseId) {
    const responseDiv = document.getElementById(responseId);
    responseDiv.style.display = 'block';
    responseDiv.textContent = 'Chargement...';
    
    try {
        const response = await fetch(endpoint);
        const data = await response.json();
        responseDiv.textContent = JSON.stringify(data, null, 2);
        responseDiv.style.background = '#f0f9ff';
        responseDiv.style.borderColor = '#bfdbfe';
    } catch (error) {
        responseDiv.textContent = 'Erreur: ' + error.message;
        responseDiv.style.background = '#fee2e2';
        responseDiv.style.borderColor = '#fca5a5';
    }
}