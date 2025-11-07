const listEl = document.getElementById('intent-list');
const searchEl = document.getElementById('search');
let intents = [];

// Fetch intents from API
async function loadIntents() {
  try {
    const response = await fetch('http://localhost:5000/intents'); // <-- your intents endpoint
    intents = await response.json();
    renderIntents();
  } catch (error) {
    console.error('Failed to load intents:', error);
    listEl.innerHTML = '<p class="text-red-500">Failed to load intents.</p>';
  }
}

// Render filtered intents
function renderIntents(filter = '') {
  listEl.innerHTML = '';
  const filtered = intents.filter(i =>
    i.name.toLowerCase().includes(filter.toLowerCase())
  );
  filtered.forEach(intent => {
    const card = document.createElement('div');
    card.className = 'card bg-white p-4 border rounded shadow';
    card.innerHTML = `<h2 class="font-bold text-lg">${intent.name}</h2>
                      <p>${intent.description || 'No description'}</p>`;
    listEl.appendChild(card);
  });
}

// Filter as user types
searchEl.addEventListener('input', (e) => {
  renderIntents(e.target.value);
});

// Initial load
loadIntents();
