import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { root } from './helpers.mjs';

test('cliente declara PATCH /consultas/{id}/situacao', () => {
  const source = readFileSync(resolve(root, 'sorrisomais/api.py'), 'utf8');
  assert.match(source, /def atualizar_situacao_consulta\(/);
  assert.match(source, /"PATCH", f"\/consultas\/\{consulta_id\}\/situacao"/);
});
