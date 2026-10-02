/**
 * Zero-Gravity Micro-Golden Stardust Trail Engine
 * Creates a dense, rich, silky trail of ultra-microscopic golden dust that levitates weightlessly
 * in place under the finger/cursor with near-zero vertical fall, slowly dissolving into the air.
 */

export const DEFAULT_DUST_CONFIG = {
  density: 26,          // Very dense, rich dust trail
  size: 0.22,           // Ultra-microscopic particle size (0.15px - 0.35px)
  brightness: 0.55,     // Soft, warm golden luminescence
  glow: 0.35,           // Delicate starlight glow
  life: 1.5,            // Levitation duration in seconds
  gravity: 0.1,         // 10x slower: near-zero gravity levitation
  sway: 0.4,            // Microscopic air shimmer
  spread: 6,            // Tight stream directly beneath fingertip
  maxFall: 10,          // Virtually zero fall distance before fading
  glints: 22,           // Shimmering micro-sparkles
  tint: "gold"
};

class MagicDustController {
  constructor(config = {}) {
    this.config = { ...DEFAULT_DUST_CONFIG, ...config };
    this.canvas = null;
    this.ctx = null;
    this.particles = [];
    this.animId = null;
    this.lastTime = 0;
    this.isEnabled = true;
    this.lastSpawnPos = null;

    // Pure warm golden palette
    this.goldColors = [
      'rgba(255, 235, 140, ', // Warm starlight gold
      'rgba(253, 218, 90, ',  // Pure glowing amber
      'rgba(248, 178, 25, ',  // Deep honey gold
      'rgba(255, 245, 190, ', // Soft fairy pollen
      'rgba(255, 255, 235, '  // Diamond white-gold shimmer
    ];
  }

  init() {
    if (this.canvas) return;

    this.canvas = document.createElement('canvas');
    this.canvas.id = 'magic-dust-canvas';
    this.canvas.style.position = 'fixed';
    this.canvas.style.top = '0';
    this.canvas.style.left = '0';
    this.canvas.style.width = '100vw';
    this.canvas.style.height = '100vh';
    this.canvas.style.pointerEvents = 'none';
    this.canvas.style.zIndex = '99999';
    this.canvas.style.imageRendering = 'auto';

    document.body.appendChild(this.canvas);
    this.ctx = this.canvas.getContext('2d', { alpha: true });

    this.resize();
    window.addEventListener('resize', () => this.resize(), { passive: true });

    this.bindEvents();
  }

  resize() {
    if (!this.canvas) return;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const w = window.innerWidth;
    const h = window.innerHeight;
    this.canvas.width = w * dpr;
    this.canvas.height = h * dpr;
    this.ctx.scale(dpr, dpr);
  }

  bindEvents() {
    const spawnStream = (x, y) => {
      if (!this.isEnabled) return;

      if (this.lastSpawnPos) {
        // Ultra-dense fine interpolation along stroke path
        const dx = x - this.lastSpawnPos.x;
        const dy = y - this.lastSpawnPos.y;
        const dist = Math.hypot(dx, dy);
        const steps = Math.min(14, Math.max(1, Math.floor(dist / 2.5)));

        for (let s = 0; s < steps; s++) {
          const t = (s + 1) / steps;
          const ix = this.lastSpawnPos.x + dx * t;
          const iy = this.lastSpawnPos.y + dy * t;
          this.spawnBurst(ix, iy, 5);
        }
      } else {
        this.spawnBurst(x, y, 14);
      }

      this.lastSpawnPos = { x, y };
      this.startLoop();
    };

    const endStream = () => {
      this.lastSpawnPos = null;
    };

    // Pointer events (Touch + Mouse unified)
    window.addEventListener('pointermove', (e) => {
      if (e.pointerType === 'touch' || e.buttons > 0) {
        spawnStream(e.clientX, e.clientY);
      } else {
        endStream();
      }
    }, { passive: true });

    window.addEventListener('pointerdown', (e) => {
      this.lastSpawnPos = { x: e.clientX, y: e.clientY };
      spawnStream(e.clientX, e.clientY);
    }, { passive: true });

    window.addEventListener('pointerup', endStream, { passive: true });
    window.addEventListener('pointercancel', endStream, { passive: true });

    window.addEventListener('touchmove', (e) => {
      if (e.touches && e.touches[0]) {
        spawnStream(e.touches[0].clientX, e.touches[0].clientY);
      }
    }, { passive: true });

    window.addEventListener('touchend', endStream, { passive: true });
  }

  spawnBurst(x, y, count) {
    const spread = this.config.spread;
    for (let i = 0; i < count; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = (0.02 + Math.random() * 0.25) * (spread * 0.15);
      const isShimmer = Math.random() * 100 < this.config.glints;

      const baseColor = this.goldColors[Math.floor(Math.random() * this.goldColors.length)];

      this.particles.push({
        x: x + (Math.random() - 0.5) * spread,
        y: y + (Math.random() - 0.5) * spread,
        startX: x,
        startY: y,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed * 0.05, // Virtually zero initial vertical drift
        baseColor,
        isShimmer,
        size: (0.2 + Math.random() * 0.4) * this.config.size, // Ultra-microscopic (0.15px - 0.35px)
        age: 0,
        maxLife: (0.9 + Math.random() * 0.4) * this.config.life,
        swayPhase: Math.random() * Math.PI * 2,
        swaySpeed: 0.8 + Math.random() * 1.2,
        twinklePhase: Math.random() * Math.PI * 2,
        twinkleSpeed: 2.5 + Math.random() * 4.0
      });
    }
  }

  startLoop() {
    if (!this.animId) {
      this.lastTime = performance.now();
      this.animId = requestAnimationFrame((t) => this.tick(t));
    }
  }

  tick(currentTime) {
    const dt = Math.min(0.05, (currentTime - this.lastTime) / 1000);
    this.lastTime = currentTime;

    if (!this.ctx || !this.canvas) return;

    const w = window.innerWidth;
    const h = window.innerHeight;

    this.ctx.clearRect(0, 0, w, h);

    if (this.particles.length === 0) {
      this.animId = null;
      return;
    }

    const nextParticles = [];
    const gravity = this.config.gravity;
    const sway = this.config.sway;
    const maxFall = this.config.maxFall;
    const baseBrightness = this.config.brightness;
    const glowFactor = this.config.glow;

    this.ctx.save();
    this.ctx.globalCompositeOperation = 'screen';

    for (let i = 0; i < this.particles.length; i++) {
      const p = this.particles[i];
      p.age += dt;

      if (p.age >= p.maxLife) continue;

      const progress = p.age / p.maxLife; // 0..1
      const fallDistance = p.y - p.startY;

      if (fallDistance > maxFall) continue;

      // Zero-gravity levitation with gentle damping
      p.vy += gravity * dt * 0.01;
      p.vx *= 0.92;
      p.vy *= 0.92;

      p.swayPhase += p.swaySpeed * dt;
      p.twinklePhase += p.twinkleSpeed * dt;

      p.x += (p.vx + Math.sin(p.swayPhase) * sway * 0.04) * dt * 60;
      p.y += p.vy * dt * 60;

      // Soft progressive fade envelope
      let alpha = 1.0;
      if (progress < 0.1) {
        alpha = progress / 0.1;
      } else {
        alpha = Math.pow(1 - (progress - 0.1) / 0.9, 1.4);
      }

      alpha *= baseBrightness;

      if (p.isShimmer) {
        const twinkle = 0.85 + 0.15 * Math.sin(p.twinklePhase);
        alpha *= twinkle;
      }

      if (alpha <= 0.005) continue;

      const curSize = p.size * (1.0 - progress * 0.15);

      // Render ultra-microscopic glowing speck
      this.ctx.shadowBlur = curSize * 3.5 * glowFactor;
      this.ctx.shadowColor = p.baseColor + `${Math.min(0.65, alpha * 1.1)})`;
      this.ctx.fillStyle = p.baseColor + `${alpha})`;

      this.ctx.beginPath();
      this.ctx.arc(p.x, p.y, Math.max(0.18, curSize), 0, Math.PI * 2);
      this.ctx.fill();

      nextParticles.push(p);
    }

    this.ctx.restore();
    this.particles = nextParticles;

    if (this.particles.length > 0) {
      this.animId = requestAnimationFrame((t) => this.tick(t));
    } else {
      this.animId = null;
    }
  }

  updateConfig(newConfig) {
    this.config = { ...this.config, ...newConfig };
  }
}

export const MagicDustService = new MagicDustController();
