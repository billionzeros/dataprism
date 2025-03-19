import { cn } from "@/lib/utils";
import type React from "react";
import BaseBlock from "./BaseBlock";
import { useEffect, useRef, useState } from "react";

interface Props {
	content: string;
	size: "small" | "medium" | "large";
	focus?: boolean;
}

const Paragraph: React.FC<Props> = ({ content, size, focus }) => {
	const editableRef = useRef<HTMLDivElement>(null);
	const [showPlaceholder, setShowPlaceholder] = useState(content.length === 0);

	const placeHolderContent = `Write, Press "Space" for AI, Type ' / " for commands`;

	const variants: Record<Props["size"], string> = {
		small: "text-base",
		medium: "text-lg",
		large: "text-xl",
	};

	useEffect(() => {
		if (focus && editableRef.current) {
			editableRef.current.focus();

			const selection = window.getSelection();
			const range = document.createRange();

			if (editableRef.current.firstChild) {
				range.setStart(editableRef.current.firstChild, 0);
			} else {
				range.setStart(editableRef.current, 0);
			}

			range.collapse(true);
			selection?.removeAllRanges();
			selection?.addRange(range);
		}
	}, [focus]);

	const handleOnChange = (e: React.ChangeEvent<HTMLDivElement>) => {
		if (e.target.textContent) {
			setShowPlaceholder(false);
		}

		if (!e.target.textContent) {
			setShowPlaceholder(true);
		}

		console.log(e.target.textContent);
	};

	const handleBlur = (e: React.FocusEvent<HTMLDivElement>) => {
		console.log("Push update to the Database", e.target.textContent);
	};

	return (
		<BaseBlock>
			<div
				ref={editableRef}
				contentEditable
				suppressContentEditableWarning
				onChange={handleOnChange}
				onInput={handleOnChange}
				onBlur={handleBlur}
				className={cn(
					"text-custom-text-primary w-full border-none outline-none",
					variants[size],
					showPlaceholder ? "text-custom-gray-primary" : "",
				)}
			>
				{!showPlaceholder ? content : placeHolderContent}
			</div>
		</BaseBlock>
	);
};

export default Paragraph;
