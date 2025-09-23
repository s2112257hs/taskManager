import {url} from "./config.js"
import {showError} from "./config.js"


document.getElementById('logoutBtn').addEventListener('click', () => {
    localStorage.removeItem('token');
    window.location.href = "login.html";
});

function checkAuth() {
    const token = localStorage.getItem("token");
    if (!token) {
        window.location.href = "login.html";
        return false;
    }
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        const now = Math.floor(Date.now() / 1000);
        if (payload.exp && payload.exp < now) {
            localStorage.removeItem("token");
            window.location.href = "login.html";
            return false;
        }
        return true;
    } catch (e) {
        localStorage.removeItem("token");
        window.location.href = "login.html";
        return false;
    }
}

async function apiRequest(url, options = {}) {
    if (!checkAuth()) {
        return;
    }
    const token = localStorage.getItem("token");
    if (!options.headers) {
        options.headers = {};
    }
    if (token) {
        options.headers["Authorization"] = `Bearer ${token}`;
    }
    try {
        const response = await fetch(url, options);
        if (!response.ok) {
            if (response.status === 401 || response.status === 403) {
                localStorage.removeItem("token");
                showError("Session expired or invalid. Please log in again.");
                window.location.href = "login.html";
                return null;
            }
            return response; // Other errors (e.g., 400, 500) handled by caller
        }
        return response;
    } catch (error) {
        showError("Unable to connect to the server. Please try again later.");
        return null;
    }
}


document.getElementById('taskForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const title = document.getElementById('taskTitle').value;
    const description = document.getElementById('taskDescription').value;
    const dueDate = document.getElementById('taskDueDate').value;
    const status = document.getElementById('taskStatus').value;

    if (!title.trim()) {
        showError("Task title is required");
        return;
    }

    const response = await apiRequest(`${url}/api/tasks`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, description, dueDate, status })
    });

    if (response) {
        const data = await response.json();
        if (data.error) {
            showError(data.error);
        } else {
            document.getElementById('taskForm').reset();
            renderTasks();
        }
    }
});

async function renderTasks() {
    const response = await apiRequest(`${url}/api/tasks`, { method: "GET" });
    if (!response) return;
    const data = await response.json();
    data.sort((a, b) => (a.status === "pending" && b.status === "completed") ? -1 : (a.status === "completed" && b.status === "pending") ? 1 : 0);
    const taskList = document.getElementById('taskList');
    taskList.innerHTML = '';
    data.forEach(task => {
        const li = document.createElement("li");
        li.className = `list-group-item d-flex align-items-center ${task.status === "completed" ? "text-muted" : ""}`;
        li.innerHTML = `
            <span class="title flex-grow-1 ${task.status === "completed" ? "text-decoration-line-through" : ""}">${task.title ?? ""}</span>
            <span class="description me-3">${task.description ?? ""}</span>
            <span class="dueDate me-3">${task.due_date ? "Due: " + task.due_date : ""}</span>
            <span class="status me-3">${task.status}</span>
            <button class="editBtn btn btn-outline-primary btn-sm me-2">Edit</button>
            <button class="deleteBtn btn btn-outline-danger btn-sm">Delete</button>
        `;

        li.querySelector('.deleteBtn').addEventListener('click', async () => {
            const response = await apiRequest(`${url}/api/tasks/${task.id}`, {
                method: "DELETE"
            });
            if (response) {
                const data = await response.json();
                if (data.error) {
                    showError(data.error);
                }
                renderTasks();
            }
        });

        li.querySelector('.editBtn').addEventListener('click', () => {
            li.innerHTML = `
                <div class="row g-2">
                    <div class="col-md-3">
                        <input class="edit-title form-control" value="${task.title ?? ""}">
                    </div>
                    <div class="col-md-3">
                        <input class="edit-description form-control" value="${task.description ?? ""}">
                    </div>
                    <div class="col-md-3">
                        <input class="edit-dueDate form-control" type="date" value="${task.due_date ?? ""}">
                    </div>
                    <div class="col-md-2">
                        <select class="edit-status form-select">
                            <option value="pending" ${task.status === "pending" ? "selected" : ""}>Pending</option>
                            <option value="completed" ${task.status === "completed" ? "selected" : ""}>Completed</option>
                        </select>
                    </div>
                    <div class="col-md-1 d-flex">
                        <button class="saveBtn btn btn-primary btn-sm me-1">Save</button>
                        <button class="cancelBtn btn btn-secondary btn-sm">Cancel</button>
                    </div>
                </div>
            `;

            li.querySelector('.cancelBtn').addEventListener('click', () => {
                renderTasks();
            });

            li.querySelector('.saveBtn').addEventListener('click', async () => {
                const title = li.querySelector('.edit-title').value;
                const description = li.querySelector('.edit-description').value;
                const dueDate = li.querySelector('.edit-dueDate').value;
                const status = li.querySelector('.edit-status').value;

                if (!title.trim()) {
                    showError("Task title is required");
                    return;
                }

                const response = await apiRequest(`${url}/api/tasks/${task.id}`, {
                    method: "PUT",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ title, description, dueDate, status })
                });

                if (response) {
                    const data = await response.json();
                    if (data.error) {
                        showError(data.error);
                    }
                    renderTasks();
                }
            });
        });

        taskList.appendChild(li);
    });
}

checkAuth();
renderTasks();
