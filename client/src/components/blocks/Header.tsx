import { cn } from "@/lib/utils";
import type React from "react";
import BaseBlock from "./BaseBlock";
import type { BlockCid, BlockContent } from "@/store/blocks";

interface Props {
	cid: BlockCid;
	content: BlockContent<"header">["content"];
}

const Header: React.FC<Props> = ({ cid, content }) => {
	const variants: Record<Props["content"]["size"], string> = {
		small: "text-2xl font-bold",
		medium: "text-3xl font-bold",
		large: "text-4xl font-bold",
	};

	return (
		<BaseBlock>
			<div
				key={`content-${cid.id}`}
				contentEditable
				suppressContentEditableWarning
				className={cn(
					"text-custom-text-primary w-full border-none outline-none",
					variants[content.size],
				)}
			>
				{content.text}
			</div>
		</BaseBlock>
	);
};

export default Header;
