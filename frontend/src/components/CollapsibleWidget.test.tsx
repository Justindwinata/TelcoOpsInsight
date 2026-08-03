import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { CollapsibleWidget } from "./CollapsibleWidget";

describe("CollapsibleWidget", () => {
  it("renders expanded by default", () => {
    render(
      <CollapsibleWidget title="Test Widget">
        <p>Content here</p>
      </CollapsibleWidget>
    );
    expect(screen.getByText("Test Widget")).toBeDefined();
    expect(screen.getByText("Content here")).toBeDefined();
  });

  it("hides content when collapsed", () => {
    render(
      <CollapsibleWidget title="Test Widget" defaultExpanded={false}>
        <p>Hidden content</p>
      </CollapsibleWidget>
    );
    expect(screen.queryByText("Hidden content")).toBeNull();
  });

  it("toggles on click", () => {
    render(
      <CollapsibleWidget title="Test Widget" defaultExpanded={false}>
        <p>Toggle content</p>
      </CollapsibleWidget>
    );
    const button = screen.getByRole("button");
    fireEvent.click(button);
    expect(screen.getByText("Toggle content")).toBeDefined();
    fireEvent.click(button);
    expect(screen.queryByText("Toggle content")).toBeNull();
  });

  it("calls onToggle callback", () => {
    const onToggle = vi.fn();
    render(
      <CollapsibleWidget title="Test Widget" defaultExpanded={true} onToggle={onToggle}>
        <p>Content</p>
      </CollapsibleWidget>
    );
    fireEvent.click(screen.getByRole("button"));
    expect(onToggle).toHaveBeenCalledWith(false);
  });
});
