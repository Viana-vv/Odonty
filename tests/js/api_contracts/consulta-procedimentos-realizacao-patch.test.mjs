import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { root } from './helpers.mjs';

const api = readFileSync(
  resolve(root, 'backend/xano/api/sorriso_acesso/consultas_id_procedimentos_consulta_procedimento_id_realizacao_PATCH.xs'),
  'utf8',
);
const client = readFileSync(resolve(root, 'sorrisomais/procedimentos_consulta.py'), 'utf8');

test('PATCH de realização é autenticado, limitado ao Profissional da Consulta e à transição permitida', () => {
  assert.match(api, /query "consultas\/\{id\}\/procedimentos\/\{consulta_procedimento_id\}\/realizacao" verb=PATCH/);
  assert.match(api, /auth = "conta_acesso"/);
  assert.match(api, /function\.run sorriso_validar_sessao/);
  assert.match(api, /\["profissional"\]/);
  assert.match(api, /\$consulta\.profissional_id != \$profissional_autenticado\.id/);
  assert.match(api, /\$vinculo\.situacao != "planejado"/);
  assert.match(api, /db\.transaction/);
  assert.match(api, /\$vinculo_atual\.situacao != "planejado"/);
  assert.match(api, /situacao: "realizado", realizado_por_profissional_id: \$profissional_autenticado\.id, realizado_em: now/);
  assert.match(api, /HTTP\/1\.1 409 Conflict/);
});

test('cliente Python usa a rota PATCH própria sem executar rede neste teste', () => {
  assert.match(client, /def marcar_procedimento_realizado\(/);
  assert.match(client, /f"\/consultas\/\{consulta_id\}\/procedimentos\/"/);
  assert.match(client, /f"\{consulta_procedimento_id\}\/realizacao"/);
});
