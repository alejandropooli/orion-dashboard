#!/usr/bin/python3
# Registro independiente de pluviómetro 3D-PAWS
# Basado en rain.py del proyecto 3D-PAWS
#
# Cada vez que se inicia el programa crea un archivo nuevo:
# /registros/rain1.txt
# /registros/rain2.txt
# /registros/rain3.txt
# ...
#
# Uso de ejemplo:
# sudo python3 rain_registro.py 5

import sys
import os
import time
from datetime import datetime

# Ruta actual del proyecto 3D-PAWS
sys.path.insert(0, '/home/raspismn/Desktop/3D-PAWS-adaptado/scripts/')

import RPi.GPIO as GPIO
import helper_functions


# -------------------------------------------------
# Configuración
# -------------------------------------------------

# Intervalo de lectura según el argumento pasado al programa
test, rest, iterations = helper_functions.getTest()

# Acumulación de lluvia por vuelco del balancín (mm)
CALIBRATION = 0.2

# GPIO del pluviómetro
PIN = 23

# Carpeta de registros
REG_DIR = "/registros"


# -------------------------------------------------
# Crear archivo de registro nuevo
# -------------------------------------------------

os.makedirs(REG_DIR, exist_ok=True)

n = 1
while os.path.exists(os.path.join(REG_DIR, f"rain{n}.txt")):
    n += 1

rain_file = os.path.join(REG_DIR, f"rain{n}.txt")


# -------------------------------------------------
# Configuración GPIO
# -------------------------------------------------

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Variable que acumula la lluvia
rain = 0.0


# -------------------------------------------------
# Callback: se ejecuta en cada vuelco
# -------------------------------------------------

def tipped(channel):
    global rain
    rain += CALIBRATION


GPIO.add_event_detect(
    PIN,
    GPIO.FALLING,
    callback=tipped,
    bouncetime=300
)


# -------------------------------------------------
# Inicio
# -------------------------------------------------

print("Rain (tipping bucket) Sensor")
print("Archivo de registro:", rain_file)
print("Intervalo de lectura:", rest, "segundos")


try:
    for x in range(iterations):

        time.sleep(rest)

        # Valor acumulado durante el intervalo
        line = "%.2f" % rain

        # Fecha y hora local
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Mostrar en pantalla
        print(timestamp, line)

        # Guardar en archivo
        with open(rain_file, "a") as f:
            f.write(f"{timestamp} {line}\n")

        # En modo test, reiniciar el acumulador en cada intervalo
        if test:
            rain = 0.0
        else:
            break

except KeyboardInterrupt:
    print("\nPrograma detenido por el usuario.")

except Exception as e:
    helper_functions.handleError(e, "rain")

finally:
    GPIO.cleanup()
    print("GPIO liberado.")
    print("Registro guardado en:", rain_file)
