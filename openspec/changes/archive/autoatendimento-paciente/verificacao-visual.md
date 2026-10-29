# Verificação visual do autoatendimento

Inspeção feita em 26/10/2026 no portal Streamlit executado localmente com Chromium headless e uma API simulada em processo. O fixture usou exclusivamente identidade e dados fictícios; o cliente da simulação bloqueou qualquer host diferente do Xano fictício local e nenhuma requisição foi enviada à rede.

## Viewports e resultado

| Área | Desktop | Celular |
|---|---:|---:|
| Viewport | 1440 × 1000 px | 390 × 844 px |
| Largura do documento / corpo | 1440 / 1440 px | 390 / 390 px |
| Rolagem horizontal | Não | Não |
| Login | E-mail, Senha mascarada, controle de exibição da senha e Entrar visíveis | Os mesmos controles visíveis, campos e botão dentro da largura |
| Área autenticada | Sair e três abas visíveis; cartões ocupam a largura disponível | Sair, três abas e cartões cabem na tela; textos extensos quebram linha |

As abas Consultas, Informações liberadas e Exames foram abertas nas duas larguras e exibiram o conteúdo fictício correspondente. Em ambas, o controle Futuras/Passadas permaneceu disponível; selecionar Passadas mudou o subtítulo para “Consultas passadas”. A tela de Exames manteve resultado e datas dentro do cartão. O Registro Clínico exibiu data, conteúdo e Profissional dentro do cartão, sem sobreposição.

Não houve erros de console ou exceções JavaScript. Não encontrei defeito visual reproduzível, então não foi necessária alteração de código.

## Capturas

As capturas abaixo foram geradas com os dados fictícios da simulação:

- [Login desktop](evidencias/desktop-login.png)
- [Login celular](evidencias/mobile-login.png)
- [Consultas desktop](evidencias/desktop-consultas.png)
- [Consultas celular](evidencias/mobile-consultas.png)
- [Consultas passadas no celular](evidencias/mobile-consultas-passadas.png)
- [Informações liberadas no celular](evidencias/mobile-registros.png)
- [Exames no celular](evidencias/mobile-exames.png)
