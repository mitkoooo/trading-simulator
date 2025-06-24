type DataMap<T> = Record<string, T>;

export function mapToArray<T>(
  data: DataMap<T>,
  keyName: string
): (T & Record<string, string>)[] {
  return Object.entries(data).map(([key, value]) => ({
    ...value,
    [keyName]: key,
  }));
}
