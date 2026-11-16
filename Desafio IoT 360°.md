“Desafio IoT 360°: Soluções Conectadas para a Indústria e a Sociedade” - Sistema de Comunicação por Código Morse:

GUIA DE INICIALIZAÇÃO DO PROJETO

Ordem de Inicialização dos Serviços

Siga os passos abaixo na Raspberry Pi para colocar toda a arquitetura em funcionamento:

Passo 1 - Broker Mosquitto (MQTT e WebSockets):
sudo systemctl restart mosquitto

Passo 2 - Gateway Serial (Arduino -> SQLite e MQTT):
Conecte o Arduino Uno a porta USB da Raspberry Pi e execute:
cd ~/projetos/morse
python3 leitor_serial.py

Passo 3 - API REST Back-End (Flask):
Em um segundo terminal SSH, inicie a API para disponibilizar o banco de dados via HTTP:
cd ~/projetos/morse
python3 api_banco.py

Passo 4 - Interface Web (Front-End):
Abra o arquivo index.html em qualquer navegador conectado a mesma rede local.

Como Visualizar e Testar a API REST
A. Via Terminal (Prompt de Comando ou Bash)
Para consultar a API e exibir a resposta JSON de forma organizada e legivel (identada), utilize o curl integrado com o formatador do Python:
curl -s http://192.168.137.138:5000/api/historico | python -m json.tool

B. Via Navegador Web (Direct API e Front-End)
Consulta Direta aos Dados em JSON: Acesse no navegador o endpoint completo: http://192.168.137.138:5000/api/historico (Acessar apenas a raiz / retornará erro 404 Not Found, pois o endpoint requer a rota inteira).

Visualização Formatada em Tabela: Abra o arquivo index.html no navegador. A aplicação consumira a API automaticamente, renderizando o histórico de requisições formatado com estilos carregados do styles.css.