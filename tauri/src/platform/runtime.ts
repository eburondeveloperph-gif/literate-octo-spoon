type TauriInternals = {
  invoke?: unknown;
  transformCallback?: unknown;
};

type TauriWindow = Window & {
  __TAURI_INTERNALS__?: TauriInternals;
};

export function hasTauriRuntime(): boolean {
  if (typeof window === 'undefined') {
    return false;
  }

  const tauriWindow = window as TauriWindow;

  return (
    typeof tauriWindow.__TAURI_INTERNALS__?.invoke === 'function' &&
    typeof tauriWindow.__TAURI_INTERNALS__?.transformCallback === 'function'
  );
}

export function requireTauriRuntime(feature: string): void {
  if (!hasTauriRuntime()) {
    throw new Error(
      `${feature} requires the Tauri runtime. Open the app through Tauri instead of loading the Vite dev server directly in a browser.`,
    );
  }
}
