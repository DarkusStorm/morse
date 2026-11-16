const int botao = 13;
const int led = 12;
const int piezo = 11;
const int botaoApagar = 10;
const int botaoEspaco = 9;

const unsigned long TEMPO_DEBOUNCE = 50;       
const unsigned long LIMITE_PONTO = 350;        
const unsigned long PAUSA_FIM_LETRA = 1000;    

// Estado Botão Morse
unsigned long tempoInicioPressao = 0;
unsigned long tempoInicioSoltura = 0;
bool estavaPressionado = false;
bool sequenciaAtiva = false;

// Estado Botão Apagar
bool estavaPressionadoApagar = false;
unsigned long tempoInicioPressaoApagar = 0;

// Estado Botão Espaço
bool estavaPressionadoEspaco = false;
unsigned long tempoInicioPressaoEspaco = 0;

String sequenciaMorse = "";

void setup() {
  Serial.begin(9600);
  pinMode(botao, INPUT);
  pinMode(led, OUTPUT);
  pinMode(piezo, OUTPUT);
  pinMode(botaoApagar, INPUT);
  pinMode(botaoEspaco, INPUT);
}

void loop() {
  int estadoAtual = digitalRead(botao);
  int estadoApagar = digitalRead(botaoApagar);
  int estadoEspaco = digitalRead(botaoEspaco);
  unsigned long tempoAtual = millis();

  // Botão de Apagar (PINO 10)
  if (estadoApagar == HIGH && !estavaPressionadoApagar) {
    tempoInicioPressaoApagar = tempoAtual;
    estavaPressionadoApagar = true;
  }

  if (estadoApagar == LOW && estavaPressionadoApagar) {
    unsigned long duracao = tempoAtual - tempoInicioPressaoApagar;
    estavaPressionadoApagar = false;

    if (duracao >= TEMPO_DEBOUNCE) {
      tone(piezo, 400, 150);
      if (sequenciaAtiva) {
        sequenciaMorse = "";
        sequenciaAtiva = false;
        Serial.println("Sinal parcial cancelado!");
      } else {
        Serial.println("[DEL]");
      }
    }
  }

  // Botão de Espaço
  if (estadoEspaco == HIGH && !estavaPressionadoEspaco) {
    tempoInicioPressaoEspaco = tempoAtual;
    estavaPressionadoEspaco = true;
  }

  if (estadoEspaco == LOW && estavaPressionadoEspaco) {
    unsigned long duracao = tempoAtual - tempoInicioPressaoEspaco;
    estavaPressionadoEspaco = false;

    if (duracao >= TEMPO_DEBOUNCE) {
      tone(piezo, 1200, 100);
      Serial.println("[SPACE]");
    }
  }

  // Botão Morse (PINO 13)
  if (estadoAtual == HIGH && !estavaPressionado) {
    tempoInicioPressao = tempoAtual;
    estavaPressionado = true;

    digitalWrite(led, HIGH);
    tone(piezo, 1000);
  }

  if (estadoAtual == LOW && estavaPressionado) {
    digitalWrite(led, LOW);
    noTone(piezo);

    unsigned long duracaoClique = tempoAtual - tempoInicioPressao;
    estavaPressionado = false;

    if (duracaoClique >= TEMPO_DEBOUNCE) {
      if (duracaoClique < LIMITE_PONTO) {
        sequenciaMorse += ".";
      } else {
        sequenciaMorse += "-";
      }
      tempoInicioSoltura = tempoAtual;
      sequenciaAtiva = true;

      Serial.print("Sinal parcial: ");
      Serial.println(sequenciaMorse);
    }
  }

  // -------------------------------------------------------------
  // 4. Fim de Caractere (Silêncio)
  // -------------------------------------------------------------
  if (sequenciaAtiva && !estavaPressionado) {
    if (tempoAtual - tempoInicioSoltura >= PAUSA_FIM_LETRA) {
      char letraTraduzida = traduzirMorse(sequenciaMorse);

      Serial.print("Sequencia: ");
      Serial.print(sequenciaMorse);
      Serial.print(" -> Letra: ");
      Serial.println(letraTraduzida);

      sequenciaMorse = "";
      sequenciaAtiva = false;
    }
  }
}

char traduzirMorse(String codigo) {
  if (codigo == ".-") return 'A';
  else if (codigo == "-...") return 'B';
  else if (codigo == "-.-.") return 'C';
  else if (codigo == "-..") return 'D';
  else if (codigo == ".") return 'E';
  else if (codigo == "..-.") return 'F';
  else if (codigo == "--.") return 'G';
  else if (codigo == "....") return 'H';
  else if (codigo == "..") return 'I';
  else if (codigo == ".---") return 'J';
  else if (codigo == "-.-") return 'K';
  else if (codigo == ".-..") return 'L';
  else if (codigo == "--") return 'M';
  else if (codigo == "-.") return 'N';
  else if (codigo == "---") return 'O';
  else if (codigo == ".--.") return 'P';
  else if (codigo == "--.-") return 'Q';
  else if (codigo == ".-.") return 'R';
  else if (codigo == "...") return 'S';
  else if (codigo == "-") return 'T';
  else if (codigo == "..-") return 'U';
  else if (codigo == "...-") return 'V';
  else if (codigo == ".--") return 'W';
  else if (codigo == "-..-") return 'X';
  else if (codigo == "-.--") return 'Y';
  else if (codigo == "--..") return 'Z';
  else if (codigo == "-----") return '0';
  else if (codigo == ".----") return '1';
  else if (codigo == "..---") return '2';
  else if (codigo == "...--") return '3';
  else if (codigo == "....-") return '4';
  else if (codigo == ".....") return '5';
  else if (codigo == "-....") return '6';
  else if (codigo == "--...") return '7';
  else if (codigo == "---..") return '8';
  else if (codigo == "----.") return '9';
  else if (codigo == ".-.-.-") return '.';
  else if (codigo == "--..--") return ',';
  else return '?';
}
