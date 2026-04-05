export function cn(...c: (string | undefined | false | null)[]) { return c.filter(Boolean).join(' ') }
export function fmt(n: number) {
  if (n >= 1e6) return (n / 1e6).toFixed(1) + 'M'
  if (n >= 1e3) return (n / 1e3).toFixed(1) + 'K'
  return n.toString()
}
