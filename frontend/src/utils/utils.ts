import type { DataMap } from "../types/domain";

export function mapToArray<T>(
  data: DataMap<T>,
  keyName: string
): (T & Record<string, string>)[] {
  return Object.entries(data).map(([key, value]) => ({
    ...value,
    [keyName]: key,
  }));
}

export function formatNumber(num: number): string {
  const [intPart, decimalPart] = num.toString().split(".");
  const formattedInt = formatNumberRecursive(parseInt(intPart));
  return decimalPart
    ? `${formattedInt}.${decimalPart.substring(0, 2)}`
    : formattedInt;
}

function formatNumberRecursive(num: number): string {
  if (num < 1000) {
    return `${num}`;
  }
  const remainder = num % 1000;
  const prefix = formatNumberRecursive(Math.floor(num / 1000));
  return `${prefix},${remainder.toString().padStart(3, "0")}`;
}
