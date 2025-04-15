// quantum-physics.js
class QuantumParticles {
    constructor(options = {}) {
      this.config = {
        selector: options.selector || 'body',
        density: this.calculateDensity(),
        mode: options.mode || 'default',
        particleTypes: ['photon', 'gluon', 'boson'],
        maxVelocity: 0.5,
        interactionRadius: 150,
        repulsionForce: 0.8
      };
  
      this.init();
    }
    // Add new method
    calculateDensity() {
        const isMobile = /Mobi|Android/i.test(navigator.userAgent);
        const hardwareScore = navigator.hardwareConcurrency || 2;
        
        if (isMobile) {
            return hardwareScore > 4 ? 'medium' : 'low';
        }
        return hardwareScore > 6 ? 'high' : 'medium';
    }
  
    init() {
      this.container = document.querySelector(this.config.selector);
      if (!this.container) return;
  
      this.setupWebGL();
      this.createParticles();
      this.initEventListeners();
      this.startAnimation();
    }
  
    setupWebGL() {
        this.canvas = document.createElement('canvas');
        this.container.appendChild(this.canvas);
        
        // Create warning element
        this.webglWarning = document.createElement('div');
        this.webglWarning.className = 'webgl-warning';
        this.webglWarning.innerHTML = `
            <div class="alert alert-warning mt-3">
                Your device does not support advanced quantum effects.
                Please update your graphics drivers or try a modern browser.
            </div>
        `;
        
        try {
            this.ctx = this.canvas.getContext('webgl', { antialias: true }) || 
                    this.canvas.getContext('experimental-webgl');
            
            if (!this.ctx) throw new Error('WebGL unavailable');
            
            // Hide warning if WebGL works
            this.webglWarning.style.display = 'none';
        } catch (e) {
            this.container.appendChild(this.webglWarning);
            console.error('Quantum effects disabled:', e);
            return;
        }
        
        this.resizeCanvas();
        this.initShaders();
        this.initBuffers();
    }
  
    initShaders() {
      const vertexShader = `
        attribute vec2 position;
        attribute vec3 color;
        attribute float size;
        
        uniform mat4 projection;
        varying vec3 vColor;
        
        void main() {
          vColor = color;
          gl_Position = projection * vec4(position, 0.0, 1.0);
          gl_PointSize = size;
        }
      `;
  
      const fragmentShader = `
        precision mediump float;
        varying vec3 vColor;
        
        void main() {
          float intensity = 1.0 - length(gl_PointCoord - vec2(0.5)) * 2.0;
          gl_FragColor = vec4(vColor, intensity * 0.8);
        }
      `;
  
      this.program = this.createProgram(vertexShader, fragmentShader);
      this.ctx.useProgram(this.program);
    }
  
    createProgram(vs, fs) {
      const program = this.ctx.createProgram();
      const vertex = this.compileShader(vs, this.ctx.VERTEX_SHADER);
      const fragment = this.compileShader(fs, this.ctx.FRAGMENT_SHADER);
  
      this.ctx.attachShader(program, vertex);
      this.ctx.attachShader(program, fragment);
      this.ctx.linkProgram(program);
  
      if (!this.ctx.getProgramParameter(program, this.ctx.LINK_STATUS)) {
        console.error('Quantum program error:', this.ctx.getProgramInfoLog(program));
      }
      return program;
    }
  
    compileShader(source, type) {
      const shader = this.ctx.createShader(type);
      this.ctx.shaderSource(shader, source);
      this.ctx.compileShader(shader);
  
      if (!this.ctx.getShaderParameter(shader, this.ctx.COMPILE_STATUS)) {
        console.error('Quantum shader error:', this.ctx.getShaderInfoLog(shader));
      }
      return shader;
    }
  
    initBuffers() {
      this.positionBuffer = this.ctx.createBuffer();
      this.colorBuffer = this.ctx.createBuffer();
      this.sizeBuffer = this.ctx.createBuffer();
  
      this.projectionMatrix = new Float32Array(16);
      mat4.ortho(this.projectionMatrix, 0, this.canvas.width, this.canvas.height, 0, -1, 1);
      
      const projectionLoc = this.ctx.getUniformLocation(this.program, 'projection');
      this.ctx.uniformMatrix4fv(projectionLoc, false, this.projectionMatrix);
    }
  
    createParticles() {
      const densityMap = { low: 200, medium: 500, high: 1000 };
      this.particles = Array.from({ length: densityMap[this.config.density] }, (_, i) => ({
        type: this.config.particleTypes[i % 3],
        x: Math.random() * this.canvas.width,
        y: Math.random() * this.canvas.height,
        vx: (Math.random() - 0.5) * this.config.maxVelocity,
        vy: (Math.random() - 0.5) * this.config.maxVelocity,
        size: 2 + Math.random() * 6,
        color: this.getParticleColor(i)
      }));
    }
  
    getParticleColor(index) {
      const neonColors = {
        photon: [255/255, 111/255, 97/255],    // #ff6f61
        gluon: [155/255, 255/255, 185/255],    // #9bffb9
        boson: [185/255, 136/255, 255/255]     // #b988ff
      };
      return neonColors[this.particles[index].type];
    }
  
    updateParticles() {
      this.particles.forEach(particle => {
        // Quantum uncertainty principle simulation
        particle.x += particle.vx + (Math.random() - 0.5) * 0.1;
        particle.y += particle.vy + (Math.random() - 0.5) * 0.1;
  
        // Containment field boundaries
        if (particle.x < 0 || particle.x > this.canvas.width) particle.vx *= -1;
        if (particle.y < 0 || particle.y > this.canvas.height) particle.vy *= -1;
  
        // Mouse interaction
        if (this.mouseX && this.mouseY) {
          const dx = particle.x - this.mouseX;
          const dy = particle.y - this.mouseY;
          const distance = Math.sqrt(dx * dx + dy * dy);
  
          if (distance < this.config.interactionRadius) {
            const force = this.config.repulsionForce * (1 - distance/this.config.interactionRadius);
            particle.vx += (dx / distance) * force;
            particle.vy += (dy / distance) * force;
          }
        }
      });
    }
  
    render() {
      if (!this.ctx) return;
  
      this.ctx.viewport(0, 0, this.canvas.width, this.canvas.height);
      this.ctx.clearColor(0, 0, 0, 0);
      this.ctx.clear(this.ctx.COLOR_BUFFER_BIT);
  
      // Update particle buffers
      const positions = new Float32Array(this.particles.flatMap(p => [p.x, p.y]));
      const colors = new Float32Array(this.particles.flatMap(p => p.color));
      const sizes = new Float32Array(this.particles.map(p => p.size));
  
      this.updateBuffer(this.positionBuffer, positions, 'position', 2);
      this.updateBuffer(this.colorBuffer, colors, 'color', 3);
      this.updateBuffer(this.sizeBuffer, sizes, 'size', 1);
  
      // Draw particles
      this.ctx.drawArrays(this.ctx.POINTS, 0, this.particles.length);
    }
  
    updateBuffer(buffer, data, attribute, size) {
      this.ctx.bindBuffer(this.ctx.ARRAY_BUFFER, buffer);
      this.ctx.bufferData(this.ctx.ARRAY_BUFFER, data, this.ctx.DYNAMIC_DRAW);
      const loc = this.ctx.getAttribLocation(this.program, attribute);
      this.ctx.enableVertexAttribArray(loc);
      this.ctx.vertexAttribPointer(loc, size, this.ctx.FLOAT, false, 0, 0);
    }
  
    initEventListeners() {
      window.addEventListener('resize', () => this.resizeCanvas());
      
      this.container.addEventListener('mousemove', (e) => {
        const rect = this.canvas.getBoundingClientRect();
        this.mouseX = e.clientX - rect.left;
        this.mouseY = e.clientY - rect.top;
      });
  
      this.container.addEventListener('mouseleave', () => {
        this.mouseX = null;
        this.mouseY = null;
      });
    }
  
    resizeCanvas() {
      if (!this.canvas) return;
      
      this.canvas.width = this.container.clientWidth;
      this.canvas.height = this.container.clientHeight;
      
      mat4.ortho(this.projectionMatrix, 0, this.canvas.width, this.canvas.height, 0, -1, 1);
      const projectionLoc = this.ctx.getUniformLocation(this.program, 'projection');
      this.ctx.uniformMatrix4fv(projectionLoc, false, this.projectionMatrix);
    }
  
    startAnimation() {
      const animate = () => {
        if (this.config.mode === 'vibrant-mode') {
          this.updateParticles();
          this.render();
        }
        requestAnimationFrame(animate);
      };
      animate();
    }
  
    destroy() {
      window.removeEventListener('resize', this.resizeCanvas);
      this.container.removeEventListener('mousemove');
      this.container.removeEventListener('mouseleave');
      this.container.removeChild(this.canvas);
    }
  }
  
  // Initialize Quantum Field
  document.addEventListener('DOMContentLoaded', () => {
    window.QuantumField = new QuantumParticles({
      selector: '.quantum-container',
      density: 'high'
    });
  });