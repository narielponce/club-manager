// main.js - Vanilla JS interactions

document.addEventListener('DOMContentLoaded', () => {
    
    // Navbar Scroll Effect
    const navbar = document.getElementById('mainNav');
    
    if (navbar) {
        const checkScroll = () => {
            if (window.scrollY > 50) {
                navbar.classList.add('is-scrolled');
            } else {
                navbar.classList.remove('is-scrolled');
            }
        };

        // Check on load
        checkScroll();
        
        // Check on scroll
        window.addEventListener('scroll', checkScroll);
    }
});
