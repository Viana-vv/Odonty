## Why

A validação do OTP usa um código numérico de seis dígitos, mas a tela apresenta um único campo, dificultando a leitura, a digitação e o uso em dispositivos móveis. A entrada deve refletir o formato real do código sem alterar a validação existente.

## What Changes

- Substituir o campo único do OTP por seis campos quadrados, um por dígito.
- Aceitar somente dígitos, avançar automaticamente entre campos e tratar backspace e colagem do código completo.
- Manter a concatenação dos seis valores e o envio ao endpoint atual de validação.
- Ajustar estilos responsivos sem redesenhar a tela de recuperação.
- Melhorar o e-mail do OTP com versão HTML, instruções claras, código destacado e imagem da marca, mantendo fallback em texto simples.

## Capabilities

### New Capabilities

### Modified Capabilities

- `recuperacao-senha`: atualizar a interação de entrada do OTP numérico de seis dígitos e a apresentação da mensagem enviada.

## Impact

- Interface Streamlit em `app.py` e estilos em `assets/estilos.css`.
- Testes de interface e validação local do OTP.
- O contrato REST permanece igual; o backend Xano terá apenas a apresentação do e-mail atualizada.
