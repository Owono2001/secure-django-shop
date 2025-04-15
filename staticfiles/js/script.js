import anime from 'animejs/lib/anime.es.js';
import { gsap } from 'gsap';

// Dark Mode Toggle
const toggleDarkMode = document.querySelector('#toggle-dark-mode');
toggleDarkMode?.addEventListener('click', () => {
    document.body.classList.toggle('dark-mode');
    localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
});

// Apply Dark Mode on Page Load
window.addEventListener('load', () => {
    if (localStorage.getItem('darkMode') === 'true') {
        document.body.classList.add('dark-mode');
    }
});

// GSAP Example: Fade-in and Bounce Animation for Product Cards
gsap.from('.card', {
    duration: 1,
    opacity: 0,
    y: 50,
    stagger: 0.2,
    ease: 'bounce',
});

// Anime.js Example: Scale Animation for Images
document.querySelectorAll('.zoomable-img').forEach((img) => {
    img.addEventListener('mouseenter', () => {
        anime({
            targets: img,
            scale: 1.2,
            duration: 300,
            easing: 'easeInOutQuad',
        });
    });
    img.addEventListener('mouseleave', () => {
        anime({
            targets: img,
            scale: 1,
            duration: 300,
            easing: 'easeInOutQuad',
        });
    });
});