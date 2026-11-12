import assert from 'node:assert/strict';
import test from 'node:test';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { assertApiContract, assertClientContract, root } from './helpers.mjs';

test('cliente declara POST de seção do Prontuário', () => {
  assertClientContract('POST', '/prontuarios/{id}/secoes', 'registrar_secao_prontuario');
  const source = assertApiContract('POST', '/prontuarios/{id}/secoes', 'api/sorriso_acesso/prontuario_secoes_POST.xs');
  assert.match(source, /auth = "conta_acesso"/);
  assert.match(source, /function\.run sorriso_validar_sessao/);
  assert.match(source, /profissional/);
  assert.match(source, /paciente_id/);
  assert.match(source, /consulta_id/);
});

test('POST de seção preserva versão e não exclui conteúdo histórico', () => {
  const source = readFileSync(resolve(root, 'backend/xano/api/sorriso_acesso/prontuario_secoes_POST.xs'), 'utf8');
  assert.match(source, /versao/);
  assert.match(source, /history = false/);
  assert.doesNotMatch(source, /db\.delete/);
  assert.doesNotMatch(source, /console\.log|logger\.|log\(/i);
});

test('POST de seção distingue validação de acesso administrativo', () => {
  const source = readFileSync(resolve(root, 'backend/xano/api/sorriso_acesso/prontuario_secoes_POST.xs'), 'utf8');
  assert.match(source, /tipo/);
  assert.match(source, /conteudo/);
  assert.match(source, /administrador|recepcionista/);
});
