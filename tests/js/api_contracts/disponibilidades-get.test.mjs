import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { assertClientContract, root } from './helpers.mjs';

test('cliente declara GET /disponibilidades', () => {
  assertClientContract('GET', '/disponibilidades', 'listar_disponibilidades');
  const source = readFileSync(resolve(root, 'backend/xano/api/sorriso_acesso/disponibilidades_GET.xs'), 'utf8');
  assert.match(source, /inicio:.*format_timestamp:"c":"UTC"/);
  assert.match(source, /fim:.*format_timestamp:"c":"UTC"/);
});
