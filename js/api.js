// API Service for connecting frontend with backend
// Configuration is loaded from window.API_CONFIG (defined in index.html)
const API_BASE_URL = window.API_CONFIG?.baseURL || 'http://localhost:8000/api';
const API_TIMEOUT = window.API_CONFIG?.timeout || 30000;

// Store auth token in localStorage
class APIService {
    constructor() {
        this.token = localStorage.getItem('authToken') || null;
        this.baseURL = API_BASE_URL;
        this.timeout = API_TIMEOUT;
        this.debug = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    }

    // Set auth token
    setToken(token) {
        this.token = token;
        localStorage.setItem('authToken', token);
    }

    // Get auth token
    getToken() {
        return this.token;
    }

    // Clear auth token (logout)
    clearToken() {
        this.token = null;
        localStorage.removeItem('authToken');
    }

    // Generic fetch wrapper with timeout and improved error handling
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        // Add auth token if available
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        // Add timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);

        if (this.debug) {
            console.log(`[API] ${options.method || 'GET'} ${endpoint}`, options.body ? JSON.parse(options.body) : '');
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers,
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            // Try to parse JSON response
            let data = {};
            try {
                data = await response.json();
            } catch {
                // If JSON parsing fails, create error message from status
                data = { detail: `HTTP ${response.status}: ${response.statusText}` };
            }

            if (!response.ok) {
                // Handle different error structures from backend
                const errorMessage = data.detail || data.message || data.error ||
                    (data.fields ? 'Validation error - check form inputs' : 'API Error');

                if (this.debug) {
                    console.error(`[API] Error ${response.status}:`, data);
                }

                throw {
                    status: response.status,
                    message: errorMessage,
                    data
                };
            }

            if (this.debug) {
                console.log(`[API] Success:`, data);
            }

            return { success: true, data, status: response.status };
        } catch (error) {
            clearTimeout(timeoutId);

            // Handle timeout errors
            if (error.name === 'AbortError') {
                console.error('[API] Request timeout');
                return {
                    success: false,
                    error: 'Request timeout - server not responding',
                    status: 0,
                    data: {}
                };
            }

            // Handle network errors
            if (!error.status) {
                console.error('[API] Network error:', error);
                return {
                    success: false,
                    error: 'Network error - cannot connect to server',
                    status: 0,
                    data: {}
                };
            }

            // Handle API errors
            console.error('[API] Error:', error);
            return {
                success: false,
                error: error.message || 'Unknown error',
                status: error.status || 0,
                data: error.data || {}
            };
        }
    }

    // ========== AUTHENTICATION ==========
    async login(username, password) {
        return this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });
    }

    async getCurrentUser() {
        return this.request('/auth/me', {
            method: 'GET'
        });
    }

    // ========== EVENTS ==========
    async getEvents(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const endpoint = queryString ? `/events?${queryString}` : '/events';
        return this.request(endpoint, {
            method: 'GET'
        });
    }

    async getEvent(eventId) {
        return this.request(`/events/${eventId}`, {
            method: 'GET'
        });
    }

    async createEvent(eventData) {
        return this.request('/events', {
            method: 'POST',
            body: JSON.stringify(eventData)
        });
    }

    async updateEvent(eventId, eventData) {
        return this.request(`/events/${eventId}`, {
            method: 'PUT',
            body: JSON.stringify(eventData)
        });
    }

    async deleteEvent(eventId) {
        return this.request(`/events/${eventId}`, {
            method: 'DELETE'
        });
    }

    // ========== REGISTRATIONS ==========
    async registerForEvent(eventId, operativeName, moodleId) {
        return this.request('/registrations', {
            method: 'POST',
            body: JSON.stringify({
                event_id: eventId,
                operative_name: operativeName,
                moodle_id: moodleId
            })
        });
    }

    async getRegistrations(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const endpoint = queryString ? `/registrations?${queryString}` : '/registrations';
        return this.request(endpoint, {
            method: 'GET'
        });
    }

    async exportRegistrations(eventId = null) {
        const endpoint = eventId
            ? `/registrations?event_id=${eventId}&export=csv`
            : '/registrations?export=csv';
        return this.request(endpoint, {
            method: 'GET'
        });
    }

    // ========== RESOURCES ==========
    async getResources(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const endpoint = queryString ? `/resources?${queryString}` : '/resources';
        return this.request(endpoint, {
            method: 'GET'
        });
    }

    async getResource(resourceId) {
        return this.request(`/resources/${resourceId}`, {
            method: 'GET'
        });
    }

    async uploadResource(title, level, file) {
        const formData = new FormData();
        formData.append('title', title);
        formData.append('level', level);
        formData.append('file', file);

        const url = `${this.baseURL}/resources`;
        const headers = {};

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers,
                body: formData
            });

            const data = await response.json().catch(() => ({}));

            if (!response.ok) {
                throw {
                    status: response.status,
                    message: data.detail || 'Upload failed',
                    data
                };
            }

            return { success: true, data, status: response.status };
        } catch (error) {
            return {
                success: false,
                error: error.message || 'Upload error',
                status: error.status || 0,
                data: error.data || {}
            };
        }
    }

    async downloadResource(resourceId) {
        const url = `${this.baseURL}/resources/${resourceId}/download`;
        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error('Download failed');

            // Get filename from Content-Disposition header
            const disposition = response.headers.get('Content-Disposition');
            let filename = `resource-${resourceId}.pdf`;
            if (disposition) {
                const filenameMatch = disposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
                if (filenameMatch && filenameMatch[1]) {
                    filename = filenameMatch[1].replace(/['"]/g, '');
                }
            }

            const blob = await response.blob();
            const link = document.createElement('a');
            link.href = window.URL.createObjectURL(blob);
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(link.href);  // Clean up
            return { success: true };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    async deleteResource(resourceId) {
        return this.request(`/resources/${resourceId}`, {
            method: 'DELETE'
        });
    }
}

// Create global instance
const apiService = new APIService();
