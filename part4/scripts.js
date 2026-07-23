/*
  HBnB Evolution - front-end scripts.

  Task: Login (part4 task1)
  - Submits the login form to the back-end API.
  - Stores the returned JWT in a cookie.
  - Redirects to index.html on success, shows an error on failure.

  Task: List of places (part4 task2)
  - Checks for a JWT token in cookies to show/hide the login link.
  - Fetches the list of places from the API and renders them as cards.
  - Filters the rendered places client-side by max price.
*/

// Base URL of the Flask API. Change this if you updated the Flask and is running somewhere else.
const API_BASE_URL = 'http://127.0.0.1:5000/api/v1';

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');

    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            hideLoginError();

            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            await loginUser(email, password);
        });
    }

    if (document.getElementById('places-list')) {
        populatePriceFilter();
        checkAuthentication();
        setupPriceFilter();
    }
});

/**
 * Sends the user's credentials to the login endpoint. On success, stores
 * the JWT in a cookie and redirects to the main page. On failure, shows
 * an error message on the form.
 */
async function loginUser(email, password) {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });

        if (response.ok) {
            const data = await response.json();
            document.cookie = `token=${data.access_token}; path=/`;
            window.location.href = 'index.html';
        } else {
            const data = await response.json().catch(() => ({}));
            showLoginError(data.error || 'Invalid email or password.');
        }
    } catch (error) {
        showLoginError('Could not reach the server. Please try again later.');
    }
}

function showLoginError(message) {
    const errorEl = document.getElementById('login-error');
    if (errorEl) {
        errorEl.textContent = message;
        errorEl.hidden = false;
    } else {
        alert('Login failed: ' + message);
    }
}

function hideLoginError() {
    const errorEl = document.getElementById('login-error');
    if (errorEl) {
        errorEl.hidden = true;
        errorEl.textContent = '';
    }
}

/**
 * Reads a cookie value by name. Returns null if the cookie isn't set.
 */
function getCookie(name) {
    const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    return match ? match[2] : null;
}

/**
 * Shows/hides the login link based on whether a JWT token cookie is
 * present, and triggers the places fetch when the user is authenticated.
 */
function checkAuthentication() {
    const token = getCookie('token');
    const loginLink = document.getElementById('login-link');

    if (!token) {
        if (loginLink) loginLink.style.display = 'inline-block';
    } else {
        if (loginLink) loginLink.style.display = 'none';
        fetchPlaces(token);
    }
}

/**
 * Fetches the list of places from the API. Includes the JWT in the
 * Authorization header when available.
 */
async function fetchPlaces(token) {
    try {
        const headers = {};
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await fetch(`${API_BASE_URL}/places/`, {
            method: 'GET',
            headers: headers
        });

        if (response.ok) {
            const places = await response.json();
            displayPlaces(places);
        } else {
            console.error('Failed to fetch places:', response.status, response.statusText);
        }
    } catch (error) {
        console.error('Error fetching places:', error);
    }
}

/**
 * Clears #places-list and renders one .place-card per place returned
 * by the API.
 */
function displayPlaces(places) {
    const placesList = document.getElementById('places-list');
    if (!placesList) return;

    placesList.innerHTML = '';

    places.forEach((place) => {
        const card = document.createElement('article');
        card.className = 'place-card';
        card.dataset.price = place.price;

        card.innerHTML = `
            <h2>${place.title}</h2>
            <p class="price">Price per night: $${place.price}</p>
            <a href="place.html?id=${place.id}" class="details-button">View Details</a>
        `;

        placesList.appendChild(card);
    });
}

/**
 * Builds the "Max Price" dropdown options: 10, 50, 100, All.
 */
function populatePriceFilter() {
    const filter = document.getElementById('price-filter');
    if (!filter) return;

    const options = [
        { value: '10', label: '$10' },
        { value: '50', label: '$50' },
        { value: '100', label: '$100' },
        { value: 'all', label: 'All' }
    ];

    filter.innerHTML = '';
    options.forEach(({ value, label }) => {
        const option = document.createElement('option');
        option.value = value;
        option.textContent = label;
        filter.appendChild(option);
    });
}

/**
 * Hides/shows rendered place cards based on the selected max price,
 * without reloading the page or re-fetching data.
 */
function setupPriceFilter() {
    const filter = document.getElementById('price-filter');
    if (!filter) return;

    filter.addEventListener('change', (event) => {
        const maxPrice = event.target.value;
        const places = document.querySelectorAll('#places-list .place-card');

        places.forEach((place) => {
            const price = parseFloat(place.dataset.price);
            const withinLimit = maxPrice === 'all' || price <= parseFloat(maxPrice);
            place.style.display = withinLimit ? '' : 'none';
        });
    });
}
