"use client";

import {createContext, useContext, useState, ReactNode, useEffect} from "react";
import {fetchBalanceERC20, fetchBalanceETH, fetchContractOwner, fetchOrders, fetchPrinters} from "@/lib/blockchain";

// Define message structure
interface ChatMessage {
    message: string;
    role: string;
}

// Define context type
interface GlobalContextProps {
    walletAddress: string | null;
    setWalletAddress: (address: string | null) => void;
    messages: ChatMessage[];
    setMessages: React.Dispatch<React.SetStateAction<ChatMessage[]>>;
    contractOwner: string | null;
    productionOrders:any|null;
    productionPrinters:any|null;
    image2Dmodel : string|null;
    setImage2Dmodel : (image:string|null) => void;
    imageSTLmodel : string|null;
    setImageSTLmodel : (image:string|null) => void;
    stlModel : string|null;
    setSTLModel : (model:string|null) => void;

    balanceETH: bigint | null;
    setBalanceETH: (balance: bigint | null) => void;
    balanceERC20: bigint | null;
    setBalanceERC20: (balance: bigint | null) => void;
}

// Create context
const GlobalContext = createContext<GlobalContextProps | undefined>(undefined);

// Provider component
export function GlobalProvider({ children }: { children: ReactNode }) {
    const [walletAddress, setWalletAddress] = useState<string | null>(null);
    const [messages, setMessages] = useState<ChatMessage[]>([]); // Store chat messages
    const [contractOwner, setContractOwner] = useState<string | null>(null);

    const [productionOrders, setProductionOrders] = useState<any | null>(null);
    const [productionPrinters, setProductionPrinters] = useState<any | null>(null);

    const [image2Dmodel, setImage2Dmodel] = useState<string | null>(null);
    const [imageSTLmodel, setImageSTLmodel] = useState<string | null>(null);
    const [stlModel, setSTLModel] = useState<string | null>(null);

    const [balanceETH, setBalanceETH] = useState<bigint | null>(null);
    const [balanceERC20, setBalanceERC20] = useState<bigint | null>(null);



    // Fetch contract data when app starts
    useEffect(() => {
        if (!walletAddress) return;
        console.log("Fetching data for wallet address:", walletAddress);
        fetchContractOwner().then(setContractOwner);
        fetchOrders().then(setProductionOrders);
        fetchPrinters().then(setProductionPrinters);

        fetchBalanceETH(walletAddress).then(setBalanceETH);
        fetchBalanceERC20(walletAddress).then(setBalanceERC20);

    }, [walletAddress]);

    return (
        <GlobalContext.Provider value={{
            walletAddress,
            setWalletAddress,
            messages, setMessages,
            contractOwner,
            productionOrders,
            productionPrinters,
            image2Dmodel,
            setImage2Dmodel,
            stlModel,
            setSTLModel,
            imageSTLmodel,
            setImageSTLmodel,
            balanceETH,
            setBalanceETH,
            balanceERC20,
            setBalanceERC20
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
