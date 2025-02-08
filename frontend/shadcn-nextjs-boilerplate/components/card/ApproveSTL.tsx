"use client";

import Image from "next/image";
import { Button } from "@/components/ui/button";
import { FaCheck } from "react-icons/fa6";
import { HiArrowPath } from "react-icons/hi2";
import {useEffect, useState} from "react";

import { useGlobalContext } from "@/contexts/GlobalContext";

export default function ApproveCardSTL() {
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
        </div>
    );
}
