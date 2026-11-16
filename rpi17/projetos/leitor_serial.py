import serial
import paho.mqtt.client as mqtt
import sqlite3
import json
import time

PORTA_SERIAL = '/dev/ttyACM0'
BAUD_RATE = 9600

BROKER_MQTT = "localhost"
PORTA_MQTT = 1883
TOPICO_MQTT = "morse/texto"

NOME_BANCO = "morse_db.db"

def inicializar_banco():
    conn = sqlite3.connect(NOME_BANCO)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historico_morse (
            id INTEGER PRIMARY KEY AUTOINCREMENT
            evento TEXT NOT NULL
            texto_resultado TEXT NOT NULL
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )    
    ''')
    conn.commit()
    conn.close()

def salvar_no_banco(evento, texto_resultado):
    try:
        conn = sqlite3.connect(NOME_BANCO)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO historico_morse (evento, texto_resultado)
            VALUES (?, ?)
        ''', (evento, texto_resultado))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[ERRO BD] Falha ao salvar no banco: {e}")

def conectar_mqtt():
    client = mqtt.Client(client_id="Gateway_Raspberry")
    try:
        client.connect(BROKER_MQTT, PORTA_MQTT, 60)
        client.loop_start()
        print("[MQTT] Conectado ao Broker com sucesso!")
        return client
    except Exception as e:
        print(f"[ERRO MQTT] Não foi possível conectar ao Broker: {e}")
        return None

# Execução
def main():
    inicializar_banco()
    cliente_mqtt = conectar_mqtt()

    try:
        ser = serial.Serial(PORTA_SERIAL, BAUD_RATE, timeout=1)
        ser.reset_input_buffer()
        print(f"[SERIAL] Conectado na porta {PORTA_SERIAL}!")
    except Exception as e:
        print(f"[ERRO SERIAL] Falha ao abrir porta serial: {e}")
        return

    texto_acumulado = ""

    print("\n--- GATEWAY OPERACIONAL (Aguardando dados...) ---\n")

    try:
        while True:
            if ser.in_waiting > 0:
                linha = ser.readline().decode('utf-8', errors='ignore').strip()

                if not linha:
                    continue

                evento_ocorreu = False
                tipo_evento = ""

                # Apagar último caractere ([DEL])
                if linha == "[DEL]":
                    if len(texto_acumulado) > 0:
                        texto_acumulado = texto_acumulado[:-1]
                        tipo_evento = "DELETAR"
                        evento_ocorreu = True
                        print("\n[AÇÃO] Caractere apagado.")

                # Adicionar espaço ([SPACE])
                elif linha == "[SPACE]":
                    texto_acumulado += " "
                    tipo_evento = "ESPAÇO"
                    evento_ocorreu = True
                    print("\n[AÇÃO] Espaço adicionado.")

                # Adicionar letra traduzida
                elif "-> Letra: " in linha:
                    partes = linha.split("-> Letra: ")
                    if len(partes) > 1:
                        letra = partes[1].strip()
                        texto_acumulado += letra
                        tipo_evento = f"INSERIR ({letra})"
                        evento_ocorreu = True
                        print(f"\n[AÇÃO] Letra inserida: {letra}")

                if evento_ocorreu:
                    print(f"Texto Atual: '{texto_acumulado}'")

                    # "Carga útil", o conteúdo real da mensagem
                    payload = {
                        "texto_completo": texto_acumulado,
                        "ultimo_evento": tipo_evento,
                        "timestamp": int(time.time())
                    }

                    if cliente_mqtt:
                        cliente_mqtt.publish(TOPICO_MQTT, json.dumps(payload))
                        print(f"[MQTT] Publicado em '{TOPICO_MQTT}': {payload}")

                    salvar_no_banco(tipo_evento, texto_acumulado)

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\n[SISTEMA] Encerrando Gateway...")
    finally:
        ser.close()
        if cliente_mqtt:
            cliente_mqtt.loop_stop()
            cliente_mqtt.disconnect()
        print("[SISTEMA] Conexões fechadas.")

if __name__ == "__main__":
    main()