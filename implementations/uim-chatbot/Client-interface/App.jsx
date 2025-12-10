import { createSignal, createEffect, Show, For } from 'solid-js';

function App() {
  // State management
  const [messages, setMessages] = createSignal([]);
  const [inputMessage, setInputMessage] = createSignal('');
  const [isLoading, setIsLoading] = createSignal(false);
  const [error, setError] = createSignal(null);
  const [userId] = createSignal(`user-${Date.now()}`); // Generate unique user ID

  // Auto-scroll to bottom when new messages appear
  let messagesEndRef;
  createEffect(() => {
    if (messages().length > 0 && messagesEndRef) {
      messagesEndRef.scrollIntoView({ behavior: 'smooth' });
    }
  });

  // Send message to chatbot
  const sendMessage = async () => {
    const message = inputMessage().trim();
    if (!message || isLoading()) return;

    // Add user message to chat
    const userMessage = {
      role: 'user',
      content: message,
      timestamp: new Date().toISOString()
    };
    setMessages([...messages(), userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8001/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId(),
          message: message,
          context: {}
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();

      // Add bot response to chat
      const botMessage = {
        role: 'assistant',
        content: data.message,
        services_discovered: data.services_discovered || [],
        service_invocation: data.service_invocation,
        success: data.success,
        timestamp: data.timestamp
      };
      setMessages([...messages(), botMessage]);

    } catch (err) {
      console.error('Failed to send message:', err);
      setError(`Failed to connect to chatbot: ${err.message}`);
      
      // Add error message to chat
      const errorMessage = {
        role: 'error',
        content: `Error: ${err.message}. Make sure the chatbot service is running on port 8001.`,
        timestamp: new Date().toISOString()
      };
      setMessages([...messages(), errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle Enter key
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Clear chat
  const clearChat = () => {
    setMessages([]);
    setError(null);
  };

  // Format timestamp
  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex flex-col">
      {/* Header */}
      <header class="bg-white shadow-md p-4 border-b-2 border-indigo-200">
        <div class="max-w-4xl mx-auto flex justify-between items-center">
          <div>
            <h1 class="text-2xl font-bold text-indigo-600">DVerse Chatbot</h1>
            <p class="text-sm text-gray-600">AI-powered service discovery and invocation</p>
          </div>
          <div class="flex gap-2">
            <button
              onClick={clearChat}
              class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition text-sm"
              disabled={messages().length === 0}
            >
              Clear Chat
            </button>
            <a
              href="http://localhost:8001/docs"
              target="_blank"
              class="px-4 py-2 bg-indigo-100 text-indigo-700 rounded-lg hover:bg-indigo-200 transition text-sm"
            >
              API Docs
            </a>
          </div>
        </div>
      </header>

      {/* Chat Messages Area */}
      <div class="flex-1 overflow-y-auto p-4">
        <div class="max-w-4xl mx-auto">
          <Show when={messages().length === 0}>
            <div class="text-center py-12">
              <div class="text-6xl mb-4">🤖</div>
              <h2 class="text-2xl font-semibold text-gray-700 mb-2">
                Welcome to DVerse Chatbot!
              </h2>
              <p class="text-gray-600 mb-4">
                Ask me to find services or information from our catalogue
              </p>
              <div class="bg-white rounded-lg p-6 max-w-md mx-auto shadow-md">
                <p class="text-sm text-gray-700 mb-2 font-semibold">Try asking:</p>
                <ul class="text-sm text-gray-600 space-y-1 text-left">
                  <li>• "Find papers about neural networks"</li>
                  <li>• "Search arXiv for machine learning"</li>
                  <li>• "What services are available?"</li>
                  <li>• "Get weather data"</li>
                </ul>
              </div>
            </div>
          </Show>

          {/* Messages */}
          <div class="space-y-4">
            <For each={messages()}>
              {(msg) => (
                <div class={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div class={`max-w-2xl ${
                    msg.role === 'user' 
                      ? 'bg-indigo-600 text-white' 
                      : msg.role === 'error'
                      ? 'bg-red-100 text-red-800 border border-red-300'
                      : 'bg-white text-gray-800 shadow-md'
                  } rounded-lg p-4`}>
                    {/* Message Header */}
                    <div class="flex items-center justify-between mb-2">
                      <span class={`text-xs font-semibold ${
                        msg.role === 'user' 
                          ? 'text-indigo-200' 
                          : msg.role === 'error'
                          ? 'text-red-600'
                          : 'text-indigo-600'
                      }`}>
                        {msg.role === 'user' ? '👤 You' : msg.role === 'error' ? '⚠️ Error' : '🤖 DVerse Bot'}
                      </span>
                      <span class={`text-xs ${
                        msg.role === 'user' 
                          ? 'text-indigo-200' 
                          : 'text-gray-500'
                      }`}>
                        {formatTime(msg.timestamp)}
                      </span>
                    </div>

                    {/* Message Content */}
                    <p class="whitespace-pre-wrap break-words">{msg.content}</p>

                    {/* Service Information (for bot messages) */}
                    <Show when={msg.role === 'assistant' && msg.services_discovered?.length > 0}>
                      <div class="mt-3 pt-3 border-t border-gray-200">
                        <p class="text-xs text-gray-500 mb-1">Services Used:</p>
                        <div class="flex flex-wrap gap-1">
                          <For each={msg.services_discovered}>
                            {(service) => (
                              <span class="px-2 py-1 bg-indigo-100 text-indigo-700 text-xs rounded-full">
                                {service}
                              </span>
                            )}
                          </For>
                        </div>
                      </div>
                    </Show>

                    {/* Service Invocation Details */}
                    <Show when={msg.service_invocation && msg.service_invocation.success}>
                      <div class="mt-3 pt-3 border-t border-gray-200">
                        <p class="text-xs text-gray-500 mb-1">
                          Invoked: <span class="font-semibold">{msg.service_invocation.service_name}</span>
                          {' '}/{' '}
                          <span class="font-semibold">{msg.service_invocation.intent_name}</span>
                        </p>
                      </div>
                    </Show>
                  </div>
                </div>
              )}
            </For>
          </div>

          {/* Loading Indicator */}
          <Show when={isLoading()}>
            <div class="flex justify-start">
              <div class="bg-white rounded-lg p-4 shadow-md">
                <div class="flex items-center space-x-2">
                  <div class="w-2 h-2 bg-indigo-600 rounded-full animate-bounce"></div>
                  <div class="w-2 h-2 bg-indigo-600 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                  <div class="w-2 h-2 bg-indigo-600 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                  <span class="text-sm text-gray-600 ml-2">DVerse Bot is thinking...</span>
                </div>
              </div>
            </div>
          </Show>

          {/* Auto-scroll anchor */}
          <div ref={messagesEndRef}></div>
        </div>
      </div>

      {/* Input Area */}
      <div class="bg-white border-t-2 border-indigo-200 p-4 shadow-lg">
        <div class="max-w-4xl mx-auto">
          <Show when={error()}>
            <div class="mb-3 p-3 bg-red-100 border border-red-300 rounded-lg text-red-800 text-sm">
              {error()}
            </div>
          </Show>

          <div class="flex gap-2">
            <textarea
              class="flex-1 p-3 border-2 border-gray-300 rounded-lg focus:border-indigo-500 focus:outline-none resize-none"
              placeholder="Ask me anything about services..."
              rows="2"
              value={inputMessage()}
              onInput={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isLoading()}
            />
            <button
              onClick={sendMessage}
              disabled={!inputMessage().trim() || isLoading()}
              class={`px-6 py-3 rounded-lg font-semibold transition ${
                !inputMessage().trim() || isLoading()
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-indigo-600 text-white hover:bg-indigo-700'
              }`}
            >
              {isLoading() ? '...' : 'Send'}
            </button>
          </div>

          <p class="text-xs text-gray-500 mt-2 text-center">
            Press Enter to send, Shift+Enter for new line
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;
