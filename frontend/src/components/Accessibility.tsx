export function AriaLabel({ label, children }: { label: string; children: React.ReactNode }) {
  return <div aria-label={label}>{children}</div>;
}

export function FocusIndicator({ children }: { children: React.ReactNode }) {
  return <div tabIndex={0} style={{ outline: "none" }}>{children}</div>;
}

export function SkipToContent() {
  return (
    <a href="#main-content" style={{
      position: "absolute", left: -9999, top: "auto",
      width: 1, height: 1, overflow: "hidden",
    }} onFocus={() => { this.style.left = "10px"; this.style.top = "10px"; this.style.width = "auto"; this.style.height = "auto"; }}>
      Skip to main content
    </a>
  );
}

export function KeyboardShortcut({ shortcut, description }: { shortcut: string; description: string }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12 }}>
      <kbd style={{ padding: "2px 6px", background: "#f1f5f9", borderRadius: 4, border: "1px solid #cbd5e1" }}>{shortcut}</kbd>
      <span>{description}</span>
    </div>
  );
}
