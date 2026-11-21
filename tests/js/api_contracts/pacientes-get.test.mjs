import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { assertApiContract, assertClientContract, root } from './helpers.mjs';

test('GET /pacientes exige sessão e perfil administrativo no Xano', () => {
  const source = assertApiContract('GET', '/pacientes', 'api/sorriso_acesso/pacientes_GET.xs');
  assertClientContract('GET', '/pacientes', 'listar_pacientes');
  assert.match(source, /auth = "conta_acesso"/);
  assert.match(source, /function.run sorriso_validar_sessao/);
  assert.match(source, /\$solicitante.situacao != "ativo"/);
  assert.match(source, /perfis\|intersect:\["administrador", "recepcionista"\]/);
  assert.match(source, /403 Forbidden/);
  assert.match(source, /Cache-Control: no-store/);
  assert.match(source, /history = false/);
});

test('GET /pacientes retorna somente Pacientes ativos sem dependências da Agenda', () => {
  const source = assertApiContract('GET', '/pacientes', 'api/sorriso_acesso/pacientes_GET.xs');
  assert.match(source, /\$db.paciente.situacao == "ativo"/);
  assert.match(source, /return = \{type: "list"\}/);
  assert.match(source, /output = \["id", "nome"\]/);
  assert.match(source, /response = \{pacientes: \$pacientes\}/);
  assert.doesNotMatch(source, /db.query (profissional|procedimento)|cpf|telefone|email/);
  const tela = readFileSync(resolve(root, 'sorrisomais/pagina_pacientes_xano.py'), 'utf8');
  assert.match(tela, /cliente.listar_pacientes\(credencial.token\)/);
  assert.doesNotMatch(tela, /listar_opcoes_agenda/);
});
