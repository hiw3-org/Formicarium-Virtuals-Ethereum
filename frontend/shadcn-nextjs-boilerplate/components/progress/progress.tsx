interface CustomProgressBarProps {
    progress: number; // Accepts progress as a prop (0-100)
    color?: string; // Accepts a custom color (optional, defaults to yellow)
}

export default function CustomProgressBar({ progress, color = "#eab71a" }: CustomProgressBarProps) {
    return (
        <div className="w-full bg-gray-300 rounded-full h-8 flex items-center relative">
            {/* Progress Bar */}
            <div
                className="absolute left-0 top-0 h-full rounded-full transition-all duration-300"
                style={{ width: `${Math.min(Math.max(progress, 0), 100)}%`, backgroundColor: color }}
            ></div>

            {/* Progress Text */}
            <p className="absolute w-full text-center font-bold text-black">
                {Math.round(progress)}%
            </p>
        </div>
    );
}
