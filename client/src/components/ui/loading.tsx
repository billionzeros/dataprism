import type React from "react";
import { Loader } from "lucide-react";
import { cn } from "@/lib/utils";

interface LoadingScreenProps {
	message?: string;
	className?: string;
}

const LoadingScreen: React.FC<LoadingScreenProps> = ({
	message = "Loading...",
	className,
}) => {
	return (
		<div
			className={cn(
				"fixed inset-0 bg-custom-background flex flex-col items-center justify-center z-50",
				className,
			)}
		>
			<div className="flex flex-col items-center gap-4">
				<Loader
					className="animate-spin text-custom-text-primary"
					size={36}
					strokeWidth={1.5}
				/>
				<p className="text-custom-text-primary font-mono text-sm">{message}</p>
			</div>
		</div>
	);
};

export default LoadingScreen;
