## Why

A Agenda consulta `GET /consultas` durante cada rerun do Streamlit. Alterar um filtro ou executar uma ação visual pode repetir a mesma leitura e consumir rapidamente o limite de requisições do plano gratuito do Xano.

## What Changes

- Reutilizar a lista bem-sucedida de Consultas por Conta de Acesso e data durante vinte segundos.
- Aplicar intervalo de vinte segundos antes de tentar novamente após uma falha de leitura.
- Invalidar o cache quando uma Consulta ou Disponibilidade for alterada, e limpar os dados temporários ao encerrar a sessão.
- Preservar busca, filtros, controles e contratos REST existentes.

Fora do escopo: alterar rotas, permissões, regras de negócio ou dados do Xano; guardar respostas de falha; modificar outras telas.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `interface-equipe`: limitar chamadas repetidas de Consultas durante a navegação na Agenda.

## Impact

- Streamlit: `sorrisomais/paginas_equipe.py` e limpeza de cache de sessão já especificada no painel administrativo.
- Testes da Agenda: cobertura de reutilização, expiração e invalidação após alterações.
- Nenhuma alteração nos contratos Python/JavaScript nem no backend Xano.
