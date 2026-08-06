import { useRef, useEffect } from "react";

export function SkipLink({ targetId = "main-content" }: { targetId?: string }) {
  const linkRef = useRef<HTMLAnchorElement>(null);

  useEffect(() => {
    const handleFocus = () => {
      if (linkRef.current) {
        linkRef.current.style.left = "10px";
        linkRef.current.style.top = "10px";
        linkRef.current.style.width = "auto";
        linkRef.current.style.height = "auto";
      }
    };
    const handleBlur = () => {
      if (linkRef.current) {
        linkRef.current.style.left = "-9999px";
        linkRef.current.style.top = "auto";
        linkRef.current.style.width = "1px";
        linkRef.current.style.height = "1px";
      }
    };
    const link = linkRef.current;
    if (link) {
      link.addEventListener("focus", handleFocus);
      link.addEventListener("blur", handleBlur);
      return () => {
        link.removeEventListener("focus", handleFocus);
        link.removeEventListener("blur", handleBlur);
      };
    }
  }, []);

  return (
    <a
      ref={linkRef}
      href={`#${targetId}`}
      style={{
        position: "absolute",
        left: "-9999px",
        top: "auto",
        width: 1,
        height: 1,
        overflow: "hidden",
        padding: "8px 16px",
        background: "#2563eb",
        color: "#fff",
        borderRadius: 4,
        textDecoration: "none",
        zIndex: 10000,
      }}
    >
      Skip to main content
    </a>
  );
}

export function KeyboardShortcut({ shortcut, description }: { shortcut: string; description: string }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#64748b" }}>
      <kbd
        style={{
          padding: "4px 8px",
          background: "#f1f5f9",
          borderRadius: 4,
          border: "1px solid #cbd5e1",
          fontFamily: "monospace",
          fontSize: 12,
        }}
      >
        {shortcut}
      </kbd>
      <span>{description}</span>
    </div>
  );
}
