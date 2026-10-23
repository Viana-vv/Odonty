## Contexto

A sessão do Profissional e a autorização continuam sob controle do Xano. O cliente já possui `listar_consultas`, que aceita intervalo temporal e normaliza os campos de horário, situação, Paciente, Profissional e procedimentos. O painel não precisa de novos contratos nem deve usar repositório demonstrativo.

## Objetivos / Não objetivos

**Objetivos:** oferecer o resumo diário do Profissional, usando somente respostas Xano autenticadas.

**Não objetivos:** mudar APIs, regras clínicas, agenda administrativa ou painel dos demais perfis.

## Decisões

- Reutilizar a página inicial existente da equipe e renderizar a composição própria quando a Conta de Acesso possuir perfil Profissional.
- Consultar `GET /consultas` uma vez para o intervalo do dia no fuso `America/Sao_Paulo`; deixar o Xano aplicar o escopo do Profissional autenticado.
- Derivar totais, concluídos/realizados e próxima Consulta da resposta, sem alegar totais globais de Pacientes.
- Mostrar lista com horário, nome do Paciente, situação e procedimentos já devolvidos pelo contrato.
- Atalhos navegam para Agenda e Prontuário já existentes. Acesso ao Prontuário continua sujeito à permissão Xano.
- Manter logs sem dados de Paciente ou informações clínicas. Não buscar Registros Clínicos nem exames para o resumo.

## Tratamento de falhas

Erro 401/403 limpa a sessão de acordo com o fluxo existente. Erros restantes mostram mensagem genérica e permitem nova tentativa. Resposta vazia é estado normal.

## Riscos / Compensações

- O Xano pode retornar um escopo diferente do esperado → o painel não envia identificador de Profissional e confia somente no filtro/autorização do backend.
- O contrato não retorna dados suficientes para alguns cards da referência → os cards sem fonte confiável são omitidos, evitando métricas inventadas.

## Implantação

Não há migração nem mudança no Xano. A reversão consiste em remover a página especializada e restaurar a chamada existente da visão geral.

## Verificação

Testes Python e JavaScript isolam o contrato `GET /consultas` e verificam parâmetros/autorização sem rede real. Smoke real só pode ocorrer se URL e token de teste estiverem configurados, limitado a 10 requisições em 20 segundos.
