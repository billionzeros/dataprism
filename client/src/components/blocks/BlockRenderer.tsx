import { cn } from "@/lib/utils";
import {
	addBlockAfterAtom,
	type AnyBlockContent,
	type Block,
	type BlockCid,
	type BlockContent,
} from "@/store/blocks";
import type React from "react";
import Header from "./Header";
import Paragraph from "./Paragraph";
import { useCallback, useRef } from "react";
import { useSetAtom } from "jotai";

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
