import { test } from 'node:test';
import assert from 'node:assert/strict';
import { fetchJson } from '../src/api/http.ts';

test('GET requests do not add a JSON content type unnecessarily', async (context) => {
  context.mock.method(
    globalThis,
    'fetch',
    async (_url: string, options: RequestInit) => {
      assert.equal(new Headers(options.headers).has('Content-Type'), false);
      return Response.json({ items: [] });
    },
  );
  assert.deepEqual(await fetchJson('https://api.example.test/services'), {
    items: [],
  });
});

test('JSON bodies get content type and failed responses remain errors', async (context) => {
  context.mock.method(
    globalThis,
    'fetch',
    async (_url: string, options: RequestInit) => {
      assert.equal(
        new Headers(options.headers).get('Content-Type'),
        'application/json',
      );
      return new Response(null, { status: 503 });
    },
  );
  await assert.rejects(
    fetchJson('https://api.example.test/assistant/query', {
      method: 'POST',
      body: '{}',
    }),
    /503/,
  );
});

test(
  'caller cancellation stops an in-flight fetch',
  { timeout: 1000 },
  async (context) => {
    const controller = new AbortController();
    let fetchSignal: AbortSignal | null | undefined;
    let markStarted: () => void = () => {};
    const started = new Promise<void>((resolve) => {
      markStarted = resolve;
    });
    context.mock.method(
      globalThis,
      'fetch',
      (_url: string, options: RequestInit) => {
        fetchSignal = options.signal;
        return new Promise<Response>((_resolve, reject) => {
          fetchSignal!.addEventListener(
            'abort',
            () => reject(fetchSignal!.reason),
            { once: true },
          );
          markStarted();
        });
      },
    );
    const pending = fetchJson('https://api.example.test/services', {
      signal: controller.signal,
    });
    await started;
    assert.ok(fetchSignal);
    assert.equal(fetchSignal.aborted, false);
    controller.abort();
    await assert.rejects(pending, { name: 'AbortError' });
    assert.equal(fetchSignal.aborted, true);
    assert.equal(fetchSignal.reason.name, 'AbortError');
  },
);
