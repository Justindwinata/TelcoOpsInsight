import { describe, expect, it } from "vitest";
import { integerValue, numberValue, percentageValue } from "./format";

describe("format utilities", () => {
  it("formats missing numeric values without exposing undefined", () => {
    expect(numberValue(undefined)).toBe("0.0");
    expect(integerValue(undefined)).toBe("0");
    expect(percentageValue(undefined)).toBe("0.0%");
  });
});
