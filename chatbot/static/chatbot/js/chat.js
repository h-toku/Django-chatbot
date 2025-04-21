// チャットアプリケーションのメインクラス
class ChatApp {
    constructor() {
        this.elements = {
            chatBox: null,
            chatForm: null,
            userInput: null,
            sendButton: null,
            typingIndicator: null
        };
        this.history = [];
        this.initialize();
    }

    initialize() {
        this.getElements();
        this.setupEventListeners();
        this.loadHistory();
        this.renderHistory();
    }

    getElements() {
        this.elements.chatBox = document.getElementById('chatBox');
        this.elements.chatForm = document.getElementById('chatForm');
        this.elements.userInput = document.getElementById('userInput');
        this.elements.sendButton = document.getElementById('sendButton');
        this.elements.typingIndicator = document.getElementById('typingIndicator');
    }

    setupEventListeners() {
        if (this.elements.chatForm) {
            this.elements.chatForm.addEventListener('submit', (e) => this.handleSubmit(e));
        }
    }

    loadHistory() {
        try {
            if (window.chatAppConfig && window.chatAppConfig.chatHistory) {
                this.history = window.chatAppConfig.chatHistory;
            }
        } catch (e) {
            console.error('チャット履歴の読み込みに失敗しました:', e);
            this.history = [];
        }
    }

    renderHistory() {
        if (!this.elements.chatBox) return;
        
        this.elements.chatBox.innerHTML = '';
        if (Array.isArray(this.history)) {
            this.history.forEach(message => {
                if (message && message.text && message.role) {
                    this.appendMessage(message.text, message.role);
                }
            });
        }
        this.scrollToBottom();
    }

    async handleSubmit(e) {
        e.preventDefault();
        if (!this.elements.userInput) return;

        const message = this.elements.userInput.value.trim();
        if (!message) return;

        this.disableSendButton();
        this.appendMessage(message, 'user');
        this.elements.userInput.value = '';
        this.showTypingIndicator();

        try {
            const response = await this.sendMessage(message);
            const data = await response.json();
            
            this.hideTypingIndicator();
            this.appendMessage(data.response, 'ai');
            
            this.history.push({role: 'user', text: message});
            this.history.push({role: 'ai', text: data.response});
        } catch (error) {
            console.error('Error:', error);
            this.hideTypingIndicator();
            this.appendMessage('エラーが発生しました。もう一度お試しください。', 'ai');
        } finally {
            this.enableSendButton();
        }
    }

    async sendMessage(message) {
        const response = await fetch('/chat/api/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': this.getCookie('csrftoken')
            },
            body: `user_input=${encodeURIComponent(message)}`
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        return response;
    }

    appendMessage(text, role) {
        if (!this.elements.chatBox) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role === 'user' ? 'user-message' : 'ai-message'}`;
        messageDiv.innerHTML = `<div class="message-content">${text}</div>`;
        this.elements.chatBox.appendChild(messageDiv);
        this.scrollToBottom();
    }

    showTypingIndicator() {
        if (this.elements.typingIndicator) {
            this.elements.typingIndicator.style.display = 'flex';
            this.scrollToBottom();
        }
    }

    hideTypingIndicator() {
        if (this.elements.typingIndicator) {
            this.elements.typingIndicator.style.display = 'none';
        }
    }

    scrollToBottom() {
        if (this.elements.chatBox) {
            this.elements.chatBox.scrollTop = this.elements.chatBox.scrollHeight;
        }
    }

    disableSendButton() {
        if (this.elements.sendButton) {
            this.elements.sendButton.disabled = true;
        }
    }

    enableSendButton() {
        if (this.elements.sendButton) {
            this.elements.sendButton.disabled = false;
        }
    }

    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}

// DOMの読み込み完了時にインスタンスを作成
document.addEventListener('DOMContentLoaded', () => {
    window.chatApp = new ChatApp();
}); 