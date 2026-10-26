"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { BackendState, getState } from "@/lib/api";

type BackendContextValue = {
  state: BackendState | null; // null = the backend cannot be reached
  refresh: () => void;
};

const BackendContext = createContext<BackendContextValue>({
  state: null,
  refresh: () => {},
});

export function useBackend() {
  return useContext(BackendContext);
}

// Asks the backend for its current state twice a second and shares it with the page.
export function BackendProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<BackendState | null>(null);

  const refresh = useCallback(() => {
    getState()
      .then(setState)
      .catch(() => setState(null));
  }, []);

  useEffect(() => {
    refresh();
    const timer = setInterval(refresh, 500);
    return () => clearInterval(timer);
  }, [refresh]);

  return (
    <BackendContext.Provider value={{ state, refresh }}>
      {children}
    </BackendContext.Provider>
  );
}
