import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { root } from './helpers.mjs';

test('cliente declara POST /registros-clinicos/{id}/retificacoes', () => {
  const source = readFileSync(resolve(root, 'sorrisomais/api.py'), 'utf8');
  assert.match(source, /def retificar_registro_clinico\(/);
  assert.match(source, /"POST", f"\/registros-clinicos\/\{registro_id\}\/retificacoes"/);
});
