"use client";

import Image from "next/image";
import { Button } from "@/components/ui/button";
import { FaCheck } from "react-icons/fa6";
import { HiArrowPath } from "react-icons/hi2";
import {useEffect, useState} from "react";

interface ImageApprovalProps {
    onApprove: () => void;
    onReject: () => void;
    text: string;
}

import { useGlobalContext } from "@/contexts/GlobalContext";

export default function ApproveCardSTL({ onApprove, onReject }: ImageApprovalProps) {
    const { imageSTLmodel } = useGlobalContext();
    const defaultImage = "/approveSTLBackground.png";
    const [imageSrc, setImageSrc] = useState<string>(defaultImage);

    useEffect(() => {
        if (imageSTLmodel) {
            setImageSrc(imageSTLmodel); // Update image when context changes
        } else {
            setImageSrc(defaultImage); // Ensure default image is always set
        }
    }, [imageSTLmodel]);


    return (
        <div className="bg-[#27272A] p-5 rounded-lg shadow-md flex border-4 border-[#eab71a] w-full max-w-2xl">
            {/* Image Section (Left Side) */}
            <div className="flex p-0 flex-col items-center">
                    <Image
                        src={imageSrc}
                        alt="Description"
                        width={600}
                        height={100}
                        className="h-auto rounded-lg shadow-lg"
                    />
            </div>

            {/*/!* Button Column (Right Side) *!/*/}
            {/*<div className="flex flex-col  items-center ml-4">*/}
            {/*    /!* Yes Button (Above) *!/*/}
            {/*    <Button*/}
            {/*        onClick={onApprove}*/}
            {/*        className="bg-[#eab71a] text-white font-bold py-2 px-6 rounded-sm shadow-md hover:bg-yellow-600 transition mb-4 flex items-center justify-center"*/}
            {/*    >*/}
            {/*        <FaCheck className="w-6 h-6 text-[#0F172A]" />*/}
            {/*    </Button>*/}

            {/*    /!* No Button (Below) *!/*/}
            {/*    <Button*/}
            {/*        onClick={onReject}*/}
            {/*        className="bg-gray-300 text-gray-800 font-bold py-2 px-6 rounded-sm shadow-md hover:bg-gray-400 transition border border-[#EAB71A]"*/}
            {/*    >*/}
            {/*        <HiArrowPath className="w-6 h-6 text-[#0F172A]" />*/}
            {/*    </Button>*/}
            {/*</div>*/}
        </div>
    );
}
