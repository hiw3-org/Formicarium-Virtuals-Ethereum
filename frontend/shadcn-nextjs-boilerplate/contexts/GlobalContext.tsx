"use client";

import { createContext, useContext, useState, ReactNode } from "react";

// Define message structure
interface ChatMessage {
    text: string;
    isUser: boolean; // True if user sent, false if AI response
}

// Define context type
interface GlobalContextProps {
    walletAddress: string | null;
    setWalletAddress: (address: string | null) => void;
    messages: ChatMessage[];
    setMessages: React.Dispatch<React.SetStateAction<ChatMessage[]>>;
}

// Create context
const GlobalContext = createContext<GlobalContextProps | undefined>(undefined);

// Provider component
export function GlobalProvider({ children }: { children: ReactNode }) {
    const [walletAddress, setWalletAddress] = useState<string | null>(null);
    const [messages, setMessages] = useState<ChatMessage[]>([]); // Store chat messages

    return (
        <GlobalContext.Provider value={{ walletAddress, setWalletAddress, messages, setMessages }}>
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
