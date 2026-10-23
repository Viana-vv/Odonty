import test from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { root } from './helpers.mjs';

test('PATCH /profissionais/{id}/situacao é exclusivo do Administrador', () => {
  const client = readFileSync(resolve(root, 'sorrisomais/api.py'), 'utf8');
  assert.match(client, /"PATCH", f"\/profissionais\/\{profissional_id\}\/situacao"/);
  assert.match(client, /def atualizar_situacao_profissional\(/);
  const path = resolve(root, 'backend/xano/api/sorriso_acesso/profissionais_id_situacao_PATCH.xs');
  assert.ok(existsSync(path));
  const source = readFileSync(path, 'utf8');
  assert.match(source, /intersect:\["administrador"\]/);
  assert.match(source, /situacao: \$situacao_armazenada/);
  assert.doesNotMatch(source, /db\.delete|db\.remove/);
});
