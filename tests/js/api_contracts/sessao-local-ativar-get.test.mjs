import assert from 'node:assert/strict';
import test from 'node:test';
import { readFileSync } from 'node:fs';

const source = readFileSync(new URL('../../../sorrisomais/sessao_local.py', import.meta.url), 'utf8');

test('ativação local limita host, exposição de credencial e cache', () => {
  assert.match(source, /ThreadingHTTPServer\(\("127\.0\.0\.1", porta\)/);
  assert.match(source, /url\.path != "\/ativar"/);
  assert.match(source, /cookie\[COOKIE\]\["httponly"\] = True/);
  assert.match(source, /cookie\[COOKIE\]\["samesite"\] = "Strict"/);
  assert.match(source, /"Cache-Control", "no-store"/);
  assert.match(source, /"Referrer-Policy", "no-referrer"/);
  assert.doesNotMatch(source, /ticket=\{.*\.token\}/);
});
