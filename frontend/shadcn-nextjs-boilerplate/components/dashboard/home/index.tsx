/* eslint-disable */
"use client";

import {Button} from "@/components/ui/button";
import Navbar from "@/components/navbar/Navbar";
import Chat from "@/components/chat/chat";
import Model2dApproval from "@/components/approvalBox/model2d";
import ModelSTLApproval from "@/components/approvalBox/modelSTL";

interface Props {
}

export default function Home(props: Props) {

    const predefinedResponses = [
        "Hello! How can I help you today?",
        "I'm just a simulated AI, but I can respond with predefined messages.",
        "Tell me more about what you're working on!",
        "That sounds interesting! Could you elaborate?",
    ];

    const handleApprove = () => {
        alert("You approved the image!");
    };

    const handleReject = () => {
        alert("You rejected the image.");
    };

    return (
        <div>
            {/* Navbar */}
            <Navbar brandText="formicarium"/>

            {/* Background Section */}
            <div
                className="w-screen h-screen bg-center bg-repeat pt-16"
                style={{backgroundImage: "url('/background.png')"}}
            >

                <div className="container mx-auto px-6 py-10">
                    <div className="grid grid-cols-2 md:grid-cols-3 ">
                        {/* Left Column (Transparent) */}
                        <div className="bg-transparent md:col-span-2 p-0 rounded-lg shadow-md">
                            <Chat responses={predefinedResponses}/>;
                        </div>

                        {/* Right Column (Image & Buttons) */}
                        <div className="md:col-span-1 ">
                            <Model2dApproval imageSrc={"/model2d.png"} onApprove={handleApprove}
                                             onReject={handleReject}/>
                            <ModelSTLApproval
                                modelSrc="/models/20mm_cube.stl" // Path to your STL file
                                onApprove={handleApprove}
                                onReject={handleReject}
                            />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
