import { useLocation, useNavigate } from "react-router-dom";
import "./Breadcrumbs.css";

interface BreadcrumbItem {
  label: string;
  path?: string;
}

export function Breadcrumbs({ items }: { items: BreadcrumbItem[] }) {
  const navigate = useNavigate();
  return (
    <nav className="breadcrumbs" aria-label="Breadcrumb">
      <ol>
        {items.map((item, idx) => (
          <li key={idx}>
            {idx < items.length - 1 && item.path ? (
              <a href="#" onClick={(e) => { e.preventDefault(); navigate(item.path!); }}>{item.label}</a>
            ) : (
              <span>{item.label}</span>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
}
