class ChatApp {
    constructor() {
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.chatForm = document.getElementById('chatForm');
        this.clearChatBtn = document.getElementById('clearChatBtn');
        this.serverStatus = document.getElementById('serverStatus');
        
        this.rasaEndpoint = 'http://localhost:5006/webhooks/rest/webhook';
        this.statusEndpoint = 'http://localhost:5006/status';
        
        this.initializeEventListeners();
        this.checkServerStatus();
        
        // Check server status every 30 seconds
        setInterval(() => this.checkServerStatus(), 30000);
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
                    sender: 'html_user',
                    message: message
                }),
                signal: AbortSignal.timeout(10000) // 10 second timeout
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
                    Hello! How can I help you today? I can assist with order status, product info, store hours, returns, and contact information.
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
                signal: AbortSignal.timeout(3000) // 3 second timeout
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

