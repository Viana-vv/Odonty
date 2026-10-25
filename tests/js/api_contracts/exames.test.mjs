import assert from 'node:assert/strict';
import test from 'node:test';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const root = resolve(import.meta.dirname, '../../..');
const read = name => readFileSync(resolve(root, 'backend/xano/api/sorriso_acesso', name), 'utf8');

test('rotas de exames exigem autenticação e sessão Xano', () => {
  for (const file of ['exames_GET.xs', 'exames_POST.xs', 'exames_id_situacao_PATCH.xs']) {
    const source = read(file);
    assert.match(source, /auth = "conta_acesso"/);
    assert.match(source, /function\.run sorriso_validar_sessao/);
    assert.doesNotMatch(source, /url_publica|arquivo/);
  }
});

test('POST exige vínculo entre paciente, consulta e profissional', () => {
  const source = read('exames_POST.xs');
  assert.match(source, /\$consulta\.paciente_id != \$paciente\.id/);
  assert.match(source, /\$consulta\.profissional_id != \$profissional\.id/);
  assert.match(source, /\$input\.solicitado_em > now/);
  assert.match(source, /db\.add exame_situacao_historico/);
});

test('PATCH valida profissional, vínculo, sequência, cronologia e resultado', () => {
  const source = read('exames_id_situacao_PATCH.xs');
  assert.match(source, /intersect:\["profissional"\]/);
  assert.match(source, /\$conta\.situacao != "ativo"/);
  assert.match(source, /\$exame\.profissional_id != \$profissional\.id/);
  assert.match(source, /\$exame\.situacao == "Solicitado"/);
  assert.match(source, /\$exame\.situacao == "Realizado" && \$input\.situacao == "Resultado disponível"/);
  assert.match(source, /\$realizado_em_final < \$exame\.solicitado_em/);
  assert.match(source, /\$resultado_final == null/);
  assert.match(source, /HTTP\/1\.1 409 Conflict/);
});

test('PATCH grava situação e histórico juntos, preservando campos omitidos', () => {
  const source = read('exames_id_situacao_PATCH.xs');
  const transaction = source.split('db.transaction')[1];
  assert.match(transaction, /db\.add exame_situacao_historico/);
  assert.match(transaction, /situacao_anterior: \$exame_atual\.situacao/);
  assert.match(transaction, /resultado: \$resultado_final/);
  assert.match(transaction, /realizado_em: \$realizado_em_final/);
  assert.match(transaction, /observacoes: \$observacoes_finais/);
  assert.match(transaction, /db\.edit exame_situacao_controle/);
  assert.match(transaction, /versao: \(\$controle_situacao\.versao \+ 1\)/);
});

test('GET limita Paciente à própria lista e libera somente resultado disponível', () => {
  const source = read('exames_GET.xs');
  assert.match(source, /field_name = "conta_acesso_id"/);
  assert.match(source, /field_value = \$auth\.id/);
  assert.match(source, /\$db\.exame\.paciente_id == \$paciente_autenticado\.id/);
  assert.match(source, /situacao == "Resultado disponível"/);
  assert.match(source, /resultado: \$resultado_liberado/);
  assert.match(source, /\$db\.exame\.profissional_id == \$profissional\.id/);
  assert.match(source, /intersect:\["profissional", "paciente"\]/);
  assert.match(source, /\$input\.paciente_id > 0/);
  assert.match(source, /\$input\.consulta_id > 0/);
});
