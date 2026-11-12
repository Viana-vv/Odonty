## 1. Contrato e modelo Xano

- [ ] 1.1 Criar tabelas versionadas para seções do Prontuário e ampliar dados cadastrais necessários, preservando compatibilidade e histórico
- [x] 1.2 Criar GET agregado autorizado do Prontuário com projeção por perfil e estados vazios
- [ ] 1.3 Criar POST/retificação das seções clínicas e validar escopo, tipos, campos obrigatórios e histórico
- [ ] 1.4 Integrar Procedimentos, Exames, Registros Clínicos e referências privadas de Documentos/Imagens sem URLs públicas

## 2. Cliente REST e interface

- [x] 2.1 Implementar clientes Python para o agregado e seções com validação de resposta e mensagens seguras
- [x] 2.2 Refazer a tela de Prontuário com resumo cadastral, abas/seções, odontograma real quando retornado e estados vazios sem dados inventados
- [ ] 2.3 Permitir registro de seções somente ao Profissional autorizado e manter Evolução legada compatível
- [ ] 2.4 Corrigir seleção para incluir Pacientes com Prontuário mesmo sem Consulta ou Registro

## 3. Testes e documentação

- [x] 3.1 Criar testes Python e JavaScript separados por rota para sucesso, campos obrigatórios, resposta vazia, escopo, sessão, perfil administrativo e resposta inválida
- [x] 3.2 Atualizar testes de tela para todas as seções, estados vazios, histórico e limpeza após sessão expirada
- [ ] 3.3 Atualizar docs/domain-model.md e specs permanentes após a implementação
- [x] 3.4 Executar suíte Python, contratos JavaScript e validação OpenSpec

## Pendências encontradas antes do arquivamento

O endereço cadastral ainda não foi ampliado no backend. Os tipos de seção e o identificador da retificação precisam ser alinhados entre cliente e Xano. A tela ainda não oferece cadastro de todas as seções, e a seleção depende de Consultas ou Registros existentes. Documentos não possuem fluxo de acesso protegido implementado. As tarefas correspondentes foram reabertas; os testes existentes não comprovam esses critérios. Sincronizar as specs desta change somente após concluir esses comportamentos.
