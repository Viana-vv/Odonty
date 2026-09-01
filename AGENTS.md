# Instruções para Agentes de IA

## 1. Contexto obrigatório

Antes de planejar ou realizar alterações, leia:

- `docs/project-overview.md`;
- `docs/domain-model.md`;
- os documentos da change atual em `openspec/changes/`, quando existirem.

Esses documentos são a fonte de verdade sobre o objetivo, o domínio e o escopo do projeto.

Se existir conflito entre o código e a documentação, informe o problema antes de continuar.

## 2. Idioma

- Escreva a documentação em português brasileiro.
- Escreva os documentos do OpenSpec em português brasileiro.
- Use os nomes definidos no modelo de domínio.
- Não utilize nomes diferentes para representar o mesmo conceito.

## 3. Tecnologias obrigatórias

O projeto utiliza:

- Python como linguagem de programação;
- Streamlit como frontend;
- Xano como backend e banco de dados;
- APIs REST para comunicação;
- OpenSpec para especificação das mudanças;
- Git e GitHub para versionamento;
- Render ou Railway para implantação.

Não introduza outro frontend, backend ou banco de dados sem autorização do grupo.

## 4. Arquitetura

- O Streamlit é responsável pela interface.
- O Xano é responsável pelos dados e pelas regras de negócio.
- O Xano deve controlar autenticação e autorização.
- O frontend não deve ser considerado mecanismo de segurança.
- Toda operação protegida deve ser validada no backend.
- A comunicação entre Streamlit e Xano deve acontecer por API REST.
- Endereços de API e configurações devem usar variáveis de ambiente.
- Regras importantes não devem existir apenas no frontend.

## 5. Desenvolvimento com OpenSpec

Mudanças funcionais ou técnicas relevantes devem utilizar OpenSpec.

O fluxo será:

```text
Explore
   ↓
Propose
   ↓
Review
   ↓
Apply
   ↓
Verify
   ↓
Archive
```

Regras:

- use Explore antes de implementar;
- não escreva código durante o Explore;
- crie changes pequenas e verificáveis;
- revise `proposal.md`, specs, `design.md` e `tasks.md`;
- implemente somente o que foi aprovado;
- não preencha `openspec/specs/` manualmente;
- execute testes antes de concluir;
- arquive somente changes concluídas.

## 6. Limites das alterações

- Trabalhe somente no que foi solicitado.
- Não construa o sistema inteiro de uma vez.
- Não adicione funcionalidades fora da change atual.
- Não altere arquivos sem relação com a tarefa.
- Não crie arquivos desnecessários.
- Não troque tecnologias sem autorização.
- Não aumente o escopo sem consultar o grupo.
- Não modifique funcionalidades prontas sem justificativa.

## 7. Regras do domínio

- Use `Paciente` para representar a pessoa atendida.
- Use `Conta de Acesso` para autenticação e permissões.
- Não confunda paciente com conta de acesso.
- Não confunda consulta com exame.
- Não confunda consulta com prontuário.
- Não confunda prontuário com registro clínico.
- Um paciente possui um prontuário.
- Um prontuário pode possuir vários registros clínicos.
- Uma consulta pertence a um paciente.
- Uma consulta pertence a um profissional.
- Uma consulta utiliza um horário da agenda.
- Uma consulta pode possuir vários procedimentos.
- Uma consulta pode possuir vários exames.
- Não permita dois agendamentos para o mesmo profissional e horário.
- Preserve o histórico das consultas.
- Preserve o histórico dos prontuários.
- Preserve o histórico dos procedimentos.
- Preserve o histórico dos exames.
- Não apague dados históricos quando um cadastro for inativado.

Consulte `docs/domain-model.md` para conhecer todas as regras e os relacionamentos.

## 8. Segurança e privacidade

- Utilize somente dados fictícios.
- Nunca utilize informações de pacientes reais.
- Não coloque CPF ou RG real no projeto.
- Não coloque prontuários ou exames reais no projeto.
- Não armazene senhas em texto puro.
- Não coloque senhas, tokens ou chaves no código.
- Use variáveis de ambiente para configurações sensíveis.
- Aplique autenticação e autorização no Xano.
- O paciente só pode acessar os próprios dados.
- O profissional só pode acessar dados necessários ao atendimento.
- A recepcionista não pode modificar informações clínicas.
- Não coloque informações clínicas nos logs.
- Não exponha informações sensíveis em mensagens de erro.
- Arquivos de exames não devem possuir links públicos permanentes.
- O sistema é um MVP acadêmico e não está pronto para uso clínico real.

## 9. Código

- Escreva código simples e compreensível.
- Use nomes claros para funções e variáveis.
- Evite duplicação.
- Reutilize código existente quando apropriado.
- Separe interface, API, configuração e controle de sessão.
- Não misture regras de negócio com componentes visuais.
- Trate falhas de conexão.
- Trate respostas vazias.
- Trate dados inválidos.
- Trate usuário não autenticado.
- Trate usuário sem permissão.
- Apresente mensagens de erro compreensíveis.
- Não exponha dados técnicos ou sensíveis nas mensagens.
- Não deixe códigos temporários ou comandos de depuração na versão final.

## 10. Testes

Toda mudança funcional deve possuir uma forma de verificação.

Verifique, quando aplicável:

- cenário de sucesso;
- campos obrigatórios;
- dados inválidos;
- recurso não encontrado;
- tentativa de duplicação;
- conflito de horário;
- usuário não autenticado;
- usuário sem permissão;
- falha na API;
- sessão expirada;
- comportamento do frontend após sucesso;
- comportamento do frontend após erro.

Não declare uma tarefa concluída sem informar como ela foi testada.

## 11. Git e GitHub

- Não faça commits diretamente na branch `main`.
- Crie uma Issue para cada tarefa ou defeito.
- Crie uma branch relacionada à Issue.
- Faça commits pequenos e descritivos.
- Abra um Pull Request para cada mudança.
- Informe no Pull Request como testar.
- Solicite revisão de outro integrante.
- Não coloque mudanças diferentes no mesmo Pull Request.
- Não envie credenciais ou dados pessoais para o GitHub.
- Mantenha a branch principal funcionando.

## 12. Documentação

- Atualize a documentação quando o comportamento mudar.
- Atualize a documentação quando o domínio mudar.
- Atualize a documentação quando a arquitetura mudar.
- Não copie toda a documentação para o `AGENTS.md`.
- Não copie toda a documentação para `openspec/config.yaml`.
- Coloque regras permanentes nos documentos de contexto.
- Coloque comportamentos específicos nas specs da change.
- Use somente dados fictícios nos exemplos.

## 13. Quando interromper o trabalho

Interrompa e peça uma decisão ao grupo quando:

- a solicitação contradizer o modelo de domínio;
- for necessário trocar uma tecnologia;
- a mudança aumentar significativamente o escopo;
- existir risco de exposição de dados;
- uma regra de negócio estiver confusa;
- for necessário alterar uma funcionalidade não relacionada;
- a documentação estiver em conflito com o código;
- a change não possuir informações suficientes.

## 14. Definição de conclusão

Uma mudança só está concluída quando:

- o escopo aprovado foi implementado;
- os critérios de aceitação foram atendidos;
- as permissões foram aplicadas no Xano;
- os cenários relevantes foram testados;
- não existem dados reais no código;
- não existem credenciais no código;
- a documentação necessária foi atualizada;
- a implementação corresponde à especificação;
- o resultado está pronto para revisão do grupo.