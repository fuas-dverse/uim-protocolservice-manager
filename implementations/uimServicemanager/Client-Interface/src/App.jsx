import { createSignal, createEffect, Show, For } from 'solid-js';

function App() {
  const [activeTab, setActiveTab] = createSignal('home');
  const [services, setServices] = createSignal([]);
  const [intents, setIntents] = createSignal([]);
  const [servicesLoading, setServicesLoading] = createSignal(false);
  const [intentsLoading, setIntentsLoading] = createSignal(false);
  const [servicesError, setServicesError] = createSignal(null);
  const [intentsError, setIntentsError] = createSignal(null);
  const [searchQuery, setSearchQuery] = createSignal('');

  // Fetch services
  const fetchServices = async () => {
    try {
      setServicesLoading(true);
      const response = await fetch('http://localhost:8000/services');
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();

      // ✅ FIXED: Handle new API response format
      // API now returns { services: [...], total: N }
      const servicesArray = data.services || data;
      setServices(servicesArray);
      setServicesError(null);
    } catch (err) {
      console.error('Failed to load services:', err);
      setServicesError('Failed to load services. Make sure API is running on port 8000.');
    } finally {
      setServicesLoading(false);
    }
  };

  // Fetch intents
  const fetchIntents = async () => {
    try {
      setIntentsLoading(true);
      const response = await fetch('http://localhost:8000/intents');
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();

      // ✅ FIXED: Handle new API response format
      // API now returns { intents: [...], total: N }
      const intentsArray = data.intents || data;
      setIntents(intentsArray);
      setIntentsError(null);
    } catch (err) {
      console.error('Failed to load intents:', err);
      setIntentsError('Failed to load intents. Make sure API is running on port 8000.');
    } finally {
      setIntentsLoading(false);
    }
  };

  // Load data when switching tabs
  createEffect(() => {
    if (activeTab() === 'services' && services().length === 0) {
      fetchServices();
    }
    if (activeTab() === 'intents' && intents().length === 0) {
      fetchIntents();
    }
  });

  // Filtered services
  const filteredServices = () => {
    const query = searchQuery().toLowerCase();
    if (!query) return services();
    return services().filter(s =>
      s.name.toLowerCase().includes(query) ||
      (s.description && s.description.toLowerCase().includes(query))
    );
  };

  // Filtered intents
  const filteredIntents = () => {
    const query = searchQuery().toLowerCase();
    if (!query) return intents();
    return intents().filter(i =>
      (i.intent_name && i.intent_name.toLowerCase().includes(query)) ||
      (i.description && i.description.toLowerCase().includes(query))
    );
  };

  // Home Page
  const HomePage = () => (
    <div class="flex flex-col items-center justify-center min-h-[70vh]">
      <header class="mb-10 text-center">
        <h1 class="text-4xl font-bold text-blue-600 mb-2">UIM Catalogue</h1>
        <p class="text-gray-700">Browse Services and Intents</p>
      </header>

      <div class="grid gap-6 md:grid-cols-2 w-full max-w-4xl px-4">
        <button
          onClick={() => setActiveTab('services')}
          class="bg-white p-8 rounded-lg shadow-lg text-center hover:bg-blue-50 transition cursor-pointer border-2 border-transparent hover:border-blue-300"
        >
          <h2 class="text-2xl font-semibold text-blue-600 mb-2">Services</h2>
          <p class="text-gray-600">View all registered services in the UIM catalogue.</p>
        </button>

        <button
          onClick={() => setActiveTab('intents')}
          class="bg-white p-8 rounded-lg shadow-lg text-center hover:bg-green-50 transition cursor-pointer border-2 border-transparent hover:border-green-300"
        >
          <h2 class="text-2xl font-semibold text-green-600 mb-2">Intents</h2>
          <p class="text-gray-600">Explore all available intents and capabilities.</p>
        </button>
      </div>
    </div>
  );

  // Services Page
  const ServicesPage = () => (
    <div class="p-6">
      <header class="text-center mb-6">
        <h1 class="text-3xl font-bold text-blue-600">Services Catalogue</h1>
        <button
          onClick={() => setActiveTab('home')}
          class="text-blue-500 hover:underline mt-2"
        >
          ← Back to Home
        </button>
      </header>

      <div class="mb-4 max-w-2xl mx-auto">
        <input
          type="text"
          placeholder="Search services..."
          class="w-full p-3 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          value={searchQuery()}
          onInput={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      <Show when={servicesLoading()}>
        <p class="text-center text-gray-600 py-8">Loading services...</p>
      </Show>

      <Show when={servicesError()}>
        <div class="max-w-2xl mx-auto bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
          {servicesError()}
        </div>
      </Show>

      <Show when={!servicesLoading() && !servicesError()}>
        <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3 max-w-7xl mx-auto">
          <For each={filteredServices()}>
            {(service) => (
              <div class="bg-white p-5 border border-gray-200 rounded-lg shadow-md hover:shadow-lg transition">
                <h2 class="font-bold text-xl text-blue-700 mb-2">{service.name}</h2>
                <p class="text-gray-600 mb-3">{service.description || 'No description'}</p>
                <div class="text-sm text-gray-500">
                  <span class="font-semibold">URL:</span>
                  {/* ✅ FIXED: Changed service_URL to service_url */}
                  <a href={service.service_url} target="_blank" class="text-blue-500 hover:underline ml-1 break-all">
                    {service.service_url}
                  </a>
                </div>
                <Show when={service.intents && service.intents.length > 0}>
                  <div class="mt-3 pt-3 border-t border-gray-200">
                    <p class="text-sm text-gray-600">
                      <span class="font-semibold">Intents:</span> {service.intents.length}
                    </p>
                  </div>
                </Show>
              </div>
            )}
          </For>
        </div>

        <Show when={filteredServices().length === 0}>
          <p class="text-center text-gray-500 mt-8">No services found matching "{searchQuery()}"</p>
        </Show>
      </Show>
    </div>
  );

  // Intents Page
  const IntentsPage = () => (
    <div class="p-6">
      <header class="text-center mb-6">
        <h1 class="text-3xl font-bold text-green-600">Intents Catalogue</h1>
        <button
          onClick={() => setActiveTab('home')}
          class="text-green-500 hover:underline mt-2"
        >
          ← Back to Home
        </button>
      </header>

      <div class="mb-4 max-w-2xl mx-auto">
        <input
          type="text"
          placeholder="Search intents..."
          class="w-full p-3 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-green-500 focus:border-transparent"
          value={searchQuery()}
          onInput={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      <Show when={intentsLoading()}>
        <p class="text-center text-gray-600 py-8">Loading intents...</p>
      </Show>

      <Show when={intentsError()}>
        <div class="max-w-2xl mx-auto bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
          {intentsError()}
        </div>
      </Show>

      <Show when={!intentsLoading() && !intentsError()}>
        <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3 max-w-7xl mx-auto">
          <For each={filteredIntents()}>
            {(intent) => (
              <div class="bg-white p-5 border border-gray-200 rounded-lg shadow-md hover:shadow-lg transition">
                {/* ✅ FIXED: Changed intent.name to intent.intent_name */}
                <h2 class="font-bold text-xl text-green-700 mb-2">{intent.intent_name}</h2>
                <p class="text-gray-600 mb-3">{intent.description || 'No description'}</p>
                <Show when={intent.tags && intent.tags.length > 0}>
                  <div class="flex flex-wrap gap-1 mb-2">
                    <For each={intent.tags}>
                      {(tag) => (
                        <span class="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                          {tag}
                        </span>
                      )}
                    </For>
                  </div>
                </Show>
                <div class="text-sm text-gray-500 space-y-1">
                  <Show when={intent.http_method}>
                    <p><span class="font-semibold">Method:</span> {intent.http_method}</p>
                  </Show>
                  <Show when={intent.endpoint_path}>
                    <p><span class="font-semibold">Path:</span> {intent.endpoint_path}</p>
                  </Show>
                  <Show when={intent.rateLimit}>
                    <p><span class="font-semibold">Rate Limit:</span> {intent.rateLimit}/min</p>
                  </Show>
                  <Show when={intent.price !== undefined}>
                    <p><span class="font-semibold">Price:</span> ${intent.price}</p>
                  </Show>
                </div>
              </div>
            )}
          </For>
        </div>

        <Show when={filteredIntents().length === 0}>
          <p class="text-center text-gray-500 mt-8">No intents found matching "{searchQuery()}"</p>
        </Show>
      </Show>
    </div>
  );

  return (
    <div class="bg-gray-50 min-h-screen font-sans">
      <Show when={activeTab() === 'home'}>
        <HomePage />
      </Show>
      <Show when={activeTab() === 'services'}>
        <ServicesPage />
      </Show>
      <Show when={activeTab() === 'intents'}>
        <IntentsPage />
      </Show>
    </div>
  );
}

export default App;