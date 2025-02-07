"use client";

import { Button } from "@/components/ui/button";

interface OrderSummaryProps {
    dimensions: number[];
    quantity: number;
    price: number;
    fee: number;
    onApprove: () => void;
}

export default function OrderSummary({ dimensions, quantity, price, fee, onApprove }: OrderSummaryProps) {
    return (
        <div className="bg-[#ebbf3a] p-5 rounded-lg shadow-md flex border-4 border-[#68510A] w-full max-w-2xl">
            <div className="flex flex-col w-full">
                {/* Order Summary Title */}
                <div className="p-2 font-bold text-[24px] text-center">Order Summary</div>

                {/* Instruction */}
                <div className="p-2 text-[12px] text-center">
                    Check the dimensions and quantity. If that is not right, define the changes in the Chat.
                </div>

                {/* Dimensions Section */}
                <div className="p-2 pb-0">
                    <p className="text-[16px]">Dimensions</p>
                    <div className="text-[20px] flex flex-row items-end space-x-2">
                        <div className="bg-[#eab71a] px-6 py-1 rounded-md text-black text-center">{dimensions[0]}</div>
                        <div className="pb-1">x</div>
                        <div className="bg-[#eab71a] px-6 py-1 rounded-md text-black text-center">{dimensions[1]}</div>
                        <div className="pb-1">x</div>
                        <div className="bg-[#eab71a] px-6 py-1 rounded-md text-black text-center">{dimensions[2]}</div>
                        <div className="pb-1">mm</div>
                    </div>
                </div>

                {/* Quantity Section */}
                <div className="flex flex-row w-full p-2 pb-0 items-center text-[16px]">
                    <p className="font-semibold">Quantity:</p>
                    <p className="text-black font-semibold pl-4">{quantity}</p>
                </div>

                {/* Price & Fee Section */}
                <div className="grid grid-cols-2 items-center w-full bg-[#D9D9D9] p-3 rounded-md border-2 border-black border-opacity-20">
                    {/* Left Column (Price & Fee) */}
                    <div className="flex flex-col space-y-2">
                        {/* Price Section */}
                        <div>
                            <p className="text-black">Price for your product:</p>
                            <p className="text-black text-[24px]">${price.toFixed(2)}</p>
                        </div>

                        {/* Fee Section */}
                        <div className="flex flex-row items-center gap-x-1 text-[#637381]">
                            <p className="text-[20px]">+</p>
                            <p className="text-[18px]">${fee.toFixed(2)}</p>
                            <p className="text-[16px]">Tx Fee</p>
                        </div>
                    </div>

                    {/* Right Column (Button) */}
                    <div className="flex justify-end items-end">
                        <Button
                            onClick={onApprove}
                            className="bg-[#eab71a] text-black font-bold py-2 px-6 rounded-sm shadow-md transition border border-black pl-10 pr-10"
                        >
                            BUY
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    );
}
