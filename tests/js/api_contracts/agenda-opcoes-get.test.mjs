import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { assertApiContract, assertClientContract, root } from './helpers.mjs';

test('GET /agenda/opcoes tem cliente e export Xano restrito a dados mínimos', () => {
  const source = assertApiContract(
    'GET', '/agenda/opcoes', 'api/sorriso_acesso/agenda_opcoes_GET.xs',
  );
  assertClientContract('GET', '/agenda/opcoes', 'listar_opcoes_agenda');
  assert.match(source, /auth = "conta_acesso"/);
  assert.match(source, /sorriso_validar_sessao/);
  assert.match(source, /administrador.*recepcionista/);
  assert.match(source, /output = \["id", "nome"\]/);
  assert.doesNotMatch(source, /telefone|cpf|email|observacoes|conteudo_clinico/);

  const client = readFileSync(resolve(root, 'sorrisomais/api.py'), 'utf8');
  assert.match(client, /def listar_opcoes_agenda\(/);
  assert.match(client, /for chave in \("pacientes", "profissionais", "procedimentos"\)/);
});
