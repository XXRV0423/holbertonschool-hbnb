/*
  HBnB Evolution - front-end scripts.

  Task: Login (part4 task1)
  - Submits the login form to the back-end API.
  - Stores the returned JWT in a cookie.
  - Redirects to index.html on success, shows an error on failure.
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
