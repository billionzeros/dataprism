import { cn } from "@/lib/utils";
import type React from "react";

interface Props {
	content: string;
	size: "small" | "medium" | "large";
}

const Header: React.FC<Props> = ({ content, size }) => {
	const variants: Record<Props["size"], string> = {
		small: "text-2xl font-bold",
		medium: "text-3xl font-bold",
		large: "text-4xl font-bold",
	};

	return (
		<div
			contentEditable
			className={cn(
				"text-custom-text-primary w-fit border-none outline-none",
				variants[size],
			)}
		>
			{content}
		</div>
	);
};

export default Header;
