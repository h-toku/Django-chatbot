document.addEventListener("DOMContentLoaded", function () {
    // フォームの送信イベントリスナーを追加
    const form = document.getElementById("chat-form");
    if (!form.hasAttribute('data-listener-added')) {  // リスナーが追加されていなければ
        form.addEventListener("submit", function (event) {
            event.preventDefault();  // フォームのデフォルトの送信を防ぐ
            sendMessage();  // メッセージ送信
        });
        form.setAttribute('data-listener-added', 'true');  // リスナーを追加したことをマーク
    }

    console.log("Event listener added to form.");

    // 履歴の描画
    renderHistory();  // 履歴の描画関数を呼び出し
});

// CSRFトークンを取得する関数
function getCsrfToken() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    console.log("CSRF Token:", csrfToken);
    return csrfToken;
}

// メッセージ送信の関数
function sendMessage() {
    const sendButton = document.getElementById("send-button");
    sendButton.disabled = true;  // 送信ボタンを無効化
    console.log("Send button disabled.");
    
    const userInputElement = document.getElementById("user-input");
    const userInput = userInputElement.value.trim();
    console.log("User input:", userInput);
    
    if (userInput) {
        appendMessage(userInput, "user");
        userInputElement.value = "";  // 入力フィールドを空にする

        const csrfToken = getCsrfToken();

        console.log("Sending message...");
        fetch("/chat/api/chat/", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": csrfToken
            },
            body: "user_input=" + encodeURIComponent(userInput)
        })
        .then(response => response.json())
        .then(data => {
            if (data && data.response) {
                console.log("Response data:", data.response);
                appendMessage(data.response, "bot");
            } else {
                console.error("No response data received.");
                appendMessage("AIからの応答がありませんでした。", "bot");
            }
        })
        .catch(error => {
            console.error("Error during fetch:", error);
            appendMessage("通信エラーが発生しました。", "bot");
        })
        .finally(() => {
            sendButton.disabled = false;  // 送信ボタンを再度有効化
        });

        console.log("Message sent to server.");
    } else {
        console.log("User input is empty, message not sent.");
        sendButton.disabled = false;
    }
}

// メッセージをチャットボックスに追加する関数
function appendMessage(message, sender) {
    const chatBox = document.getElementById("chat-box");

    const messageElement = document.createElement("div");
    messageElement.classList.add("message");
    
    if (sender === "user") {
        messageElement.classList.add("user-message");
    } else {
        messageElement.classList.add("bot-message");
    }

    messageElement.innerText = message;
    chatBox.appendChild(messageElement);
}

// ページ初期表示時に履歴を描画する関数
function renderHistory() {
    if (typeof chatHistory === 'undefined') {
        console.warn("chatHistory is not defined.");
        return;
    }

    chatHistory.forEach(msg => {
        const sender = msg.role === 'user' ? 'user' : 'bot';
        appendMessage(msg.text, sender);
    });
}
