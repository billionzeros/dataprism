import { cn } from "@/lib/utils";
import type {
	AnyBlockContent,
	Block,
	BlockCid,
	BlockContent,
} from "@/store/blocks";
import type React from "react";
import Header from "./Header";
import Paragraph from "./Paragraph";

interface Props {
	className?: string;
	blockCid: BlockCid;
	blockContent: AnyBlockContent;
}

const BlockRenderer: React.FC<Props> = ({
	blockContent,
	blockCid,
	className,
}) => {
	const renderBlock = () => {
		switch (blockContent.type) {
			case "header":
				return (
					<Header
						key={`renderer-${blockCid.id}`}
						cid={blockCid}
						content={blockContent.content}
					/>
				);

			case "paragraph":
				return (
					<Paragraph
						key={`renderer-${blockCid.id}`}
						content={blockContent.content}
						cid={blockCid}
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
