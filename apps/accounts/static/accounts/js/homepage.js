const body = document.querySelector('body');
const sidebar = body.querySelector('nav');
const toggle = body.querySelector(".toggle");
const searchBtn = body.querySelector(".search-box");
const modeSwitch = body.querySelector(".toggle-switch");
const modeText = body.querySelector(".mode-text");

// Função para definir o estado do modo com base na preferência armazenada
function setModeFromStorage() {
    const isDarkMode = localStorage.getItem('darkMode') === 'true';
    body.classList.toggle('dark', isDarkMode);

    if (isDarkMode) {
        modeText.innerText = "Light mode";
    } else {
        modeText.innerText = "Dark mode";
    }
}

// Função para definir o estado da barra lateral com base na preferência armazenada
function setSidebarStateFromStorage() {
    const isSidebarClosed = localStorage.getItem('sidebarClosed') === 'true';
    sidebar.classList.toggle('close', isSidebarClosed);
}

// Adiciona um ouvinte de evento para alternar o estado do modo e armazenar a preferência
modeSwitch.addEventListener("click", () => {
    body.classList.toggle("dark");

    const isDarkMode = body.classList.contains("dark");
    localStorage.setItem('darkMode', isDarkMode);

    if (isDarkMode) {
        modeText.innerText = "Light mode";
    } else {
        modeText.innerText = "Dark mode";
    }
});

// Adiciona um ouvinte de evento para alternar o estado da barra lateral e armazenar a preferência
toggle.addEventListener("click", () => {
    sidebar.classList.toggle("close");

    const isSidebarClosed = sidebar.classList.contains("close");
    localStorage.setItem('sidebarClosed', isSidebarClosed);
});

// Configura o estado do modo e da barra lateral com base nas preferências armazenadas ao carregar a página
document.addEventListener("DOMContentLoaded", () => {
    setModeFromStorage();
    setSidebarStateFromStorage();
});