import { createSignal, createEffect, Show, For } from 'solid-js';

function App() {
  // State management
  const [messages, setMessages] = createSignal([]);
  const [inputMessage, setInputMessage] = createSignal('');
  const [isLoading, setIsLoading] = createSignal(false);
  const [processingStatus, setProcessingStatus] = createSignal('');
  const [currentService, setCurrentService] = createSignal(''); // NEW: Track current service
  const [error, setError] = createSignal(null);
  const [userId] = createSignal(`user-${Date.now()}`);
  const [showHowItWorks, setShowHowItWorks] = createSignal(false);
  const [availableServices, setAvailableServices] = createSignal([]); // NEW: Store services from catalogue

  // Fetch available services from catalogue on mount
  createEffect(() => {
    fetchAvailableServices();
  });

  const fetchAvailableServices = async () => {
    try {
      const response = await fetch('http://localhost:8000/services/', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setAvailableServices(data.services || []);
        console.log('Fetched services:', data.services?.length);
      }
    } catch (err) {
      console.error('Failed to fetch services:', err);
      // Don't show error to user, just log it
    }
  };

  // Auto-scroll to bottom when new messages appear
  let messagesEndRef;
  createEffect(() => {
    if (messages().length > 0 && messagesEndRef) {
      messagesEndRef.scrollIntoView({ behavior: 'smooth' });
    }
  });

  // Send message to chatbot - NOW SPLIT INTO TWO CALLS
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
    
    // STEP 1: Discover which service to use
    setProcessingStatus('🔍 Discovering the right service for your query...');
    setCurrentService('');

    try {
      // ===== STEP 1: DISCOVER =====
      const discoverResponse = await fetch('http://localhost:8001/chat/discover', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId(),
          message: message
        })
      });

      if (!discoverResponse.ok) {
        if (discoverResponse.status === 401) {
          throw new Error('Authentication required - Missing API key for discovery');
        }
        throw new Error(`Discovery failed: HTTP ${discoverResponse.status}`);
      }

      const discoverData = await discoverResponse.json();
      const serviceName = discoverData.service_name;
      const intentName = discoverData.intent_name;
      
      // Show which service is being used
      setCurrentService(serviceName);
      setProcessingStatus(`🚀 Using ${serviceName}...`);
      
      // Small delay so user can see the service name
      await new Promise(resolve => setTimeout(resolve, 500));

      // ===== STEP 2: INVOKE =====
      setProcessingStatus(`🚀 Calling ${serviceName} API...`);
      
      const invokeResponse = await fetch('http://localhost:8001/chat/invoke', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId(),
          query: message,
          service_name: serviceName,
          intent_name: intentName,
          service_data: discoverData.service_data
        })
      });

      if (!invokeResponse.ok) {
        if (invokeResponse.status === 401) {
          throw new Error(`Authentication required - Missing API key for ${serviceName}`);
        }
        throw new Error(`Invocation failed: HTTP ${invokeResponse.status}`);
      }

      const data = await invokeResponse.json();

      // Check for authentication errors in response
      if (data.error && (data.error.includes('401') || data.error.includes('authentication') || data.error.includes('API key'))) {
        throw new Error(`Oops! Missing API key for ${serviceName}. Please configure the API key to use this service.`);
      }

      // Add bot response to chat
      const botMessage = {
        role: 'assistant',
        content: data.message,
        services_discovered: [serviceName],
        service_invocation: data.service_invocation,
        success: data.success,
        timestamp: data.timestamp
      };
      
      // Debug logging
      console.log("Bot message:", botMessage);
      console.log("Service invocation:", data.service_invocation);
      console.log("Has papers?", data.service_invocation?.data?.papers?.length);
      
      setMessages([...messages(), botMessage]);
      
      // Clear status on success
      setProcessingStatus('');
      setCurrentService('');

    } catch (err) {
      console.error('Failed to send message:', err);
      
      // More user-friendly error messages
      let errorMessage = err.message;
      
      if (err.message.includes('Failed to fetch') || err.message.includes('NetworkError')) {
        errorMessage = 'Cannot connect to DVerse Demo. Please make sure the chatbot service is running on port 8001.';
      }
      
      // Add error message to chat (NOT as banner)
      const errorChatMessage = {
        role: 'error',
        content: errorMessage,
        timestamp: new Date().toISOString()
      };
      setMessages([...messages(), errorChatMessage]);
      
      // Clear status on error
      setProcessingStatus('');
      setCurrentService('');
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
    setProcessingStatus('');
    setCurrentService('');
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
            <h1 class="text-2xl font-bold text-indigo-600">DVerse Demo</h1>
            <p class="text-sm text-gray-600">AI-powered service discovery and invocation</p>
          </div>
          <div class="flex gap-2">
            <button
              onClick={() => setShowHowItWorks(true)}
              class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition text-sm font-semibold"
            >
              ℹ️ How It Works
            </button>
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

      {/* How It Works Modal */}
      <Show when={showHowItWorks()}>
        <div 
          class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
          onClick={() => setShowHowItWorks(false)}
        >
          <div 
            class="bg-white rounded-lg shadow-2xl max-w-4xl max-h-[80vh] overflow-y-auto p-8 m-4"
            onClick={(e) => e.stopPropagation()}
          >
            <div class="flex justify-between items-start mb-6">
              <h2 class="text-3xl font-bold text-indigo-600">How DVerse Demo Works</h2>
              <button
                onClick={() => setShowHowItWorks(false)}
                class="text-gray-500 hover:text-gray-700 text-2xl font-bold"
              >
                ×
              </button>
            </div>

            <div class="space-y-6 text-gray-700">
              <section>
                <h3 class="text-xl font-semibold text-indigo-700 mb-2">🎯 What is DVerse?</h3>
                <p>
                  DVerse is a <strong>Unified Intent Mediator (UIM)</strong> implementation that enables intelligent 
                  service discovery and invocation. It acts as a smart bridge between you and external APIs, 
                  automatically finding and calling the right service based on your natural language query.
                </p>
              </section>

              <section>
                <h3 class="text-xl font-semibold text-indigo-700 mb-2">🔄 The Process</h3>
                <div class="space-y-3">
                  <div class="flex items-start gap-3 p-3 bg-indigo-50 rounded-lg">
                    <span class="text-2xl">1️⃣</span>
                    <div>
                      <strong>You ask a question</strong>
                      <p class="text-sm">Example: "Find papers about neural networks"</p>
                    </div>
                  </div>

                  <div class="flex items-start gap-3 p-3 bg-indigo-50 rounded-lg">
                    <span class="text-2xl">2️⃣</span>
                    <div>
                      <strong>Service Discovery</strong>
                      <p class="text-sm">
                        Our AI analyzes your query and searches the UIM catalogue to find the best matching 
                        service (e.g., arXiv for academic papers, OpenWeather for weather data)
                      </p>
                    </div>
                  </div>

                  <div class="flex items-start gap-3 p-3 bg-indigo-50 rounded-lg">
                    <span class="text-2xl">3️⃣</span>
                    <div>
                      <strong>Service Invocation</strong>
                      <p class="text-sm">
                        The system automatically calls the selected service with the right parameters, 
                        handling API authentication and data formatting for you
                      </p>
                    </div>
                  </div>

                  <div class="flex items-start gap-3 p-3 bg-indigo-50 rounded-lg">
                    <span class="text-2xl">4️⃣</span>
                    <div>
                      <strong>You get results</strong>
                      <p class="text-sm">
                        The response is formatted in a clear, readable way with relevant information 
                        extracted from the API
                      </p>
                    </div>
                  </div>
                </div>
              </section>

              <section>
                <h3 class="text-xl font-semibold text-indigo-700 mb-2">🛠️ Technical Architecture</h3>
                <div class="bg-gray-50 p-4 rounded-lg font-mono text-sm">
                  <div>Your Query</div>
                  <div class="ml-4">↓ Discovery Agent (LLM-powered)</div>
                  <div class="ml-4">↓ UIM Catalogue (MongoDB)</div>
                  <div class="ml-4">↓ Service Invoker</div>
                  <div class="ml-4">↓ External API (arXiv, OpenWeather, etc.)</div>
                  <div class="ml-4">↓ Formatted Response</div>
                  <div>Back to You ✅</div>
                </div>
              </section>

              <section>
                <h3 class="text-xl font-semibold text-indigo-700 mb-2">🔌 Available Services</h3>
                <Show 
                  when={availableServices().length > 0}
                  fallback={
                    <p class="text-sm text-gray-500">Loading services from catalogue...</p>
                  }
                >
                  <ul class="list-disc list-inside space-y-1 text-sm">
                    <For each={availableServices()}>
                      {(service) => (
                        <li>
                          <strong>{service.name}</strong>
                          {service.description && ` - ${service.description}`}
                        </li>
                      )}
                    </For>
                  </ul>
                </Show>
                <p class="text-xs text-gray-500 mt-2">
                  * Some services require API keys. If you see an error about missing API keys, 
                  contact the system administrator to configure authentication.
                </p>
              </section>

              <section>
                <h3 class="text-xl font-semibold text-indigo-700 mb-2">🎓 Research Context</h3>
                <p class="text-sm">
                  This is a <strong>Level 2 UIM implementation</strong> created as part of a university 
                  research project at Fontys ICT. It demonstrates how UIM principles can work with 
                  existing non-UIM REST APIs by using the catalogue as a translation layer.
                </p>
              </section>
            </div>

            <button
              onClick={() => setShowHowItWorks(false)}
              class="mt-6 w-full px-4 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition font-semibold"
            >
              Got it! Let's try it
            </button>
          </div>
        </div>
      </Show>

      {/* Chat Messages Area */}
      <div class="flex-1 overflow-y-auto p-4">
        <div class="max-w-4xl mx-auto">
          <Show when={messages().length === 0}>
            <div class="text-center py-12">
              <div class="text-6xl mb-4">🤖</div>
              <h2 class="text-2xl font-semibold text-gray-700 mb-2">
                Welcome to DVerse Demo!
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
                        {msg.role === 'user' ? '👤 You' : msg.role === 'error' ? '⚠️ Error' : '🤖 DVerse Demo'}
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

                    {/* Structured Paper Rendering - Title and URL Only */}
                    <Show when={msg.service_invocation?.data?.papers}>
                      <div class="mt-4 space-y-3">
                        <For each={msg.service_invocation.data.papers}>
                          {(paper, index) => (
                            <div class="border-l-4 border-indigo-300 pl-3 py-1">
                              <div class="font-semibold text-gray-900">
                                {index() + 1}. {paper.title}
                              </div>
                              <Show when={paper.url || paper.pdf_url}>
                                <a
                                  href={paper.url || paper.pdf_url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  class="text-sm text-indigo-600 hover:text-indigo-800 mt-1 inline-block"
                                >
                                  📄 View PDF
                                </a>
                              </Show>
                            </div>
                          )}
                        </For>
                      </div>
                    </Show>

                    {/* Service Information */}
                    <Show when={msg.role === 'assistant' && msg.services_discovered?.length > 0}>
                      <div class="mt-3 pt-3 border-t border-gray-200">
                        <p class="text-xs text-gray-500 mb-1">Service Used:</p>
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
                  </div>
                </div>
              )}
            </For>
          </div>

          {/* Processing Status with Service Name */}
          <Show when={processingStatus()}>
            <div class="flex justify-start">
              <div class="bg-indigo-50 border-2 border-indigo-300 rounded-lg p-4 shadow-md">
                <div class="flex items-center space-x-3">
                  <div class="flex space-x-1">
                    <div class="w-2 h-2 bg-indigo-600 rounded-full animate-bounce"></div>
                    <div class="w-2 h-2 bg-indigo-600 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                    <div class="w-2 h-2 bg-indigo-600 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                  </div>
                  <span class="text-sm text-indigo-700 font-medium">{processingStatus()}</span>
                </div>
                {/* Show service badge if we know which service */}
                <Show when={currentService()}>
                  <div class="mt-2 flex items-center gap-2">
                    <span class="px-3 py-1 bg-indigo-600 text-white text-xs rounded-full font-semibold">
                      {currentService()}
                    </span>
                  </div>
                </Show>
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