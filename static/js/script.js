// Initialize AOS animation only if not already initialized in base.html
document.addEventListener('DOMContentLoaded', function() {
    // AOS is initialized in base.html
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
    const image = document.querySelectorAll('img');
    
    image.forEach(img => {
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

// Only add search-related event listeners if both elements exist
if (searchContainer && searchInput) {
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
}

// Load More AJAX functionality
document.addEventListener('DOMContentLoaded', function() {
    const loadMoreBtn = document.getElementById('load-more-btn');
    const productsContainer = document.getElementById('products-container');
    
    console.log('Load more button found:', !!loadMoreBtn);
    console.log('Products container found:', !!productsContainer);
    
    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', function(e) {
            e.preventDefault(); // Prevent default button behavior
            console.log('Load more button clicked');
            
            const nextPage = this.getAttribute('data-next-page');
            console.log('Next page:', nextPage);
            if (!nextPage) return;
            
            // Show loading state
            loadMoreBtn.disabled = true;
            loadMoreBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
            
            // Get CSRF token from the meta tag or from a form
            let csrfToken = null;
            // First check for CSRF token in the form within the section
            const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
            if (csrfInput) {
                csrfToken = csrfInput.value;
                console.log('Found CSRF token in input field');
            } else {
                console.error('CSRF token not found!');
                loadMoreBtn.disabled = false;
                loadMoreBtn.innerHTML = 'Try Again';
                alert('Could not authenticate request. Please refresh the page and try again.');
                return;
            }
            
            // Make AJAX request
            fetch(`/load-more-products/?page=${nextPage}`, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                credentials: 'same-origin'
            })
            .then(response => {
                console.log('Response status:', response.status);
                if (!response.ok) {
                    console.error('Server error:', response.statusText);
                    throw new Error(`Network response was not ok: ${response.status} ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Received data:', data); // Debug logging
                
                // Append new products
                if (data.products_html && data.products_html.length) {
                    data.products_html.forEach(html => {
                        // Directly append the HTML to the container
                        productsContainer.insertAdjacentHTML('beforeend', html);
                    });
                    
                    // Handle image loading errors for new images
                    const newImages = productsContainer.querySelectorAll('.col-md-3:nth-last-child(-n+8) img');
                    newImages.forEach(img => {
                        img.addEventListener('error', function() {
                            // If image fails to load, show placeholder text
                            const parent = this.parentElement;
                            if (parent && parent.classList.contains('placeholder-img')) {
                                this.style.display = 'none';
                                parent.innerHTML = this.alt || 'Image Placeholder';
                            }
                        });
                    });
                    
                    // Initialize AOS for new elements
                    if (typeof AOS !== 'undefined') {
                        AOS.refresh();
                    }
                }
                
                // Update or remove the load more button
                if (data.has_next) {
                    loadMoreBtn.setAttribute('data-next-page', data.next_page);
                    loadMoreBtn.disabled = false;
                    loadMoreBtn.innerHTML = 'Load More';
                } else {
                    loadMoreBtn.remove();
                }
            })
            .catch(error => {
                console.error('Error loading more products:', error);
                loadMoreBtn.disabled = false;
                loadMoreBtn.innerHTML = 'Try Again';
                alert('Failed to load more products. Please try again later.');
            });
        });
    }
});
