/**
 * Traveloop Frontend JavaScript
 */

// Global state
const AppState = {
    currentUserId: 1, // Hardcoded for demo/hackathon purposes
    currentTripId: 1
};

// Utility: Show Toast Notification
function showToast(message, type = 'success') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.style.borderLeftColor = type === 'error' ? 'var(--danger)' : 'var(--primary)';
    toast.innerHTML = `<p>${message}</p>`;
    
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'fadeOut 0.3s ease forwards';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Generic API Fetch Wrapper
async function apiCall(endpoint, method = 'GET', body = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json'
        }
    };

    if (body) {
        options.body = JSON.stringify(body);
    }

    try {
        const response = await fetch(endpoint, options);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'API request failed');
        }
        return data;
    } catch (error) {
        showToast(error.message, 'error');
        throw error;
    }
}
