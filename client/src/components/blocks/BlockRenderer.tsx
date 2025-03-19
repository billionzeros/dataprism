import { cn } from "@/lib/utils";
import type React from "react";

interface Props {
	className?: string;
	children: React.ReactNode;
}

const BlockRenderer: React.FC<Props> = ({ children, className }) => {
	return (
		<div className={cn("cursor-text min-h-screen", className)}>{children}</div>
	);
};

export default BlockRenderer;
