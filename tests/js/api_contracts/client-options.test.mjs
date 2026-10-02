import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import test from 'node:test';
import { root } from './helpers.mjs';

test('cliente HTTP configura timeout e bloqueia redirecionamentos', () => {
  const source = readFileSync(resolve(root, 'sorrisomais/api.py'), 'utf8');
  assert.match(source, /allow_redirects=False/);
  assert.match(source, /timeout=self\.configuracao\.timeout/);
});
