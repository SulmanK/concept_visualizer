import React, { HTMLAttributes } from "react";
import { usePrefersReducedMotion } from "../../hooks";

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  /**
   * Card variant
   */
  variant?: "default" | "gradient" | "elevated";

  /**
   * Header content
   */
  header?: React.ReactNode;

  /**
   * Footer content
   */
  footer?: React.ReactNode;

  /**
   * Add extra padding to the card
   */
  padded?: boolean;

  /**
   * Card is in loading state
   */
  isLoading?: boolean;

  /**
   * Whether the card should have hover effects
   * @default false
   */
  interactive?: boolean;

  /**
   * Type of hover animation
   * @default 'lift'
   */
  hoverEffect?: "lift" | "glow" | "border" | "scale" | "none";
}

/**
 * Card component for containing content
 */
export const Card: React.FC<CardProps> = ({
  variant = "default",
  header,
  footer,
  padded = true,
  isLoading = false,
  interactive = true,
  hoverEffect = "lift",
  className = "",
  children,
  ...props
}) => {
  const prefersReducedMotion = usePrefersReducedMotion();

  // Base card styles for each variant
  const baseClasses = {
    default:
      "bg-white/90 backdrop-blur-sm rounded-lg shadow-modern border border-indigo-100 overflow-hidden",
    gradient:
      "bg-gradient-to-br from-indigo-50/90 to-white/90 backdrop-blur-sm rounded-lg shadow-modern border border-indigo-100 overflow-hidden",
    elevated: "bg-white border-none rounded-lg shadow-lg overflow-hidden",
  };

  // Transition classes (skip if reduced motion is preferred)
  const transitionClass = !prefersReducedMotion
    ? "transition-all duration-300"
    : "";

  // Classes for different hover effects when card is interactive
  const getHoverClasses = () => {
    if (!interactive || prefersReducedMotion) return "";

    switch (hoverEffect) {
      case "lift":
        return "hover:translate-y-[-4px] hover:shadow-lg";
      case "glow":
        return "hover:shadow-[0_0_15px_rgba(79,70,229,0.3)]";
      case "border":
        return "hover:border-indigo-300";
      case "scale":
        return "hover:scale-[1.02]";
      case "none":
        return "";
      default:
        return "";
    }
  };

  // Combine all card classes
  const cardClass = `${
    baseClasses[variant]
  } ${transitionClass} ${getHoverClasses()} ${className}`.trim();

  // Content, header and footer classes
  const contentClass = padded ? "p-4 sm:p-6" : "";
  const headerClass =
    "px-4 py-3 sm:px-6 border-b border-indigo-200 bg-indigo-50/50";
  const footerClass =
    "px-4 py-3 sm:px-6 border-t border-indigo-200 bg-indigo-50/50";

  return (
    <div className={cardClass} {...props}>
      {header && <div className={headerClass}>{header}</div>}

      <div className={contentClass}>
        {isLoading ? (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
          </div>
        ) : (
          children
        )}
      </div>

      {footer && <div className={footerClass}>{footer}</div>}
    </div>
  );
};

// Add default export to fix import issue
export default Card;
