# Projeto: WakePi
O projeto WakePi serve como um alarme inteligente para motoristas, detectando quando o motorista cai no sono através do fechar de seus olhos, para então acordá-lo e evitar acidentes.

## Componentes utilizados
- Raspberry Pi 3B
- Câmera do Raspberry Pi
- LED
- Buzzer

## Integrantes
Nome | RA | GitHub
------------ | ------------- | -------------
Felipe Andrade | 15.00175-0 | Kaisen-san
Matheus Mandotti | 16.00177-0 | matheusmf1
Vinícius Pereira | 16.03343-4 | VinPer

## Montagem

## Funcionamento do programa

### Detecção de face
Ao iniciar o programa, ele começa a captar imagens através da câmera. Utilizando a biblioteca OpenCV para Python, ele tenta detectar um rosto através do algoritmo pré-treinado de Haar Cascades. Se não identificado, o LED é apagado, indicando que há algum problema na detecção.

### Detecção de olhos
Se um rosto é detectado, o programa então tenta identificar os olhos, também utilizando um algoritmo pré-treinado de Haar Cascades. Se não identificado, o LED é apagado, indicando que há algum problema na detecção.

### Análise do estado do motorista
Após detectar os olhos, o programa realiza um cálculo sobre os níveis de preto e de branco na imagem para determinar se os olhos do motorista estão fechados, analisando a média de cinza em uma região reduzida do olho além da proporção de pixels brancos contra pixels pretos na mesma região.

Caso o valor passe do limite determinado, o motorista está com os olhos fechados. Nesse caso, uma contagem é incrementada, para evitar detectar quando o motorista apenas pisca. Se essa contagem é incrementada suficientemente, o buzzer é acionado e roda em loop até o motorista abrir os olhos novamente.

O programa repete todos os passos utilizando um pequeno delay entre cada execução por questões de performance.

## Imagens
![PiCase](https://raw.githubusercontent.com/Kaisen-san/wakepi/master/Imagens/piCase.jpg) | ![CameraCase](https://raw.githubusercontent.com/Kaisen-san/wakepi/master/Imagens/cameraCase.jpg)
------------ | ------------
Case Raspberry Pi | Case Câmera Raspberry Pi
![PiWithCase](https://raw.githubusercontent.com/Kaisen-san/wakepi/master/Imagens/piWithCase.jpg) | ![CameraWithCase](https://raw.githubusercontent.com/Kaisen-san/wakepi/master/Imagens/cameraWithCase.jpg)
Raspberry Pi com Case | Câmera com Case
