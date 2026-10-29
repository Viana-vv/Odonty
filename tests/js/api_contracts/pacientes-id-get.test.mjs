import test from 'node:test';
import { assertClientContract, root } from './helpers.mjs';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

test('GET /pacientes/{id} tem contrato Xano autenticado e sem histórico', () => {
  assertClientContract('GET', '/pacientes/{paciente_id}', 'obter_paciente');
  const source = readFileSync(resolve(root, 'backend/xano/api/sorriso_acesso/pacientes_id_GET.xs'), 'utf8');
  assert.match(source, /auth = "conta_acesso"/);
  assert.match(source, /Cache-Control: no-store/);
  assert.match(source, /intersect:\["administrador", "recepcionista"\]/);
  assert.match(source, /output = \["id", "nome", "data_nascimento", "cpf", "telefone", "celular", "email"\]/);
  assert.match(source, /var \$cpf \{ value = "" \}/);
  assert.match(source, /var \$celular \{ value = "" \}/);
  assert.match(source, /var \$email \{ value = "" \}/);
  assert.doesNotMatch(source, /\|default:/);
  assert.match(source, /history = false/);
  assert.doesNotMatch(source.replace(/^\s*\/\/.*$/gm, ''), /observacoes|prontuario|registro_clinico/i);
});
