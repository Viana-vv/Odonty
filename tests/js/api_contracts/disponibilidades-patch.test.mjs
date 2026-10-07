import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { assertClientContract, root } from './helpers.mjs';

test('cliente declara PATCH /disponibilidades/{id}', () => {
  assertClientContract('PATCH', '/disponibilidades/{disponibilidade_id}', 'atualizar_disponibilidade');
  const source = readFileSync(resolve(root, 'backend/xano/api/sorriso_acesso/disponibilidades_id_PATCH.xs'), 'utf8');
  assert.match(source, /inicio:.*format_timestamp:"c":"UTC"/);
  assert.match(source, /fim:.*format_timestamp:"c":"UTC"/);
});
