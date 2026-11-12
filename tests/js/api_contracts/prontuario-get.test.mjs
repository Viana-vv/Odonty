import assert from 'node:assert/strict';
import test from 'node:test';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { assertApiContract, assertClientContract, root } from './helpers.mjs';

test('cliente declara GET agregado de Prontuário', () => {
  assertClientContract('GET', '/prontuarios/{id}', 'obter_prontuario');
  const source = assertApiContract('GET', '/prontuarios/{id}', 'api/sorriso_acesso/prontuarios_id_GET.xs');
  assert.match(source, /auth = "conta_acesso"/);
  assert.match(source, /function\.run sorriso_validar_sessao/);
  assert.match(source, /paciente_id/);
  assert.match(source, /liberado_paciente/);
  assert.match(source, /history = false/);
});

test('GET agregado declara todas as seções do Prontuário', () => {
  const source = readFileSync(resolve(root, 'backend/xano/api/sorriso_acesso/prontuarios_id_GET.xs'), 'utf8');
  for (const section of [
    'anamnese', 'historico_odontologico', 'odontograma', 'exame_clinico',
    'diagnosticos', 'plano_tratamento', 'procedimentos', 'exames',
    'prescricoes', 'evolucoes', 'documentos',
  ]) {
    assert.match(source, new RegExp(section));
  }
});

test('GET agregado restringe perfil administrativo e referências de arquivos', () => {
  const source = readFileSync(resolve(root, 'backend/xano/api/sorriso_acesso/prontuarios_id_GET.xs'), 'utf8');
  assert.doesNotMatch(source, /url_publica(?:_permanente)?/i);
  assert.match(source, /administrador|recepcionista/);
  assert.match(source, /conteudo_clinico|liberado_paciente/);
});
