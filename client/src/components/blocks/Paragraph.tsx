import { cn } from "@/lib/utils";
import type React from "react";
import BaseBlock from "./BaseBlock";

interface Props {
	content: string;
	size: "small" | "medium" | "large";
}

const Paragraph: React.FC<Props> = ({ content, size }) => {
	const variants: Record<Props["size"], string> = {
		small: "text-base",
		medium: "text-lg",
		large: "text-xl",
	};

	return (
		<BaseBlock>
			<div
				contentEditable
				className={cn(
					"text-custom-text-primary w-fit border-none outline-none",
					variants[size],
				)}
			>
				{content}
			</div>
		</BaseBlock>
	);
};

export default Paragraph;
