/* global fetch */
import { mkdir, writeFile } from 'node:fs/promises';
import { join } from 'node:path';

const baseUrl = process.env.RN_DATA_SERVICE_BASE_URL ?? process.env.VITE_DATA_SERVICE_BASE_URL ?? 'http://127.0.0.1:8003';
const fixtureDir = join(process.cwd(), 'fixtures', 'real', 'v1_5', 'ai-provider');
const results = [];
const fixtures = {};
let finalDecision = 'BLOCKED';

function mark(name, status, detail = '') {
  results.push({ name, status, detail });
  const label = status === 'pass' ? 'PASS' : status === 'blocked' ? 'BLOCKED' : 'FAIL';
  console.log(`${label} ${name}${detail ? ` - ${detail}` : ''}`);
}

function sanitize(value) {
  if (Array.isArray(value)) return value.map(sanitize);
  if (value && typeof value === 'object') {
    const output = {};
    for (const [key, item] of Object.entries(value)) {
      const lowered = key.toLowerCase();
      if (
        lowered.includes('api_key') ||
        lowered.includes('authorization') ||
        lowered.includes('secret') ||
        lowered.endsWith('_path') ||
        lowered.includes('cache') ||
        lowered.includes('physical') ||
        lowered.includes('stack')
      ) {
        if (lowered === 'api_key_configured') output[key] = Boolean(item);
        continue;
      }
      output[key] = sanitize(item);
    }
    return output;
  }
  if (typeof value === 'string') {
    return value
      .replaceAll(process.env.DATA_SERVICE_AI_API_KEY ?? '__NO_KEY__', '[redacted-api-key]')
      .replaceAll('/Users', '[home]')
      .replaceAll('/private/tmp', '[tmp]')
      .replaceAll('/tmp', '[tmp]')
      .replaceAll('file://', 'file-redacted://');
  }
  return value;
}

function hasSensitiveValue(value) {
  const text = JSON.stringify(value);
  const apiKey = process.env.DATA_SERVICE_AI_API_KEY ?? '';
  return (
    /\/Users|file:\/\/|cache_path|artifact_path|physical_path|\/private\/tmp|\/tmp\//.test(text) ||
    (apiKey.length > 0 && text.includes(apiKey)) ||
    /authorization/i.test(text)
  );
}

async function request(path) {
  const response = await fetch(`${baseUrl}${path}`, { method: 'GET', headers: { 'Content-Type': 'application/json' } });
  const text = await response.text();
  return {
    ok: response.ok,
    status: response.status,
    payload: text ? JSON.parse(text) : null
  };
}

async function saveFixtures() {
  await mkdir(fixtureDir, { recursive: true });
  await Promise.all(
    Object.entries(fixtures).map(([name, payload]) =>
      writeFile(join(fixtureDir, name), JSON.stringify(sanitize(payload), null, 2) + '\n')
    )
  );
}

async function main() {
  try {
    const result = await request('/api/workspaces/-/ai-provider/health');
    fixtures['provider-health.json'] = result.payload;
    mark('provider health route reachable', result.ok ? 'pass' : 'fail', `HTTP ${result.status}`);
    if (!result.ok) {
      finalDecision = 'FAIL';
    } else {
      const health = result.payload?.data?.provider_health;
      if (!health || typeof health !== 'object') {
        mark('provider health schema', 'fail', 'missing data.provider_health');
        finalDecision = 'FAIL';
      } else if (health.provider_available !== true) {
        mark('real provider call', 'blocked', health.error_code ?? 'provider unavailable');
        finalDecision = 'BLOCKED';
      } else {
        mark('real provider call', 'pass', `${health.provider?.provider_name ?? 'provider'} / ${health.provider?.model ?? 'model'}`);
        mark('response schema', health.response_schema === 'openai_chat_completions' ? 'pass' : 'fail', health.response_schema ?? '');
        mark('sanitized payload', hasSensitiveValue(result.payload) ? 'fail' : 'pass');
        finalDecision = results.every((item) => item.status === 'pass') ? 'PASS' : 'FAIL';
      }
    }
  } catch (error) {
    mark('provider smoke exception', 'fail', error instanceof Error ? error.message : String(error));
    finalDecision = 'FAIL';
  } finally {
    fixtures['v1_5_a_ai_provider_smoke_result.json'] = {
      generated_at: new Date().toISOString(),
      base_url: baseUrl,
      results,
      final_decision: finalDecision,
      declaration:
        finalDecision === 'PASS'
          ? 'V1.5-A provider contract PASS; V1.5-B may be audited next.'
          : 'V1.5-A remains blocked; AI quality stages cannot start.'
    };
    await saveFixtures();
  }

  if (finalDecision !== 'PASS') {
    process.exitCode = 1;
  }
}

await main();
