document.addEventListener("DOMContentLoaded", () => {
  // Elementos del DOM
  const chatMessages = document.getElementById("chat-messages")
  const messageInput = document.getElementById("message-input")
  const sendButton = document.getElementById("send-button")
  const sttButton = document.getElementById("stt-button")
  const themeToggle = document.querySelector(".theme-toggle")
  const statusElement = document.querySelector(".status")
  const emotionElement = document.querySelector(".emotion")

  // Estado
  let darkMode = true
  let isListening = false
  let recognition = null

  // Emojis y kaomojis para usar en los mensajes
  const kaomojis = [
    "(◕‿◕)", "(✿◠‿◠)", "(◕ᴗ◕✿)", "ʕ•ᴥ•ʔ", "(｡♥‿♥｡)",
    "(づ｡◕‿‿◕｡)づ", "(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧", "(≧◡≦)", "(◠‿◠✿)",
    "ヽ(・∀・)ﾉ", "(◕‿◕✿)", "(◠﹏◠)", "(✿ ♥‿♥)", "ヾ(≧▽≦*)o"
  ]

  const emojis = [
    "✨", "💖", "🌸", "😊", "🎀", "💫", "🌟", "💕", "🌈", "🍰",
    "🌷", "🦄", "🌹", "🎵", "🎶", "🌺", "🍭", "🧁", "🍬", "🎊"
  ]

  const emotions = [
    "Feliz", "Curiosa", "Emocionada", "Pensativa", "Sorprendida",
    "Tímida", "Entusiasta", "Soñadora", "Juguetona", "Inspirada"
  ]

  if ("webkitSpeechRecognition" in window || "SpeechRecognition" in window) {
    recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)()
    recognition.lang = "es-ES"
    recognition.continuous = false
    recognition.interimResults = false

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript
      messageInput.value = transcript
      isListening = false
      sttButton.textContent = "🎤"
    }

    recognition.onend = () => {
      isListening = false
      sttButton.textContent = "🎤"
    }
  }

  function toggleTheme() {
    darkMode = !darkMode
    document.body.classList.toggle("dark-mode", darkMode)
    document.body.classList.toggle("light-mode", !darkMode)
    themeToggle.textContent = darkMode ? "🌙" : "☀️"
  }

  function addMessage(text, isUser) {
    const messageElement = document.createElement("div")
    messageElement.classList.add("message")
    messageElement.classList.add(isUser ? "user-message" : "bot-message")

    if (!isUser) {
      const randomEmoji = emojis[Math.floor(Math.random() * emojis.length)]
      const randomKaomoji = kaomojis[Math.floor(Math.random() * kaomojis.length)]
      text = `${randomEmoji} ${text} ${randomKaomoji}`
    }

    messageElement.textContent = text
    chatMessages.appendChild(messageElement)
    chatMessages.scrollTop = chatMessages.scrollHeight
  }

  function addCuteStyle(text) {
    const randomEmoji = emojis[Math.floor(Math.random() * emojis.length)]
    const randomKaomoji = kaomojis[Math.floor(Math.random() * kaomojis.length)]
    return `${randomEmoji} ${text} ${randomKaomoji}`
  }

  async function sendMessageToBackend(message) {
    try {
      updateStatus("Pensando")
      updateEmotion("Curiosa")

      const response = await fetch("http://localhost:3000/akemi/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ message })
      });

      if (!response.ok) throw new Error("Respuesta inválida del servidor");
      const data = await response.json();
      const akemiMessage = data.response || "...";
      addMessage(addCuteStyle(akemiMessage), false);

      updateStatus("En línea")
      const randomEmotion = emotions[Math.floor(Math.random() * emotions.length)]
      updateEmotion(randomEmotion)

    } catch (error) {
      console.error("🔥 Error al enviar mensaje:", error)
      updateStatus("Error")
      updateEmotion("Confundida")
      addMessage("Lo siento... tuve un error interno. (；￣Д￣)", false)
    }
  }

  async function getMessagesFromBackend() {
    try {
      const response = await fetch("http://localhost:3000/akemi/welcome")
      if (!response.ok) throw new Error("No se pudo conectar al servidor")
      const data = await response.json();
      return data.messages || ["Akemi no pudo decir hola..."];
    } catch (error) {
      console.error("Error al obtener mensajes:", error);
      return ["Lo siento... no pude conectarme al servidor (；￣Д￣)"];
    }
  }

  function updateStatus(status) {
    statusElement.textContent = status
    statusElement.classList.add("status-update")
    setTimeout(() => {
      statusElement.classList.remove("status-update")
    }, 500)
  }

  function updateEmotion(emotion) {
    emotionElement.textContent = emotion
    emotionElement.classList.add("emotion-update")
    setTimeout(() => {
      emotionElement.classList.remove("emotion-update")
    }, 500)
  }

  function sendMessage() {
    const message = messageInput.value.trim()
    if (message) {
      addMessage(message, true)
      messageInput.value = ""
      sendMessageToBackend(message)
    }
  }

  sendButton.addEventListener("click", sendMessage)

  messageInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      e.preventDefault()
      sendMessage()
    }
  })

  sttButton.addEventListener("click", () => {
    if (recognition) {
      if (!isListening) {
        recognition.start()
        isListening = true
        sttButton.textContent = "🔴"
      } else {
        recognition.stop()
        isListening = false
        sttButton.textContent = "🎤"
      }
    }
  })

  themeToggle.addEventListener("click", toggleTheme)

  const style = document.createElement("style")
  style.textContent = `
    .status-update, .emotion-update {
      animation: pulse 0.3s ease;
    }

    @keyframes pulse {
      0% { transform: scale(1); }
      50% { transform: scale(1.1); }
      100% { transform: scale(1); }
    }

    .typing-indicator {
      animation: typing 0.8s infinite;
    }

    @keyframes typing {
      0% { opacity: 0.5; }
      50% { opacity: 1; }
      100% { opacity: 0.5; }
    }
  `
  document.head.appendChild(style)

  async function initialize() {
    updateStatus("Conectando")
    updateEmotion("Emocionada")

    const initialMessages = await getMessagesFromBackend()
    initialMessages.forEach((message) => {
      addMessage(message, false)
    })

    updateStatus("En línea")
    updateEmotion("Feliz")
  }

  initialize()
})
