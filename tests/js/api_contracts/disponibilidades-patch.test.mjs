import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { assertClientContract, root } from './helpers.mjs';

test('cliente declara PATCH /disponibilidades/{id}', () => {
  assertClientContract('PATCH', '/disponibilidades/{disponibilidade_id}', 'atualizar_disponibilidade');
  const source = readFileSync(resolve(root, 'backend/xano/api/sorriso_acesso/disponibilidades_id_PATCH.xs'), 'utf8');
  assert.match(source, /inicio:.*format_timestamp:"c":"UTC"/);
  assert.match(source, /fim:.*format_timestamp:"c":"UTC"/);
});
test('edição aguardando trava não pode sobrescrever reserva concorrente', () => {
  const source = readFileSync(resolve(root, 'backend/xano/api/sorriso_acesso/disponibilidades_id_PATCH.xs'), 'utf8');
  assert.doesNotMatch(source, /agenda_lock_version/);
  assert.match(source, /db\.edit agenda_controle/);
  const transacao = source.split('db.transaction')[1];
  const trava = transacao.indexOf('} as $trava_agenda');
  const releitura = transacao.indexOf('db.get disponibilidade_agenda', trava);
  const validacao = transacao.indexOf('if ($disponibilidade_atual == null', releitura);
  const escrita = transacao.indexOf('db.edit disponibilidade_agenda', validacao);
  assert.ok(trava >= 0 && trava < releitura && releitura < validacao && validacao < escrita);
  const guarda = transacao.slice(validacao, escrita);
  for (const campo of ['profissional_id', 'inicio', 'fim', 'situacao']) {
    assert.ok(guarda.includes(`$disponibilidade_atual.${campo} != $disponibilidade.${campo}`));
  }
  assert.ok(guarda.includes('$disponibilidade_atual.situacao == "reservado"'));
  assert.ok(guarda.includes('var.update $conflito { value = true }'));
});
