// Initialize AOS animation
AOS.init({
    duration: 800,
    easing: 'ease-in-out',
    once: true
});

// Navbar scroll effect
window.addEventListener('scroll', function() {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
});

// Fade up animation for elements
const fadeElements = document.querySelectorAll('.fade-up');

function checkFade() {
    fadeElements.forEach(element => {
        const elementTop = element.getBoundingClientRect().top;
        const windowHeight = window.innerHeight;
        
        if (elementTop < windowHeight - 100) {
            element.classList.add('active');
        }
    });
}

window.addEventListener('scroll', checkFade);
window.addEventListener('load', checkFade);

// Handle image loading errors
document.addEventListener('DOMContentLoaded', function() {
    const images = document.querySelectorAll('img');
    
    images.forEach(img => {
        img.addEventListener('error', function() {
            // If image fails to load, show placeholder text
            const parent = this.parentElement;
            if (parent.classList.contains('placeholder-img')) {
                this.style.display = 'none';
                parent.innerHTML = this.alt || 'Image Placeholder';
            }
        });
    });
});
const searchContainer = document.querySelector('.search-container');
const searchInput = document.querySelector('.search-input');

let isInputFocused = false;

// Expand and show input on hover (only if not focused)
searchContainer.addEventListener('mouseenter', () => {
    if (!isInputFocused) {
        searchContainer.classList.add('active');
        searchInput.classList.add('visible'); // Fade in
    }
});

searchContainer.addEventListener('mouseleave', () => {
    if (!isInputFocused && !searchInput.value.trim()) {
        searchContainer.classList.remove('active');
        setTimeout(() => {
            if (!searchContainer.classList.contains('active')) {
                searchInput.classList.remove('visible'); // Fade out after shrink
            }
        }, 500);
    }
});

// Focus keeps expanded and visible
searchInput.addEventListener('focus', () => {
    isInputFocused = true;
    searchContainer.classList.add('active');
    searchInput.classList.add('visible');
});

searchInput.addEventListener('blur', () => {
    isInputFocused = false;
    if (!searchInput.value.trim()) {
        searchContainer.classList.remove('active');
        setTimeout(() => {
            if (!searchContainer.classList.contains('active')) {
                searchInput.classList.remove('visible');
            }
        }, 500);
    }
});

// Optional: shrink on Enter if input is empty
searchInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !searchInput.value.trim()) {
        searchContainer.classList.remove('active');
        setTimeout(() => {
            if (!searchContainer.classList.contains('active')) {
                searchInput.classList.remove('visible');
            }
        }, 500);
    }
});
