import { StorageService } from './storageService.js';

class AudioServiceController {
  constructor() {
    this.audio = null;
    this.fadeInterval = null;
    this.currentScreen = 'levels';
    this.hasUserInteracted = false;
    this.isFinished = false;
    this.targetVolume = 0.4;
  }

  init() {
    // Check if intro music has already played to the end in the current session
    if (sessionStorage.getItem('eb_intro_finished') === 'true') {
      this.isFinished = true;
    }

    try {
      const audioUrl = new URL('../assets/audio/intro_theme.mp3', import.meta.url).href;
      this.audio = new Audio(audioUrl);
      this.audio.preload = 'auto';
      this.audio.volume = this.targetVolume;

      // Track when the melody completes naturally
      this.audio.addEventListener('ended', () => {
        this.isFinished = true;
        sessionStorage.setItem('eb_intro_finished', 'true');
        console.log('[AudioService] Intro music finished. Marked for session.');
      });

      // Global user interaction listener (for browser autoplay policies)
      const tryPlayOnGesture = () => {
        this.hasUserInteracted = true;
        if (!this.isFinished && StorageService.getSoundEnabled() && this.currentScreen !== 'theory' && this.currentScreen !== 'test') {
          if (this.audio && this.audio.paused) {
            this.playIntro();
          }
        }
        window.removeEventListener('pointerdown', tryPlayOnGesture);
        window.removeEventListener('keydown', tryPlayOnGesture);
      };

      window.addEventListener('pointerdown', tryPlayOnGesture, { once: true });
      window.addEventListener('keydown', tryPlayOnGesture, { once: true });

      // Attempt immediate autoplay on start
      this.playIntro();
    } catch (e) {
      console.warn('[AudioService] Audio init error:', e);
    }
  }

  playIntro() {
    if (!this.audio || this.isFinished) return;
    if (!StorageService.getSoundEnabled()) return;
    if (this.currentScreen === 'theory' || this.currentScreen === 'test') return;
    if (!this.audio.paused) return;

    this.audio.volume = this.targetVolume;
    const playPromise = this.audio.play();
    if (playPromise !== undefined) {
      playPromise.catch(() => {
        // Autoplay policy prevented immediate playback; gesture listener will trigger it.
      });
    }
  }

  onScreenChange(newScreen) {
    this.currentScreen = newScreen;

    if (!this.audio || this.isFinished) return;

    // Fade out softly when entering Rules or Test
    if (newScreen === 'theory' || newScreen === 'test') {
      this.fadeOut(900);
    } 
    // Resume when returning to menus (if not finished and sound is enabled)
    else if (newScreen === 'levels' || newScreen === 'lessons' || newScreen === 'leaderboard') {
      if (StorageService.getSoundEnabled() && this.audio.paused && !this.isFinished) {
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
    if (!this.audio || this.isFinished) return;
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
      if (this.currentScreen !== 'theory' && this.currentScreen !== 'test' && !this.isFinished) {
        this.fadeIn(this.targetVolume, 700);
      }
    }
  }
}

export const AudioService = new AudioServiceController();
