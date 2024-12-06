document.addEventListener("DOMContentLoaded", function () {
  const chatbotToggle = document.getElementById("chatbot-toggle");
  const chatbotWindow = document.getElementById("chatbot-window");
  const chatbotClose = document.getElementById("chatbot-close");
  const chatbotClear = document.getElementById("chatbot-clear");
  const chatbotForm = document.getElementById("chatbot-form");
  const chatbotInput = document.getElementById("chatbot-input");
  const chatbotBody = document.getElementById("chatbot-body");

  const MAX_MESSAGES = 20; // Maximum number of messages to store
  const MAX_MESSAGE_LENGTH = 500; // Maximum length of a single message

  // Function to load chat history from sessionStorage
  function loadChatHistory() {
    chatbotBody.innerHTML = ""; // Clear existing messages to prevent duplication

    const chatHistory = sessionStorage.getItem("chatHistory");
    if (chatHistory) {
      const messages = JSON.parse(chatHistory);
      messages.forEach((msg) => {
        appendMessage(msg.sender, msg.message, false, false); // Do not save when loading history
      });
    } else {
      // If no history, add system message
      appendMessage(
        "system",
        "Hello! I am your shopping assistant. How can I help you today?",
        true,
        false
      );
    }
  }

  // Function to save a message to sessionStorage
  function saveMessage(sender, message) {
    if (sender === "system") return; // Do not save system messages

    let chatHistory = sessionStorage.getItem("chatHistory");
    let messages = chatHistory ? JSON.parse(chatHistory) : [];

    // Add new message
    messages.push({ sender: sender, message: message });

    // Limit the number of messages
    if (messages.length > MAX_MESSAGES) {
      messages = messages.slice(messages.length - MAX_MESSAGES);
    }

    // Save back to sessionStorage
    sessionStorage.setItem("chatHistory", JSON.stringify(messages));
  }

  // Function to toggle chatbot visibility
  chatbotToggle.addEventListener("click", () => {
    const isVisible = chatbotWindow.style.display === "flex";
    chatbotWindow.style.display = isVisible ? "none" : "flex";

    if (!isVisible) {
      // Load chat history when opening the chatbot
      loadChatHistory();
    }
  });

  // Function to close chatbot
  chatbotClose.addEventListener("click", () => {
    chatbotWindow.style.display = "none";
  });

  // Function to clear chat history
  chatbotClear.addEventListener("click", () => {
    sessionStorage.removeItem("chatHistory");
    chatbotBody.innerHTML = "";
    appendMessage(
      "system",
      "Chat history cleared. How can I assist you today?",
      true,
      false
    );

    // Reset the backend session as well
    fetch("/reset_chatbot_session", { method: "POST" })
      .then((response) => response.json())
      .then((data) => {
        console.log("Chatbot session reset:", data);
      })
      .catch((error) => {
        console.error("Error resetting chatbot session:", error);
      });
  });

  // Function to append messages to chat body
  function appendMessage(
    sender,
    message,
    isSystem = false,
    saveToHistory = true
  ) {
    const messageElement = document.createElement("div");

    if (sender === "user" || sender === "bot") {
      messageElement.classList.add("chatbot-message", sender);
    } else if (sender === "system") {
      messageElement.classList.add("chatbot-message", "system");
    }

    const messageContent = document.createElement("div");
    messageContent.classList.add("message-content");
    messageContent.innerHTML = message;

    const timestamp = document.createElement("div");
    timestamp.classList.add("message-timestamp");
    const now = new Date();
    timestamp.textContent = now.toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });

    messageElement.appendChild(messageContent);
    messageElement.appendChild(timestamp);
    chatbotBody.appendChild(messageElement);

    // Scroll to the bottom
    chatbotBody.scrollTop = chatbotBody.scrollHeight;

    if (!isSystem && saveToHistory) {
      // Save only user and bot messages
      saveMessage(sender, message);
    }
  }

  // Handle form submission
  chatbotForm.addEventListener("submit", function (e) {
    e.preventDefault();
    const message = chatbotInput.value.trim();
    if (message === "") return;

    if (message.length > MAX_MESSAGE_LENGTH) {
      appendMessage("bot", "Message is too long.");
      chatbotInput.value = "";
      return;
    }

    // Display user's message
    appendMessage("user", message);
    chatbotInput.value = "";

    // Send message to the backend
    fetch("/chatbot", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message: message }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.response) {
          // Display bot's response
          appendMessage("bot", data.response);
        } else if (data.error) {
          appendMessage(
            "bot",
            `<span class="text-danger">Error: ${data.error}</span>`
          );
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        appendMessage(
          "bot",
          `<span class="text-danger">An error occurred. Please try again later.</span>`
        );
      });
  });

  // Initialize chat history on page load if chatbot is visible
  if (chatbotWindow.style.display === "flex") {
    loadChatHistory();
  }

  function scrollSlider(sliderId, direction) {
    const slider = document.getElementById(`${sliderId}-slider`);
    const scrollAmount = direction * 250; // Width of one product card
    slider.scrollBy({
      left: scrollAmount,
      behavior: "smooth",
    });
  }
});
