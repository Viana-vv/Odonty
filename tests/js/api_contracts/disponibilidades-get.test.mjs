import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { assertClientContract, root } from './helpers.mjs';

test('cliente declara GET /disponibilidades', () => {
  assertClientContract('GET', '/disponibilidades', 'listar_disponibilidades');
  const source = readFileSync(resolve(root, 'backend/xano/api/sorriso_acesso/disponibilidades_GET.xs'), 'utf8');
  assert.doesNotMatch(source, /eval\s*=\s*\{[^}]*format_timestamp/s);
  assert.match(source, /var \$inicio_iso \{ value = \$disponibilidade\.inicio\|format_timestamp:"c":"UTC" \}/);
  assert.match(source, /var \$fim_iso \{ value = \$disponibilidade\.fim\|format_timestamp:"c":"UTC" \}/);
});
