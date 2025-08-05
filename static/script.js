function sendMessage() {
    let userInput = document.getElementById("user-input").value;
    if (userInput.trim() === "") return;

    let chatBox = document.getElementById("chat-box");
    chatBox.innerHTML += `<div class="message user">${userInput}</div>`;
    document.getElementById("user-input").value = "";

    fetch("/get", {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: userInput })
    })
    .then(res => res.json())
    .then(data => {
        chatBox.innerHTML += `<div class="message bot">${data.response}</div>`;
        chatBox.scrollTop = chatBox.scrollHeight;
    });
}
