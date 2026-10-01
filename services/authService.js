const STORAGE_KEY_USER = 'eb_current_user';
const STORAGE_KEY_GUEST_ID = 'eb_guest_device_id';

let currentUser = null;

try {
  if (typeof localStorage !== 'undefined') {
    const saved = localStorage.getItem(STORAGE_KEY_USER);
    if (saved) {
      currentUser = JSON.parse(saved);
    }
  }
} catch (e) {
  console.warn('Failed to load user session from localStorage', e);
}

function getGuestId() {
  let guestId = localStorage.getItem(STORAGE_KEY_GUEST_ID);
  if (!guestId) {
    const randomPart =
      typeof crypto !== 'undefined' && crypto.randomUUID
        ? crypto.randomUUID().slice(0, 8)
        : Math.random().toString(36).substring(2, 10);
    guestId = `guest_${randomPart}`;
    localStorage.setItem(STORAGE_KEY_GUEST_ID, guestId);
  }
  return guestId;
}

export const AuthService = {
  getCurrentUser() {
    return currentUser;
  },

  getUserAvatar() {
    if (currentUser && currentUser.avatar) {
      return currentUser.avatar;
    }
    return '';
  },

  isLoggedIn() {
    return currentUser !== null && currentUser.id !== 'guest';
  },

  login(userData) {
    currentUser = {
      id: userData.id || `u_${Date.now()}`,
      name: userData.name || 'Student',
      email: userData.email || '',
      avatar: userData.avatar || ''
    };
    try {
      localStorage.setItem(STORAGE_KEY_USER, JSON.stringify(currentUser));
    } catch (e) {
      console.warn('Failed to save user session', e);
    }
    window.dispatchEvent(new CustomEvent('eb:user_changed', { detail: currentUser }));
    return currentUser;
  },

  logout() {
    currentUser = null;
    try {
      localStorage.removeItem(STORAGE_KEY_USER);
    } catch (e) {
      console.warn('Failed to remove user session', e);
    }
    window.dispatchEvent(new CustomEvent('eb:user_changed', { detail: null }));
  }
};
