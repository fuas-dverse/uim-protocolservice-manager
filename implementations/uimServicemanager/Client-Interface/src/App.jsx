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
      setServices(data);
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
      setIntents(data);
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
      s.description.toLowerCase().includes(query)
    );
  };

  // Filtered intents
  const filteredIntents = () => {
    const query = searchQuery().toLowerCase();
    if (!query) return intents();
    return intents().filter(i =>
      i.name.toLowerCase().includes(query) ||
      i.description.toLowerCase().includes(query)
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
          <p class="text-gray-600">View all available intents for the AI agents.</p>
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
        <div class="text-center py-8">
          <p class="text-red-500 mb-2">{servicesError()}</p>
          <button
            onClick={fetchServices}
            class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Retry
          </button>
        </div>
      </Show>

      <Show when={!servicesLoading() && !servicesError()}>
        <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3 max-w-6xl mx-auto">
          <For each={filteredServices()}>
            {(service) => (
              <div class="bg-white p-5 border border-gray-200 rounded-lg shadow-md hover:shadow-lg transition">
                <h2 class="font-bold text-xl text-blue-700 mb-2">{service.name}</h2>
                <p class="text-gray-600 mb-3">{service.description}</p>
                <div class="text-sm text-gray-500">
                  <span class="font-semibold">URL:</span>
                  <a href={service.service_URL} target="_blank" class="text-blue-500 hover:underline ml-1">
                    {service.service_URL}
                  </a>
                </div>
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
        <div class="text-center py-8">
          <p class="text-red-500 mb-2">{intentsError()}</p>
          <button
            onClick={fetchIntents}
            class="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
          >
            Retry
          </button>
        </div>
      </Show>

      <Show when={!intentsLoading() && !intentsError()}>
        <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3 max-w-6xl mx-auto">
          <For each={filteredIntents()}>
            {(intent) => (
              <div class="bg-white p-5 border border-gray-200 rounded-lg shadow-md hover:shadow-lg transition">
                <h2 class="font-bold text-xl text-green-700 mb-2">{intent.name}</h2>
                <p class="text-gray-600 mb-3">{intent.description}</p>

                <Show when={intent.tags && intent.tags.length > 0}>
                  <div class="mb-3">
                    <span class="text-sm font-semibold text-gray-700">Tags:</span>
                    <div class="flex flex-wrap gap-1 mt-1">
                      <For each={intent.tags}>
                        {(tag) => (
                          <span class="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">
                            {tag}
                          </span>
                        )}
                      </For>
                    </div>
                  </div>
                </Show>

                <div class="text-sm text-gray-600 space-y-1">
                  <div>
                    <span class="font-semibold">Rate Limit:</span> {intent.rateLimit || 'N/A'}
                  </div>
                  <div>
                    <span class="font-semibold">Price:</span> {intent.price === 0 ? 'Free' : `$${intent.price}`}
                  </div>
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
    <div class="min-h-screen bg-gray-50">
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