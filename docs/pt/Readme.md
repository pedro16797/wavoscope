<p align="center">
  <img src="resources/icons/WavoscopeLogo.svg" alt="Wavoscope Logo" width="256">
</p>

# Wavoscope - Ferramenta de Análise e Transcrição de Áudio

Wavoscope é uma ferramenta poderosa de visualização de áudio em tempo real e auxílio à transcrição, projetada para músicos, transcritores e engenheiros de áudio. Oferece formas de onda de alta fidelidade, análise espectral e um sistema robusto de marcadores para ajudar você a desconstruir áudios complexos.

![Interface Principal](docs/images/main_view.png)

---

## 🚀 Primeiros Passos

### Iniciando o Wavoscope
O Wavoscope foi projetado para ser independente. Você não precisa instalar o Python ou qualquer outra dependência manualmente.
- **Windows:** Clique duas vezes em `run.bat`. Isso configurará automaticamente o ambiente e criará um `Wavoscope.exe` na pasta raiz para uso futuro.
- **Linux/macOS:** Execute `bash run.sh` no seu terminal. Isso criará um binário `Wavoscope` na pasta raiz.

### Desenvolvimento e Testes
Se você estiver executando a partir do código fonte e quiser executar testes:
- **Testes do Backend:** `PYTHONPATH=src python3 -m pytest src/tests`
- **Testes do Frontend:** `cd src/frontend && npm test`

Na primeira inicialização, o Wavoscope baixará automaticamente seu próprio tempo de execução Python e configurará o ambiente necessário. Isso pode levar alguns minutos, dependendo da sua conexão com a Internet. Após a primeira execução, você pode simplesmente usar o executável `Wavoscope` gerado (com o ícone do aplicativo).

### Gerenciamento de Projetos e Salvamento Automático
O Wavoscope usa um sistema de arquivo "sidecar". Quando você abre um arquivo de áudio, o Wavoscope cria ou carrega um arquivo `.oscope` no mesmo diretório para armazenar seus marcadores, loops e configurações.
- **Abrir:** Clique no ícone de pasta na barra de reprodução para carregar qualquer formato de áudio comum (MP3, WAV, FLAC, etc.).
- **Salvar:** Clique no ícone de disquete. O ícone brilhará com a cor de destaque do seu tema quando houver alterações não salvas.
- **Salvamento automático:** O Wavoscope cria automaticamente instantâneos do seu trabalho em intervalos regulares. Você pode configurar a frequência do salvamento automático, o número máximo de instantâneos a serem mantidos e o local de armazenamento na guia **Configurações > Salvamento automático**. Por padrão, os salvamentos ocorrem apenas se houver alterações não salvas. Você pode habilitar o **Salvamento forçado** para sempre criar instantâneos independentemente das alterações. Por padrão, os salvamentos automáticos são armazenados na pasta temporária do seu sistema.

---

## 🎵 Navegação e Reprodução

- **Zoom:** Use a **roda do mouse** sobre a forma de onda ou o espectro para ampliar/reduzir.
- **Rolagem:** Use a **roda do mouse** sobre a **linha do tempo** para rolar para frente/trás no tempo.
- **Panorâmica:** **Clique e arraste** a forma de onda ou o espectro para se mover pela linha do tempo.
- **Subdivisões Adaptativas:** A linha do tempo ajusta automaticamente seus passos de grade (de 0,01s até várias horas) conforme você aplica o zoom, garantindo o nível ideal de detalhes sem poluição visual.
- **Cursor de Reprodução:** **Clique esquerdo** na forma de onda para mover o cursor.
- **Controle de Velocidade:** Use o controle deslizante na barra inferior para ajustar a velocidade de 0,1x a 2.0x. Wavoscope utiliza estiramento de tempo de alta qualidade que preserva a afinação (pitch).
- **Volume e Overdrive:** Ajuste o volume geral com o controle deslizante. Clique no **ícone de volume** ou pressione `G` para alternar o **modo Overdrive**, que estende o intervalo de volume de 100% para 400%. O aplicativo lembra níveis de volume independentes para os modos normal e overdrive.
- **Tempo e Tap Tempo:** O tempo atual (em BPM) é exibido no cabeçalho da forma de onda. Clique repetidamente para medir manualmente o tempo (**Tap Tempo**). Ele retorna automaticamente ao tempo calculado do compasso após 3 segundos de inatividade.
- **Controle Remoto:** Ative o **Acesso Remoto** nas configurações para controlar o Wavoscope a partir de outros dispositivos (como um telemóvel) na mesma rede local. As configurações exibirão um URL que pode inserir no navegador do seu dispositivo remoto para aceder à interface e controlar a reprodução.
    - **Interface Otimizada:** Dispositivos remotos recebem uma interface simplificada que oculta ferramentas complexas como o analisador de espectro e foca nos controles de reprodução.
    - **Suporte Táctil:** Navegação táctil completa é suportada, incluindo panorâmica e zoom (pinch-to-zoom) na forma de onda.
    - **Proteção do Host:** Para evitar edições acidentais, dispositivos remotos apenas podem controlar a reprodução e visualizar marcadores; a adição ou edição de sinalizadores e letras é restrita à máquina host.
    - *Nota: O acesso remoto não é autenticado; qualquer pessoa na sua rede local poderá controlar a aplicação.*

![Interface Remota](docs/images/remote_view.png)

---

## 🔍 Análise Espectral e Filtragem

A metade inferior da tela exibe um espectrograma de transformada Q constante (CQT), mapeado para um teclado de piano. Você pode ajustar a **janela FFT** e o **deslocamento de oitava** usando os controles no cabeçalho do analisador de espectro.

![Filtragem Espectral](docs/images/spectrum_filter.png)

### Filtragem Avançada
Você pode isolar instrumentos ou notas específicas usando o filtro passa-banda em tempo real. As alças do filtro (linhas verticais no espectro) estão sempre disponíveis:
- **Alternar Corte:** **Clique direito** em uma alça de filtro para ativar ou desativar esse limite.
- **Posicionamento Rápido:** **Clique direito** em qualquer lugar do espectrograma para mover a alça de filtro mais próxima e ativá-la.
- **Feedback Visual:** Quando um corte está ativado, a área fora do seu alcance é escurecida para ajudar você a se concentrar. Se ambos estiverem desativados, o filtro é ignorado.

---

## 🚩 Marcadores e Transcrição

Wavoscope utiliza um sistema de marcadores duplos para ajudar você a mapear a estrutura e a harmonia de uma faixa.

### Marcadores de Ritmo (Compassos/Batidas)
- **Posicionamento:** Pressione `B` (padrão) ou **clique esquerdo** na linha do tempo para inserir um marcador de ritmo.
- **Subdivisões:** Abra o diálogo do marcador (**clique direito** na alça) para definir subdivisões (ex: 4 para semínimas). Elas aparecem como linhas verticais suaves na linha do tempo.
- **Metrônomo:** Marcadores de ritmo acionam automaticamente um clique de metrônomo durante a reprodução se os cliques de subdivisão estiverem ativados.
- **Shift-Click:** Coloca automaticamente uma nova marca com o mesmo intervalo da anterior, ideal para mapear rapidamente um ritmo regular.
- **Seções:** Marque um marcador como "Início de Seção" para dar a ele um rótulo (como "Verso" ou "Refrão").

![Diálogo de Marcador de Ritmo](docs/images/rhythm_dialog.png)

### Marcadores de Harmonia (Acordes)
- **Posicionamento:** Pressione `C` (padrão) ou **clique direito** na linha do tempo para inserir um marcador de harmonia.
- **Editor de Acordes:** **Clique direito** em um marcador existente para abrir o diálogo de acordes. Você pode digitar nomes de acordes (ex: "Am7", "C/G") ou usar os seletores.
- **Análise Automática:** Use o botão **Sugerir** para deixar o Wavoscope analisar o áudio naquela posição e recomendar o acorde mais provável.
- **Audição:** **Mantenha o clique esquerdo** pressionado em uma alça de marcador de harmonia ou clique no botão "Play" no diálogo para ouvir o acorde através do sintetizador interno.

![Diálogo de Marcador de Harmonia](docs/images/harmony_dialog.png)

### Gerenciando Marcadores
- **Arrastar:** Você pode **clicar e arrastar** qualquer alça de marcador na linha do tempo para ajustar sua posição.
- **Sobreposições:** Quando um marcador de Ritmo e um de Harmonia ocupam o mesmo espaço, eles são exibidos em meia altura (Harmonia no topo, Ritmo na base) para que você possa interagir com ambos.
- **Loops:** Use o botão de Loop na barra de reprodução para alternar entre marcadores ou a faixa inteira.

---

## 🎤 Transcrição de Letras

Wavoscope possui uma trilha de letras interativa que permite transcrição e alinhamento em alta velocidade.

![Transcrição de Letras](docs/images/lyrics_track.png)

### Fluxo de Trabalho de Transcrição
1. **Alternar Trilha:** Clique no botão "Letras" no cabeçalho da forma de onda para exibir a trilha de transcrição.
2. **Adicionar e Digitar:** Pressione `V` ou dê um **clique único** em um espaço vazio na trilha para adicionar uma palavra.
3. **Entrada de Alta Velocidade:** Ao digitar em uma caixa de letra, pressione **Espaço** ou **Hífen (`-`)**. Isso irá automaticamente:
    - Confirmar a palavra atual.
    - Criar uma nova caixa de letra imediatamente após (na posição atual do cursor ou fim da anterior).
    - Mover o foco para a nova caixa para que você possa continuar digitando sem parar a música.
4. **Busca:** Use `Shift + Esquerda/Direita` para saltar entre os elementos da letra. Isso é perfeito para verificar o tempo.

### Edição e Redimensionamento
- **Movimento:** **Arraste** o centro (80%) de uma caixa de letra para movê-la.
- **Tempo:** **Arraste** as bordas (limite de 10%) de uma caixa de letra para ajustar seu início ou fim.
- **Precisão:** Use as **teclas de seta** quando uma letra estiver selecionada para movê-la em 0,1s. Use as setas **Cima/Baixo** para ajustar a duração.
- **Formatação:** Caixas de letra desaparecem gradualmente e ocultam o texto automaticamente quando ficam muito pequenas em níveis baixos de zoom, mantendo a interface limpa.

---

## ⚙️ Configurações e Personalização

![Diálogo de Configurações](docs/images/settings_dialog.png)

Acesse as configurações através do ícone de engrenagem na barra de reprodução:
- **Teclas de Piano Visíveis:** Ajuste quantas teclas são mostradas no teclado do espectro.
- **Volume do Clique:** Controle o volume das subdivisões do metrônomo.

### Temas
Wavoscope é totalmente personalizável com temas. Escolha um visual que combine com seu ambiente:
- **Cosmic:** Roxos profundos e detalhes nebulosos.
- **Dark:** Modo escuro clássico, confortável para os olhos.
- **Doll:** Rosas energéticos e tons divertidos.
- **Hacker:** Verde terminal retrô sobre preto.
- **Light:** Visual profissional limpo e de alto brilho.
- **Neon:** Azuis elétricos e vibração de alto contraste.
- **OLED:** Fundo preto puro para máximo contraste.
- **Retrowave:** Estética synthwave dos anos 80.
- **Toy:** Cores primárias vibrantes.
- **Warm:** Tons terrosos e confortáveis para longas sessões.


---

## 🌍 Localização

Wavoscope suporta vários idiomas. Você pode alterar o idioma na aba **Configurações > Global**.

### Traduções Personalizadas
Wavoscope foi projetado para ser impulsionado pela comunidade. Você pode adicionar ou modificar traduções editando os arquivos JSON no diretório `resources/locales`.
- Para adicionar um novo idioma, crie um novo arquivo JSON (ex: `fr.json`) e adicione um campo `"meta": { "name": "Français" }`.
- O aplicativo detectará e listará automaticamente qualquer arquivo de tradução válido no menu de configurações.

---

## ⌨️ Controles Completos

### Atalhos de Teclado
| Ação | Tecla |
| :--- | :--- |
| **Reproduzir / Pausar** | `Espaço` |
| **Parar reprodução** | `Shift + Espaço` |
| **Alternar Metrônomo** | `M` |
| **Alternar Configurações** | `Esc` |
| **Pular para Frente/Trás** | `Esquerda` / `Direita` / `A` / `D` |
| **Aumentar/Diminuir Velocidade** | `Cima` / `Baixo` / `W` / `S` |
| **Subir/Baixar oitava** | `Shift + Esquerda/Direita` |
| **Tamanho da janela FFT** | `Shift + Cima/Baixo` |
| **Adicionar Marcador Ritmo** | `B` |
| **Adicionar Marcador Harmonia** | `C` |
| **Alternar passa-baixas** | `F` |
| **Alternar passa-altas** | `Shift + F` |
| **Adicionar/Confirmar Letra** | `V` |
| **Dividir e Avançar Letra**| `Espaço` / `-` (Dentro da entrada) |
| **Ciclar Modos de Loop** | `Tab` |
| **Desmarcar Seleção** | `Shift + V` |
| **Pular entre Letras** | `Shift + Esquerda/Direita` |
| **Excluir Item Selecionado** | `Delete` / `Backspace` |
| **Abrir Arquivo** | `Ctrl + O` |
| **Salvar Projeto** | `Ctrl + S` |
| **Exportar MusicXML** | `Ctrl + E` |

### Interações com o Mouse
| Área | Ação | Interação |
| :--- | :--- | :--- |
| **Linha do Tempo** | Adicionar Marcador Ritmo | `Clique Esquerdo` |
| **Linha do Tempo** | Colocação Auto de Marcador de Ritmo | `Shift + Clique Esquerdo` |
| **Linha do Tempo** | Adicionar Marcador Harmonia | `Clique Direito` |
| **Linha do Tempo** | Mover Marcador | `Arrastar com Esquerdo` |
| **Linha do Tempo** | Ouvir Acorde | `Manter Clique Esquerdo` no marcador de harmonia |
| **Linha do Tempo** | Rolar a Vista | `Roda do Mouse` |
| **Forma de Onda** | Mover o Cursor | `Clique Esquerdo` |
| **Forma de Onda** | Mover a Vista | `Arrastar com Esquerdo` |
| **Forma de Onda** | Zoom | `Roda do Mouse` |
| **Espectro** | Tocar Tom Senoidal | `Clique / Arrastar com Esquerdo` |
| **Espectro** | Alternar Corte | `Clique Direito` na alça |
| **Espectro** | Posicionar Corte | `Clique Direito` em qualquer lugar |
| **Espectro** | Ajustar Corte | `Arrastar com Esquerdo` na alça |
