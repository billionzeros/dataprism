import { cn } from "@/lib/utils";
import type React from "react";
import BaseBlock from "./BaseBlock";

interface Props {
	content: string;
	size: "small" | "medium" | "large";
}

const Header: React.FC<Props> = ({ content = "", size = "small" }) => {
	const variants: Record<Props["size"], string> = {
		small: "text-2xl font-bold",
		medium: "text-3xl font-bold",
		large: "text-4xl font-bold",
	};

	return (
		<BaseBlock>
			<div
				contentEditable
				suppressContentEditableWarning
				className={cn(
					"text-custom-text-primary w-full border-none outline-none",
					variants[size],
				)}
			>
				{content}
			</div>
		</BaseBlock>
	);
};

export default Header;
