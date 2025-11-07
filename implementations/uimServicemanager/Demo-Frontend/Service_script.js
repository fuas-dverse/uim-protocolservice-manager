const listEl = document.getElementById('service-list');
const searchEl = document.getElementById('search');
let services = [];

// Fetch services from API
async function loadServices() {
  try {
    const response = await fetch('http://localhost:5000/services');
    services = await response.json();
    renderServices();
  } catch (error) {
    console.error('Failed to load services:', error);
    listEl.innerHTML = '<p class="text-red-500">Failed to load services.</p>';
  }
}

// Render filtered services
function renderServices(filter = '') {
  listEl.innerHTML = '';
  const filtered = services.filter(s =>
    s.name.toLowerCase().includes(filter.toLowerCase())
  );
  filtered.forEach(service => {
    const card = document.createElement('div');
    card.className = 'card';
    card.innerHTML = `<h2 class="font-bold">${service.name}</h2>
                      <p>${service.description}</p>`;
    listEl.appendChild(card);
  });
}

// Filter as user types
searchEl.addEventListener('input', (e) => {
  renderServices(e.target.value);
});

// Initial load
loadServices();
