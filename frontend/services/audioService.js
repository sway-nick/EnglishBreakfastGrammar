import { StorageService } from './storageService.js';

class AudioServiceController {
  constructor() {
    this.audio = null;
    this.fadeInterval = null;
    this.currentScreen = 'levels';
    this.hasUserInteracted = false;
    this.targetVolume = 0.4;
  }

  init() {
    try {
      const audioUrl = new URL('../assets/audio/intro_theme.mp3', import.meta.url).href;
      this.audio = new Audio(audioUrl);
      this.audio.preload = 'auto';
      this.audio.volume = this.targetVolume;
      this.audio.loop = true; // Continuous loop

      // Global user interaction listener to unlock browser autoplay
      const tryPlayOnGesture = () => {
        this.hasUserInteracted = true;
        if (StorageService.getSoundEnabled() && this.currentScreen !== 'theory' && this.currentScreen !== 'test') {
          if (this.audio && this.audio.paused) {
            this.playMusic();
          }
        }
        window.removeEventListener('pointerdown', tryPlayOnGesture);
        window.removeEventListener('keydown', tryPlayOnGesture);
      };

      window.addEventListener('pointerdown', tryPlayOnGesture, { once: true });
      window.addEventListener('keydown', tryPlayOnGesture, { once: true });

      // Attempt immediate start
      this.playMusic();
    } catch (e) {
      console.warn('[AudioService] Audio init error:', e);
    }
  }

  playMusic() {
    if (!this.audio) return;
    if (!StorageService.getSoundEnabled()) return;
    if (this.currentScreen === 'theory' || this.currentScreen === 'test') return;
    if (!this.audio.paused) return;

    this.audio.volume = this.targetVolume;
    const playPromise = this.audio.play();
    if (playPromise !== undefined) {
      playPromise.catch(() => {
        // Handled by user gesture listener
      });
    }
  }

  onScreenChange(newScreen) {
    const prevScreen = this.currentScreen;
    this.currentScreen = newScreen;

    if (!this.audio) return;

    // 1. Moving to theory (rules) or test -> fade out 2x slower (1800ms smooth dissolve)
    if (newScreen === 'theory' || newScreen === 'test') {
      this.fadeOut(1800);
    } 
    // 2. Navigating in menu screens (levels, lessons, leaderboard)
    else {
      // ONLY fade in if we were previously in theory/test or the audio was paused
      if (prevScreen === 'theory' || prevScreen === 'test' || this.audio.paused) {
        if (StorageService.getSoundEnabled()) {
          this.fadeIn(this.targetVolume, 900);
        }
      }
      // If already playing between menus (levels <-> lessons <-> leaderboard), do nothing! (Zero sound drop / no dip)
    }
  }

  fadeOut(durationMs = 1800) {
    if (!this.audio || this.audio.paused) return;
    if (this.fadeInterval) clearInterval(this.fadeInterval);

    const startVol = this.audio.volume;
    const steps = 36; // Extra smooth dissolution
    const stepTime = Math.max(20, durationMs / steps);
    const volStep = startVol / steps;

    this.fadeInterval = setInterval(() => {
      if (this.audio.volume > volStep) {
        this.audio.volume = Math.max(0, this.audio.volume - volStep);
      } else {
        this.audio.volume = 0;
        this.audio.pause();
        clearInterval(this.fadeInterval);
        this.fadeInterval = null;
      }
    }, stepTime);
  }

  fadeIn(targetVol = 0.4, durationMs = 900) {
    if (!this.audio) return;
    if (!StorageService.getSoundEnabled()) return;
    if (this.currentScreen === 'theory' || this.currentScreen === 'test') return;

    // If already playing at or near target volume, do NOT dip or touch volume
    if (!this.audio.paused && Math.abs(this.audio.volume - targetVol) < 0.05 && !this.fadeInterval) {
      return;
    }

    if (this.fadeInterval) clearInterval(this.fadeInterval);

    // If paused, start from 0
    if (this.audio.paused) {
      this.audio.volume = 0;
    }

    const startVol = this.audio.volume;
    const playPromise = this.audio.play();
    if (playPromise !== undefined) {
      playPromise.then(() => {
        const steps = 18;
        const stepTime = Math.max(20, durationMs / steps);
        const volStep = Math.max(0.01, (targetVol - startVol) / steps);

        this.fadeInterval = setInterval(() => {
          if (this.audio.volume < targetVol - 0.02) {
            this.audio.volume = Math.min(targetVol, this.audio.volume + volStep);
          } else {
            this.audio.volume = targetVol;
            clearInterval(this.fadeInterval);
            this.fadeInterval = null;
          }
        }, stepTime);
      }).catch(() => {});
    }
  }

  setSoundEnabled(enabled) {
    StorageService.setSoundEnabled(enabled);
    if (!enabled) {
      this.fadeOut(500);
    } else {
      if (this.currentScreen !== 'theory' && this.currentScreen !== 'test') {
        this.fadeIn(this.targetVolume, 700);
      }
    }
  }
}

export const AudioService = new AudioServiceController();
