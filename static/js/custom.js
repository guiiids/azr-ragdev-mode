// Custom overrides for chat message styling
document.addEventListener('DOMContentLoaded', function() {
  console.log('Loading custom message styling...');
  
  // Store original functions if they exist
  const originalAddUserMessage = window.addUserMessage;
  const originalAddBotMessage = window.addBotMessage;
  const originalAddTypingIndicator = window.addTypingIndicator;
  const originalFormatMessage = window.formatMessage;
  
  // Override formatMessage to handle citation links
  window.formatMessage = function(message) {
    if (typeof message !== 'string') {
      console.warn('formatMessage received non-string input:', message);
      return message || '';
    }
    
    // First use the original formatMessage function if it exists
    if (originalFormatMessage && typeof originalFormatMessage === 'function') {
      message = originalFormatMessage(message);
    } else {
      // Otherwise apply basic formatting
      // Convert URLs to links
      message = message.replace(
        /(https?:\/\/[^\s]+)/g, 
        '<a href="$1" target="_blank" class="text-blue-600 hover:underline">$1</a>'
      );
      // Convert **bold** to <strong>
      message = message.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      // Convert *italic* to <em>
      message = message.replace(/\*(.*?)\*/g, '<em>$1</em>');
      // Convert newlines to <br>
      message = message.replace(/\\n/g, '<br>');
    }
    
    // Add citation link handling - convert [n] to clickable links
    message = message.replace(
      /\[(\d+)\]/g,
      '<a href="#source-$1" class="citation-link text-blue-600 hover:underline" data-source-id="$1">[$1]</a>'
    );
    
    return message;
  };
  
  // Function to get current time in hh:mm format
  function getCurrentTime() {
    const now = new Date();
    const hours = now.getHours().toString().padStart(2, '0');
    const minutes = now.getMinutes().toString().padStart(2, '0');
    return `${hours}:${minutes}`;
  }
  
  // Override addUserMessage function
  window.addUserMessage = function(message) {
    // Hide center logo if visible
    const centerLogo = document.getElementById('center-logo');
    if (centerLogo && !centerLogo.classList.contains('hidden')) {
      centerLogo.classList.add('hidden');
    }
    
    // Get current time
    const currentTime = getCurrentTime();
    
    // Create message element
    const messageDiv = document.createElement('div');
    messageDiv.className = 'user-message';
    messageDiv.innerHTML = `
      <div class="message-bubble user-bubble">
        <div class="flex items-center justify-end space-x-2 rtl:space-x-reverse mb-1">
          <span class="text-sm font-bold" style="font-size: 0.85rem;">SPARK/Me</span>
          <span class="text-xs text-gray-300">${currentTime}</span>
        </div>
        ${formatMessage(escapeHtml(message))}
      </div>
      <img class="avatar" src="https://content.tst-34.aws.agilent.com/wp-content/uploads/2025/05/dalle.png" alt="User">
    `;
    
    // Add to chat
    const chatMessages = document.getElementById('chat-messages');
    if (chatMessages) {
      chatMessages.appendChild(messageDiv);
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }
  };
  
  // Override addBotMessage function
  window.addBotMessage = function(message) {
    // Hide center logo if visible
    const centerLogo = document.getElementById('center-logo');
    if (centerLogo && !centerLogo.classList.contains('hidden')) {
      centerLogo.classList.add('hidden');
    }
    
    // Get current time
    const currentTime = getCurrentTime();
    
    // Create message element
    const messageDiv = document.createElement('div');
    messageDiv.className = 'bot-message';
    messageDiv.innerHTML = `
      <img class="avatar" src="https://content.tst-34.aws.agilent.com/wp-content/uploads/2025/05/dalle.png" alt="AI">
      <div class="message-bubble bot-bubble">
        <div class="flex items-center space-x-2 rtl:space-x-reverse mb-1">
          <span class="text-sm font-bold" style="font-size: 0.85rem;">SPARK/<span class="text-indigo-500">AI</span></span>
          <span class="text-xs text-gray-500">${currentTime}</span>
        </div>
        ${formatMessage(message)}
      </div>
    `;
    
    // Add to chat
    const chatMessages = document.getElementById('chat-messages');
    if (chatMessages) {
      chatMessages.appendChild(messageDiv);
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }
  };
  
  // Override addTypingIndicator function
  window.addTypingIndicator = function() {
    const currentTime = getCurrentTime();
    
    const indicatorDiv = document.createElement('div');
    indicatorDiv.className = 'bot-message';
    indicatorDiv.innerHTML = `
      <img class="avatar" src="https://content.tst-34.aws.agilent.com/wp-content/uploads/2025/05/dalle.png" alt="AI">
      <div class="typing-indicator">
        <div class="flex items-center space-x-2 rtl:space-x-reverse mb-1">
          <span class="text-sm font-bold" style="font-size: 0.85rem;">SPARK/<span class="text-indigo-500">AI</span></span>
          <span class="text-xs text-gray-500">${currentTime}</span>
        </div>
        <span></span><span></span><span></span>
      </div>
    `;
    
    const chatMessages = document.getElementById('chat-messages');
    if (chatMessages) {
      chatMessages.appendChild(indicatorDiv);
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    return indicatorDiv;
  };
  
  console.log('Custom message styling loaded successfully');
});
