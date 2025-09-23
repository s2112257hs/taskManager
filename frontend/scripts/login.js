import {url} from "./config.js"
import {showError} from "./config.js"

document.getElementById('loginForm').addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    if (!email || !password) {
        showError("Email and password are required");
        return;
    }

    try {
        const response = await fetch(`${url}/api/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password }),
        });
        if (!response.ok) {
            const data = await response.json();
            showError(data.error || "Login failed. Please try again.");
            return;
        }
        const data = await response.json();
        if (data.token) {
            localStorage.setItem("token", data.token);
            window.location.href = data.redirect;
        }
    } catch (error) {
        showError("Unable to connect to the server. Please try again later.");
    }
});
