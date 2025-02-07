"use client";

import Image from "next/image";
import {Button} from "@/components/ui/button";

interface ImageApprovalProps {
    imageSrc: string;
    onApprove: () => void;
    onReject: () => void;
}

export default function Model2dApproval({ imageSrc, onApprove, onReject }: ImageApprovalProps) {
    return (
        <div className="bg-[#27272A] p-5 rounded-lg shadow-md flex flex-col items-center border-4 border-[#eab71a]">
            {/* Image (Full Width) */}
            <Image
                src={imageSrc}
                alt="Description"
                width={500}
                height={100}
                className="h-auto rounded-lg shadow-lg"
            />

            {/* Text Below Image */}
            <p className="mt-4 text-lg font-semibold text-white">
                Are you happy with the image?
            </p>

            {/* Buttons */}
            <div className="mt-4 flex space-x-4">
                {/* Yes Button */}
                <Button
                    onClick={onApprove}
                    className="bg-[#eab71a] text-white font-bold py-2 px-6 rounded-md shadow-md hover:bg-yellow-600 transition"
                >
                    Yes!
                </Button>

                {/* No Button */}
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
