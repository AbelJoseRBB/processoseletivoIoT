# Processo Seletivo – Intensivo Maker | IoT

## Etapa Prática – Sistemas Embarcados

### Identificação do Candidato

- **Nome completo: Abel José Rocha Barros Bezerra**
- **GitHub: https://github.com/AbelJoseRBB**

---

## Visão Geral da Solução

O sistema tem como objetivo o monitoramento de temperatura de ambientes refrigerados/estufas, simulado no Wokwi com um ESP32. acompanhando duas condiçoes de risco:

- Tempo cuja porta fica aberta - Simulado por um botão
- Variação de temperatura - Medido através do sensor MPU6050

Caso um limite configurado seja ultrapassado, o sistema emitirá um alerta via Serial e quando ambas as condições retornam para os padrões seguros simultaneamente, o sistema reporta a normalização. 

---

## Arquitetura do Sistema Embarcado

O fluxo do `main.py` é feito da seguinte foram: 

**1. Inicialização**
- Configura o barramento I2C (`SCL=22`, `SDA=21`) e tira o MPU6050 do modo *sleep* escrevendo `0x00`
  no registrador `PWR_MGMT_1`.
- Configura o botão (`Pin 4`) com `PULL_UP`, de forma que soltar o botão gera leitura `0` (porta aberta).
- Imprime a mensagem `"Sistema de Monitoramento Inicializado"` assim que os periféricos estão prontos.

**2. Loop principal**
- A cada iteração, lê o estado do botão e a temperatura atual do MPU6050.
- Usa `utime.sleep_ms(600)` como intervalo de amostragem (em vez de um `sleep` longo bloqueante),
  mantendo o loop responsivo entre uma leitura e outra.

**3. Máquina de estados — Porta**
- Ao detectar a porta aberta pela primeira vez, guarda o timestamp (`utime.ticks_ms()`).
- A cada iteração seguinte, verifica com `utime.ticks_diff()` se o tempo decorrido ultrapassou
  `LIMITE_TEMPO_X` (5000 ms). Se sim, e o alarme ainda não foi disparado, imprime o alerta de porta
  aberta e marca `alarme_porta = True` , evitando reimpressão a cada loop.

**4. Máquina de estados — Temperatura**
- Enquanto a porta está fechada, se ainda não existe uma referência definida, captura a temperatura
  atual como `temperatura_referencia`.
- A cada iteração, calcula `delta_t = temperatura_atual - temperatura_referencia`.
- Se `delta_t >= LIMITE_VARIACAO_Y` (3.0 °C) e o alarme térmico ainda não foi disparado, imprime o
  alerta de degradação térmica e marca `alarme_termico = True`.

**5. Normalização**
- Só reseta os alarmes (`alarme_porta`, `alarme_termico`) e a referência de temperatura quando,
  simultaneamente: a porta está fechada **e** a temperatura está dentro do gradiente aceitável.
- Nesse momento, imprime `"Status: Sistema Normalizado."` e limpa `referencia_definida`, permitindo
  que uma nova referência seja capturada no próximo fechamento.

---

## Componentes Utilizados na Simulação

- **ESP32:** microcontrolador principal, executa o firmware em MicroPython.

- **MPU6050:** conectado via I2C , utilizado como sensor de temperatura ambiente.

- **Botão:** conectado com pull-up interno, simula o estado físico da porta/tampa (`pressionado = fechada` - `solto = aberta`)

- **Serial (UART):** usada para enviar as mensagens de status/alerta lidas pela esteira de CI.

---

## Decisões Técnicas Relevantes

- **Função `ler_temperatura(i2c)`:** Utilizando bibliotecas externas do MPU6050 como refêrencia, a implementação foi simplificada para incluir somente as funcionalidades necessárias ao problema, evitando dependências externas e reduzindo a complexidade do código.

- **Flags de estado** (`alarme_porta`, `alarme_termico`, `referencia_definida`) para controlar
  transições e impedir que a mesma mensagem seja impressa repetidamente enquanto a condição persiste. 

- **Arquitetura não bloqueante:** o único delay do loop é um `sleep_ms(600)` curto, garantindo que o
  firmware não perca a janela de tempo em que o simulador altera botão/temperatura.

- **Função `ler_botao_debounced()`:** Utilizada para eliminar os efeitos de bounce do botão, garantindo leituras mais confiáveis do estado da porta por meio da validação temporal das mudanças de sinal.

---

## Resultados Obtidos

- O sistema imprime corretamente a mensagem de inicialização ao ligar.
- Ao manter a porta aberta por tempo igual ou superior a `LIMITE_TEMPO_X`, o alerta de porta aberta
  é disparado uma única vez.
- Ao elevar a temperatura acima do gradiente `LIMITE_VARIACAO_Y` em relação à referência, o alerta de
  degradação térmica é disparado uma única vez.
- Ao fechar a porta com a temperatura dentro do limite aceitável, o sistema reporta a normalização e
  limpa os estados de alarme.

---

## Comentários Adicionais (Opcional)

Com o desenvolvimento deste projeto, foi possível aprofundar os conhecimentos sobre o sensor MPU6050, explorando sua comunicação via I2C, seus registradores e as diferentes formas de integração em sistemas embarcados. Para isso, foram consultadas bibliotecas e materiais de referência, dos quais foram aproveitadas apenas as funcionalidades necessárias para a solução proposta. Além do aprendizado técnico, o projeto proporcionou uma experiência próxima de aplicações encontradas no ambiente industrial, onde o monitoramento de condições operacionais e a geração de alertas são requisitos comuns, contribuindo para a preparação em desafios semelhantes no futuro.

---


