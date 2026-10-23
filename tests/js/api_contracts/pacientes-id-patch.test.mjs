import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { assertClientContract, root } from './helpers.mjs';

test('PATCH /pacientes/{id} valida campos, permissão e mantém escopo cadastral', () => {
  assertClientContract('PATCH', '/pacientes/{paciente_id}', 'atualizar_paciente');
  const source = readFileSync(resolve(root, 'backend/xano/api/sorriso_acesso/pacientes_id_PATCH.xs'), 'utf8');
  assert.match(source, /auth = "conta_acesso"/);
  assert.match(source, /Cache-Control: no-store/);
  assert.match(source, /intersect:\["administrador", "recepcionista"\]/);
  assert.ok(source.includes('where = $db.paciente.id != $input.id && $db.paciente.cpf == $cpf'));
  assert.match(source, /data = \{nome: \$nome, data_nascimento: \$data_nascimento, telefone: \$telefone, cpf: \$cpf, email: \$email, celular: \$celular, atualizado_em: now\}/);
  assert.match(source, /history = false/);
  assert.doesNotMatch(source.replace(/^\s*\/\/.*$/gm, ''), /observacoes|prontuario|registro_clinico/i);
});
