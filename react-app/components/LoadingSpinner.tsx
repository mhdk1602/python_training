import React from "react";

interface Props {
  label?: string;
}

const LoadingSpinner: React.FC<Props> = ({ label = "Loading..." }) => (
  <div className="flex flex-col items-center justify-center gap-3 py-12 text-terminal-muted">
    <svg
      className="h-8 w-8 animate-spin"
      viewBox="0 0 24 24"
      fill="none"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="3"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
      />
    </svg>
    <span className="text-sm">{label}</span>
  </div>
);

export default LoadingSpinner;
