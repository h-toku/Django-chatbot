// グローバル変数の定義
let chatHistory = [];

// DOMContentLoadedイベントリスナー
document.addEventListener("DOMContentLoaded", function () {
    // チャット履歴の初期化
    initializeChatHistory();
    
    // フォームの送信イベントリスナーを追加
    const form = document.getElementById("chat-form");
    form.addEventListener("submit", function (event) {
        event.preventDefault();
        handleMessageSubmit();
    });
});

// チャット履歴の初期化
function initializeChatHistory() {
    const chatHistoryElement = document.getElementById("chat-history");
    if (chatHistoryElement) {
        try {
            chatHistory = JSON.parse(chatHistoryElement.textContent);
            renderHistory();
        } catch (error) {
            console.error("Error parsing chat history:", error);
        }
    }
}

// CSRFトークンを取得する関数
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

// メッセージ送信の処理
function handleMessageSubmit() {
    const userInputElement = document.getElementById("user-input");
    const userInput = userInputElement.value.trim();
    
    if (!userInput) return;

    // 送信ボタンを無効化
    const sendButton = document.getElementById("send-button");
    sendButton.disabled = true;

    // ユーザーメッセージを表示
    displayUserMessage(userInput);
    userInputElement.value = "";

    // 入力中表示を追加
    displayTypingIndicator();

    // サーバーにリクエストを送信
    sendRequestToServer(userInput)
        .then(response => {
            removeTypingIndicator();
            if (response && response.response) {
                displayBotMessage(response.response);
            } else {
                displayBotMessage("AIからの応答がありませんでした。");
            }
        })
        .catch(error => {
            removeTypingIndicator();
            displayBotMessage("通信エラーが発生しました。");
        })
        .finally(() => {
            sendButton.disabled = false;
        });
}

// サーバーにリクエストを送信
function sendRequestToServer(userInput) {
    return fetch("/chat/api/chat/", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": getCsrfToken()
        },
        body: "user_input=" + encodeURIComponent(userInput)
    }).then(response => response.json());
}

// ユーザーメッセージを表示
function displayUserMessage(message) {
    const messageElement = createMessageElement(message, "user-message");
    document.getElementById("chat-box").appendChild(messageElement);
    scrollToBottom();
}

// ボットメッセージを表示
function displayBotMessage(message) {
    const messageElement = createMessageElement(message, "bot-message");
    document.getElementById("chat-box").appendChild(messageElement);
    scrollToBottom();
}

// 入力中表示を追加
function displayTypingIndicator() {
    const typingElement = createMessageElement("入力中...", "bot-message");
    typingElement.id = "typing-indicator";
    document.getElementById("chat-box").appendChild(typingElement);
    scrollToBottom();
}

// 入力中表示を削除
function removeTypingIndicator() {
    const typingIndicator = document.getElementById("typing-indicator");
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// メッセージ要素を作成
function createMessageElement(text, className) {
    const element = document.createElement("div");
    element.classList.add("message", className);
    element.innerText = text;
    return element;
}

// チャットボックスを最下部にスクロール
function scrollToBottom() {
    const chatBox = document.getElementById("chat-box");
    chatBox.scrollTop = chatBox.scrollHeight;
}

// 履歴を描画
function renderHistory() {
    if (!Array.isArray(chatHistory)) return;

    chatHistory.forEach(msg => {
        const className = msg.role === 'user' ? 'user-message' : 'bot-message';
        const messageElement = createMessageElement(msg.text, className);
        document.getElementById("chat-box").appendChild(messageElement);
    });
    scrollToBottom();
}
