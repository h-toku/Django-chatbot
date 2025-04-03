document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("chat-form").addEventListener("submit", function (event) {
        event.preventDefault();  // フォームのデフォルトの送信を防ぐ
        sendMessage();
    });
});

function getCsrfToken() {
    let cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        let cookie = cookies[i].trim();
        if (cookie.startsWith("csrftoken=")) {
            return cookie.split("=")[1];
        }
    }
    return "";
}

function sendMessage() {
    let userInput = document.getElementById("user-input").value;
    console.log("Sending user input:", userInput);  // 送信する入力を確認

    appendMessage(userInput, "user");
    document.getElementById("user-input").value = "";  // 入力フィールドをクリア

    fetch("/chat/", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": getCsrfToken()  // CSRFトークンを追加
        },
        body: "user_input=" + encodeURIComponent(userInput),
    })
        .then(response => response.json())
        .then(data => {
            console.log("Received response:", data);  // 受け取ったレスポンスを確認
            appendMessage(data.response, "bot");
        })
        .catch(error => {
            console.error("Error:", error);
        });
}

// メッセージを表示する関数
function appendMessage(message, sender) {
    const chatBox = document.getElementById("chat-box");  // チャットボックスの取得
    const messageDiv = document.createElement("div");  // メッセージ用のdivを作成
    messageDiv.classList.add("message", sender === "user" ? "user-message" : "bot-message");  // 送信者によってクラスを変更
    messageDiv.textContent = message;  // メッセージ内容を設定
    chatBox.appendChild(messageDiv);  // チャットボックスに追加

    // チャットボックスをスクロールして最新のメッセージが見えるようにする
    chatBox.scrollTop = chatBox.scrollHeight;
}

