/**
 * Delicate Golden Dust Trail Engine for English Breakfast Grammar
 * Creates an ethereal, subtle trail of glowing golden dust under the finger/cursor,
 * gently floating down and softly fading into the air.
 */

export const DEFAULT_DUST_CONFIG = {
  density: 6,           // Balanced delicate spawn rate
  size: 0.8,            // Tiny micro-particle radius (0.5px - 1.2px)
  brightness: 0.55,     // Subtle non-intrusive transparency
  glow: 0.4,            // Soft warm glow halo
  life: 1.5,            // Lifespan in seconds before vanishing
  gravity: 24,          // Slow, gentle settling
  sway: 1.8,            // Gentle organic micro-drift
  spread: 6,            // Tight stream directly beneath fingertip
  maxFall: 70,          // Softly dissolves after gentle drop
  glints: 15,           // Delicate twinkle
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

    // Pure ethereal gold palette: no harsh or foreign colors
    this.goldColors = [
      'rgba(255, 230, 130, ', // Warm starlight gold
      'rgba(252, 211, 77, ',  // Pure glowing amber
      'rgba(245, 158, 11, ',  // Deep honey gold
      'rgba(254, 240, 138, ', // Soft fairy pollen
      'rgba(255, 250, 220, '  // Diamond white-gold shimmer
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
        // Interpolate points for a smooth continuous stream along movement
        const dx = x - this.lastSpawnPos.x;
        const dy = y - this.lastSpawnPos.y;
        const dist = Math.hypot(dx, dy);
        const steps = Math.min(6, Math.max(1, Math.floor(dist / 8)));

        for (let s = 0; s < steps; s++) {
          const t = (s + 1) / steps;
          const ix = this.lastSpawnPos.x + dx * t;
          const iy = this.lastSpawnPos.y + dy * t;
          this.spawnBurst(ix, iy, 2);
        }
      } else {
        this.spawnBurst(x, y, 3);
      }

      this.lastSpawnPos = { x, y };
      this.startLoop();
    };

    const endStream = () => {
      this.lastSpawnPos = null;
    };

    // Pointer events (Smooth touch + mouse drag)
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
      const speed = (0.2 + Math.random() * 0.8) * (spread * 0.3);
      const isShimmer = Math.random() * 100 < this.config.glints;

      const baseColor = this.goldColors[Math.floor(Math.random() * this.goldColors.length)];

      this.particles.push({
        x: x + (Math.random() - 0.5) * spread,
        y: y + (Math.random() - 0.5) * spread,
        startY: y,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed * 0.3 - 0.2, // slight upward float before settling
        baseColor,
        isShimmer,
        size: (0.4 + Math.random() * 0.7) * this.config.size, // Tiny micro-mote (0.4 - 0.9px)
        age: 0,
        maxLife: (0.9 + Math.random() * 0.6) * this.config.life,
        swayPhase: Math.random() * Math.PI * 2,
        swaySpeed: 1.5 + Math.random() * 2.5,
        twinklePhase: Math.random() * Math.PI * 2,
        twinkleSpeed: 4.0 + Math.random() * 6.0
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

      // Gentle floating physics with air resistance
      p.vy += gravity * dt * 0.4;
      p.vx *= 0.97;
      p.vy *= 0.98;

      p.swayPhase += p.swaySpeed * dt;
      p.twinklePhase += p.twinkleSpeed * dt;

      p.x += (p.vx + Math.sin(p.swayPhase) * sway * 0.2) * dt * 60;
      p.y += p.vy * dt * 60;

      // Extremely soft, delicate fade envelope
      let alpha = 1.0;
      if (progress < 0.12) {
        alpha = progress / 0.12; // gentle rise
      } else {
        alpha = Math.pow(1 - (progress - 0.12) / 0.88, 1.8); // soft exponential decay
      }

      // Fade smoothly as it falls past 65% of maxFall
      if (fallDistance > maxFall * 0.6) {
        const dropFade = 1 - (fallDistance - maxFall * 0.6) / (maxFall * 0.4);
        alpha *= Math.max(0, dropFade);
      }

      alpha *= baseBrightness;

      // Delicate shimmer modulation
      if (p.isShimmer) {
        const twinkle = 0.75 + 0.25 * Math.sin(p.twinklePhase);
        alpha *= twinkle;
      }

      if (alpha <= 0.005) continue;

      const curSize = p.size * (1.0 - progress * 0.25);

      // Render delicate glowing golden speck
      this.ctx.shadowBlur = curSize * 4 * glowFactor;
      this.ctx.shadowColor = p.baseColor + `${Math.min(0.8, alpha * 1.2)})`;
      this.ctx.fillStyle = p.baseColor + `${alpha})`;

      this.ctx.beginPath();
      this.ctx.arc(p.x, p.y, Math.max(0.35, curSize), 0, Math.PI * 2);
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
