"use client";

import ServiceCard from "@/components/card/Service";

import {Syncopate} from "next/font/google";

const syncopate = Syncopate({weight: "700", subsets: ["latin"]});

export default function ProductionPage() {

    const fakeService = {
        imageSrc: "/model2d.png",  // Replace with your image path
        serviceId: "123ABC",
        serviceState: "printing",
        servicePrintTime: 120, // in minutes
        serviceTimeRemaining: 60, // in minutes
        servicePrice: 29.99, // in dollars
    };


    return (
        <div>
            <div className="flex flex-col w-full">
                {/* Order Summary Title */}
                <div
                    className={`${syncopate.className} text-[#eab71a] text-[36px] text-center font-bold flex items-center`}>Production
                    orders
                </div>
            </div>
            <div className={"flex gap-4"}>


                <ServiceCard
                    imageSrc={fakeService.imageSrc}
                    serviceId={fakeService.serviceId}
                    serviceState={fakeService.serviceState}
                    servicePrintTime={fakeService.servicePrintTime}
                    serviceTimeRemaining={fakeService.serviceTimeRemaining}
                    servicePrice={fakeService.servicePrice}
                    onWatch={() => alert(`Watching service: ${fakeService.serviceId}`)}
                    onReport={() => alert(`Reporting service: ${fakeService.serviceId}`)}
                />
                <ServiceCard
                    imageSrc={fakeService.imageSrc}
                    serviceId={fakeService.serviceId}
                    serviceState={"waiting"}
                    servicePrintTime={fakeService.servicePrintTime}
                    serviceTimeRemaining={fakeService.serviceTimeRemaining}
                    servicePrice={fakeService.servicePrice}
                    onWatch={() => alert(`Watching service: ${fakeService.serviceId}`)}
                    onReport={() => alert(`Reporting service: ${fakeService.serviceId}`)}
                />
                <ServiceCard
                    imageSrc={fakeService.imageSrc}
                    serviceId={fakeService.serviceId}
                    serviceState={"completed"}
                    servicePrintTime={fakeService.servicePrintTime}
                    serviceTimeRemaining={fakeService.serviceTimeRemaining}
                    servicePrice={fakeService.servicePrice}
                    onWatch={() => alert(`Watching service: ${fakeService.serviceId}`)}
                    onReport={() => alert(`Reporting service: ${fakeService.serviceId}`)}
                />
            </div>
        </div>
    );
}
