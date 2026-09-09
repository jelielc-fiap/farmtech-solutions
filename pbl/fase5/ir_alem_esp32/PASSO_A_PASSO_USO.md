# Passo a passo completo - ESP32 + sensores + FarmTech

Este guia considera que:

- o ESP32 já está conectado ao computador via USB;
- a Arduino IDE já está instalada;
- o DHT22 e o sensor resistivo de umidade do solo já estão montados;
- o objetivo é validar primeiro as leituras no Serial Monitor e depois enviar os dados por Wi-Fi para o sistema local da FarmTech.

## 1. Confirmar se o computador reconheceu o ESP32

1. Deixe o ESP32 plugado no USB.
2. Aguarde alguns segundos para o Windows reconhecer a placa.
3. Abra a **Arduino IDE**.
4. Vá em **Tools > Port**.
5. Veja se aparece uma porta serial, por exemplo:

```text
COM3
COM4
COM5
```

Se aparecer uma porta, selecione essa porta.

Se não aparecer nenhuma porta:

- troque o cabo USB, porque alguns cabos só carregam energia e não transmitem dados;
- teste outra porta USB do computador;
- confira no Gerenciador de Dispositivos do Windows se apareceu algum dispositivo USB Serial;
- se aparecer erro de driver, instale o driver compatível com o conversor USB da sua placa, normalmente CP210x ou CH340.

No diagnóstico deste computador, o Windows encontrou:

```text
CP2102 USB to UART Bridge Controller
Status: Error
Problem: CM_PROB_FAILED_INSTALL
```

Isso indica que sua placa usa conversor USB-serial **CP2102** e que o driver não foi instalado corretamente. Para resolver:

1. Baixe o driver oficial **CP210x Universal Windows Driver** no site da Silicon Labs:

```text
https://www.silabs.com/software-and-tools/usb-to-uart-bridge-vcp-drivers
```

2. Instale o driver.
3. Desconecte e conecte o ESP32 novamente.
4. Feche e abra a Arduino IDE.
5. Volte em **Tools > Port**.

Depois da instalação correta, a porta deve aparecer como `COM3`, `COM4`, `COM5` ou semelhante.

Só continue depois que a Arduino IDE mostrar uma porta `COM`.

No computador usado neste projeto, depois da instalação do driver CP210x, a porta reconhecida foi:

```text
Silicon Labs CP210x USB to UART Bridge (COM3)
```

## 2. Configurar a placa ESP32 na Arduino IDE

Na Arduino IDE:

1. Abra **Tools > Board**.
2. Selecione uma placa ESP32 compatível.
3. Se você não souber o modelo exato, use normalmente:

```text
ESP32 Dev Module
```

Se nenhuma placa ESP32 aparecer:

1. Vá em **Tools > Board > Boards Manager**.
2. Pesquise por:

```text
esp32
```

3. Instale o pacote:

```text
esp32 by Espressif Systems
```

4. Depois volte em **Tools > Board** e selecione `ESP32 Dev Module`.

## 3. Instalar as bibliotecas necessárias

Na Arduino IDE:

1. Abra **Tools > Manage Libraries** ou **Sketch > Include Library > Manage Libraries**.
2. Pesquise e instale:

```text
DHT sensor library
```

3. Pesquise e instale:

```text
Adafruit Unified Sensor
```

Essas bibliotecas são necessárias para ler o DHT22.

## 4. Abrir a sketch do projeto

Na Arduino IDE:

1. Vá em **File > Open**.
2. Abra este arquivo:

```text
C:\Users\jelie\Desktop\farmtech-solutions\pbl\fase5\ir_alem_esp32\arduino\farmtech_esp32_iot\farmtech_esp32_iot.ino
```

O arquivo também pode ser aberto com dois cliques pelo Windows Explorer.

## 5. Conferir a montagem antes de gravar

Com o ESP32 plugado, confira as conexões:

### DHT22

- ESP32 `3V3` no DHT22 pino 1;
- ESP32 `D27` no DHT22 pino 2;
- DHT22 pino 3 sem conexão;
- ESP32 `GND` no DHT22 pino 4;
- resistor de `10 kΩ` entre pino 1, VCC, e pino 2, DATA.

### Sensor de umidade do solo

- ESP32 `3V3` no `VCC` do módulo;
- ESP32 `GND` no `GND` do módulo;
- ESP32 `D34` no `AO` do módulo;
- `DO` do módulo sem conexão;
- sonda resistiva ligada nos bornes próprios do módulo.

## 6. Primeiro teste: validar sensores sem Wi-Fi

Na pasta da sketch, copie:

```text
config.example.h
```

e cole com o nome:

```text
config.h
```

No arquivo `config.h`, deixe assim:

```cpp
const bool ENABLE_WIFI_SEND = false;
```

Neste primeiro teste, não precisa preencher Wi-Fi ainda. O objetivo é só confirmar que o DHT22 e o sensor de solo estão lendo.

Clique em **Upload** na Arduino IDE.

Se durante o upload aparecer mensagem pedindo boot/manual reset:

1. mantenha pressionado o botão `BOOT` do ESP32;
2. clique em upload novamente ou aguarde o upload começar;
3. solte o botão `BOOT` quando a gravação iniciar.

Se aparecer este erro:

```text
A fatal error occurred: Failed to connect to ESP32: Wrong boot mode detected (0x13)!
The chip needs to be in download mode.
```

Isso não é erro do código, Wi-Fi, senha ou `SERVER_URL`. O ESP32 não entrou no modo de gravação.

Faça o procedimento manual:

1. Feche o Serial Monitor, se ele estiver aberto.
2. Na Arduino IDE, confirme `Tools > Port > COM3`.
3. Clique em **Upload**.
4. Quando o terminal mostrar `Connecting...`, mantenha pressionado o botão `BOOT`.
5. Se não avançar, ainda segurando `BOOT`, aperte e solte uma vez o botão `EN` ou `RST`.
6. Continue segurando `BOOT` até aparecer algo como `Writing at...`, `Chip is ESP32` ou início da porcentagem de gravação.
7. Solte o botão `BOOT`.

Se ainda falhar, desconecte e conecte o USB, feche e abra a Arduino IDE e tente novamente com o mesmo procedimento.

Um detalhe importante: o **Serial Monitor precisa estar fechado durante o upload**. Se ele estiver aberto, ele pode manter a porta serial ocupada ou confundir o processo. Use esta ordem:

1. Feche o Serial Monitor.
2. Clique em Upload.
3. Use o botão `BOOT` quando aparecer `Connecting...`.
4. Espere a gravação terminar.
5. Só então abra o Serial Monitor novamente.

Se o Serial Monitor mostrar apenas pontos (`. . . . .`), normalmente o ESP32 está executando um programa que tenta conectar no Wi-Fi. Isso não confirma que o upload novo funcionou. O upload só foi bem-sucedido quando a Arduino IDE mostrar algo como:

```text
Hard resetting via RTS pin...
```

ou concluir sem `Failed uploading`.

Depois do upload:

1. abra o **Serial Monitor**;
2. configure a velocidade para:

```text
115200 baud
```

Resultado esperado no Serial Monitor:

```text
FarmTech Solutions - ESP32 IoT
DHT22 no GPIO 27 e sensor de solo analogico no GPIO 34.
Temperatura do ar (C): ...
Umidade do ar (%): ...
Umidade do solo bruta: ...
Umidade do solo (%): ...
Payload: {...}
```

Se esses valores aparecerem, o hardware básico está funcionando.

Se aparecer `Falha ao ler o DHT22`:

- confira se o DATA está no `D27`;
- confira se o resistor de `10 kΩ` está entre VCC e DATA;
- confira se o DHT22 está alimentado em `3V3`;
- confira se o GND do DHT22 está no GND do ESP32.

Se a umidade do solo ficar sempre `0%`, com leitura bruta `4095`:

- isso significa que o ESP32 está lendo o valor máximo no pino analógico;
- o DHT22 está funcionando, então o problema fica isolado no sensor de solo, no fio `AO -> D34`, ou na calibração;
- confirme se o módulo do solo está alimentado em `3V3`, nunca em `5V`;
- confirme se o fio está na saída `AO`, não em `DO`;
- confirme se `AO` está ligado ao GPIO `D34`;
- confirme se o `GND` do módulo de solo está no mesmo `GND` do ESP32;
- coloque a sonda em solo úmido ou encoste os terminais da sonda em um pano úmido por alguns segundos e veja se o valor bruto cai;
- se continuar em `4095`, desconecte o fio que vem do `AO` e teste rapidamente o pino `D34`:
  - `D34` ligado ao `GND` deve ler próximo de `0`;
  - `D34` ligado ao `3V3` deve ler próximo de `4095`;
  - nunca ligue `D34` em `5V`.

Se `D34` responder nesse teste, o ESP32 está bom e o problema está no módulo, na sonda ou no fio `AO`.

Se a umidade do solo ficar sempre `0%` ou `100%`, mesmo mudando a umidade da sonda:

- confira se está usando a saída `AO`, não `DO`;
- confira se `AO` está no `D34`;
- gire o trimpot do módulo apenas se necessário;
- faça a calibração explicada no final deste guia.

## 7. Preparar o sistema local no computador

Agora que os sensores estão lendo, prepare o serviço local que receberá os dados.

Abra no Windows Explorer a pasta:

```text
C:\Users\jelie\Desktop\farmtech-solutions\pbl\fase5\ir_alem_esp32
```

Dê dois cliques em:

```text
run_all.bat
```

Esse arquivo deve abrir duas janelas:

- servidor HTTP local em `http://localhost:5000`;
- dashboard Streamlit em `http://localhost:8502`.

Na janela do `run_all.bat`, observe a URL exibida para o ESP32. Ela deve ser parecida com:

```cpp
const char* SERVER_URL = "http://192.168.18.202:5000/api/sensores";
```

Esse IP é do seu computador na rede. Ele será usado pelo ESP32.

Importante: não use `localhost` no ESP32. Para o ESP32, `localhost` significa o próprio ESP32, não o computador.

## 8. Testar o servidor local sem o ESP32

Com `run_all.bat` aberto, dê dois cliques em:

```text
run_api_test.bat
```

Resultado esperado:

```text
[OK] Health HTTP 200
[OK] POST HTTP 201
[OK] API, gravacao SQLite e leitura de retorno validadas.
```

Depois abra no navegador:

```text
http://localhost:5000
```

Você deve ver a página HTML simples com:

- cards de temperatura, umidade do ar, umidade do solo e risco;
- recomendação automática;
- gráfico;
- tabela de leituras.

Abra também:

```text
http://localhost:8502
```

Você deve ver o dashboard Streamlit com a leitura de teste.

## 9. Configurar Wi-Fi e URL do servidor na sketch

Volte para a Arduino IDE e edite estas linhas no arquivo `config.h`:

```cpp
const char* WIFI_SSID = "SUA_REDE_WIFI";
const char* WIFI_PASSWORD = "SUA_SENHA_WIFI";
const char* SERVER_URL = "http://192.168.0.100:5000/api/sensores";
```

Troque por dados reais.

Exemplo:

```cpp
const char* WIFI_SSID = "MinhaRedeWiFi";
const char* WIFI_PASSWORD = "MinhaSenhaDoWiFi";
const char* SERVER_URL = "http://192.168.18.202:5000/api/sensores";
```

Use o nome e a senha da rede Wi-Fi da sua casa.

O computador pode estar no cabo de rede, desde que esteja no mesmo roteador/rede local do Wi-Fi usado pelo ESP32.

Depois altere:

```cpp
const bool ENABLE_WIFI_SEND = true;
```

## 10. Gravar novamente o ESP32 com envio Wi-Fi

Na Arduino IDE:

1. confirme a placa em **Tools > Board**;
2. confirme a porta em **Tools > Port**;
3. clique em **Upload**;
4. abra o **Serial Monitor** em `115200 baud`.

Resultado esperado:

```text
Conectando ao Wi-Fi: ...
Wi-Fi conectado.
IP do ESP32: ...
Temperatura do ar (C): ...
Umidade do ar (%): ...
Umidade do solo bruta: ...
Umidade do solo (%): ...
Payload: {...}
HTTP status: 201
Resposta: {"id":...,"recommendation":...,"risk_level":...,"status":"ok"}
```

Se aparecer `HTTP status: 201`, o sistema completo está funcionando.

## 11. Ver os dados reais chegando

Com o ESP32 enviando dados, abra:

```text
http://localhost:5000/api/ultima
```

Resultado esperado:

- JSON da última leitura real;
- `device_id` igual a `esp32-farmtech-01`;
- temperatura do ar;
- umidade do ar;
- umidade do solo;
- recomendação automática.

Depois abra:

```text
http://localhost:5000
```

Essa página HTML deve atualizar automaticamente.

Abra também:

```text
http://localhost:8502
```

No dashboard Streamlit, confira:

- card de temperatura do ar;
- card de umidade do ar;
- card de umidade do solo;
- card de risco operacional;
- recomendação automática;
- gráfico histórico;
- tabela com registros recebidos do ESP32.

## 12. Se o ESP32 conecta no Wi-Fi, mas não envia

Confira:

- `run_all.bat` ou `run_receiver.bat` está aberto;
- `SERVER_URL` usa o IP do computador, não `localhost`;
- ESP32 e PC estão na mesma rede;
- o IP do PC não mudou;
- a URL termina com `/api/sensores`;
- o Firewall do Windows liberou o Python para rede privada.

Se o IP do PC mudar, rode:

```text
show_pc_ip.bat
```

Copie a nova URL para a sketch e grave novamente.

## 13. Calibrar o sensor de solo

No Serial Monitor, observe:

```text
Umidade do solo bruta: ...
```

Com a sonda seca, anote o valor bruto e coloque em:

```cpp
const int SOIL_DRY_RAW = 3200;
```

Com a sonda em solo bem úmido, anote o valor bruto e coloque em:

```cpp
const int SOIL_WET_RAW = 1200;
```

Depois faça upload novamente.

## 14. Ordem recomendada para apresentar em vídeo

1. Mostre o ESP32 conectado no USB e os sensores montados.
2. Mostre a Arduino IDE com a sketch aberta.
3. Aponte para `DHTPIN 27`, `SOIL_PIN 34`, `WIFI_SSID` e `SERVER_URL`.
4. Mostre o Serial Monitor com temperatura, umidade do ar e solo.
5. Mostre `HTTP status: 201`.
6. Abra `http://localhost:5000` e mostre a página recebendo dados.
7. Abra `http://localhost:8502` e mostre o dashboard.
8. Explique que o servidor grava as leituras em SQLite e gera recomendação automática.
