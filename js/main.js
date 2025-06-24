const loginBtn = document.getElementById('loginBtn');
const loginModal = document.getElementById('loginModal');
const closeModal = document.getElementById('closeModal');
const loginForm = document.getElementById('login-form');
const loginError = document.getElementById('login-error');
const searchInput = document.getElementById('searchInput');
const carouselInner = document.getElementById('carouselInner');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');

let currentIndex = 0;
let products = [];
const itemsPerPage = 4;

// Login modal handlers
loginBtn.addEventListener('click', () => {
  loginModal.classList.remove('hidden');
});

closeModal.addEventListener('click', () => {
  loginModal.classList.add('hidden');
  loginError.textContent = '';
  loginError.classList.add('hidden');
  loginForm.reset();
});

loginForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  loginError.textContent = '';
  loginError.classList.add('hidden');

  const email = loginForm.email.value;
  const password = loginForm.password.value;

  try {
    const res = await fetch('/login', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({email, password})
    });
    const data = await res.json();
    if (res.ok) {
      localStorage.setItem('token', data.token);
      localStorage.setItem('role', data.role);
      loginModal.classList.add('hidden');
      loginForm.reset();
      alert('Inicio de sesión exitoso');
    } else {
      loginError.textContent = data.message || 'Credenciales inválidas';
      loginError.classList.remove('hidden');
    }
  } catch (err) {
    loginError.textContent = 'Error de conexión';
    loginError.classList.remove('hidden');
  }
});

// Carousel functions
function updateCarousel() {
  const offset = -currentIndex * 100;
  carouselInner.style.transform = `translateX(${offset}%)`;
}

prevBtn.addEventListener('click', () => {
  currentIndex = (currentIndex - 1 + Math.ceil(products.length / itemsPerPage)) % Math.ceil(products.length / itemsPerPage);
  updateCarousel();
});

nextBtn.addEventListener('click', () => {
  currentIndex = (currentIndex + 1) % Math.ceil(products.length / itemsPerPage);
  updateCarousel();
});

// Fetch and render products
async function fetchProducts() {
  try {
    const res = await fetch('/products');
    if (!res.ok) throw new Error('Error fetching products');
    products = await res.json();
    renderProducts(products);
  } catch (error) {
    console.error(error);
  }
}

function renderProducts(productsToRender) {
  carouselInner.innerHTML = '';
  productsToRender.forEach(product => {
    const productCard = document.createElement('div');
    productCard.className = 'min-w-[25%] p-2';
    productCard.innerHTML = `
      <div class="border border-gray-300 rounded-lg p-4 hover:shadow-lg transition">
        <div class="h-40 bg-gray-200 rounded-md mb-4 flex items-center justify-center text-gray-400">Imagen</div>
        <h3 class="font-semibold text-lg text-blue-900 mb-2">${product.name}</h3>
        <p class="text-yellow-500 font-bold mb-2">$${product.price.toFixed(2)}</p>
        <button class="w-full bg-yellow-400 text-blue-900 font-semibold py-2 rounded-md hover:bg-yellow-500 transition" onclick="addToCart(${product.id})">
          Comprar
        </button>
      </div>
    `;
    carouselInner.appendChild(productCard);
  });
}

// Add to cart function
async function addToCart(productId) {
  const token = localStorage.getItem('token');
  if (!token) {
    alert('Por favor, inicia sesión para agregar productos al carrito.');
    return;
  }
  try {
    const res = await fetch('/cart', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ product_id: productId, quantity: 1 })
    });
    if (res.ok) {
      alert('Producto agregado al carrito');
    } else {
      const data = await res.json();
      alert(data.message || 'Error al agregar al carrito');
    }
  } catch (error) {
    alert('Error de conexión');
  }
}

// Search functionality
async function handleSearch() {
  const query = searchInput.value.toLowerCase();
  const filtered = products.filter(p => p.name.toLowerCase().includes(query));
  renderProducts(filtered);
}

searchInput.addEventListener('input', handleSearch);

// Initial load
fetchProducts();
