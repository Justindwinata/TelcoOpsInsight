import { useState, type ReactNode } from "react";

interface CollapsibleWidgetProps {
  title: string;
  defaultExpanded?: boolean;
  badge?: string | number;
  children: ReactNode;
  onToggle?: (expanded: boolean) => void;
}

export function CollapsibleWidget({
  title,
  defaultExpanded = true,
  badge,
  children,
  onToggle,
}: CollapsibleWidgetProps) {
  const [expanded, setExpanded] = useState(defaultExpanded);

  const toggle = () => {
    const next = !expanded;
    setExpanded(next);
    onToggle?.(next);
  };

  return (
    <article className={`panel collapsible-widget ${expanded ? "expanded" : "collapsed"}`}>
      <div className="panel-heading widget-heading">
        <button
          type="button"
          className="widget-toggle"
          onClick={toggle}
          aria-expanded={expanded}
          aria-label={expanded ? `Collapse ${title}` : `Expand ${title}`}
        >
          <span className={`toggle-icon ${expanded ? "down" : "right"}`} aria-hidden="true">
            ▶
          </span>
          <h3>{title}</h3>
          {badge !== undefined && <span className="badge">{badge}</span>}
        </button>
      </div>
      {expanded && <div className="widget-body">{children}</div>}
    </article>
  );
}
