export async function fetchJson(
  url: string,
  options: RequestInit = {},
): Promise<unknown> {
  const headers = new Headers(options.headers);
  if (options.body != null && !headers.has('Content-Type'))
    headers.set('Content-Type', 'application/json');
  const timeout = AbortSignal.timeout(12000);
  const signal = options.signal
    ? AbortSignal.any([options.signal, timeout])
    : timeout;
  const response = await fetch(url, { ...options, headers, signal });
  if (!response.ok) throw new Error(`API request failed: ${response.status}`);
  return response.json();
}
