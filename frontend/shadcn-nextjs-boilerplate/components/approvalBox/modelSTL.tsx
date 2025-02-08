"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { Button } from "@/components/ui/button";

// Dynamically import StlViewer to avoid SSR issues
const StlViewer = dynamic(() => import("react-stl-viewer").then((mod) => mod.StlViewer), {
    ssr: false,
});

interface ModelSTLApprovalProps {
    modelSrc: string; // STL file path
    onApprove: () => void;
    onReject: () => void;
}

export default function ModelSTLApproval({ modelSrc, onApprove, onReject }: ModelSTLApprovalProps) {
    const style = {
        width: "100%",
        height: "100%",
    };

    return (
        <div className="bg-[#27272A] p-5 rounded-lg shadow-md flex flex-col items-center border-4 border-[#eab71a] w-full">
            {/* STL Model Viewer */}
            <div className="w-full h-64">
                {/*<StlViewer style={style} orbitControls shadows url={modelSrc} />*/}
            </div>

            {/* Buttons */}
            <div className="mt-4 flex space-x-4">
                <Button
                    onClick={onApprove}
                    className="bg-[#eab71a] text-white font-bold py-2 px-6 rounded-md shadow-md hover:bg-yellow-600 transition"
                >
                    Yes!
                </Button>

                <Button
                    onClick={onReject}
                    className="bg-gray-300 text-gray-800 font-bold py-2 px-6 rounded-md shadow-md hover:bg-gray-400 transition border border-[#EAB71A]"
                >
                    No
                </Button>
            </div>
        </div>
    );
}
