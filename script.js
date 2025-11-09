const chatBox = document.getElementById("chat-box");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");

function addMessageToChat(message, isUser = false) {
    const messageClass = isUser ? "user-message" : "bot-message";
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("chat-message", messageClass);
    messageDiv.innerText = message;
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

async function handleUserInput() {
    const userMessage = userInput.value;
    userInput.value = "";
    addMessageToChat(userMessage, true);

    // Call the Flask API for generating response
    const response = await fetch("http://127.0.0.1:5000/get_response", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ dialog: [userMessage] }),
    });

    if (response.ok) {
        const responseData = await response.json();
        const botResponse = responseData.generated_response;
        const emotion = responseData.emotion;
        const songPaths = responseData.song_paths;

        addMessageToChat(botResponse);

        // Display song recommendations
        displaySongRecommendations(songPaths);
    }
}

function displaySongRecommendations(songPaths) {
    const audioContainer = document.getElementById("audio-container");
    audioContainer.style.display = "block";

    const audioPlayer = document.createElement("div");
    audioPlayer.classList.add("audio-player");

    // Clear previous recommendations
    audioContainer.innerHTML = "";

    // Loop through song paths and create audio elements for each song
    songPaths.forEach(songPath => {
        const audio = document.createElement("audio");
        audio.src = songPath;
        audio.controls = true;
        audioPlayer.appendChild(audio);
    });

    audioContainer.appendChild(audioPlayer);
}

sendBtn.addEventListener("click", handleUserInput);

