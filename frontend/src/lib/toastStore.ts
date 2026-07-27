import { writable } from 'svelte/store';

export interface ToastMessage {
  id: string;
  type: 'success' | 'error' | 'info' | 'warning';
  title: string;
  message: string;
  duration?: number;
}

function createToastStore() {
  const { subscribe, update } = writable<ToastMessage[]>([]);

  function addToast(type: ToastMessage['type'], title: string, message: string, duration = 4000) {
    const id = Math.random().toString(36).substring(2, 9);
    const newToast: ToastMessage = { id, type, title, message, duration };

    update(toasts => [...toasts, newToast]);

    if (duration > 0) {
      setTimeout(() => {
        removeToast(id);
      }, duration);
    }
  }

  function removeToast(id: string) {
    update(toasts => toasts.filter(t => t.id !== id));
  }

  return {
    subscribe,
    success: (title: string, message: string, duration?: number) => addToast('success', title, message, duration),
    error: (title: string, message: string, duration?: number) => addToast('error', title, message, duration),
    info: (title: string, message: string, duration?: number) => addToast('info', title, message, duration),
    warning: (title: string, message: string, duration?: number) => addToast('warning', title, message, duration),
    remove: removeToast
  };
}

export const toast = createToastStore();
