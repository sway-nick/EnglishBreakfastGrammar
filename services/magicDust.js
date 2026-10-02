/**
 * Magic Dust Particle Engine for English Breakfast Grammar
 * Spawns enchanting sparkling particles following touch / mouse movements on screen.
 */

export const DEFAULT_DUST_CONFIG = {
  density: 22,
  size: 0.5,
  brightness: 0.6,
  glow: 0.35,
  life: 2,
  gravity: 52,
  sway: 0,
  spread: 10,
  maxFall: 140,
  glints: 8,
  tint: "warm",
  persist: 0
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
    this.activeScreen = 'levels';

    this.palette = {
      warm: [
        'rgba(254, 240, 138, ', // Light gold
        'rgba(253, 224, 71, ',  // Bright gold
        'rgba(251, 191, 36, ',  // Rich amber
        'rgba(245, 158, 11, ',  // Honey topaz
        'rgba(251, 146, 60, ',  // Warm flame
        'rgba(255, 255, 255, '   // Bright white glint
      ],
      gold: [
        'rgba(254, 240, 138, ',
        'rgba(253, 224, 71, ',
        'rgba(245, 158, 11, ',
        'rgba(255, 255, 255, '
      ],
      mix: [
        'rgba(253, 224, 71, ',  // Golden yellow
        'rgba(245, 158, 11, ',  // Amber gold
        'rgba(56, 189, 248, ',  // Starlight cyan
        'rgba(192, 132, 252, ', // Mystic violet
        'rgba(244, 114, 182, ', // Rose pink
        'rgba(255, 255, 255, '   // Pure diamond white
      ]
    };
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
    const dpr = window.devicePixelRatio || 1;
    const w = window.innerWidth;
    const h = window.innerHeight;
    this.canvas.width = w * dpr;
    this.canvas.height = h * dpr;
    this.ctx.scale(dpr, dpr);
  }

  bindEvents() {
    let lastX = 0;
    let lastY = 0;
    let isTouching = false;

    const spawnAt = (x, y) => {
      if (!this.isEnabled) return;
      const count = Math.max(1, Math.round(this.config.density * 0.35));
      for (let i = 0; i < count; i++) {
        this.addParticle(x, y);
      }
      this.startLoop();
    };

    // Pointer events (Touch + Mouse unified)
    window.addEventListener('pointermove', (e) => {
      // Check if mouse is pressed or touch is active
      if (e.pointerType === 'touch' || e.buttons > 0 || (e.clientX !== lastX || e.clientY !== lastY)) {
        spawnAt(e.clientX, e.clientY);
        lastX = e.clientX;
        lastY = e.clientY;
      }
    }, { passive: true });

    window.addEventListener('pointerdown', (e) => {
      isTouching = true;
      spawnAt(e.clientX, e.clientY);
    }, { passive: true });

    window.addEventListener('pointerup', () => {
      isTouching = false;
    }, { passive: true });

    window.addEventListener('touchmove', (e) => {
      if (e.touches && e.touches[0]) {
        spawnAt(e.touches[0].clientX, e.touches[0].clientY);
      }
    }, { passive: true });
  }

  addParticle(x, y) {
    const spread = this.config.spread;
    const colors = this.palette[this.config.tint] || this.palette.mix;
    const baseColor = colors[Math.floor(Math.random() * colors.length)];
    const isGlint = (Math.random() * 100) < this.config.glints;

    // Angle and velocity
    const angle = Math.random() * Math.PI * 2;
    const speed = (Math.random() * spread * 0.8);
    const vx = Math.cos(angle) * speed;
    const vy = Math.sin(angle) * speed * 0.5;

    this.particles.push({
      x: x + (Math.random() - 0.5) * spread,
      y: y + (Math.random() - 0.5) * spread,
      startY: y,
      vx,
      vy,
      baseColor,
      isGlint,
      size: (0.8 + Math.random() * 1.6) * this.config.size * (isGlint ? 1.4 : 1.0),
      age: 0,
      maxLife: (0.8 + Math.random() * 0.4) * this.config.life,
      swayPhase: Math.random() * Math.PI * 2,
      swaySpeed: 2.0 + Math.random() * 3.0,
      twinklePhase: Math.random() * Math.PI * 2,
      twinkleSpeed: 5.0 + Math.random() * 8.0,
      rotation: Math.random() * Math.PI
    });
  }

  startLoop() {
    if (!this.animId) {
      this.lastTime = performance.now();
      this.animId = requestAnimationFrame((t) => this.tick(t));
    }
  }

  tick(currentTime) {
    const dt = Math.min(0.1, (currentTime - this.lastTime) / 1000);
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
    // Use composite operation for vibrant magical sparkles
    this.ctx.globalCompositeOperation = 'screen';

    for (let i = 0; i < this.particles.length; i++) {
      const p = this.particles[i];
      p.age += dt;

      if (p.age >= p.maxLife) continue;

      const progress = p.age / p.maxLife; // 0..1
      const fallDistance = p.y - p.startY;

      if (fallDistance > maxFall) continue;

      // Update position
      p.vy += gravity * dt * 0.6;
      p.swayPhase += p.swaySpeed * dt;
      p.twinklePhase += p.twinkleSpeed * dt;
      p.rotation += 1.5 * dt;

      p.x += (p.vx + Math.sin(p.swayPhase) * sway * 0.4) * dt * 60;
      p.y += p.vy * dt * 60;

      // Alpha fade curve (smooth rise and soft decay)
      let alpha = 1.0;
      if (progress < 0.15) {
        alpha = progress / 0.15;
      } else {
        alpha = Math.pow(1 - (progress - 0.15) / 0.85, 1.4);
      }

      // Height fall fade
      if (fallDistance > maxFall * 0.7) {
        const fallFade = 1 - (fallDistance - maxFall * 0.7) / (maxFall * 0.3);
        alpha *= Math.max(0, fallFade);
      }

      alpha *= baseBrightness;

      // Glint sparkle multiplier
      if (p.isGlint) {
        const twinkle = 0.6 + 0.4 * Math.sin(p.twinklePhase);
        alpha = Math.min(1.0, alpha * twinkle * 1.5);
      }

      if (alpha <= 0.01) continue;

      const curSize = p.size * (1.0 - progress * 0.35);

      // Render glowing sparkle
      this.ctx.shadowBlur = curSize * 6 * glowFactor;
      this.ctx.shadowColor = p.baseColor + `${Math.min(1, alpha * 1.5)})`;
      this.ctx.fillStyle = p.baseColor + `${alpha})`;

      if (p.isGlint && curSize > 1.2) {
        // Render 4-point star sparkle
        this.ctx.save();
        this.ctx.translate(p.x, p.y);
        this.ctx.rotate(p.rotation);

        const r1 = curSize * 1.8;
        const r2 = curSize * 0.4;

        this.ctx.beginPath();
        for (let j = 0; j < 8; j++) {
          const a = (j * Math.PI) / 4;
          const r = j % 2 === 0 ? r1 : r2;
          const px = Math.cos(a) * r;
          const py = Math.sin(a) * r;
          if (j === 0) this.ctx.moveTo(px, py);
          else this.ctx.lineTo(px, py);
        }
        this.ctx.closePath();
        this.ctx.fill();
        this.ctx.restore();
      } else {
        // Render round glowing particle
        this.ctx.beginPath();
        this.ctx.arc(p.x, p.y, Math.max(0.6, curSize), 0, Math.PI * 2);
        this.ctx.fill();
      }

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
