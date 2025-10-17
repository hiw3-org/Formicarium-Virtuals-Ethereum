"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useEffect, useRef, useState } from "react";
import { useGlobalContext } from "@/contexts/GlobalContext"; // Import Global Context
import axios from "axios";

export default function Chat() {
    // Access messages from global context
    const { messages, setMessages , setImage2Dmodel, setSTLModel, walletAddress, setImageSTLmodel} = useGlobalContext();

    // Input state for new messages
    const [inputMessage, setInputMessage] = useState<string>("");
    const [loading, setLoading] = useState<boolean>(false); // State to manage loading

    // Reference for auto-scrolling
    const messagesEndRef = useRef<HTMLDivElement | null>(null);

    // Scroll to the bottom when a new message is added
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const handleSendMessage = async () => {
        if (!inputMessage.trim()) return;

        if(!walletAddress) {
            alert("Please connect your wallet first");
            return;
        }

        setLoading(true); // Show loading state

        // Add user message to chat
        const newMessages = [...messages, { role: "user", message: inputMessage }];
        setMessages(newMessages);

        try {
            const response = await fetch("https://82cf-146-212-21-11.ngrok-free.app/agent/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    prompt: inputMessage,
                    user_id: "12325", // Set user ID dynamically if needed
                }),
            });

            if (!response.ok) throw new Error("Failed to fetch AI response");

            const data = await response.json();
            const aiMessage = data.response; // Extract

            console.log("Data from AI: ", data);

            // Store AI message in chat
            setMessages([...newMessages, { role: "agent", message: aiMessage }]);

            // Store image in global context
            if (data.image_file && data.image_file.content) {
                const imageData=`data:${data.image_file.content_type};base64,${data.image_file.content}`;
                setImage2Dmodel(imageData);
            }

            //Check if image stl file is present
            if (data.stl_file && data.stl_file.content) {
                const stlData=`data:${data.stl_file.content_type};base64,${data.stl_file.content}`;
                setImageSTLmodel(stlData);
            }

        } catch (error) {
            console.error("Error sending message:", error);
            setMessages([...newMessages, { role: "agent", message: "Error: Unable to fetch response from AI." }]);
        }

        setLoading(false); // Hide loading state
        setInputMessage(""); // Clear input field
    };


    // Handle Enter key press
    const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === "Enter") {
            e.preventDefault(); // Prevent default form submission
            handleSendMessage();
        }
    };

    return (
        <div className="flex flex-col w-full max-w-3xl mx-auto p-6 bg-black/50 backdrop-blur-lg rounded-lg shadow-lg border-4 border-[#09090B]">
            {/* Chat Messages */}
            <div className="flex flex-col space-y-4 h-[400px] overflow-y-auto p-2">
                {messages.map((msg, index) => (
                    <div key={index} className={`flex w-full items-center ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                        {msg.role === "user" ? ( // User message
                            <div className="flex w-[70%] rounded-lg border border-gray-600 bg-gray-800/50 p-4 shadow-md">
                                <p className="text-sm text-white">{msg.message}</p>
                            </div>
                        ) : ( // AI response
                            <div className="flex w-[70%] rounded-lg border border-gray-600 bg-gray-700/50 p-4 shadow-md">
                                <p className="text-sm text-white">{msg.message}</p>
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
                    onKeyDown={handleKeyPress}
                    disabled={loading}
                />
                <Button
                    className="h-[60px] w-[100px] px-4 py-2 bg-gray-500/80 hover:bg-gray-600 text-white text-base font-medium rounded-md"
                    onClick={handleSendMessage}
                    disabled={loading}
                >
                    {loading ? "Sending..." : "Submit"}
                </Button>
            </div>
        </div>
    );
}
