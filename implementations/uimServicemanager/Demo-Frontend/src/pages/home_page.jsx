import { A } from '@solidjs/router';

function Home() {
  return (
    <div class="bg-gray-50 flex flex-col items-center justify-center min-h-screen font-sans">
      <header class="mb-10 text-center">
        <h1 class="text-4xl font-bold text-blue-600 mb-2">UIM Catalogue</h1>
        <p class="text-gray-700">Browse Services and Intents</p>
      </header>

      <div class="grid gap-6 md:grid-cols-2">
        <A 
          href="/services" 
          class="block bg-white p-6 rounded-lg shadow-lg text-center hover:bg-blue-50 transition"
        >
          <h2 class="text-2xl font-semibold text-blue-600 mb-2">Services</h2>
          <p class="text-gray-600">View all registered services in the UIM catalogue.</p>
        </A>

        <A 
          href="/intents" 
          class="block bg-white p-6 rounded-lg shadow-lg text-center hover:bg-green-50 transition"
        >
          <h2 class="text-2xl font-semibold text-green-600 mb-2">Intents</h2>
          <p class="text-gray-600">View all available intents for the AI agents.</p>
        </A>
      </div>
    </div>
  );
}

export default Home;