import { cn } from "@/lib/utils";
import type React from "react";
import { forwardRef } from "react";

type IconProps = {
	icon: React.ElementType;
	size?: number;
	strokeWidth?: number;
	className?: string;
} & React.ComponentPropsWithoutRef<"svg">;

// This component is used to render icons with a specific size and stroke width.
const Icon = forwardRef<SVGSVGElement, IconProps>(
	(
		{ icon: IconComponent, size = 20, strokeWidth = 2, className, ...props },
		ref,
	) => {
		return (
			<IconComponent
				ref={ref}
				size={size}
				strokeWidth={strokeWidth}
				className={cn("text-custom-gray-secondary", className)}
				{...props}
			/>
		);
	},
);

export default Icon;
