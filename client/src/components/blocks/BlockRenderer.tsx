import { cn } from "@/lib/utils";
import type { Block, BlockCid, BlockContent } from "@/store/blocks";
import type React from "react";
import Header from "./Header";
import Paragraph from "./Paragraph";

interface Props {
	className?: string;
	blockCid: BlockCid;
	blockContent: BlockContent;
	focus?: boolean;
}

const BlockRenderer: React.FC<Props> = ({
	blockContent,
	blockCid,
	className,
	focus,
}) => {
	const renderBlock = () => {
		switch (blockContent.type) {
			case "header":
				return (
					<Header
						key={`header-${blockCid.id}`}
						content={blockContent.text ?? ""}
						size={blockContent.size ?? "small"}
					/>
				);

			case "paragraph":
				return (
					<Paragraph
						key={`paragraph-${blockCid.id}`}
						content={blockContent.text ?? ""}
						size={blockContent.size ?? "small"}
						focus={focus}
					/>
				);
		}
	};
	return (
		<div key="block-renderer" className={cn("block-renderer", className)}>
			{renderBlock()}
		</div>
	);
};

export default BlockRenderer;
