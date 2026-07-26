from machine import Pin, I2C
import utime

PINO_BOTAO = 4
MPU6050_ADDR = 0x68

REG_PWR_MGMT_1 = 0x6B
REG_TEMP_OUT_H = 0x41

LIMITE_TEMPO_X = 5000
LIMITE_VARIACAO_Y = 3.0

porta_estava_aberta = False
porta_aberta_desde = 0
alarme_porta = False

referencia_definida = False
temperatura_referencia = 0.0
alarme_termico = False
tempo_normalizacao = 0

def ler_temperatura(i2c):
    dados = i2c.readfrom_mem(MPU6050_ADDR, REG_TEMP_OUT_H, 2)
    bruto = (dados[0] << 8) | dados[1]

    if bruto >= 0x8000:
        bruto -= 0x10000

    return (bruto / 340.0) + 36.53


def setup():
    global i2c, botao

    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    i2c.writeto_mem(MPU6050_ADDR, REG_PWR_MGMT_1, bytes([0]))

    botao = Pin(PINO_BOTAO, Pin.IN, Pin.PULL_UP)

    print("Sistema de Monitoramento Inicializado")


def loop():
    global porta_estava_aberta, porta_aberta_desde, alarme_porta, tempo_normalizacao
    global referencia_definida, temperatura_referencia, alarme_termico

    estado_porta_fechada = not botao.value()
    temperatura_atual = ler_temperatura(i2c)

    if not estado_porta_fechada:
        if not porta_estava_aberta:
            porta_aberta_desde = utime.ticks_ms()
            porta_estava_aberta = True

        elif (
            not alarme_porta
            and utime.ticks_diff(
                utime.ticks_ms(),
                porta_aberta_desde
            ) >= LIMITE_TEMPO_X
        ):
            alarme_porta = True
            print("ALERTA: Porta aberta por muito tempo!")

    else:
        porta_estava_aberta = False

        if not referencia_definida:
            temperatura_referencia = temperatura_atual
            referencia_definida = True

    delta_t = 0.0

    if referencia_definida:
        delta_t = temperatura_atual - temperatura_referencia

        if not alarme_termico and delta_t >= LIMITE_VARIACAO_Y:
            alarme_termico = True
            print("ALERTA: Degradacao termica detectada!")

    temperatura_ok = (
        not referencia_definida
        or delta_t < LIMITE_VARIACAO_Y
    )

    if (
        (alarme_porta or alarme_termico)
        and estado_porta_fechada
        and temperatura_ok
    ):
        alarme_porta = False
        alarme_termico = False
        referencia_definida = False
        print("Status: Sistema Normalizado.")

    utime.sleep_ms(600)


setup()

while True:
    loop()