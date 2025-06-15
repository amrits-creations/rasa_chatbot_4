class ChatApp {
    constructor() {
        this.token = localStorage.getItem('userToken');
        this.userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}');
        
        // Check authentication first
        if (!this.token || !this.userInfo.user_id) {
            this.redirectToLogin();
            return;
        }

        // Initialize UI elements
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.chatForm = document.getElementById('chatForm');
        this.clearChatBtn = document.getElementById('clearChatBtn');
        this.serverStatus = document.getElementById('serverStatus');
        this.logoutBtn = document.getElementById('logoutBtn');
        this.userDisplay = document.getElementById('userDisplay');

        this.rasaEndpoint = 'http://localhost:5006/webhooks/rest/webhook';
        this.statusEndpoint = 'http://localhost:5006/status';
        this.authEndpoint = 'http://localhost:5000/api';

        this.initializeEventListeners();
        this.updateUserDisplay();
        this.checkServerStatus();
        this.verifySession();

        // Check server status every 30 seconds
        setInterval(() => this.checkServerStatus(), 30000);
        // Verify session every 5 minutes
        setInterval(() => this.verifySession(), 300000);
    }

    redirectToLogin() {
        window.location.href = 'login.html';
    }

    updateUserDisplay() {
        if (this.userDisplay) {
            this.userDisplay.textContent = `Welcome, ${this.userInfo.username}`;
        }
    }

    async verifySession() {
        try {
            const response = await fetch(`${this.authEndpoint}/user/verify`, {
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                },
                signal: AbortSignal.timeout(5000)
            });

            if (!response.ok) {
                // Session invalid, logout
                this.logout();
            }
        } catch (error) {
            // Network error, don't auto-logout but show warning
            console.warn('Session verification failed:', error);
        }
    }

    async logout() {
        try {
            await fetch(`${this.authEndpoint}/user/logout`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                }
            });
        } catch (error) {
            // Ignore logout errors
        } finally {
            localStorage.removeItem('userToken');
            localStorage.removeItem('userInfo');
            this.redirectToLogin();
        }
    }

    initializeEventListeners() {
        // Form submission
        this.chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendMessage();
        });

        // Clear chat button
        this.clearChatBtn.addEventListener('click', () => {
            this.clearChat();
        });

        // Logout button
        if (this.logoutBtn) {
            this.logoutBtn.addEventListener('click', () => {
                this.logout();
            });
        }

        // Enter key handling
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;

        // Display user message
        this.addMessage(message, 'user');

        // Clear input and disable send button
        this.messageInput.value = '';
        this.setSendButtonState(false);

        try {
            const response = await fetch(this.rasaEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    sender: `user_${this.userInfo.user_id}`, // Include user ID for tracking
                    message: message
                }),
                signal: AbortSignal.timeout(10000)
            });

            if (response.ok) {
                const botMessages = await response.json();

                if (botMessages && botMessages.length > 0) {
                    botMessages.forEach(msg => {
                        if (msg.text) {
                            this.addMessage(msg.text, 'assistant');
                        }
                    });
                } else {
                    this.addMessage('I received your message but have no response.', 'assistant');
                }
            } else {
                this.addMessage(`❌ Server error: ${response.status}`, 'assistant error-message');
            }

        } catch (error) {
            if (error.name === 'AbortError') {
                this.addMessage('❌ Request timed out. Please try again.', 'assistant error-message');
            } else if (error.name === 'TypeError' && error.message.includes('fetch')) {
                this.addMessage('❌ Cannot connect to chatbot. Make sure Rasa is running on port 5006.', 'assistant error-message');
            } else {
                this.addMessage(`❌ Error: ${error.message}`, 'assistant error-message');
            }
        } finally {
            this.setSendButtonState(true);
            this.messageInput.focus();
        }
    }

    addMessage(text, sender, extraClass = '') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender} ${extraClass}`.trim();

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = text;

        messageDiv.appendChild(contentDiv);
        this.chatMessages.appendChild(messageDiv);

        // Scroll to bottom
        this.scrollToBottom();
    }

    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    setSendButtonState(enabled) {
        this.sendButton.disabled = !enabled;
        this.sendButton.textContent = enabled ? 'Send' : 'Sending...';
    }

    clearChat() {
        // Remove all messages except keep the initial greeting
        this.chatMessages.innerHTML = `
            <div class="message assistant">
                <div class="message-content">
                    Hello ${this.userInfo.username}! How can I help you today? I can assist with order status, product info, store hours, returns, and contact information.
                </div>
            </div>
        `;
        this.messageInput.focus();
    }

    async checkServerStatus() {
        const statusDot = this.serverStatus.querySelector('.status-dot');
        const statusText = this.serverStatus.querySelector('.status-text');

        try {
            const response = await fetch(this.statusEndpoint, {
                method: 'GET',
                signal: AbortSignal.timeout(3000)
            });

            if (response.ok) {
                statusDot.className = 'status-dot online';
                statusText.textContent = '✅ Rasa Server Online';
            } else {
                statusDot.className = 'status-dot offline';
                statusText.textContent = '❌ Rasa Server Error';
            }
        } catch (error) {
            statusDot.className = 'status-dot offline';
            statusText.textContent = '❌ Rasa Server Offline';
        }
    }
}

// Initialize the chat app when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ChatApp();
});
