// Free-memory check for the phase boundaries of a build. A build that runs on
// into heavy swapping slows to a crawl, so before each phase the run reads
// /proc/meminfo, waits while memory is low, and stops at the last checkpoint if
// it stays low, so `resume` carries on later. Only numbers and codes leave this
// module, which is what status.log allows.

import fs from 'node:fs';
import { sleepUnlessAborted } from './abort.mjs';

const MIB_PER_KIB = 1 / 1024;

/** MemAvailable and swap use, in MiB and percent, from the text of /proc/meminfo; null if MemAvailable is absent. */
export function parseMeminfo(text) {
  const kib = {};
  for (const line of String(text).split('\n')) {
    const match = /^(\w+):\s+(\d+)\s*kB/.exec(line);
    if (match) kib[match[1]] = Number(match[2]);
  }
  if (!Number.isFinite(kib.MemAvailable)) return null;
  const swapTotal = kib.SwapTotal ?? 0;
  const swapUsed = Math.max(0, swapTotal - (kib.SwapFree ?? swapTotal));
  return {
    availableMiB: Math.round(kib.MemAvailable * MIB_PER_KIB),
    swapTotalMiB: Math.round(swapTotal * MIB_PER_KIB),
    swapUsedMiB: Math.round(swapUsed * MIB_PER_KIB),
    swapPercent: swapTotal > 0 ? Math.round((swapUsed / swapTotal) * 100) : 0,
  };
}

/** The current reading, or null when the file cannot be read or parsed. */
export function readMeminfo(file = '/proc/meminfo') {
  try {
    return parseMeminfo(fs.readFileSync(file, 'utf8'));
  } catch {
    return null;
  }
}

/**
 * True when free memory is under the floor, or swap use is over the ceiling while
 * free memory is under twice the floor. Swapped pages stay in swap after the
 * pressure ends, so a full swap with plenty of memory free is not a reason to wait.
 */
export const memoryLow = (reading, { minAvailableMiB, maxSwapPercent }) =>
  reading.availableMiB < minAvailableMiB
  || (reading.swapPercent > maxSwapPercent && reading.availableMiB < 2 * minAvailableMiB);

/** A stop for low memory; `counts` are the numbers its status line carries. */
export class MemoryLow extends Error {
  constructor(counts) {
    super('memory stayed low');
    this.code = 'low';
    this.counts = counts;
  }
}

/**
 * Checks memory and, while it is low, polls every `pollSeconds` for up to
 * `waitMinutes`. Returns { ok, unreadable, polls, waitedMs, availableMiB, swapPercent };
 * `ok` is false when memory is still low at the end of the wait. `onWait` is
 * called once with the first low reading. An unreadable /proc/meminfo is ok
 * with `unreadable` set, since there is nothing to judge by. A `signal` that
 * aborts ends the wait at once, with `ok` false, so the caller can stop.
 */
export async function waitForMemory(settings, { read = readMeminfo, onWait = () => {},
  sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms)), now = Date.now,
  signal = null } = {}) {
  let reading = read();
  if (!reading) return { ok: true, unreadable: true, polls: 0, waitedMs: 0 };
  const result = (ok, polls, waitedMs) => ({ ok, polls, waitedMs,
    availableMiB: reading.availableMiB, swapPercent: reading.swapPercent });
  if (!memoryLow(reading, settings)) return result(true, 0, 0);
  onWait(reading);
  const started = now();
  const limit = settings.waitMinutes * 60000;
  let polls = 0;
  while (now() - started < limit && !signal?.aborted) {
    await sleepUnlessAborted(sleep, Math.min(settings.pollSeconds * 1000, limit - (now() - started)), signal);
    if (signal?.aborted) break;
    polls += 1;
    reading = read() ?? reading;
    if (!memoryLow(reading, settings)) return result(true, polls, now() - started);
  }
  return result(false, polls, now() - started);
}
