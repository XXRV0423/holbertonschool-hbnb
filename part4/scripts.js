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

  Task: Place details (part4 task3)
  - Reads the place id from the URL (place.html?id=...).
  - Fetches that place's details from the API and renders them.
  - Shows the "Add a Review" link only if the user is authenticated.
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
        const token = checkAuthentication();
        if (token) fetchPlaces(token);
        setupPriceFilter();
    }

    if (document.getElementById('place-details')) {
        const placeId = getPlaceIdFromURL();
        const token = checkAuthentication();

        const addReviewSection = document.getElementById('add-review');
        if (addReviewSection) {
            addReviewSection.style.display = token ? 'block' : 'none';

            const reviewLink = addReviewSection.querySelector('.details-button');
            if (reviewLink && placeId) {
                reviewLink.href = `add_review.html?id=${placeId}`;
            }
        }

        if (!placeId) {
            console.error('No place ID found in the URL.');
        } else if (token) {
            fetchPlaceDetails(token, placeId);
        }
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
 * present. Returns the token (or null) so callers can decide what
 * page-specific data to fetch.
 */
function checkAuthentication() {
    const token = getCookie('token');
    const loginLink = document.getElementById('login-link');

    if (!token) {
        if (loginLink) loginLink.style.display = 'inline-block';
    } else {
        if (loginLink) loginLink.style.display = 'none';
    }

    return token;
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

/**
 * Reads the "id" query parameter from the current URL, e.g.
 * place.html?id=<uuid> -> <uuid>.
 */
function getPlaceIdFromURL() {
    const params = new URLSearchParams(window.location.search);
    return params.get('id');
}

/**
 * Fetches a single place's details from the API. Includes the JWT in
 * the Authorization header when available.
 */
async function fetchPlaceDetails(token, placeId) {
    try {
        const headers = {};
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await fetch(`${API_BASE_URL}/places/${placeId}`, {
            method: 'GET',
            headers: headers
        });

        if (response.ok) {
            const place = await response.json();
            await displayPlaceDetails(place);
        } else {
            console.error('Failed to fetch place details:', response.status, response.statusText);
        }
    } catch (error) {
        console.error('Error fetching place details:', error);
    }
}

// Best-effort icon match for common amenity names. Unmatched amenities
// are still listed, just without an icon.
function getAmenityIcon(name) {
    const lower = name.toLowerCase();
    if (lower.includes('wifi')) return 'images/icon_wifi.png';
    if (lower.includes('bed')) return 'images/icon_bed.png';
    if (lower.includes('bath')) return 'images/icon_bath.png';
    return null;
}

// Reviews only carry a user_id, so reviewer names are looked up from
// GET /users/<id> (a public endpoint) and cached to avoid re-fetching
// the same reviewer more than once per page load.
const userNameCache = new Map();

async function getUserName(userId) {
    if (!userId) return 'Guest';
    if (userNameCache.has(userId)) return userNameCache.get(userId);

    let name = 'Guest';
    try {
        const response = await fetch(`${API_BASE_URL}/users/${userId}`);
        if (response.ok) {
            const user = await response.json();
            name = `${user.first_name} ${user.last_name}`;
        }
    } catch (error) {
        console.error('Error fetching reviewer name:', error);
    }

    userNameCache.set(userId, name);
    return name;
}

/**
 * Renders the fetched place into #place-details and #reviews, and
 * updates the page title/heading with the place's name.
 */
async function displayPlaceDetails(place) {
    document.title = `Place Details - ${place.title}`;

    const pageTitle = document.querySelector('h1.page-title');
    if (pageTitle) pageTitle.textContent = place.title;

    const placeDetailsSection = document.getElementById('place-details');
    if (placeDetailsSection) {
        // Beds/bathrooms are dedicated numeric fields on the place (not
        // generic amenities), shown first with the same icons the
        // original design used.
        const roomCountItems = [];
        if (place.beds) {
            const label = place.beds === 1 ? 'Bed' : 'Beds';
            roomCountItems.push(`<li><img src="images/icon_bed.png" alt="Beds icon" class="amenity-icon"> ${place.beds} ${label}</li>`);
        }
        if (place.bathrooms) {
            const label = place.bathrooms === 1 ? 'Bathroom' : 'Bathrooms';
            roomCountItems.push(`<li><img src="images/icon_bath.png" alt="Bathrooms icon" class="amenity-icon"> ${place.bathrooms} ${label}</li>`);
        }

        const amenities = place.amenities || [];
        const amenityItems = amenities.map((amenity) => {
            const icon = getAmenityIcon(amenity.name);
            const iconTag = icon
                ? `<img src="${icon}" alt="${amenity.name} icon" class="amenity-icon"> `
                : '';
            return `<li>${iconTag}${amenity.name}</li>`;
        });

        const allItems = roomCountItems.concat(amenityItems);
        const amenitiesHTML = allItems.length ? allItems.join('') : '<li>No amenities listed</li>';

        placeDetailsSection.innerHTML = `
            <div class="place-info">
                <p><strong>Host:</strong> ${place.owner ? `${place.owner.first_name} ${place.owner.last_name}` : 'Unknown'}</p>
                <p><strong>Price per night:</strong> $${place.price}</p>
                <p><strong>Description:</strong> ${place.description || 'No description provided.'}</p>

                <div class="amenities">
                    <h3>Amenities</h3>
                    <ul>${amenitiesHTML}</ul>
                </div>
            </div>
        `;
    }

    const reviewsSection = document.getElementById('reviews');
    if (reviewsSection) {
        const reviews = place.reviews || [];
        reviewsSection.innerHTML = '<h2>Reviews</h2>';

        if (reviews.length === 0) {
            const empty = document.createElement('p');
            empty.textContent = 'No reviews yet.';
            reviewsSection.appendChild(empty);
        } else {
            for (const review of reviews) {
                const name = await getUserName(review.user_id);

                const card = document.createElement('article');
                card.className = 'review-card';
                card.innerHTML = `
                    <p class="review-user"><strong>${name}:</strong></p>
                    <p class="review-comment">${review.text}</p>
                    <p class="review-rating">Rating: ${review.rating}/5</p>
                `;
                reviewsSection.appendChild(card);
            }
        }
    }
}
