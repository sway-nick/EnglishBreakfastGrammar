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
      this.audio.loop = true; // Seamless loop across sessions

      // Global user interaction listener (to unlock browser autoplay policies)
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

      // Attempt immediate autoplay on startup
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
        // Handled by user gesture listener on first click
      });
    }
  }

  onScreenChange(newScreen) {
    this.currentScreen = newScreen;

    if (!this.audio) return;

    // Fade out softly when entering Rules or Test mode
    if (newScreen === 'theory' || newScreen === 'test') {
      this.fadeOut(900);
    } 
    // Smoothly resume and fade back in when returning to menus (levels, lessons, leaderboard)
    else if (newScreen === 'levels' || newScreen === 'lessons' || newScreen === 'leaderboard') {
      if (StorageService.getSoundEnabled()) {
        this.fadeIn(this.targetVolume, 900);
      }
    }
  }

  fadeOut(durationMs = 900) {
    if (!this.audio || this.audio.paused) return;
    if (this.fadeInterval) clearInterval(this.fadeInterval);

    const startVol = this.audio.volume;
    const steps = 18;
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
    if (this.fadeInterval) clearInterval(this.fadeInterval);

    this.audio.volume = 0;
    const playPromise = this.audio.play();
    if (playPromise !== undefined) {
      playPromise.then(() => {
        const steps = 18;
        const stepTime = Math.max(20, durationMs / steps);
        const volStep = targetVol / steps;

        this.fadeInterval = setInterval(() => {
          if (this.audio.volume < targetVol - volStep) {
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
