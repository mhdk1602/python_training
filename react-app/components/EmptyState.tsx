import React from "react";

interface Props {
  title: string;
  message?: string;
}

const EmptyState: React.FC<Props> = ({ title, message }) => (
  <div className="flex flex-col items-center justify-center gap-2 rounded-xl border border-dashed border-terminal-border py-12 text-center">
    <p className="text-sm font-medium text-terminal-text">{title}</p>
    {message && <p className="text-xs text-terminal-muted">{message}</p>}
  </div>
);

export default EmptyState;
