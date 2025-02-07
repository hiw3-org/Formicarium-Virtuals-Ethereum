"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import Image from "next/image";
import Link from "next/link";
import { Syncopate } from "next/font/google";
import { ethers } from "ethers"; // Import ethers.js

// Import Google Font using Next.js
const syncopate = Syncopate({ weight: "700", subsets: ["latin"] });

export default function Navbar(props: { brandText: string }) {
    const [walletAddress, setWalletAddress] = useState<string | null>(null);

    // Function to Connect MetaMask Wallet
    const connectWallet = async () => {
        if (typeof window.ethereum !== "undefined") {
            try {
                const provider = new ethers.BrowserProvider(window.ethereum);
                const accounts = await provider.send("eth_requestAccounts", []);
                setWalletAddress(accounts[0]); // Set connected wallet address
            } catch (error) {
                console.error("Error connecting wallet:", error);
            }
        } else {
            alert("MetaMask is not installed. Please install it to connect.");
        }
    };

    return (
        <nav className="fixed left-0 right-0 z-50 flex items-center px-6 py-3 bg-white/0 backdrop-blur-md shadow-md dark:bg-black/50">
            {/* Left Side - Logo & Styled Brand Name */}
            <div className="flex items-center space-x-3">
                <Image src="/logo.png" alt="Logo" width={40} height={40} className="w-10 h-10" />
                <Link
                    href="/"
                    className={`${syncopate.className} text-[#eab71a] text-center font-bold flex items-center`}
                    style={{ fontSize: "13px" }} // Set font size to 15px
                >
                    {props.brandText}
                </Link>
            </div>

            {/* Right Side - Navigation Tabs & Connect Wallet Button */}
            <div className="flex items-center space-x-6 ml-auto">
                <Link href="/dashboard/chat/" className="text-[#FDFFFE] hover:text-[#EAB71A] transition">Chat</Link>
                <Link href="/dashboard/production/" className="text-[#FDFFFE] hover:text-[#EAB71A] transition">Production</Link>
                <Link href="/dashboard/help/" className="text-[#FDFFFE] hover:text-[#EAB71A] transition">Help</Link>

                {/* Connect Wallet Button */}
                {walletAddress ? (
                    <span className="text-[#eab71a] font-bold">
                        {walletAddress.slice(0, 6)}...{walletAddress.slice(-4)}
                    </span>
                ) : (
                    <Button
                        onClick={connectWallet}
                        className="bg-black text-white font-bold py-2 px-4 rounded-md shadow-md border border-white
                                   hover:bg-[#eab71a] hover:text-black transition duration-300"
                    >
                        Connect Wallet
                    </Button>
                )}
            </div>
        </nav>
    );
}
