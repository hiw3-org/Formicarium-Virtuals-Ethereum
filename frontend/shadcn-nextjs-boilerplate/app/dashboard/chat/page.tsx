"use client";
import Chat from "@/components/chat/chat";
import OrderSummary from "@/components/card/OrderSummary";
import ApproveCard from "@/components/card/Approve";
import ApproveCardSTL from "@/components/card/ApproveSTL";
import {Syncopate} from "next/font/google";
import {useEffect} from "react";

const syncopate = Syncopate({ weight: "700", subsets: ["latin"] });

import { useGlobalContext } from "@/contexts/GlobalContext";

export default function ChatPage() {

    const { image2Dmodel } = useGlobalContext();

    const approve2Dmodel = async () => {
        console.log("Approved 2D Model");

    }
    return (
      <div className="grid grid-cols-2 gap-8">
        {/* Left Column (Chat) */}
        <div className="bg-transparent md:col-span-1 p-0 rounded-lg shadow-md">
          <div className="flex flex-col w-full">
            {/* Order Summary Title */}
            <div
              className={`${syncopate.className} text-[#eab71a] text-[48px] text-center font-bold flex items-center`}
            >
              formicarium
            </div>
            <div className="text-[22px] text-[#2AB0CA]">
              Next-Gen Manufacturing
            </div>
            <div className="text-[20px] text-[#F0F0F0]} text-white">
              Shared Machines, Infinite Possibilities.
            </div>
          </div>
          <Chat/>
        </div>

        {/* Right Column (Approval & Order Summary) */}
        <div className="md:col-span-1 w-6/7 max-w-lg min-w-[400px] flex flex-col space-y-4">
          <ApproveCard/>
          <ApproveCardSTL          />
          <OrderSummary/>
        </div>
      </div>
    );
}
