## 1. Ajuste responsivo

- [x] 1.1 Corrigir o seletor do breakpoint do painel Profissional para alcançar o bloco horizontal por meio do wrapper Streamlit; `tests/test_painel_profissional.py` verifica o seletor responsivo.
- [x] 1.2 Capturar e inspecionar o painel em 360, 390, 768 e 1440 px; verificadas composição vertical no celular e tablet, colunas no desktop, rótulo completo e ausência de rolagem horizontal. Capturas locais: `%TEMP%/odonty-panel-final-{360,390,768,1440}.png`.

## 2. Verificação

- [x] 2.1 `pytest tests/test_painel_profissional.py -q -p no:cacheprovider` passou (9 testes); `openspec validate ajuste-responsividade-painel-profissional-86 --strict` e `git diff --check` passaram.
