## Contexto e exploração

Os assets estáticos vivem em assets e são renderizados por Streamlit e HTML com data URI. As referências mostram banners de fundo menta, ondas suaves, texto à esquerda e personagem à direita. Não havia change ativa na retomada. O pedido do usuário autoriza a implementação deste escopo visual.

## Decisões

### Retorno da Visão geral solicitado pelo usuário

Restaurar somente a composição da Visão geral dos três perfis ao estado anterior à última auditoria: quatro indicadores em disposição vertical, atualização do resumo fora de popover e Agenda/atalhos do Profissional visíveis. Restaurar proporção anterior do banner e tamanhos de títulos, ícones e valores apenas dentro de visao-geral. Preservar a marca atual, o menu fixo com rolagem independente e as correções das demais telas, inclusive Agenda.

### Auditoria da Agenda e dos três painéis

Conferência final: 18 composições em duas resoluções concluídas pelo navegador. Regressão específica de Agenda e painéis: 56 testes aprovados; regressão ampliada de navegação, listagens, formulários, Exames e Reagendamento: 200 testes aprovados. Os grupos se sobrepõem. A checagem visual exige cinco colunas na tabela e quatro/três/três cartões primários por perfil, além da assinatura atual e das rolagens independentes. Como a lista de Pacientes ficou mais compacta, o teste de rolagem natural passou a usar janela de 1365×300, sem aumentar artificialmente o conteúdo.

A auditoria geral retirou divisores duplicados de Pacientes, alinhou o cabeçalho de Prontuários, uniformizou o título de Reagendamento e removeu detalhes de implementação do texto de Exames. A composição final dos painéis segue o retorno da Visão geral descrito acima, com quatro indicadores por perfil.

Agenda passa a usar uma única tabela HTML sem cartões entre as linhas. Filtros ficam alinhados pela base; navegação de data, atualização e criação de horário permanecem no popover Opções. Alterações de situação e gestão dos horários continuam disponíveis em seção expansível abaixo da tabela. Em celular, cada linha apresenta rótulos dos cinco campos. Todos os valores são escapados na saída HTML.

O arranjo experimental dos painéis nesta auditoria foi substituído pelo retorno da Visão geral solicitado pelo usuário: quatro indicadores com ícones acima dos valores, atualização fora de popover e Agenda e atalhos do Profissional visíveis. Os indicadores continuam baseados nos dados já autorizados.

### Correção da marca e da rolagem independente

Substituir a imagem antiga assets/mascote-sorriso.png por marca_html(), assinatura compartilhada com 04-profissionais.png transparente, nome e subtítulo da clínica. Não existe um arquivo independente de logo nova no conjunto fornecido; a composição reutiliza o mascote atual sem redesenhá-lo. Login da equipe, menu, área do Paciente e favicon deixam de apontar para o recurso antigo, que permanece preservado no disco.

Em desktop, o menu usa position:fixed e altura 100dvh; a coluna reserva a largura definida por variável CSS. overflow-y:auto e overscroll-behavior-y:contain isolam sua rolagem. O seletor considera o stLayoutWrapper realmente gerado pelo Streamlit. Em celular permanece a navegação compacta no fluxo normal.

### Correção de composição solicitada pelo usuário

Substituir integralmente o CSS acumulado por uma base única. Banners grandes exclusivamente nos painéis, abaixo da saudação. Listagens sem banners nem títulos duplicados; cabeçalhos compactos, tabela de Agenda em cinco colunas, catálogo de Procedimentos em linhas e fichas de Profissionais. Menu verde-escuro com item ativo menta. Formulários sem artes acima dos campos. Preservar todos os controles e dados disponíveis; não inventar valores, contatos ou ações ausentes nos contratos para imitar imagens estáticas.

- Centralizar a leitura e cache das imagens em sorrisomais/ilustracoes.py; escapar os textos de HTML.
- Usar somente cópias tratadas, sem fallback para originais com fundo.
- Em celular, posicionar a ilustração abaixo do texto.
- Manter mensagens Streamlit acessíveis junto das artes de estados, sem substituir feedback funcional.
- Usar a assinatura atual compartilhada descrita acima. Mascote 14 ilustra o login; 01 e 02 os painéis administrativos; 16 o acompanhamento do Profissional; 09 a 12 feedback e estados da Agenda. Recursos 03 a 08 permanecem preparados, mas as referências de listagens e formulários não comportam os banners anteriormente adicionados.
- Recursos 13 e 15 preparados, mas reservados: não criar telas nem indicadores fora do escopo.

## Preparação e limitações

Os recortes automáticos iniciais foram rejeitados por halos e remoção de detalhes. As versões finais de 02-agenda e 11-sem-agendamentos exigiram extração pelo editor de imagens. A ferramenta produziu variantes em resolução maior; esta exceção deve ser informada na entrega. Os demais recursos preservam o bitmap original. A fonte 01 já tem parte do acessório cortada na borda direita; não é possível recuperar pixels ausentes sem reconstrução.

## Verificação

### Reconstrução final

Executado tests/visual/conferir_referencias.py: 18 composições em 1365×900 e 390×844, sem exceções de aplicação, imagens quebradas ou largura excedida. Capturas em test-results/reconstrucao-frontend, inclusive vistas do conteúdo após rolagem e modais isolados. Inclui login, três perfis de painel, Agenda, vazio, erro, Pacientes, Profissionais, Procedimentos, Prontuários, cadastros de Paciente e Profissional, Nova Consulta, evolução, edição, Exames e Reagendamento. Conferidos no navegador a expansão de Gerenciar consulta, a validação de evolução vazia e o fechamento de modais por Cancelar. Os dados são fictícios e o cliente de teste não envia requisições externas.

Regressão ampla: 264 testes aprovados. Depois dos ajustes nos badges, 49 testes focados aprovados. Após os ajustes finais de formulários e cabeçalho de Pacientes, 50 testes focados aprovados. Os números representam rodadas com sobreposição, não totais cumulativos.

Diferenças necessárias de conteúdo: a API atual do catálogo fornece nomes, não valores e duração; a lista de Pacientes usa o contrato administrativo mínimo, sem buscar dados pessoais adicionais apenas para completar colunas da imagem. Cadastro de Profissional mantém campos de credenciais exigidos pelo fluxo existente. Evolução mantém autoria vinculada à Conta de Acesso e campos previstos no contrato. Configurações e relatórios não foram criados. A aparência segue as referências compatíveis sem inventar capacidades de backend.

O mascote 02 exigiu uma segunda extração assistida para remover um fragmento de outro personagem presente no recorte de origem. Os arquivos 02 e 11 são variantes de maior resolução; os demais mantêm os pixels originais.

Testes existentes de interface e rotas, revisão dos 16 recursos sobre fundo menta e capturas reais de Streamlit com API fictícia em desktop e celular. O roteiro legado de Agenda encontrou uma asserção de conteúdo sem relação com o banner; um roteiro específico verifica carregamento, largura e separação entre texto e arte.
