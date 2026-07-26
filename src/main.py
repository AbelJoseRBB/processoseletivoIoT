from machine import Pin, I2C
import utime

# Configuração dos pinos e endereço do sensor 
PINO_BOTAO = 4
MPU6050_ADDR = 0x68

# Registradores usados pelo sensor
REG_PWR_MGMT_1 = 0x6B
REG_TEMP_OUT_H = 0x41

# Limites para o monitoramento 
LIMITE_TEMPO_X = 5000
LIMITE_VARIACAO_Y = 3.0

INTERVALO_AMOSTRAGEM = 600

# --- Debounce do botão ---
DEBOUNCE_MS = 50
leitura_anterior = 1          # último valor bruto lido do pino (1 = solto/pull-up)
estado_debounced = 1          # último valor considerado "estável"
ultimo_tempo_mudanca = 0      # timestamp da última mudança bruta detectada

# Monitoramento porta
porta_estava_aberta = False
porta_aberta_desde = 0
alarme_porta = False

# Monitoramento temperatura
referencia_definida = False
temperatura_referencia = 0.0
alarme_termico = False

def ler_temperatura(i2c):
    # Lê 2 bytes da temperatura   
    dados = i2c.readfrom_mem(MPU6050_ADDR, REG_TEMP_OUT_H, 2)
    bruto = (dados[0] << 8) | dados[1]

    # Conversão para inteiro 
    if bruto >= 0x8000:
        bruto -= 0x10000

    # Conversão para graus Celsius
    return (bruto / 340.0) + 36.53

#Realiza o debounce do botão
def ler_botao_debounced():
    global leitura_anterior, estado_debounced, ultimo_tempo_mudanca

    leitura_atual = botao.value()

    if leitura_atual != leitura_anterior:
        ultimo_tempo_mudanca = utime.ticks_ms()
        leitura_anterior = leitura_atual

    if utime.ticks_diff(utime.ticks_ms(), ultimo_tempo_mudanca) >= DEBOUNCE_MS:
        estado_debounced = leitura_atual

    return estado_debounced

def loop():
    global porta_estava_aberta, porta_aberta_desde, alarme_porta
    global referencia_definida, temperatura_referencia, alarme_termico

    porta_fechada = not ler_botao_debounced()
    temperatura_atual = ler_temperatura(i2c)

    # Caso a porta esteja aberta 
    if not porta_fechada:
        # Contagem de tempo da porta aberta 
        if not porta_estava_aberta:
            porta_aberta_desde = utime.ticks_ms()
            porta_estava_aberta = True

        # Dispara o alarme se o tempo limite for ultrapassado
        elif (not alarme_porta and utime.ticks_diff(utime.ticks_ms(),porta_aberta_desde) >= LIMITE_TEMPO_X):
            alarme_porta = True
            print("ALERTA: Porta aberta por muito tempo!")

    else:
        porta_estava_aberta = False

        # Armazena uma temperatura de referencia
        if not referencia_definida:
            temperatura_referencia = temperatura_atual
            referencia_definida = True

    delta_t = 0.0

    # Calcula a variação de temperatura e dispara o alarme 
    if referencia_definida:
        delta_t = temperatura_atual - temperatura_referencia

        if not alarme_termico and delta_t >= LIMITE_VARIACAO_Y:
            alarme_termico = True
            print("ALERTA: Degradacao termica detectada!")

    temperatura_ok = (not referencia_definida or delta_t < LIMITE_VARIACAO_Y)

    # Cancela os alarmes no estado regular 
    if ((alarme_porta or alarme_termico) and porta_fechada and temperatura_ok):
        alarme_porta = False
        alarme_termico = False
        referencia_definida = False
        print("Status: Sistema Normalizado.")

    utime.sleep_ms(INTERVALO_AMOSTRAGEM)

# Inicialização dos periféricos 
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
i2c.writeto_mem(MPU6050_ADDR, REG_PWR_MGMT_1, bytes([0]))
botao = Pin(PINO_BOTAO, Pin.IN, Pin.PULL_UP)

print("Sistema de Monitoramento Inicializado")

while True:
    loop()