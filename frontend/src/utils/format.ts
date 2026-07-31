export function numberValue(value: number | undefined, digits = 1) {
  return typeof value === "number" && Number.isFinite(value) ? value.toFixed(digits) : "0.0";
}

export function integerValue(value: number | undefined) {
  return typeof value === "number" && Number.isFinite(value) ? Math.round(value).toLocaleString() : "0";
}

export function percentageValue(value: number | undefined, digits = 1) {
  return `${numberValue(value, digits)}%`;
}
