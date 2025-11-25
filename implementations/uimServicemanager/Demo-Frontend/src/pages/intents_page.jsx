import { createSignal, createEffect, Show, For } from 'solid-js';
import { A } from '@solidjs/router';

function Intents() {
  const [intents, setIntents] = createSignal([]);
  const [searchQuery, setSearchQuery] = createSignal('');
  const [loading, setLoading] = createSignal(true);
  const [error, setError] = createSignal(null);

  // Fetch intents on mount
  createEffect(async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/intents');
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setIntents(data);
      setError(null);
    } catch (err) {
      console.error('Failed to load intents:', err);
      setError('Failed to load intents. Make sure the API is running on port 8000.');
    } finally {
      setLoading(false);
    }
  });

  // Filtered intents based on search
  const filteredIntents = () => {
    const query = searchQuery().toLowerCase();
    if (!query) return intents();
    
    return intents().filter(intent => 
      intent.name.toLowerCase().includes(query)
    );
  };

  return (
    <div class="bg-gray-50 p-6 font-sans min-h-screen">
      <header class="text-center mb-6">
        <h1 class="text-3xl font-bold text-green-600">UIM Intents</h1>
        <A href="/" class="text-green-500 hover:underline mt-2 inline-block">← Back to Home</A>
      </header>

      <div class="mb-4">
        <input 
          id="search"
          type="text" 
          placeholder="Search intents..." 
          class="w-full p-2 border rounded"
          value={searchQuery()}
          onInput={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      <Show when={loading()}>
        <p class="text-center text-gray-600">Loading intents...</p>
      </Show>

      <Show when={error()}>
        <p class="text-center text-red-500">{error()}</p>
      </Show>

      <Show when={!loading() && !error()}>
        <div class="grid gap-4 md:grid-cols-2">
          <For each={filteredIntents()}>
            {(intent) => (
              <div class="card bg-white p-4 border rounded shadow">
                <h2 class="font-bold text-lg">{intent.name}</h2>
                <p class="text-gray-600">{intent.description || 'No description'}</p>
              </div>
            )}
          </For>
        </div>
        
        <Show when={filteredIntents().length === 0 && !loading()}>
          <p class="text-center text-gray-500 mt-4">No intents found.</p>
        </Show>
      </Show>
    </div>
  );
}

export default Intents;