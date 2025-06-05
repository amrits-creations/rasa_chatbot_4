class LoginApp {
    constructor() {
        this.apiEndpoint = 'http://localhost:5000/api';
        this.loginForm = document.getElementById('loginForm');
        this.errorMessage = document.getElementById('errorMessage');

        this.initializeEventListeners();
    }

    initializeEventListeners() {
        this.loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleLogin();
        });
    }

    async handleLogin() {
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value;

        if (!username || !password) {
            this.showError('Please enter both username and password');
            return;
        }

        try {
            const response = await fetch(`${this.apiEndpoint}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password }),
                signal: AbortSignal.timeout(10000)
            });

            const result = await response.json();

            if (result.success) {
                // Store token and user info
                localStorage.setItem('adminToken', result.token);
                localStorage.setItem('adminUser', JSON.stringify(result.user));

                // Redirect to dashboard
                window.location.href = 'dashboard.html';
            } else {
                this.showError(result.message || 'Login failed');
            }

        } catch (error) {
            this.showError('Connection error. Make sure the admin server is running on port 5000.');
        }
    }

    showError(message) {
        this.errorMessage.textContent = message;
        this.errorMessage.style.display = 'block';

        // Hide error after 5 seconds
        setTimeout(() => {
            this.errorMessage.style.display = 'none';
        }, 5000);
    }
}

// Initialize login app
document.addEventListener('DOMContentLoaded', () => {
    new LoginApp();
});

