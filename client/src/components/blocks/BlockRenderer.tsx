import { cn } from "@/lib/utils";
import type { Block } from "@/store/blocks";
import type React from "react";
import Header from "./Header";
import Paragraph from "./Paragraph";

interface Props {
	className?: string;
	block: Block;
}

const BlockRenderer: React.FC<Props> = ({ block, className }) => {
	const renderBlock = () => {
		switch (block.content.type) {
			case "header":
				return (
					<Header
						key={block.cid.id}
						content={block.content.text ?? ""}
						size={block.content.size ?? "small"}
					/>
				);

			case "paragraph":
				return (
					<Paragraph
						key={block.cid.id}
						content={block.content.text ?? ""}
						size={block.content.size ?? "small"}
					/>
				);
		}
	};
	return (
		<div
			key="block-renderer"
			className={cn("cursor-text min-h-screen", className)}
		>
			{renderBlock()}
		</div>
	);
};

export default BlockRenderer;
