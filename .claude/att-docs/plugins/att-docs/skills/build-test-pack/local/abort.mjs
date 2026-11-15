// A wait that ends early when a stop signal aborts.

/**
 * Runs `sleep(ms)` and returns when it settles or when `signal` aborts,
 * whichever is first. The abort listener is removed afterward, so a loop that
 * waits many times leaves none behind.
 */
export async function sleepUnlessAborted(sleep, ms, signal) {
  if (!signal) return sleep(ms);
  if (signal.aborted) return undefined;
  let onAbort;
  const aborted = new Promise((resolve) => {
    onAbort = resolve;
    signal.addEventListener('abort', onAbort, { once: true });
  });
  try {
    return await Promise.race([sleep(ms), aborted]);
  } finally {
    signal.removeEventListener('abort', onAbort);
  }
}
