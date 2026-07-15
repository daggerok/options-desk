import { describe, expect, test } from 'bun:test';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';

const main = readFileSync(join(import.meta.dir, 'main.tsx'), 'utf8');
const ci = readFileSync(join(import.meta.dir, '../.github/workflows/ci.yaml'), 'utf8');
const pkg = JSON.parse(readFileSync(join(import.meta.dir, '../package.json'), 'utf8'));

describe('header parity + CACHE-muted proxies (options-desk)', () => {
  test('TopBar includes fundamentals-like control order markers', () => {
    expect(main).toContain('data-proxy-indicators=');
    expect(main).toContain('data-provider-select=');
    expect(main).toContain("providerId: 'static'");
    expect(main).toContain('topBar.proxyDisabled');
    expect(main).toContain('💾');
    expect(main).toContain('🌐');
    expect(main).toContain('topBar.debug');
  });

  test('CACHE mode disables provider select and mutes proxy dots', () => {
    expect(main).toContain("isCache ? 'disabled' : 'live'");
    expect(main).toContain('bg-slate-400/50 dark:bg-slate-600/50');
    expect(main).toContain('cursor-not-allowed');
    expect(main).toContain("disabled={isCache}");
    expect(main).toContain("disabled={settings.providerId === 'static'}");
  });

  test('LIVE mode probes proxyBase /health', () => {
    expect(main).toContain('fetch(`${base}/health`');
    expect(main).toContain('proxyOk');
    expect(main).toContain('proxyChecking');
  });

  test('CI runs unit tests and fails the job on test failure', () => {
    expect(pkg.scripts.test).toBe('bun test');
    expect(ci).toContain('bun run test');
    expect(ci).toContain('pull_request');
    // test step must run before build so failures block pipeline
    const testIdx = ci.indexOf('bun run test');
    const buildIdx = ci.indexOf('bun run build');
    expect(testIdx).toBeGreaterThan(0);
    expect(buildIdx).toBeGreaterThan(testIdx);
  });
});
