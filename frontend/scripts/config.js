export const url = 'https://task-manager-3ll7.onrender.com';

export function showError(message) {
    const errorBox = document.getElementById('errorBox');
    errorBox.textContent = message;
    errorBox.classList.remove('d-none');
    setTimeout(() => errorBox.classList.add('d-none'), 5000);
}