"use client";

import { createContext, useContext, useState, ReactNode } from "react";

// Define context type
interface GlobalContextProps {
    walletAddress: string | null;
    setWalletAddress: (address: string | null) => void;
}

// Create context
const GlobalContext = createContext<GlobalContextProps | undefined>(undefined);

// Provider component
export function GlobalProvider({ children }: { children: ReactNode }) {
    const [walletAddress, setWalletAddress] = useState<string | null>(null);

    return (
        <GlobalContext.Provider value={{ walletAddress, setWalletAddress }}>
            {children}
        </GlobalContext.Provider>
    );
}

// Custom hook to use GlobalContext
export function useGlobalContext() {
    const context = useContext(GlobalContext);
    if (!context) {
        throw new Error("useGlobalContext must be used within a GlobalProvider");
    }
    return context;
}
