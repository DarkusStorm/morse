from flask import Flask, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)
# CORS (Cross-Origin Resource Sharing/Compartilhamento de Recursos entre Origens Diferentes, "CROD") é um mecanismo dos navegadores para controlar navegações para servidores localizados em endereços diferentes. Por padrão, requisições feitas por JavaScript (ex: fetch) não podem ler dados de um servidor de outra origem para evitar roubos de dados armazenados em APIs de outros domínios. CORS(app) injeta automaticamente "Acess-Control-Allow-Origin: *" em respostas HTTP;

# Localiza o caminho onde o script está salvo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOME_BANCO = os.path.join(BASE_DIR, "morse_db.db")

def inicializar_banco():
    conn = sqlite3.connect(NOME_BANCO)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historico_morse (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            evento TEXT NOT NULL,
            texto_resultado TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/api/historico', methods=['GET'])
def obter_historico():
    try:
        conn = sqlite3.connect(NOME_BANCO)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, evento, texto_resultado, timestamp 
            FROM historico_morse 
            ORDER BY id DESC 
            LIMIT 30
        ''')
        linhas = cursor.fetchall()
        conn.close()

        historico = [
            {
                "id": r[0],
                "evento": r[1],
                "texto_resultado": r[2],
                "timestamp": r[3]
            }
            for r in linhas
        ]

        return jsonify({"status": "sucesso", "dados": historico}), 200

    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route('/api/ultima-mensagem', methods=['GET'])
def obter_ultima_mensagem():
    try:
        conn = sqlite3.connect(NOME_BANCO)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT texto_resultado, timestamp 
            FROM historico_morse 
            ORDER BY id DESC 
            LIMIT 1
        ''')
        resultado = cursor.fetchone()
        conn.close()

        if resultado:
            return jsonify({
                "status": "sucesso", 
                "texto": resultado[0], 
                "timestamp": resultado[1]
            }), 200
        else:
            return jsonify({"status": "sucesso", "texto": "", "timestamp": None}), 200

    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

if __name__ == '__main__':
    inicializar_banco()
    app.run(host='0.0.0.0', port=5000, debug=False)