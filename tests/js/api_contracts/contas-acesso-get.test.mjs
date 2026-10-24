import test from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { root } from './helpers.mjs';

test('GET /contas-acesso usa rota dedicada e exporta somente campos autorizados', () => {
  const adapter = readFileSync(resolve(root, 'sorrisomais/api_contas_acesso.py'), 'utf8');
  assert.match(adapter, /_request\("GET", "\/contas-acesso"/);
  assert.match(adapter, /_CAMPOS_CONTA = \("id", "nome", "email", "perfis", "situacao"\)/);

  const exportPath = resolve(root, 'backend/xano/api/sorriso_acesso/contas_acesso_GET.xs');
  assert.ok(existsSync(exportPath), 'export GET de Contas de Acesso ausente');
  const source = readFileSync(exportPath, 'utf8');
  assert.match(source, /auth = "conta_acesso"/);
  assert.match(source, /sorriso_validar_sessao/);
  assert.match(source, /intersect:\["administrador", "recepcionista"\]/);
  assert.match(source, /output = \["id", "nome", "email", "perfis", "situacao"\]/);
  assert.match(source, /history = false/);
  assert.doesNotMatch(source, /"senha"|"token"|"hash"|"cpf"/);
});
