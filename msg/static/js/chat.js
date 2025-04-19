const socket = io();
const messageInput = document.getElementById('message-input');
const messagesDiv = document.getElementById('messages');
const userStatusDiv = document.getElementById('user-status');

// Send message when user presses Enter
messageInput.addEventListener('keypress', function(event) {
    if (event.key === 'Enter' && messageInput.value.trim() !== '') {
        socket.send(messageInput.value);  // Send the message to the backend
        messageInput.value = '';  // Clear the input field
    }
});

// Listen for new messages from the server
socket.on('message', function(msg) {
    const messageElement = document.createElement('div');
    messageElement.textContent = msg;  // Display the message
    messagesDiv.appendChild(messageElement);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;  // Auto-scroll to the latest message
});

// Listen for user status updates (online/offline)
socket.on('user_status', function(data) {
    const statusElement = document.createElement('div');
    statusElement.textContent = `${data.username} is ${data.status}`;
    userStatusDiv.appendChild(statusElement);
});
