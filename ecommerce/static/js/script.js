// script.js
class ModeManager {
    constructor() {
      this.modes = ['default', 'vibrant', 'vibrant-plus'];
      this.init();
    }
  
    init() {
      this.loadSavedMode();
      this.initParticles();
      this.initQuantumEffects();
      this.initServiceWorker();
    }
  
    loadSavedMode() {
      const savedMode = localStorage.getItem('quantumMode') || 'default';
      document.body.className = `${savedMode}-mode`;
      this.activateQuantumPhysics(savedMode);
    }
  
    activateQuantumPhysics(mode) {
      document.documentElement.style.setProperty('--quantum-intensity', 
        mode === 'vibrant-plus' ? '1' : '0.5'
      );
      
      if(mode === 'vibrant-plus') {
        this.initNeutrinoParticles();
        this.startChromaticAberration();
      }
    }
  
    initNeutrinoParticles() {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      canvas.className = 'quantum-canvas';
      document.body.appendChild(canvas);
  
      // Advanced particle system using WebGL/Canvas
      // ... (implementation using requestAnimationFrame and physics simulation)
    }
  
    initQuantumEffects() {
      document.querySelectorAll('[data-quantum="true"]').forEach(element => {
        element.addEventListener('mousemove', this.applyQuantumEntanglement);
      });
    }
  
    applyQuantumEntanglement(e) {
      // Advanced physics-based interactions
      const rect = e.target.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      
      gsap.to(e.target, {
        x: (x - rect.width/2) * 0.1,
        y: (y - rect.height/2) * 0.1,
        rotation: (x - rect.width/2) * 0.5,
        duration: 1.5,
        ease: 'power3.out'
      });
    }
  
    initServiceWorker() {
      if('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js')
          .then(() => console.log('Quantum Service Worker engaged'))
          .catch(err => console.error('Quantum entanglement failed:', err));
      }
    }
  }
  
  class QuantumDOM {
    constructor() {
      this.observer = new MutationObserver(this.handleMutations);
      this.config = { 
        childList: true, 
        subtree: true,
        attributes: true,
        attributeFilter: ['class']
      };
    }
  
    observe() {
      this.observer.observe(document.body, this.config);
    }
  
    handleMutations(mutations) {
      mutations.forEach(mutation => {
        if(mutation.type === 'attributes' && mutation.attributeName === 'class') {
          const currentMode = document.body.className.replace('-mode', '');
          localStorage.setItem('quantumMode', currentMode);
        }
      });
    }
  }
  
  // Initialize Quantum System
  document.addEventListener('DOMContentLoaded', () => {
    const quantumDOM = new QuantumDOM();
    quantumDOM.observe();
    
    new ModeManager();
    
    // Initialize Quantum Field Generator
    const quantumField = new QuantumField();
    quantumField.generate();
  });
  
  class QuantumField {
    generate() {
      document.querySelectorAll('.card').forEach(card => {
        card.style.transform = 'translateZ(50px)';
        card.addEventListener('mouseenter', this.entangleParticles);
      });
    }
  
    startAnimation() {
        let lastTime = 0;
        const fps = 60;
        const interval = 1000/fps;
        
        const animate = (timestamp) => {
            if (!lastTime) lastTime = timestamp;
            const delta = timestamp - lastTime;
            
            if (delta > interval) {
                if (this.config.mode === 'vibrant-mode') {
                    this.updateParticles();
                    this.render();
                }
                lastTime = timestamp - (delta % interval);
            }
            requestAnimationFrame(animate);
        };
        
        // Start synchronized animation loop
        requestAnimationFrame(animate);
        
        // Sync GSAP with RAF
        gsap.ticker.fps(fps);
        gsap.ticker.useRAF(true);
    }
    
    entangleParticles(e) {
      anime({
        targets: e.target,
        translateZ: [50, 100],
        scale: [1, 1.05],
        duration: 1000,
        elasticity: 400,
        easing: 'easeOutElastic'
      });
    }
  }


