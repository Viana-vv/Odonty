import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { assertClientContract, root } from './helpers.mjs';

test('cliente declara POST /disponibilidades', () => {
  assertClientContract('POST', '/disponibilidades', 'criar_disponibilidade');
  const source = readFileSync(resolve(root, 'backend/xano/api/sorriso_acesso/disponibilidades_POST.xs'), 'utf8');
  assert.match(source, /auth = "conta_acesso"/);
  assert.match(source, /sorriso_validar_sessao/);
  assert.match(source, /profissional.*administrador.*recepcionista/);
  assert.match(source, /HTTP\/1\.1 409 Conflict/);
  assert.doesNotMatch(source, /\|default:/);
  assert.match(source, /db\.query agenda_controle/);
  assert.doesNotMatch(source, /agenda_lock_version/);
  assert.match(source, /timestamp inicio\?/);
  assert.match(source, /timestamp fim\?/);
  assert.match(source, /\$input\.inicio <= now/);
  assert.match(source, /inicio:.*format_timestamp:"c":"UTC"/);
  assert.match(source, /fim:.*format_timestamp:"c":"UTC"/);
});
