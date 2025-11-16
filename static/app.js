// Configuration
const API_BASE_URL = window.location.origin;
const API_ENDPOINT = `${API_BASE_URL}/api/v1/chat`;
const API_STREAM_ENDPOINT = `${API_BASE_URL}/api/v1/chat/stream`;

// State
let conversationHistory = [];
let messageCount = 0;

// DOM Elements
const chatForm = document.getElementById('chatForm');
const messageInput = document.getElementById('messageInput');
const messagesContainer = document.getElementById('messages');
const loadingIndicator = document.getElementById('loading');
const sendBtn = document.getElementById('sendBtn');
const statusElement = document.getElementById('status');
const messageCountElement = document.getElementById('messageCount');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    messageInput.focus();
    loadConversationFromStorage();
});

// Form Submit Handler
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const message = messageInput.value.trim();
    if (!message) return;

    // Add user message to UI
    addMessage('user', message);

    // Clear input
    messageInput.value = '';
    messageInput.focus();

    // Show loading
    setLoading(true);
    updateStatus('מחבר למודל...');

    try {
        // Send to API with streaming
        await sendMessageStream(message);

        updateStatus('מוכן');
    } catch (error) {
        console.error('Error:', error);
        addErrorMessage('מצטער, אירעה שגיאה. אנא נסה שוב.');
        updateStatus('שגיאה - נסה שוב');
    } finally {
        setLoading(false);
    }
});

// Send Message to API
async function sendMessage(message) {
    const requestBody = {
        message: message,
        conversation_history: conversationHistory,
        temperature: 0.7,
        max_tokens: 2048
    };

    const response = await fetch(API_ENDPOINT, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Network response was not ok');
    }

    return await response.json();
}

// Send Message to API with Streaming
async function sendMessageStream(message) {
    const requestBody = {
        message: message,
        conversation_history: conversationHistory,
        temperature: 0.7,
        max_tokens: 2048
    };

    const response = await fetch(API_STREAM_ENDPOINT, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Network response was not ok');
    }

    // Create a placeholder message element for streaming
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant-message';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = '';  // Start empty

    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();

    // Process the streaming response
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let fullResponse = '';
    let firstChunk = true;

    while (true) {
        const { done, value } = await reader.read();

        if (done) {
            break;
        }

        // Decode the chunk
        const chunk = decoder.decode(value, { stream: true });

        // Process Server-Sent Events format
        const lines = chunk.split('\n');
        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const data = line.substring(6);

                // Check for completion signal
                if (data === '[DONE]') {
                    break;
                }

                // Check for error
                if (data.startsWith('[ERROR:')) {
                    throw new Error(data);
                }

                // Hide loading and update status on first chunk
                if (firstChunk && data.trim()) {
                    setLoading(false);
                    updateStatus('מקבל תשובה...');
                    firstChunk = false;
                }

                // Add the text chunk to the response
                fullResponse += data;

                // Update the message content in real-time
                contentDiv.innerHTML = formatMessage(fullResponse);
                scrollToBottom();
            }
        }
    }

    // Add to conversation history
    conversationHistory.push({
        role: 'assistant',
        content: fullResponse
    });

    // Save to localStorage
    saveConversationToStorage();

    // Update message count
    messageCount++;
    updateMessageCount();
}

// Add Message to UI and History
function addMessage(role, content) {
    // Add to conversation history
    conversationHistory.push({
        role: role === 'user' ? 'user' : 'assistant',
        content: content
    });

    // Save to localStorage
    saveConversationToStorage();

    // Create message element
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}-message`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    // Format content (preserve line breaks and links)
    contentDiv.innerHTML = formatMessage(content);

    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);

    // Scroll to bottom
    scrollToBottom();

    // Update message count
    messageCount++;
    updateMessageCount();
}

// Format Message (make links clickable, preserve formatting)
function formatMessage(text) {
    // Make URLs clickable
    text = text.replace(
        /(https?:\/\/[^\s]+)/g,
        '<a href="$1" target="_blank">$1</a>'
    );

    // Preserve line breaks
    text = text.replace(/\n/g, '<br>');

    // Bold text (for **text**)
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    return text;
}

// Add Error Message
function addErrorMessage(errorText) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = errorText;
    messagesContainer.appendChild(errorDiv);
    scrollToBottom();
}

// Set Loading State
function setLoading(isLoading) {
    loadingIndicator.style.display = isLoading ? 'flex' : 'none';
    sendBtn.disabled = isLoading;
    messageInput.disabled = isLoading;

    if (isLoading) {
        scrollToBottom();
    }
}

// Update Status
function updateStatus(status) {
    statusElement.textContent = status;
}

// Update Message Count
function updateMessageCount() {
    messageCountElement.textContent = `${messageCount} הודעות`;
}

// Scroll to Bottom
function scrollToBottom() {
    const chatContainer = document.querySelector('.chat-container');
    setTimeout(() => {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }, 100);
}

// Clear Conversation
function clearConversation() {
    if (confirm('האם אתה בטוח שברצונך לנקות את השיחה?')) {
        conversationHistory = [];
        messageCount = 0;

        // Clear UI (keep welcome message)
        const welcomeMessage = messagesContainer.querySelector('.assistant-message');
        messagesContainer.innerHTML = '';
        if (welcomeMessage) {
            messagesContainer.appendChild(welcomeMessage);
        }

        // Update UI
        updateMessageCount();
        updateStatus('השיחה נוקתה');

        // Clear storage
        localStorage.removeItem('conversation_history');

        // Reset after 2 seconds
        setTimeout(() => {
            updateStatus('מוכן');
        }, 2000);
    }
}

// Save to localStorage
function saveConversationToStorage() {
    try {
        localStorage.setItem('conversation_history', JSON.stringify(conversationHistory));
    } catch (e) {
        console.warn('Could not save to localStorage:', e);
    }
}

// Load from localStorage
function loadConversationFromStorage() {
    try {
        const saved = localStorage.getItem('conversation_history');
        if (saved) {
            conversationHistory = JSON.parse(saved);

            // Restore messages to UI
            conversationHistory.forEach(msg => {
                const role = msg.role === 'user' ? 'user' : 'assistant';
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${role}-message`;

                const contentDiv = document.createElement('div');
                contentDiv.className = 'message-content';
                contentDiv.innerHTML = formatMessage(msg.content);

                messageDiv.appendChild(contentDiv);
                messagesContainer.appendChild(messageDiv);

                messageCount++;
            });

            updateMessageCount();
            scrollToBottom();
        }
    } catch (e) {
        console.warn('Could not load from localStorage:', e);
    }
}

// Keyboard shortcuts
messageInput.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + Enter to send
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        chatForm.dispatchEvent(new Event('submit'));
    }
});
