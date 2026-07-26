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
- A cada iteração, lê o estado do botão e a temperatura atual do MPU6050 (registrador `TEMP_OUT_H`,
  convertido para °C).
- Usa `utime.sleep_ms(600)` como intervalo de amostragem (em vez de um `sleep` longo bloqueante),
  mantendo o loop responsivo entre uma leitura e outra.

**3. Máquina de estados — Porta**
- Ao detectar a porta aberta pela primeira vez, guarda o timestamp (`utime.ticks_ms()`).
- A cada iteração seguinte, verifica com `utime.ticks_diff()` se o tempo decorrido ultrapassou
  `LIMITE_TEMPO_X` (5000 ms). Se sim, e o alarme ainda não foi disparado, imprime o alerta de porta
  aberta e marca `alarme_porta = True` (evita reimpressão a cada loop).

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


Explique a arquitetura lógica do seu projeto, abordando:

- Fluxo principal do programa (`main.py`)
- Estrutura de estados, loops ou temporizações
- Como os componentes interagem entre si

Se desejar, utilize tópicos ou um pequeno diagrama em texto.

---

## Componentes Utilizados na Simulação

- **ESP32:** microcontrolador principal, executa o firmware em MicroPython.
- **MPU6050:** conectado via I2C , utilizado como sensor de temperatura ambiente.
- **Botão:** conectado com pull-up interno, simula o estado físico da porta/tampa (`pressionado = fechada`, `solto = aberta`).
- **Serial (UART):** usada para enviar as mensagens de status/alerta lidas pela esteira de CI.

---

## Decisões Técnicas Relevantes

Explique brevemente decisões importantes tomadas durante o desenvolvimento, como:

- Organização do código
- Uso de funções, estados ou constantes
- Estratégias para temporização ou controle lógico

---

## Resultados Obtidos

Descreva o comportamento final do sistema:

- O que funciona corretamente
- Quais requisitos foram atendidos
- Resultado observado na simulação do Wokwi

---

## Comentários Adicionais (Opcional)

Utilize este espaço para comentar, se desejar:

- Dificuldades encontradas
- Limitações da solução
- Melhorias que você faria com mais tempo
- Principais aprendizados durante o desafio

---

> Este relatório faz parte da avaliação técnica.  
> Clareza, objetividade e organização são tão importantes quanto o funcionamento do código.

---

## Especificação dos Testes Automatizados (Wokwi CI)

Para que o projeto seja validado com sucesso na esteira de integração contínua (CI), o firmware escrito em MicroPython deve interagir corretamente com as leituras dos sensores descritos em cada cenário e enviar as mensagens de status exatas.

### Requisitos Críticos de Implementação

1. **Casamento Exato de Strings:** O Wokwi CI faz uma verificação estrita caractere por caractere. Se houver divergência em maiúsculas/minúsculas, acentuação ou falta de pontuação, o teste irá falhar.
2. **Arquitetura Não-Bloqueante:** Evite o uso de funções bloqueantes. Elas podem fazer com que o firmware perca a janela de tempo em que o simulador altera o peso, quebrando a sincronia do teste automatizado.

---

## Suporte

Em caso de dúvidas:

- Consulte o material dos cursos EAD
- Leia atentamente este README
- Analise os logs das GitHub Actions
- Utilize os canais oficiais para contato com os instrutores
