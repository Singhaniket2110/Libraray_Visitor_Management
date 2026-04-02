// static/js/darkmode.js - GLOBAL DARK MODE

// Function to toggle dark mode
function toggleDarkMode() {
    const body = document.body;
    const isDarkMode = body.classList.toggle('dark-mode');
    
    // Save to localStorage
    if (isDarkMode) {
        localStorage.setItem('darkMode', 'enabled');
    } else {
        localStorage.setItem('darkMode', 'disabled');
    }
    
    // Update all toggle buttons on the page (if multiple)
    updateAllToggleButtons(isDarkMode);
}

// Update all toggle buttons on current page
function updateAllToggleButtons(isDarkMode) {
    const toggleBtns = document.querySelectorAll('.dark-mode-toggle');
    toggleBtns.forEach(btn => {
        if (isDarkMode) {
            btn.innerHTML = '<i class="fas fa-sun"></i>';
        } else {
            btn.innerHTML = '<i class="fas fa-moon"></i>';
        }
    });
}

// Load dark mode preference on page load
function loadDarkModePreference() {
    const darkMode = localStorage.getItem('darkMode');
    const isDarkMode = darkMode === 'enabled';
    
    if (isDarkMode) {
        document.body.classList.add('dark-mode');
    } else {
        document.body.classList.remove('dark-mode');
    }
    
    updateAllToggleButtons(isDarkMode);
}

// Run when page loads
document.addEventListener('DOMContentLoaded', loadDarkModePreference);
