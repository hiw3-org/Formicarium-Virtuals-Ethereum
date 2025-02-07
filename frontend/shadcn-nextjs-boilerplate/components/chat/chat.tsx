"use client";

/* eslint-disable */
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useEffect, useRef, useState } from "react";

interface Props {
    responses: string[]; // Predefined responses passed as props
}

export default function Chat({ responses }: Props) {
    // Input States
    const [inputMessage, setInputMessage] = useState<string>("");
    const [outputMessages, setOutputMessages] = useState<string[]>([]);

    // Reference for auto-scrolling
    const messagesEndRef = useRef<HTMLDivElement | null>(null);

    // Scroll to the bottom when a new message is added
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [outputMessages]);

    // Simulate response handling (without API)
    const handleTranslate = () => {
        if (!inputMessage.trim()) return; // Prevent empty submissions

        // Simulate response selection from props
        const responseIndex = outputMessages.length % responses.length; // Cycle through responses
        const newResponse = responses[responseIndex];

        setOutputMessages([...outputMessages, inputMessage, newResponse]); // Add both user message & response
        setInputMessage(""); // Clear input
    };

    // Handle Enter key press
    const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === "Enter") {
            e.preventDefault(); // Prevent default form submission
            handleTranslate();
        }
    };

    return (
        <div className="flex flex-col w-full max-w-3xl mx-auto p-6 bg-black/50 backdrop-blur-lg rounded-lg shadow-lg border-4 border-[#09090B] ">
            {/* Chat Messages */}
            <div className="flex flex-col space-y-4 h-[400px] overflow-y-auto p-2">
                {outputMessages.map((msg, index) => (
                    <div key={index} className={`flex w-full items-center ${index % 2 === 0 ? "justify-end" : "justify-start"}`}>
                        {index % 2 === 0 ? ( // User message
                            <div className="flex w-[70%] rounded-lg border border-gray-600 bg-gray-800/50 p-4 shadow-md">
                                <p className="text-sm text-white">{msg}</p>
                            </div>
                        ) : ( // AI response
                            <div className="flex w-[70%] rounded-lg border border-gray-600 bg-gray-700/50 p-4 shadow-md">
                                <p className="text-sm text-white">{msg}</p>
                            </div>
                        )}
                    </div>
                ))}
                {/* Invisible div to auto-scroll to */}
                <div ref={messagesEndRef} />
            </div>

            {/* Chat Input */}
            <div className="mt-5 flex items-center">
                <Input
                    className="mr-2.5 h-full min-h-[54px] w-full px-5 py-5 bg-gray-800/50 text-white border-gray-600 placeholder-gray-400 focus:outline-none focus:border-white"
                    placeholder="Type your message here..."
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyDown={handleKeyPress} // 🔥 Listen for Enter key
                />
                <Button className="h-[60px] w-[100px] px-4 py-2 bg-gray-500/80 hover:bg-gray-600 text-white text-base font-medium rounded-md" onClick={handleTranslate}>
                    Submit
                </Button>
            </div>
        </div>
    );
}
