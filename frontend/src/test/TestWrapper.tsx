import { type ReactNode } from "react";
import { FilterProvider } from "../filters/FilterContext";

export function TestWrapper({ children }: { children: ReactNode }) {
  return <FilterProvider>{children}</FilterProvider>;
}