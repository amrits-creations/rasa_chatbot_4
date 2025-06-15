class UserLoginApp {
    constructor() {
        this.apiEndpoint = 'http://localhost:5000/api';
        this.loginForm = document.getElementById('loginForm');
        this.errorMessage = document.getElementById('errorMessage');
        this.loginBtnText = document.getElementById('loginBtnText');
        this.loginSpinner = document.getElementById('loginSpinner');

        this.initializeEventListeners();
        this.checkExistingSession();
    }

    initializeEventListeners() {
        this.loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleLogin();
        });

        // Enter key handling for better UX
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !this.loginForm.contains(document.activeElement)) {
                document.getElementById('username').focus();
            }
        });
    }

    async checkExistingSession() {
        const token = localStorage.getItem('userToken');
        if (token) {
            try {
                const response = await fetch(`${this.apiEndpoint}/user/verify`, {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    signal: AbortSignal.timeout(5000)
                });

                if (response.ok) {
                    // User is already logged in, redirect to chat
                    window.location.href = 'chat.html';
                } else {
                    // Invalid session, clear storage
                    localStorage.removeItem('userToken');
                    localStorage.removeItem('userInfo');
                }
            } catch (error) {
                // Network error or timeout, proceed with login
                localStorage.removeItem('userToken');
                localStorage.removeItem('userInfo');
            }
        }
    }

    async handleLogin() {
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value;

        if (!username || !password) {
            this.showError('Please enter both username and password');
            return;
        }

        this.setLoadingState(true);

        try {
            const response = await fetch(`${this.apiEndpoint}/user/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password }),
                signal: AbortSignal.timeout(10000)
            });

            const result = await response.json();

            if (result.success) {
                // Store authentication data
                localStorage.setItem('userToken', result.token);
                localStorage.setItem('userInfo', JSON.stringify(result.user));

                // Show success message briefly before redirect
                this.showSuccess('Login successful! Redirecting to chat...');
                
                // Redirect to chat interface
                setTimeout(() => {
                    window.location.href = 'chat.html';
                }, 1500);
            } else {
                this.showError(result.message || 'Login failed');
            }

        } catch (error) {
            if (error.name === 'AbortError') {
                this.showError('Login request timed out. Please try again.');
            } else {
                this.showError('Connection error. Make sure the server is running on port 5000.');
            }
        } finally {
            this.setLoadingState(false);
        }
    }

    setLoadingState(loading) {
        const button = this.loginForm.querySelector('button[type="submit"]');
        button.disabled = loading;
        
        if (loading) {
            this.loginBtnText.style.display = 'none';
            this.loginSpinner.style.display = 'inline-block';
        } else {
            this.loginBtnText.style.display = 'inline';
            this.loginSpinner.style.display = 'none';
        }
    }

    showError(message) {
        this.hideMessages();
        this.errorMessage.textContent = message;
        this.errorMessage.className = 'error-message';
        this.errorMessage.style.display = 'block';

        // Auto-hide after 5 seconds
        setTimeout(() => {
            this.errorMessage.style.display = 'none';
        }, 5000);
    }

    showSuccess(message) {
        this.hideMessages();
        this.errorMessage.textContent = message;
        this.errorMessage.className = 'success-message';
        this.errorMessage.style.display = 'block';
    }

    hideMessages() {
        this.errorMessage.style.display = 'none';
    }
}

// Initialize login app
document.addEventListener('DOMContentLoaded', () => {
    new UserLoginApp();
});

