"use client";

import Image from "next/image";
import {Button} from "@/components/ui/button";
import {FaEye} from "react-icons/fa";
import {HiOutlineExclamationTriangle} from "react-icons/hi2";
import CustomProgressBar from "@/components/progress/progress";

interface ServiceCardProps {
    imageSrc: string;
    onWatch: () => void;
    onReport: () => void;
    serviceId: string;
    serviceState: "printing" | "completed" | "waiting"; // State Options
    servicePrintTime: number;
    servicePrice: number;
    serviceTimeRemaining: number;
}

export default function ServiceCard({
                                        serviceId,
                                        serviceState,
                                        servicePrice,
                                        serviceTimeRemaining,
                                        servicePrintTime,
                                        onWatch,
                                        onReport,
                                        imageSrc,
                                    }: ServiceCardProps) {
    // State-based text colors
    const stateStyle = {
        waiting: "text-[#FDFFFE] border-[#FDFFFE] border-2 text-[20px]",
        completed: "text-[#2AB0CA] border-[#2AB0CA] border-2 text-[20px]",
        printing: "text-[#eab71a] border-[#eab71a] border-2 text-[20px]",
    };

    return (
        <div className="bg-[#27272A] p-5 rounded-lg shadow-md border-4 border-[#eab71a] w-full max-w-lg">

            {/* First Row: Image + Service Details */}
            <div className="grid grid-cols-2 gap-2">
                {/* Left Column (Image) */}
                <div className="flex items-center justify-center">
                    <Image
                        src={imageSrc}
                        alt="Service Image"
                        width={200}
                        height={200}
                        className="rounded-lg shadow-lg"
                    />
                </div>

                {/* Right Column (Service Details) */}
                <div className="flex flex-col space-y-3 text-white">
                    <p className=" text-left text-[16px]"># <span className="font-normal">{serviceId}</span>
                    </p>
                    <div className={`font-semibold text-center ml-1 ${stateStyle[serviceState]}`}>
                        {serviceState.toUpperCase()}
                    </div>
                    <div className={"pl-1 pr-1 pb-5"}>
                        <CustomProgressBar progress={70} color={"#eab71a"}/>
                    </div>
                    <p className="text-[16px]">Print Time: <span className="font-normal">{servicePrintTime} min</span></p>
                    <p className="text-[16px]">Time Remaining: <span
                        className="font-normal">{serviceTimeRemaining} min</span></p>
                    <p className="text-[16px]">Price: <span className="font-normal">${servicePrice.toFixed(2)}</span></p>
                </div>
            </div>

            {/* Second Row: Actions (Watch & Report) */}
            <div className="flex flex-col items-center mt-4 space-y-3">
                {/* Watch Button */}
                <Button
                    disabled={serviceState === "waiting"}
                    onClick={onWatch}
                    className="bg-[#27272A] text-white font-bold py-2 px-6 rounded-md shadow-md border border-white
               hover:bg-[#eab71a] hover:text-black transition duration-300"
                >
                    Watch on camera
                </Button>


                {/* Report Button */}
                <Button
                    disabled={serviceState === "printing" || serviceState === "waiting"}
                    onClick={onReport}
                    className="bg-[#27272A] text-[#2AB0CA] font-bold py-2 px-6 rounded-md shadow-md border border-[#2AB0CA]
               hover:bg-[#2AB0CA] hover:text-black transition duration-300"
                >
                    Report as uncompleted
                </Button>
            </div>
        </div>
    );
}
