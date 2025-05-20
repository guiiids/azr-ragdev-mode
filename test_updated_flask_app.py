import traceback
from flask import Flask, request, jsonify, render_template_string, Response
import json
import logging
import sys
import os

# Add the repository directory to the path so we can import modules
sys.path.append('/home/ubuntu')

from test_flask_rag_assistant import FlaskRAGAssistant

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
  <title>RAG Knowledge Assistant (New Layout)</title> <script src="https://cdn.tailwindcss.com"></script>
  <style id="custom-styles">
    p, li, a {
      font-size: 14px !important;
    }
    /* Added to ensure hidden class works as expected */
    .hidden {
        display: none !important;
    }
  </style>
</head>
<body class="bg-white p-4 ">
   <div class="max-w-xl mx-auto bg-white rounded-xl shadow-md overflow-hidden lg:max-w-2xl">
    <div>
      <div class="p-6"> <h1 class="text-2xl font-bold mb-4 text-center">RAG Knowledge Assistant</h1> <div class="md:shrink-0 mb-6 text-center"> <img class="h-40 w-auto inline-block object-cover md:h-48" src="https://content.tst-34.aws.agilent.com/wp-content/uploads/2025/05/This-is-a-to-do-item-This-is-completed-item.png" alt="Logo">
        </div>
 <div class="inline-flex rounded-md shadow-xs">
        <a href="#" aria-current="page" class="px-4 py-2 text-sm font-medium text-blue-700 bg-white border border-gray-200 rounded-s-lg hover:bg-gray-100 focus:z-10 focus:ring-2 focus:ring-blue-700 focus:text-blue-700">
          Chat
        </a>
        <a href="#" id="toggle-settings-btn" class="px-4 py-2 text-sm font-medium text-gray-900 bg-white border-t border-b border-gray-200 hover:bg-gray-100 hover:text-blue-700 focus:z-10 focus:ring-2 focus:ring-blue-700 focus:text-blue-700">
          Settings
        </a>
        <a href="#" class="px-4 py-2 text-sm font-medium text-gray-900 bg-white border border-gray-200 rounded-e-lg hover:bg-gray-100 hover:text-blue-700 focus:z-10 focus:ring-2 focus:ring-blue-700 focus:text-blue-700">
          Analytics
        </a>
      </div>
        <div id="chat-messages" class="mt-4 p-4 bg-white rounded shadow-md hidden">
            <div class="flex items-start gap-2.5 mb-4"> <img class="w-8 h-8 rounded-full" src="https://content.tst-34.aws.agilent.com/wp-content/uploads/2025/05/dalle.png" alt="AI Agent image">
                <div class="flex flex-col w-full max-w-[90%] leading-1.5">
                    <div class="flex items-center space-x-2 rtl:space-x-reverse">
                        <span class="text-sm font-semibold text-gray-900 dark:text-white">AI Agent</span>
                        </div>
                    <div id="answer" class="text-sm font-normal py-2 text-gray-900 dark:text-white">
                        </div>
                    </div>
            </div>

            <div id="sources-container" class="mt-4 border-t pt-4"> <h2 class="text-xl font-semibold">Sources:</h2>
                <div id="sources" class="mt-2"></div>
            </div>

            <div id="feedback-section" class="mt-6 border-t pt-4 hidden"> <h2 class="text-lg font-semibold mb-2">Rate this response:</h2>
                <div class="flex items-center space-x-4 mb-2">
                    <button id="thumbs-up" class="px-4 py-2 bg-green-100 text-green-700 rounded hover:bg-green-200 focus:outline-none">👍 Looks Good</button>
                    <button id="thumbs-down" class="px-4 py-2 bg-red-100 text-red-700 rounded hover:bg-red-200 focus:outline-none">👎 Needs Improvement</button>
                </div>
                <div id="feedback-tags-container" class="mb-2 hidden">
                    <label class="block mb-1 font-medium">Select issues (optional):</label>
                    <div class="flex flex-wrap gap-2">
                        <label><input type="checkbox" value="factualError" class="feedback-tag"> <span class="ml-1">Factual Error</span></label>
                        <label><input type="checkbox" value="irrelevant" class="feedback-tag"> <span class="ml-1">Irrelevant</span></label>
                        <label><input type="checkbox" value="missingInfo" class="feedback-tag"> <span class="ml-1">Missing Info</span></label>
                        <label><input type="checkbox" value="tooVerbose" class="feedback-tag"> <span class="ml-1">Too Verbose</span></label>
                        <label><input type="checkbox" value="formatting" class="feedback-tag"> <span class="ml-1">Formatting</span></label>
                    </div>
                </div>
                <textarea id="feedback-comment" class="w-full p-2 border rounded mb-2" rows="2" placeholder="Additional comments (optional)"></textarea>
                <button id="submit-feedback" class="px-4 py-2 bg-blue-500 text-white rounded">Submit Feedback</button>
                <div id="feedback-confirmation" class="mt-2 text-green-700 font-semibold hidden">Thank you for your feedback!</div>
            </div>
        </div> <div class="border-t-2 border-neutral-100 px-0 sm:px-6 py-3 mt-8"> <div class="relative">
                <input type="text" id="query-input" class="w-full bg-gray-50 placeholder:text-slate-400 text-slate-700 text-sm border border-slate-300 rounded-md pl-3 pr-20 py-3 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-slate-400 shadow-sm focus:shadow" placeholder="Ask a question..." />
                <button id="submit-btn" class="absolute right-1.5 top-1/2 -translate-y-1/2 rounded bg-blue-600 py-2 px-4 border border-transparent text-center text-sm text-white transition-all shadow-sm hover:shadow focus:bg-blue-700 focus:shadow-none active:bg-blue-700 hover:bg-blue-700 active:shadow-none disabled:pointer-events-none disabled:opacity-50 disabled:shadow-none" type="button">
                  Submit
                </button>
            </div>
        </div>
      </div> </div>
  </div>
 <button id="toggle-console-btn" class="ml-4 px-3 py-1 bg-gray-200 hover:bg-gray-300 rounded">Console Logs</button>
    <!-- Settings Drawer Backdrop & Panel -->
    <div id="settings-backdrop" class="fixed inset-0 bg-black/50 hidden z-40"></div>
    <div id="settings-drawer" class="fixed inset-y-0 right-0 w-96 bg-white shadow-lg transform translate-x-full transition-transform duration-300 z-50 flex flex-col">
      <div class="p-4 border-b flex items-center justify-between">
        <h2 class="text-lg font-semibold">Settings</h2>
        <button id="close-settings-btn" class="px-2 py-1 bg-gray-200 hover:bg-gray-300 rounded">&times;</button>
      </div>
      <form id="settings-form" class="flex-1 flex flex-col p-4 space-y-4">
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

// Function to show chat area
function showChatMessages() {
  chatMessages.classList.remove('hidden');
}

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
  showChatMessages();
      // Clear input
      queryInput.value = '';
      
      // Show typing indicator
      const typingIndicator = addTypingIndicator();

            // Disable submit button
      submitBtn.disabled = false;
      

      
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

      console.log('Connected to the endpoint.');
      console.log('Message = ' + JSON.stringify(payload));
      console.log('Sending message');
      console.log('Request payload:', payload);
      console.log('Fetch config:', {
        url: '/api/stream_query',
        options: {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        }
      });
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
          console.log('Retrieved response');
          console.log('Response = ' + botMessageContent);
          scrollToBottom();
          // Enable submit button
          submitBtn.disabled = false;
        });
      })
      .catch(error => {
        console.error('Error:', error);
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
      userMessageDiv.className = 'user-message';
      userMessageDiv.innerHTML = `
        <div class="message-bubble user-bubble">
          <p>${escapeHtml(message)}</p>
        </div>
        <img class="avatar" src="https://ui-avatars.com/api/?name=User&background=0D8ABC&color=fff" alt="User">
      `;
      chatMessages.appendChild(userMessageDiv);
      scrollToBottom();
      return userMessageDiv;
    }
    
    // Function to add bot message to chat
    function addBotMessage(message) {
      const botMessageDiv = document.createElement('div');
      botMessageDiv.className = 'bot-message';
      botMessageDiv.innerHTML = `
        <img class="avatar" src="https://content.tst-34.aws.agilent.com/wp-content/uploads/2025/05/dalle.png" alt="Bot">
        <div class="message-bubble bot-bubble">
          <p>${formatMessage(message)}</p>
        </div>
      `;
      chatMessages.appendChild(botMessageDiv);
      scrollToBottom();
      return botMessageDiv;
    }
    
    // Function to update bot message content
    function updateBotMessage(element, message) {
      const messageBubble = element.querySelector('.bot-bubble p');
      if (messageBubble) {
        messageBubble.innerHTML = formatMessage(message);
      }
    }
    
    // Function to add typing indicator
    function addTypingIndicator() {
      const typingDiv = document.createElement('div');
      typingDiv.className = 'bot-message';
      typingDiv.innerHTML = `
        <img class="avatar" src="https://content.tst-34.aws.agilent.com/wp-content/uploads/2025/05/dalle.png" alt="Bot">
        <div class="typing-indicator">
          <span></span>
          <span></span>
          <span></span>
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
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
    }
    
    // Function to format message with markdown-like syntax
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
  // Drawer toggle handlers
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5005))
    logger.info(f"Starting Flask app on port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)
