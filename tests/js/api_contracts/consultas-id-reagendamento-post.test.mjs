import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { root } from './helpers.mjs';

const backend = readFileSync(resolve(root, 'backend/xano/api/sorriso_acesso/consultas_id_reagendamento_POST.xs'), 'utf8');
const cliente = readFileSync(resolve(root, 'sorrisomais/reagendamento_consulta.py'), 'utf8');
const tabela = readFileSync(resolve(root, 'backend/xano/table/consulta_reagendamento.xs'), 'utf8');

test('POST /consultas/{id}/reagendamento exige sessão e perfil administrativo no backend', () => {
  assert.match(backend, /query "consultas\/\{id\}\/reagendamento" verb=POST/);
  assert.match(backend, /auth = "conta_acesso"/);
  assert.match(backend, /function\.run sorriso_validar_sessao/);
  assert.match(backend, /intersect:\["administrador", "recepcionista"\]/);
  assert.match(backend, /\$solicitante\.situacao != "ativo"/);
  assert.match(backend, /history = false/);
  assert.match(backend, /Cache-Control: no-store/);
});

test('contrato aceita apenas destino e justificativa, derivando Paciente e Profissional', () => {
  assert.match(cliente, /"POST", f"\/consultas\/\{consulta_id\}\/reagendamento"/);
  assert.match(cliente, /status_esperado=201/);
  assert.match(backend, /\(\$bruto\|keys\|count\) != 2/);
  assert.match(backend, /\$bruto\|get:"disponibilidade_id"\|is_int/);
  assert.match(backend, /\$bruto\|get:"justificativa"\|is_text/);
  assert.match(backend, /\(\$justificativa\|strlen\) > 1000/);
  assert.match(backend, /paciente_id: \$consulta\.paciente_id, profissional_id: \$destino\.profissional_id/);
  assert.doesNotMatch(backend, /\$bruto\.(paciente_id|profissional_id)/);
});

test('vínculo explícito e mutações pertencem à mesma transação', () => {
  const transacao = backend.split('db.transaction')[1].split('catch {')[0];
  for (const operacao of ['db.add consulta {', 'db.edit consulta {', 'db.add consulta_reagendamento {',
    'db.add consulta_disponibilidade {', 'db.add consulta_situacao_historico {', 'db.edit disponibilidade_agenda {']) {
    assert.ok(transacao.includes(operacao), operacao);
  }
  assert.match(transacao, /consulta_original_id: \$consulta\.id, consulta_nova_id: \$nova_consulta\.id/);
  assert.match(transacao, /\$db\.consulta\.id != \$consulta\.id/);
  assert.match(transacao, /\$original_atual\.situacao != \$consulta\.situacao/);
  assert.match(transacao, /\$destino_atual\.inicio <= now/);
  assert.match(transacao, /\$destino_atual\.fim <= \$destino_atual\.inicio/);
  assert.match(transacao, /\$destino_atual\.situacao != "disponivel"/);
  assert.match(transacao, /\$paciente_atual\.situacao != "ativo"/);
  assert.match(transacao, /\$profissional_atual\.situacao != "Ativo"/);
  assert.match(transacao, /agenda_controle/);
  assert.equal((tabela.match(/type: "btree\|unique"/g) || []).length, 2);
  assert.doesNotMatch(backend, /db\.delete|db\.add consulta_procedimento|db\.edit registro_clinico/);
});
