"use client";

import { useGlobalContext } from "@/contexts/GlobalContext";
import { Syncopate } from "next/font/google";
import ServiceCard from "@/components/card/Service";

const syncopate = Syncopate({ weight: "700", subsets: ["latin"] });

export default function ProductionPage() {
    const { productionOrders } = useGlobalContext();

    if (!productionOrders) return <div>Loading...</div>;

    return (
        <div>
            <div className="flex flex-col w-full">
                {/* Order Summary Title */}
                <div className={`${syncopate.className} text-[#eab71a] text-[36px] text-center font-bold flex items-center`}>
                    Production Orders
                </div>
            </div>
            <div className="flex gap-4 flex-wrap">
                {/* Map production orders array to Service Cards */}
                {productionOrders.map((order) => {
                    const currentTime = Math.floor(Date.now() / 1000); // Get current time in seconds

                    // ✅ Ensure all values are numbers, not BigInts
                    const startTime = Number(order.startTime);
                    const duration = Number(order.duration);
                    const price = order.actualPrice ? Number(order.actualPrice.toString()) / 1e18 : 0;


                    let serviceState;
                    if (startTime > currentTime) {
                        serviceState = "waiting";
                    } else if (currentTime < startTime + duration) {
                        serviceState = "printing";

                    } else {
                        serviceState = "completed";
                    }
                    //Log state more explicitly
                    console.log(`Service ${order.ID} is in state: ${serviceState}`);

                    // ✅ Convert remaining time to a safe number
                    const serviceTimeRemaining = Math.max(0, startTime + duration - currentTime);

                    return (
                        <ServiceCard
                            key={order.ID}
                            imageSrc={order.imageSrc}
                            serviceId={order.ID?.slice(0, 10)} // Safer than .substr
                            serviceState={serviceState}
                            servicePrintTime={duration}
                            serviceTimeRemaining={serviceTimeRemaining}
                            servicePrice={price}
                            onWatch={() => alert(`Watching service: ${order.ID}`)}
                            onReport={() => alert(`Reporting service: ${order.ID}`)}
                        />
                    );
                })}
            </div>
        </div>
    );
}
