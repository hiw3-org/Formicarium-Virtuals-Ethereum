"use client";

import {createContext, useContext, useState, ReactNode, useEffect} from "react";
import {fetchContractOwner, fetchOrders, fetchPrinters} from "@/lib/blockchain";

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
    contractOwner: string | null;
    contractOrders:any|null;
    contractPrinters:any|null;
    image2Dmodel : string|null;
    setImage2Dmodel : (image:string|null) => void;
    imageSTLmodel : string|null;
    setImageSTLmodel : (image:string|null) => void;
    stlModel : string|null;
    setSTLModel : (model:string|null) => void;
}

// Create context
const GlobalContext = createContext<GlobalContextProps | undefined>(undefined);

// Provider component
export function GlobalProvider({ children }: { children: ReactNode }) {
    const [walletAddress, setWalletAddress] = useState<string | null>(null);
    const [messages, setMessages] = useState<ChatMessage[]>([]); // Store chat messages
    const [contractOwner, setContractOwner] = useState<string | null>(null);
    const [contractOrders, setContractOrders] = useState<any | null>(null);
    const [contractPrinters, setContractPrinters] = useState<any | null>(null);
    const [image2Dmodel, setImage2Dmodel] = useState<string | null>(null);
    const [imageSTLmodel, setImageSTLmodel] = useState<string | null>(null);
    const [stlModel, setSTLModel] = useState<string | null>(null);



    // Fetch contract data when app starts
    useEffect(() => {
        fetchContractOwner().then(setContractOwner);
        fetchOrders().then(setContractOrders);
        fetchPrinters().then(setContractPrinters);
    }, []);

    return (
        <GlobalContext.Provider value={{
            walletAddress,
            setWalletAddress,
            messages, setMessages,
            contractOwner,
            contractOrders,
            contractPrinters,
            image2Dmodel,
            setImage2Dmodel,
            stlModel,
            setSTLModel,
            imageSTLmodel,
            setImageSTLmodel
        }}>
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
