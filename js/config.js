// API Configuration
// Generated from environment variables
// DO NOT EDIT MANUALLY - regenerate with: python generate-config.py

window.API_CONFIG = {
    baseURL: 'http://localhost:8000/api',
    timeout: 30000
};

// Log configuration in development mode
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    console.log('[Config] Backend URL:', 'http://localhost:8000/api');
    console.log('[Config] Timeout:', 30000ms);
}
