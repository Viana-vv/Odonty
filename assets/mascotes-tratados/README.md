# Mascotes Sorriso+

Os 16 PNGs correspondem às fontes de SorrisoPlus_Mascotes_Individuais. Os originais permanecem intactos. A remoção do fundo é gravada no canal alfa; não depende de CSS.

Uso atual: 01 boas-vindas da Administração; 02 painel da Recepção; 09 confirmação na Agenda; 10 aviso na Agenda; 11 Agenda vazia; 12 erro da Agenda; 14 segurança do login; 16 acompanhamento do Profissional. Recursos 03 a 08 estão preparados para uso contextual, mas os banners e artes acima dos formulários foram retirados para respeitar as referências das listagens e modais.

13-configuracoes e 15-relatorios estão preparados e reservados para funcionalidades futuras. Não foram criadas telas fora do escopo.

O mascote 11 exigiu extração assistida pelo editor de imagens, porque a segmentação inicial removeu corpo e mãos. Prompt: remover somente o fundo, preservar personagem completo, jaleco, braços, mãos e balão de calendário; PNG realmente transparente, sem halo. A ferramenta gerou uma variante em resolução maior, cuja fidelidade deve ser considerada na revisão do grupo.

O arquivo fonte 01 contém acessório já cortado pela borda da imagem. O tratamento preserva esse limite de origem.

O arquivo 02 também passou pelo editor de imagens para remover um fragmento desconectado de outro personagem na borda esquerda. Prompt: remover somente esse fragmento, preservando o mascote principal e calendário, sem fundo. Assim como 11, é uma variante assistida em resolução maior, e não uma garantia de identidade pixel a pixel.

Validação: 222 testes de regressão, OpenSpec válido e capturas automatizadas desktop/celular em test-results/mascotes. O script tests/visual/conferir_mascotes.py utiliza exclusivamente respostas fictícias da API.
