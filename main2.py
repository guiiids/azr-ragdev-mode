import traceback
from flask import Flask, request, jsonify, render_template_string, Response, send_from_directory
import json
import logging
import sys
import os

# Import directly from the current directory
from rag_assistant import FlaskRAGAssistant

# Configure logging
logger = logging.getLogger(__name__)
# Clear any existing handlers
if logger.handlers:
    logger.handlers.clear()
# Add file handler with absolute path
file_handler = logging.FileHandler('app.log')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
# Stream logs to stdout for visibility
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)

# Log startup message to verify logging is working
logger.info("Flask RAG application starting up")

app = Flask(__name__)

# HTML template with Tailwind CSS
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>RAG Knowledge Assistant</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style id="custom-styles">
    p, li, a {
      font-size: 14px !important;
    }
    body, html {
      height: 100%;
      margin: 0;
      padding: 0;
      overflow: hidden;
    }
    .chat-container {
      display: flex;
      flex-direction: column;
      height: 100vh;
    }
    .chat-messages {
      flex-grow: 1;
      overflow-y: auto;
      padding: 1rem;
    }
    .chat-input {
      border-top: 2px solid #e5e7eb;
      padding: 1rem;
      background-color: white;
    }
    .user-message {
      display: flex;
      justify-content: flex-end;
      margin-bottom: 1rem;
    }
    .bot-message {
      display: flex;
      justify-content: flex-start;
      margin-bottom: 1rem;
    }
    .message-bubble {
      max-width: 80%;
      padding: 0.75rem 1rem;
      border-radius: 1rem;
    }
    .user-bubble {
      background-color: #3b82f6;
      color: white;
      border-bottom-right-radius: 0.25rem;
    }
    .bot-bubble {
      background-color: #f3f4f6;
      color: #1f2937;
      border-bottom-left-radius: 0.25rem;
    }
    .avatar {
      width: 2rem;
      height: 2rem;
      border-radius: 50%;
      margin: 0 0.5rem;
    }
    .typing-indicator {
      display: inline-block;
      padding: 0.75rem 1rem;
      background-color: #f3f4f6;
      border-radius: 1rem;
      border-bottom-left-radius: 0.25rem;
      margin-bottom: 1rem;
    }
    .typing-indicator span {
      display: inline-block;
      width: 0.5rem;
      height: 0.5rem;
      background-color: #9ca3af;
      border-radius: 50%;
      margin-right: 0.25rem;
      animation: typing 1.4s infinite both;
    }
    .typing-indicator span:nth-child(2) {
      animation-delay: 0.2s;
    }
    .typing-indicator span:nth-child(3) {
      animation-delay: 0.4s;
      margin-right: 0;
    }
    @keyframes typing {
      0% { transform: translateY(0); }
      50% { transform: translateY(-0.5rem); }
      100% { transform: translateY(0); }
    }
    /* Added to ensure hidden class works as expected */
    .hidden {
      display: none !important;
    }
  </style>
</head>
<body class="bg-gray-100">
  <div class="chat-container">
    <!-- Header -->
    <div class="bg-white border-b-2 border-gray-200 px-4 py-3 flex items-center justify-between">
      <div class="flex items-center">
        <h1 class="text-xl font-bold text-gray-900">RAG Knowledge Assistant</h1>
      </div>
      <div class="inline-flex rounded-md shadow-xs">
        <a href="#" aria-current="page" class="px-4 py-2 text-sm font-medium text-blue-700 bg-white border border-gray-200 rounded-s-lg hover:bg-gray-100 focus:z-10 focus:ring-2 focus:ring-blue-700 focus:text-blue-700">
          Chat
        </a>
        <a href="#" id="toggle-settings-btn" class="px-4 py-2 text-sm font-medium text-gray-900 bg-white border-t border-b border-gray-200 hover:bg-gray-100 hover:text-blue-700 focus:z-10 focus:ring-2 focus:ring-blue-700 focus:text-blue-700">
          Settings
        </a>
        <a href="#" class="px-4 py-2 text-sm font-medium text-gray-900 bg-white border border-gray-200 hover:bg-gray-100 hover:text-blue-700 focus:z-10 focus:ring-2 focus:ring-blue-700 focus:text-blue-700">
          Analytics
        </a>
        <button id="toggle-developer-mode-btn" class="ml-4 px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500" type="button">
          Developer Mode
        </button>
      </div>
    </div>
    
    <!-- Chat Messages Area -->
    <div id="chat-messages" class="chat-messages">
      <!-- Bot welcome message -->
      <div class="flex items-start gap-2.5 mb-4">
        <img class="w-8 h-8 rounded-full" src="https://content.tst-34.aws.agilent.com/wp-content/uploads/2025/05/dalle.png" alt="AI Agent">
        <div class="flex flex-col w-full max-w-[90%] leading-1.5">
          <div class="flex items-center space-x-2 rtl:space-x-reverse">
            <span class="text-sm font-semibold text-gray-900 dark:text-white">SPARK/<span class="mt-1 text-sm leading-tight font-medium text-indigo-500 hover:underline">AI Agent</span></span>
          </div>
          <div class="text-sm font-normal py-2 text-gray-900 dark:text-white">
            Hi there! I'm an AI assistant trained on your knowledge base. What would you like to know?
          </div>
          <span class="text-sm font-normal text-gray-500 dark:text-gray-400">Delivered</span>
        </div>
      </div>
      <!-- Messages will be added here dynamically -->
    </div>

    <!-- Sources Section -->
    <div id="sources-container" class="mt-4 border-t pt-4 hidden">
      <h2 class="text-xl font-semibold">Sources:</h2>
      <div id="sources" class="mt-2"></div>
    </div>
    
    <!-- Chat Input Area -->
    <div class="chat-input">
      <div class="relative">
        <input id="query-input" type="text" class="w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md pl-3 pr-20 py-3 transition duration-300 ease focus:outline-none focus:border-slate-400 hover:border-slate-300 shadow-sm focus:shadow" placeholder="Ask me anything about our knowledge base..." />
        <button id="submit-btn" class="absolute right-1 top-1 rounded bg-slate-800 py-2 px-4 border border-transparent text-center text-sm text-white transition-all shadow-sm hover:shadow focus:bg-slate-700 focus:shadow-none active:bg-slate-700 hover:bg-slate-700 active:shadow-none disabled:pointer-events-none disabled:opacity-50 disabled:shadow-none" type="button">
          Send
        </button>
      </div>
    </div>
    <button id="toggle-console-btn" class="ml-4 px-3 py-1 bg-gray-200 hover:bg-gray-300 rounded">Console Logs</button>
    <!-- Settings Drawer Backdrop & Panel -->
    <div id="settings-backdrop" class="fixed inset-0 bg-black/50 hidden z-40"></div>
    <div id="settings-drawer" class="fixed inset-y-0 right-0 w-96 bg-white shadow-lg transform translate-x-full transition-transform duration-300 z-50 flex flex-col">
      <div class="p-4 border-b flex items-center justify-between">
        <h2 class="text-lg font-semibold">Settings</h2>
        <button id="close-settings-btn" class="px-2 py-1 bg-gray-200 hover:bg-gray-300 rounded">&times;</button>
      </div>
      <form id="settings-form" class="flex-1 flex flex-col p-4 space-y-4 overflow-y-auto">
        <div>
          <label for="custom-prompt" class="block text-sm font-medium text-gray-700 mb-1">Custom Instructions</label>
          <textarea id="custom-prompt" rows="5" class="w-full border border-gray-300 rounded p-2 text-sm" placeholder="Add custom instructions to the system prompt..."></textarea>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Prompt Mode</label>
          <div class="flex items-center space-x-4">
            <label class="inline-flex items-center">
              <input type="radio" name="prompt-mode" value="Append" class="form-radio" checked>
              <span class="ml-2">Append</span>
            </label>
            <label class="inline-flex items-center">
              <input type="radio" name="prompt-mode" value="Override" class="form-radio">
              <span class="ml-2">Override</span>
            </label>
          </div>
        </div>
        
        <!-- Developer Settings Section -->
        <div id="developer-settings" class="mt-4 pt-4 border-t border-gray-200">
          <h3 class="text-lg font-medium text-gray-900 mb-2">Developer Settings</h3>
          <p class="text-sm text-gray-500 mb-4">These settings are used in Developer Mode for evaluation.</p>
          
          <div class="mb-4">
            <label for="dev-temperature" class="block text-sm font-medium text-gray-700 mb-1">Temperature: <span id="temperature-value">0.3</span></label>
            <input type="range" id="dev-temperature" min="0" max="2" step="0.1" value="0.3" class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer">
            <div class="flex justify-between text-xs text-gray-500">
              <span>0.0</span>
              <span>1.0</span>
              <span>2.0</span>
            </div>
          </div>
          
          <div class="mb-4">
            <label for="dev-top-p" class="block text-sm font-medium text-gray-700 mb-1">Top P: <span id="top-p-value">1.0</span></label>
            <input type="range" id="dev-top-p" min="0" max="1" step="0.05" value="1.0" class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer">
            <div class="flex justify-between text-xs text-gray-500">
              <span>0.0</span>
              <span>0.5</span>
              <span>1.0</span>
            </div>
          </div>
          
          <div class="mb-4">
            <label for="dev-max-tokens" class="block text-sm font-medium text-gray-700 mb-1">Max Tokens:</label>
            <input type="number" id="dev-max-tokens" min="1" max="4000" value="1000" class="w-full border border-gray-300 rounded p-2 text-sm">
            <div class="text-xs text-gray-500 mt-1">Range: 1-4000</div>
          </div>
        </div>
        <div class="flex space-x-2">
          <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">Apply</button>
          <button type="button" id="reset-settings-btn" class="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300">Reset</button>
          <button type="button" id="restore-default-btn" class="px-4 py-2 bg-green-100 text-green-800 rounded hover:bg-green-200 border border-green-300">Restore Default</button>
        </div>
        <div id="settings-status" class="hidden mt-2 flex items-center space-x-2 bg-green-100 border border-green-300 text-green-800 px-3 py-2 rounded text-sm">
          <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"></path></svg>
          <span id="settings-status-text"></span>
        </div>
      </form>
    </div>
    <!-- Console Drawer Backdrop & Panel -->
    <div id="console-backdrop" class="fixed inset-0 bg-black/50 hidden z-40"></div>
    <div id="console-drawer" class="fixed inset-y-0 right-0 w-80 bg-white shadow-lg transform translate-x-full transition-transform duration-300 z-50 flex flex-col">
      <div class="p-4 border-b flex items-center justify-between">
        <h2 class="text-lg font-semibold">Console Logs</h2>
        <div class="flex items-center">
          <button id="clear-console-btn" class="px-2 py-1 bg-red-500 text-white rounded">Clear Logs</button>
          <button id="close-console-btn" class="ml-2 px-2 py-1 bg-gray-200 hover:bg-gray-300 rounded">&times;</button>
        </div>
      </div>
      <div id="console-logs-content" class="flex-1 p-4 overflow-auto font-mono text-sm bg-gray-50"></div>
    </div>
  </div>

  <script>
    // --- Utility Functions: Must be defined first for global scope ---
    function escapeHtml(unsafe) {
      return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
    }
    function formatMessage(message) {
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
      return message;
    }

    // --- Developer Mode State and Toggle ---
    let isDeveloperMode = false;
    const devModeBtn = document.getElementById('toggle-developer-mode-btn');
    function updateModeUI() {
      if (isDeveloperMode) {
        devModeBtn.classList.add('bg-green-600', 'hover:bg-green-700');
        devModeBtn.classList.remove('bg-indigo-600', 'hover:bg-indigo-700');
        devModeBtn.textContent = 'Developer Mode: ON';
        addBotMessage("Developer Evaluation mode enabled. Please enter your query for developer analysis.");
      } else {
        devModeBtn.classList.remove('bg-green-600', 'hover:bg-green-700');
        devModeBtn.classList.add('bg-indigo-600', 'hover:bg-indigo-700');
        devModeBtn.textContent = 'Developer Mode';
        addBotMessage("Standard chat mode enabled.");
      }
    }
    if (devModeBtn) {
      devModeBtn.addEventListener('click', function() {
        isDeveloperMode = !isDeveloperMode;
        updateModeUI();
      });
    }

    // --- Custom Instructions Reset on Page Load ---
    // Always clear custom instructions and mode on page load (refresh/new tab)
    if (window.localStorage) {
      localStorage.removeItem('systemPrompt');
      localStorage.removeItem('systemPromptMode');
    }
    // DOM elements
    const chatMessages = document.getElementById('chat-messages');
    const queryInput = document.getElementById('query-input');
    const submitBtn = document.getElementById('submit-btn');
    if (queryInput && submitBtn) {
  queryInput.addEventListener('keydown', function() {
    submitBtn.disabled = false;
    // console.log('Keydown in queryInput, submitBtn enabled.'); // For testing
  });
} else {
  console.error('Query input or submit button not found!');
}
    // Function to handle query submission
    function submitQuery() {
      const query = queryInput.value.trim();
      if (!query) return;
      addUserMessage(query);
      queryInput.value = '';
      submitBtn.disabled = false;

      if (isDeveloperMode) {
        // Developer Mode: handled by dev_eval_chat.js
        return;
      }

      // --- Standard Chat Mode ---
      // Show typing indicator
      const typingIndicator = addTypingIndicator();

      // Call API to get response
      // Build settings object for system prompt
      let settings = undefined;
      if (systemPrompt && systemPrompt.trim() !== '') {
        if (systemPromptMode === 'Append') {
          // Only send user's custom instructions for append
          settings = {
            system_prompt: systemPrompt,
            system_prompt_mode: 'Append'
          };
        } else if (systemPromptMode === 'Override') {
          // Send full prompt for override
          settings = {
            system_prompt: systemPrompt,
            system_prompt_mode: 'Override'
          };
        }
      }
      const payload = settings ? { query, settings } : { query };

      fetch('/api/stream_query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      .then(response => {
        if (!response.body) throw new Error('No response body');
        
        // Remove typing indicator
        if (typingIndicator) {
          typingIndicator.remove();
        }
        
        // Process streaming response
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let botMessageElement = null;
        let botMessageContent = '';
        let meta = null;
        let done = false;
        let buffer = '';
        
        function processStream() {
          return reader.read().then(({ value, done: streamDone }) => {
            if (value) {
              buffer += decoder.decode(value, { stream: true });
              
              // Process buffer for [[META]]
              let metaIdx = buffer.indexOf('[[META]]');
              if (metaIdx !== -1) {
                // Everything before [[META]] is answer, after is meta JSON
                const answerPart = buffer.slice(0, metaIdx);
                if (answerPart) {
                  botMessageContent += answerPart;
                  if (!botMessageElement) {
                    botMessageElement = addBotMessage(botMessageContent);
                  } else {
                    updateBotMessage(botMessageElement, botMessageContent);
                  }
                }
                
                const metaJson = buffer.slice(metaIdx + 8).trim();
                if (metaJson) {
                  try {
                    meta = JSON.parse(metaJson);
                    console.log('Citation data:', meta.sources);
                  } catch (e) {
                    console.error('Error parsing meta:', e);
                  }
                }
                
                done = true;
                return;
              } else {
                // No meta yet, just append to answer
                botMessageContent += buffer;
                if (!botMessageElement) {
                  botMessageElement = addBotMessage(botMessageContent);
                } else {
                  updateBotMessage(botMessageElement, botMessageContent);
                }
                buffer = '';
              }
            }
            
            if (streamDone) {
              done = true;
              return;
            }
            
            // Continue reading
            return processStream();
          });
        }
        
        return processStream().then(() => {
          // Scroll to bottom
          // --- Citation and Sources Handling ---
          if (meta && meta.sources && Array.isArray(meta.sources) && meta.sources.length > 0) {
            // Show sources section
            const sourcesContainer = document.getElementById('sources-container');
            const sourcesDiv = document.getElementById('sources');
            sourcesContainer.classList.remove('hidden');
            // Render sources
            sourcesDiv.innerHTML = meta.sources.map((src, idx) => {
              // src can be string or object
              let label = src.title || src.name || src.url || src.text || src.id || src;
              let url = src.url || (typeof src === 'string' && src.startsWith('http') ? src : null);
              let extra = src.extra || '';
              // Remove direct hyperlinking from label; add a "View Source" button if URL exists
              return `<div id="source-${idx+1}" class="mb-2">
                <span class="font-semibold">[${idx+1}]</span>
                <span>${label}</span>
                ${url ? `<button class="ml-2 px-2 py-1 bg-blue-100 text-blue-700 rounded view-source-btn" data-url="${url}" data-source="${idx+1}">View Source</button>` : ''}
                ${extra ? `<span class="text-gray-500 ml-2">${extra}</span>` : ''}
              </div>`;
            }).join('');
            // Add click handlers for "View Source" buttons
            const viewBtns = sourcesDiv.querySelectorAll('.view-source-btn');
            viewBtns.forEach(btn => {
              btn.addEventListener('click', function(e) {
                const url = this.getAttribute('data-url');
                if (url) window.open(url, '_blank');
              });
            });
            // Update the last bot message to hyperlink citations
            if (botMessageElement) {
              const messageContent = botMessageElement.querySelector('.text-sm.font-normal.py-2');
              if (messageContent) {
                // Replace [n] with anchor links
                let html = messageContent.innerHTML;
                html = html.replace(/\[(\d+)\]/g, function(match, n) {
                  if (n > 0 && n <= meta.sources.length) {
                    return `<a href="#source-${n}" class="text-blue-600 hover:underline citation-link" data-cite="${n}">[${n}]</a>`;
                  }
                  return match;
                });
                messageContent.innerHTML = html;
                // Add click handler to scroll to source and open URL if present
                const links = messageContent.querySelectorAll('.citation-link');
                links.forEach(link => {
                  link.addEventListener('click', function(e) {
                    e.preventDefault();
                    // Always show sources panel
                    const sourcesContainer = document.getElementById('sources-container');
                    if (sourcesContainer) sourcesContainer.classList.remove('hidden');
                    const n = this.getAttribute('data-cite');
                    const target = document.getElementById('source-' + n);
                    if (target) {
                      target.scrollIntoView({ behavior: 'smooth', block: 'center' });
                      target.classList.add('bg-yellow-100');
                      setTimeout(() => target.classList.remove('bg-yellow-100'), 1200);
                      // If the source has a URL, open it in a new tab
                      const src = meta.sources[parseInt(n, 10) - 1];
                      let url = src && (src.url || (typeof src === 'string' && src.startsWith('http') ? src : null));
                      if (url) window.open(url, '_blank');
                    }
                  });
                });
              }
            }
          } else {
            // Hide sources section if no sources
            const sourcesContainer = document.getElementById('sources-container');
            if (sourcesContainer) sourcesContainer.classList.add('hidden');
            const sourcesDiv = document.getElementById('sources');
            if (sourcesDiv) sourcesDiv.innerHTML = '';
          }
          scrollToBottom();
          // Enable submit button
          submitBtn.disabled = false;
        });
      })
      .catch(error => {
        if (typingIndicator) typingIndicator.remove();
        addBotMessage('Sorry, I encountered an error while processing your request. Please try again.');
        // Enable submit button
        submitBtn.disabled = false;
      });
    }
    
    // Add event listener for Enter key
    queryInput.addEventListener('keydown', function(event) {
      if (event.key === 'Enter') {
        event.preventDefault();
        submitQuery();
      }
    });
    
    // Add event listener for submit button
    submitBtn.addEventListener('click', submitQuery);
    
    // Function to add user message to chat
    function addUserMessage(message) {
      const userMessageDiv = document.createElement('div');
      userMessageDiv.className = 'flex items-start gap-2.5 mb-4 justify-end';
      
      // Get current time in HH:MM format
      const now = new Date();
      const hours = now.getHours().toString().padStart(2, '0');
      const minutes = now.getMinutes().toString().padStart(2, '0');
      const timeString = `${hours}:${minutes}`;
      
      userMessageDiv.innerHTML = `
        <div class="flex flex-col w-full max-w-[90%] leading-1.5 items-end">
          <div class="flex items-center justify-end space-x-2 rtl:space-x-reverse">
            <span class="text-sm font-normal text-gray-500 dark:text-gray-400">${timeString}</span>
            <span class="text-sm font-semibold text-gray-900 dark:text-white">You</span>
          </div>
          <div class="text-sm font-normal py-2 px-4 bg-blue-600 text-white rounded-lg">
            ${escapeHtml(message)}
          </div>
        </div>
        <img class="w-8 h-8 rounded-full" src="https://ui-avatars.com/api/?name=User&background=0D8ABC&color=fff" alt="User">
      `;
      chatMessages.appendChild(userMessageDiv);
      scrollToBottom();
      return userMessageDiv;
    }
    
    // Function to add bot message to chat
    function addBotMessage(message) {
      const botMessageDiv = document.createElement('div');
      botMessageDiv.className = 'flex items-start gap-2.5 mb-4';
      
      // Get current time in HH:MM format
      const now = new Date();
      const hours = now.getHours().toString().padStart(2, '0');
      const minutes = now.getMinutes().toString().padStart(2, '0');
      const timeString = `${hours}:${minutes}`;
      
      botMessageDiv.innerHTML = `
        <img class="w-8 h-8 rounded-full" src="https://content.tst-34.aws.agilent.com/wp-content/uploads/2025/05/dalle.png" alt="AI Agent">
        <div class="flex flex-col w-full max-w-[90%] leading-1.5">
          <div class="flex items-center space-x-2 rtl:space-x-reverse">
            <span class="text-sm font-semibold text-gray-900 dark:text-white">SPARK/<span class="mt-1 text-sm leading-tight font-medium text-indigo-500 hover:underline">AI Agent</span></span>
            <span class="text-sm font-normal text-gray-500 dark:text-gray-400">${timeString}</span>
          </div>
          <div class="text-sm font-normal py-2 text-gray-900 dark:text-white">
            ${formatMessage(message)}
          </div>
          <span class="text-sm font-normal text-gray-500 dark:text-gray-400">Delivered</span>
        </div>
      `;
      chatMessages.appendChild(botMessageDiv);
      scrollToBottom();
      return botMessageDiv;
    }
    
    // Function to update bot message content
    function updateBotMessage(element, message) {
      const messageContent = element.querySelector('.text-sm.font-normal.py-2');
      if (messageContent) {
        messageContent.innerHTML = formatMessage(message);
      }
    }
    
    // Function to add typing indicator
    function addTypingIndicator() {
      const typingDiv = document.createElement('div');
      typingDiv.className = 'flex items-start gap-2.5 mb-4';
      typingDiv.innerHTML = `
        <img class="w-8 h-8 rounded-full" src="https://content.tst-34.aws.agilent.com/wp-content/uploads/2025/05/dalle.png" alt="AI Agent">
        <div class="flex flex-col w-full max-w-[90%] leading-1.5">
          <div class="flex items-center space-x-2 rtl:space-x-reverse">
            <span class="text-sm font-semibold text-gray-900 dark:text-white">SPARK/<span class="mt-1 text-sm leading-tight font-medium text-indigo-500 hover:underline">AI Agent</span></span>
          </div>
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      `;
      chatMessages.appendChild(typingDiv);
      scrollToBottom();
      return typingDiv;
    }
    
    // Function to scroll to bottom of chat
    function scrollToBottom() {
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Function to escape HTML
    function escapeHtml(unsafe) {
      return unsafe
        .replace(/&/g, "&")
        .replace(/</g, "<")
        .replace(/>/g, ">")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
    }
    
    
  // Console Drawer
  const toggleBtn = document.getElementById('toggle-console-btn');
  const closeBtn = document.getElementById('close-console-btn');
  const backdrop = document.getElementById('console-backdrop');
  const drawer = document.getElementById('console-drawer');
  const logsContainer = document.getElementById('console-logs-content');

  function openDrawer() {
    backdrop.classList.remove('hidden');
    drawer.classList.remove('translate-x-full');
    drawer.classList.add('translate-x-0');
  }

  function closeDrawer() {
    backdrop.classList.add('hidden');
    drawer.classList.remove('translate-x-0');
    drawer.classList.add('translate-x-full');
  }

  toggleBtn.addEventListener('click', openDrawer);
  closeBtn.addEventListener('click', closeDrawer);
  backdrop.addEventListener('click', closeDrawer);

  // Settings Drawer
  const toggleSettingsBtn = document.getElementById('toggle-settings-btn');
  const closeSettingsBtn = document.getElementById('close-settings-btn');
  const settingsBackdrop = document.getElementById('settings-backdrop');
  const settingsDrawer = document.getElementById('settings-drawer');
  const settingsForm = document.getElementById('settings-form');
  const customPromptInput = document.getElementById('custom-prompt');
  const resetSettingsBtn = document.getElementById('reset-settings-btn');
  const settingsStatus = document.getElementById('settings-status');
  const settingsStatusText = document.getElementById('settings-status-text');
  const restoreDefaultBtn = document.getElementById('restore-default-btn');

  // Default system prompt (should match backend)
  const DEFAULT_SYSTEM_PROMPT = `
    ### Task:

    Respond to the user query using the provided context, incorporating inline citations in the format [id] **only when the <source> tag includes an explicit id attribute** (e.g., <source id="1">).
    
    ### Guidelines:

    - If you don't know the answer, clearly state that.
    - If uncertain, ask the user for clarification.
    - Respond in the same language as the user's query.
    - If the context is unreadable or of poor quality, inform the user and provide the best possible answer.
    - If the answer isn't present in the context but you possess the knowledge, explain this to the user and provide the answer using your own understanding.
    - **Only include inline citations using [id] (e.g., [1], [2]) when the <source> tag includes an id attribute.**
    - Do not cite if the <source> tag does not contain an id attribute.
    - Do not use XML tags in your response.
    - Ensure citations are concise and directly related to the information provided.
  `.trim();

  function openSettingsDrawer() {
    settingsBackdrop.classList.remove('hidden');
    settingsDrawer.classList.remove('translate-x-full');
    settingsDrawer.classList.add('translate-x-0');
  }

  function closeSettingsDrawer() {
    settingsBackdrop.classList.add('hidden');
    settingsDrawer.classList.remove('translate-x-0');
    settingsDrawer.classList.add('translate-x-full');
  }

  toggleSettingsBtn.addEventListener('click', openSettingsDrawer);
  closeSettingsBtn.addEventListener('click', closeSettingsDrawer);
  settingsBackdrop.addEventListener('click', closeSettingsDrawer);

  // Developer settings sliders
  const temperatureSlider = document.getElementById('dev-temperature');
  const temperatureValue = document.getElementById('temperature-value');
  const topPSlider = document.getElementById('dev-top-p');
  const topPValue = document.getElementById('top-p-value');
  
  if (temperatureSlider && temperatureValue) {
    temperatureSlider.addEventListener('input', function() {
      temperatureValue.textContent = this.value;
    });
  }
  
  if (topPSlider && topPValue) {
    topPSlider.addEventListener('input', function() {
      topPValue.textContent = this.value;
    });
  }

  // Settings state
  let systemPrompt = '';
  let systemPromptMode = 'Append';

  // Load from localStorage if available
  if (window.localStorage) {
    systemPrompt = localStorage.getItem('systemPrompt') || '';
    systemPromptMode = localStorage.getItem('systemPromptMode') || 'Append';
    customPromptInput.value = systemPrompt;
    const modeInputs = settingsForm.querySelectorAll('input[name="prompt-mode"]');
    modeInputs.forEach(input => {
      input.checked = (input.value === systemPromptMode);
    });
  }

  // Handle settings form submit
  settingsForm.addEventListener('submit', function(e) {
    e.preventDefault();
    systemPrompt = customPromptInput.value.trim();
    const modeInputs = settingsForm.querySelectorAll('input[name="prompt-mode"]');
    systemPromptMode = Array.from(modeInputs).find(i => i.checked).value;
    if (window.localStorage) {
      localStorage.setItem('systemPrompt', systemPrompt);
      localStorage.setItem('systemPromptMode', systemPromptMode);
    }
    settingsStatusText.textContent = 'Settings applied!';
    settingsStatus.classList.remove('hidden');
    setTimeout(() => { settingsStatus.classList.add('hidden'); }, 2000);
    closeSettingsDrawer();
  });

  // Handle reset
  resetSettingsBtn.addEventListener('click', function() {
    systemPrompt = '';
    systemPromptMode = 'Append';
    customPromptInput.value = '';
    const modeInputs = settingsForm.querySelectorAll('input[name="prompt-mode"]');
    modeInputs.forEach(input => {
      input.checked = (input.value === 'Append');
    });
    if (window.localStorage) {
      localStorage.removeItem('systemPrompt');
      localStorage.removeItem('systemPromptMode');
    }
    settingsStatusText.textContent = 'Settings reset!';
    settingsStatus.classList.remove('hidden');
    setTimeout(() => { settingsStatus.classList.add('hidden'); }, 2000);
  });

  // Restore default button
  restoreDefaultBtn.addEventListener('click', function() {
    // Wipe all custom instructions and mode from localStorage and reset UI to default
    if (window.localStorage) {
      localStorage.removeItem('systemPrompt');
      localStorage.removeItem('systemPromptMode');
    }
    systemPrompt = '';
    systemPromptMode = 'Append';
    customPromptInput.value = DEFAULT_SYSTEM_PROMPT;
    const modeInputs = settingsForm.querySelectorAll('input[name="prompt-mode"]');
    modeInputs.forEach(input => {
      input.checked = (input.value === 'Append');
    });
    settingsStatusText.textContent = 'Restored to default settings!';
    settingsStatus.classList.remove('hidden');
    setTimeout(() => { settingsStatus.classList.add('hidden'); }, 2000);
  });

  // Override console methods
  ['log','info','warn','error'].forEach(level => {
    const original = console[level];
    console[level] = function(...args) {
      original.apply(console, args);
      const msg = args
        .map(a => typeof a === 'object' ? JSON.stringify(a) : a)
        .join(' ');
      const entry = document.createElement('div');
      entry.textContent = '[' + level.toUpperCase() + '] ' + msg;
      if (level === 'warn') entry.classList.add('text-yellow-600');
      if (level === 'error') entry.classList.add('text-red-600');
      logsContainer.appendChild(entry);
      logsContainer.scrollTop = logsContainer.scrollHeight;
    };
  });

  // Clear logs button
  document.getElementById('clear-console-btn').addEventListener('click', () => {
    logsContainer.innerHTML = '';
  });
  </script>
  
  <!-- Developer Evaluation Chat Interface -->
  <script src="/static/js/dev_eval_chat.js"></script>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    logger.info("Index page accessed")
    return render_template_string(HTML_TEMPLATE)

@app.route("/api/query", methods=["POST"])
def api_query():
    data = request.get_json()
    logger.info("DEBUG - Incoming /api/query payload: %s", json.dumps(data))
    user_query = data.get("query", "")
    logger.info(f"API query received: {user_query}")
    
    # Extract any settings from the request
    settings = data.get("settings", {})
    logger.info(f"DEBUG - Request settings: {json.dumps(settings)}")
    
    try:
        # Initialize the RAG assistant with settings if provided
        rag_assistant = FlaskRAGAssistant(settings=settings)
        logger.info(f"DEBUG - Using model: {rag_assistant.deployment_name}")
        logger.info(f"DEBUG - Temperature: {rag_assistant.temperature}")
        logger.info(f"DEBUG - Max tokens: {rag_assistant.max_tokens}")
        logger.info(f"DEBUG - Top P: {rag_assistant.top_p}")
        logger.info(f"DEBUG - Presence penalty: {rag_assistant.presence_penalty}")
        logger.info(f"DEBUG - Frequency penalty: {rag_assistant.frequency_penalty}")
        
        answer, cited_sources, _, evaluation, context = rag_assistant.generate_rag_response(user_query)
        logger.info(f"API query response generated for: {user_query}")
        logger.info(f"DEBUG - Response length: {len(answer)}")
        logger.info(f"DEBUG - Number of cited sources: {len(cited_sources)}")
        
        return jsonify({
            "answer": answer,
            "sources": cited_sources,
            "evaluation": evaluation
        })
    except Exception as e:
        logger.error(f"Error in api_query: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            "error": str(e)
        }), 500

@app.route("/api/stream_query", methods=["POST"])
def api_stream_query():
    data = request.get_json()
    user_query = data.get("query", "")
    logger.info(f"Stream query received: {user_query}")
    logger.info(f"DEBUG - Full request payload: {json.dumps(data)}")
    
    # Extract any settings from the request
    settings = data.get("settings", {})
    logger.info(f"DEBUG - Request settings: {json.dumps(settings)}")
    
    def generate():
        try:
            # Initialize the RAG assistant with settings if provided
            rag_assistant = FlaskRAGAssistant(settings=settings)
            logger.info(f"Starting stream response for: {user_query}")
            logger.info(f"DEBUG - Using model: {rag_assistant.deployment_name}")
            logger.info(f"DEBUG - Temperature: {rag_assistant.temperature}")
            logger.info(f"DEBUG - Max tokens: {rag_assistant.max_tokens}")
            logger.info(f"DEBUG - Top P: {rag_assistant.top_p}")
            logger.info(f"DEBUG - Presence penalty: {rag_assistant.presence_penalty}")
            logger.info(f"DEBUG - Frequency penalty: {rag_assistant.frequency_penalty}")
            
            # Use streaming method
            for chunk in rag_assistant.stream_rag_response(user_query):
                logger.info("DEBUG - AI stream chunk: %s", chunk)
                if isinstance(chunk, str):
                    yield chunk
                else:
                    yield f"\n[[META]]{json.dumps(chunk)}"
            
            logger.info(f"Completed stream response for: {user_query}")
                
        except Exception as e:
            logger.error(f"Error in stream_query: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            yield f"Sorry, I encountered an error: {str(e)}"
            yield f"\n[[META]]" + json.dumps({"error": str(e)})
    
    return Response(generate(), mimetype="text/plain")

@app.route("/api/feedback", methods=["POST"])
def api_feedback():
    data = request.get_json()
    feedback_data = {
        "question": data.get("question", ""),
        "response": data.get("response", ""),
        "feedback_tags": data.get("feedback_tags", []),
        "comment": data.get("comment", ""),
        "evaluation_json": {}
    }
    
    try:
        # For now, just log the feedback
        logger.info(f"Feedback received: {feedback_data}")
        return jsonify({"success": True}), 200
    except Exception as e:
        logger.error(f"Error saving feedback: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# Serve static files from both static/ and reask_dashboard/static/
@app.route("/static/<path:filename>")
def serve_static(filename):
    # First check if the file exists in the local static directory
    local_static_path = os.path.join(os.path.dirname(__file__), "static")
    if os.path.exists(os.path.join(local_static_path, filename)):
        return send_from_directory(local_static_path, filename)
    
    # If not found in local static, check in reask_dashboard/static
    reask_static_path = os.path.join(os.path.dirname(__file__), "reask_dashboard", "static")
    if os.path.exists(os.path.join(reask_static_path, filename)):
        return send_from_directory(reask_static_path, filename)
    
    # If not found in either location, return 404
    return "File not found", 404

@app.route("/api/dev_eval", methods=["POST"])
def api_dev_eval():
    """
    Developer Evaluation API endpoint.
    Expects JSON: { "query": ..., "prompt": ..., "parameters": { "temperature": ..., "top_p": ..., "max_tokens": ... } }
    Returns: { "result": ..., "developer_evaluation": ..., "download_url_json": ..., "download_url_md": ..., "markdown_report": ... }
    """
    from llm_summary import developer_evaluate_job, generate_markdown_report
    import uuid

    data = request.get_json()
    query = data.get("query", "")
    prompt = data.get("prompt", "")
    params = data.get("parameters", {}) or {}
    temperature = params.get("temperature", 0.3)
    top_p = params.get("top_p", 1.0)
    max_tokens = params.get("max_tokens", 1000)

    settings = {
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens
    }
    if prompt:
        settings["system_prompt"] = prompt
        settings["system_prompt_mode"] = "Override"

    try:
        rag_assistant = FlaskRAGAssistant(settings=settings)
        answer, sources, _, evaluation, context = rag_assistant.generate_rag_response(query)
        dev_eval = developer_evaluate_job(
            query=query,
            prompt=prompt,
            parameters=params,
            result=answer
        )
        # Save to file and provide download link
        result_obj = {
            "query": query,
            "prompt": prompt,
            "parameters": params,
            "result": answer,
            "sources": sources,
            "developer_evaluation": dev_eval
        }
        
        # Generate markdown report
        markdown_report = generate_markdown_report(result_obj)
        
        # Save with a unique filename
        file_id = str(uuid.uuid4())
        json_filename = f"dev_eval_{file_id}.json"
        md_filename = f"dev_eval_{file_id}.md"
        
        file_path = os.path.join("reask_dashboard", "static", "dev_eval_reports")
        os.makedirs(file_path, exist_ok=True)
        
        # Save JSON file
        json_path = os.path.join(file_path, json_filename)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(result_obj, f, indent=2, ensure_ascii=False)
        
        # Save Markdown file
        md_path = os.path.join(file_path, md_filename)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(markdown_report)
        
        # Download URLs
        json_url = f"/static/dev_eval_reports/{json_filename}"
        md_url = f"/static/dev_eval_reports/{md_filename}"
        
        return jsonify({
            "result": answer,
            "sources": sources,
            "developer_evaluation": dev_eval,
            "download_url_json": json_url,
            "download_url_md": md_url,
            "markdown_report": markdown_report
        })
    except Exception as e:
        logger.error(f"Error in api_dev_eval: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            "error": str(e)
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5002))
    logger.info(f"Starting Flask app on port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)
