import { createSignal, createEffect, Show, For } from 'solid-js';
import { A } from '@solidjs/router';

function Services() {
  const [services, setServices] = createSignal([]);
  const [searchQuery, setSearchQuery] = createSignal('');
  const [loading, setLoading] = createSignal(true);
  const [error, setError] = createSignal(null);

  // Fetch services on mount
  createEffect(async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/services');
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setServices(data);
      setError(null);
    } catch (err) {
      console.error('Failed to load services:', err);
      setError('Failed to load services. Make sure the API is running on port 8000.');
    } finally {
      setLoading(false);
    }
  });

  // Filtered services based on search
  const filteredServices = () => {
    const query = searchQuery().toLowerCase();
    if (!query) return services();
    
    return services().filter(service => 
      service.name.toLowerCase().includes(query)
    );
  };

  return (
    <div class="bg-gray-50 p-6 font-sans min-h-screen">
      <header class="text-center mb-6">
        <h1 class="text-3xl font-bold text-blue-600">UIM Catalogue</h1>
        <A href="/" class="text-blue-500 hover:underline mt-2 inline-block">← Back to Home</A>
      </header>

      <div class="mb-4">
        <input 
          id="search"
          type="text" 
          placeholder="Search services..." 
          class="w-full p-2 border rounded"
          value={searchQuery()}
          onInput={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      <Show when={loading()}>
        <p class="text-center text-gray-600">Loading services...</p>
      </Show>

      <Show when={error()}>
        <p class="text-center text-red-500">{error()}</p>
      </Show>

      <Show when={!loading() && !error()}>
        <div class="grid gap-4 md:grid-cols-2">
          <For each={filteredServices()}>
            {(service) => (
              <div class="card">
                <h2 class="font-bold text-lg">{service.name}</h2>
                <p class="text-gray-600">{service.description}</p>
              </div>
            )}
          </For>
        </div>
        
        <Show when={filteredServices().length === 0 && !loading()}>
          <p class="text-center text-gray-500 mt-4">No services found.</p>
        </Show>
      </Show>
    </div>
  );
}

export default Services;