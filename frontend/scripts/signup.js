import {url} from "./config.js"
import {showError} from "./config.js"

document.getElementById('signupForm').addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("email").value;
    const password = document.getElementById("pass").value;
    const confirmPassword = document.getElementById("cpass").value;

    if (!email || !password) {
        showError("Email and password are required");
        return;
    }
    if (password !== confirmPassword) {
        showError("Passwords do not match");
        return;
    }

    try {
        const response = await fetch(`${url}/api/signup`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password, confirmPassword }),
        });
        if (!response.ok) {
            const data = await response.json();
            showError(data.error || "Sign up failed. Please try again.");
            return;
        }
        const data = await response.json();
        if (data.redirect) {
            window.location.href = data.redirect;
        }
    } catch (error) {
        showError("Unable to connect to the server. Please try again later.");
    }
});