<p align="center">
  <img src="resources/icons/WavoscopeLogo.svg" alt="Wavoscope Logo" width="256">
</p>

# Wavoscope - Ferramenta de análise e transcrición de audio

Wavoscope é unha potente ferramenta de visualización de audio en tempo real e axuda á transcrición deseñada para músicos, transcriptores e enxeñeiros de audio. Proporciona formas de onda de alta fidelidade, análise espectral e un robusto sistema de marcas para axudarche a deconstruír audios complexos.

![Interface principal](docs/images/main_view.png)

---

## 🚀 Primeiros pasos

### Iniciar Wavoscope
Wavoscope está deseñado para ser autónomo. Non é necesario instalar Python nin ningunha outra dependencia manualmente.
- **Windows:** Fai dobre clic en `run.bat`. Isto configurará automaticamente o contorno e creará un arquivo `Wavoscope.exe` na carpeta raíz para o seu uso futuro.
- **Linux/macOS:** Executa `bash run.sh` na túa terminal. Isto creará un binario `Wavoscope` na carpeta raíz.

No primeiro inicio, Wavoscope descargará automaticamente o seu propio contorno de execución de Python e configurará o contorno necesario. Isto pode tardar uns minutos dependendo da túa conexión a Internet. Despois da primeira execución, podes usar simplemente o executable `Wavoscope` xerado (coa icona da aplicación).

### Xestión de proxectos e autogardado
Wavoscope utiliza un sistema de ficheiros "sidecar". Cando abres un ficheiro de audio, Wavoscope crea ou carga un ficheiro `.oscope` no mesmo directorio para gardar as túas marcas, bucles e axustes.
- **Abrir:** Fai clic na icona do cartafol na barra de reprodución para cargar calquera formato de audio común (MP3, WAV, FLAC, etc.).
- **Gardar:** Fai clic na icona do disquete. A icona brillará coa cor de acento do teu tema cando haxa cambios sen gardar.
- **Autogardado:** Wavoscope crea automaticamente capturas do teu traballo a intervalos regulares. Podes configurar a frecuencia do autogardado, o número máximo de capturas a conservar e a localización de almacenamento na pestana **Axustes > Autogardado**. Por defecto, os autogardados só ocorren se hai cambios sen gardar. Podes activar o **Autogardado forzado** para crear sempre capturas independentemente dos cambios. Por defecto, os autogardados almacénanse no cartafol temporal do teu sistema.

---

## 🎵 Navegación e reprodución

- **Zoom:** Usa a **roda do rato** sobre a forma de onda ou o espectro para ampliar ou reducir.
- **Desprazamento:** Usa a **roda do rato** sobre a **liña de tempo** para desprazarte cara atrás ou cara adiante no tempo.
- **Desprazamento lateral:** **Clica e arrastra** a forma de onda ou o espectro para moverte pola liña de tempo.
- **Subdivisións adaptativas:** A liña de tempo axusta automaticamente os seus pasos de grade (dende 0,01s ata varias horas) a medida que fas zoom, garantindo un nivel de detalle óptimo sen sobrecargar a vista.
- **Cursor de reprodución:** **Clic esquerdo** na forma de onda para mover o cursor de reprodución.
- **Control de velocidade:** Usa o desprazable na barra inferior para axustar a velocidade de 0,1x a 2.0x. Wavoscope utiliza un estiramento de tempo de alta calidade que preserva o ton.
- **Volume e Overdrive:** Axusta o volume xeral co deslizador. Fai clic na **icona de volume** ou preme `G` para alternar o **modo Overdrive**, que estende o rango de volume do 100% ao 400%. A aplicación lembra niveis de volume independentes para os modos normal e overdrive.
- **Tempo e Tap Tempo:** O tempo actual (en BPM) amósase na cabeceira da forma de onda. Fai clic repetidamente para medir o tempo manualmente (**Tap Tempo**). Volve automaticamente ao tempo calculado do compás tras 3 segundos de inactividade.
- **Control Remoto:** Activa o **Acceso Remoto** nos axustes para controlar Wavoscope desde outros dispositivos (como un teléfono móbil) na mesma rede local. Os axustes amosarán un URL que podes introducir no navegador do teu dispositivo remoto para acceder á interface e controlar a reprodución.
    - **Interface Optimizada:** Os dispositivos remotos reciben unha interface simplificada que oculta ferramentas complexas como o analizador de espectro e céntrase nos controis de reprodución.
    - **Soporte Táctil:** Soporte completo para navegación táctil, incluíndo desprazamento e zoom con pellizco na forma de onda.
    - **Protección do Host:** Para evitar edicións accidentais, os dispositivos remotos só poden controlar a reprodución e ver as marcas; a creación ou edición de marcas e letras está restrinxida ao equipo principal.
    - *Nota: O acceso remoto non require autenticación; calquera persoa na túa rede local poderá controlar a aplicación.*

![Interface Remota](docs/images/remote_view.png)

---

## 🔍 Análise espectral e filtrado

A metade inferior da pantalla mostra un espectrograma de transformada de Q constante (CQT), mapeado a un teclado de piano. Podes axustar a **ventá FFT** e o **desprazamento de oitava** usando os controis na cabeceira do analizador de espectro.

![Filtrado espectral](docs/images/spectrum_filter.png)

### Filtrado avanzado
Podes illar instrumentos ou notas específicas usando o filtro de banda en tempo real. Os controladores do filtro (liñas verticais no espectro) están sempre dispoñibles:
- **Alternar corte:** **Clic dereito** nun controlador de filtro para activar ou desactivar ese límite.
- **Colocación rápida:** **Clic dereito** en calquera lugar do espectrograma para mover o controlador de filtro máis próximo e activalo.
- **Resposta visual:** Cando un corte está activado, a área fóra do seu rango escurece para axudarche a concentrarte. Se ambos están desactivados, o filtro omítese.

---

## 🚩 Marcas e transcrición

Wavoscope utiliza un sistema de dobre marca para axudarche a mapear a estrutura e a harmonía dunha pista.

### Marcas de ritmo (Marcadores de ritmo/compás)
- **Colocación:** Preme `B` (por defecto) ou fai **clic esquerdo** na liña de tempo para colocar unha marca de ritmo.
- **Subdivisiones:** Abre o diálogo da marca (**clic dereito** no controlador da marca) para establecer subdivisións (p. ex., 4 para negras). Estas aparecen como liñas verticais tenues na liña de tempo.
- **Metrónomo:** As marcas de ritmo activan automaticamente un clic de metrónomo durante a reprodución se os clics de subdivisión están activados.
- **Shift-Click:** Coloca automaticamente unha nova marca ao mesmo intervalo que a anterior, ideal para mapear rapidamente un ritmo regular.
- **Seccións:** Marca unha marca como "Inicio de sección" para darlle unha etiqueta (como "Verso" ou "Estribillo").

![Diálogo de marca de ritmo](docs/images/rhythm_dialog.png)

### Marcas de harmonía (Marcadores de acordes)
- **Colocación:** Preme `C` (por defecto) ou fai **clic dereito** na liña de tempo para colocar unha marca de harmonía.
- **Editor de acordes:** **Clic dereito** nunha marca existente para abrir o diálogo de acordes. Podes escribir nomes de acordes (p. ex., "Am7", "C/G") ou usar os selectores.
- **Análise automática:** Usa o botón **Suxerir** para que Wavoscope analice o audio nesa posición e recomende o acorde máis probable.
- **Escoita:** **Mantén o clic esquerdo** nun controlador de marca de harmonía ou fai clic no botón "Reproducir" no diálogo para escoitar o acorde a través do sintetizador interno.

![Diálogo de marca de harmonía](docs/images/harmony_dialog.png)

### Xestión de marcas
- **Arrastrar:** Podes **clicar e arrastrar** calquera controlador de marca na liña de tempo para axustar a súa posición.
- **Solapamentos:** Cando unha marca de ritmo e outra de harmonía ocupan o mesmo espazo, móstranse a media altura (harmonía arriba, ritmo abaixo) para que poidas interactuar con ambas.
- **Bucles:** Usa o botón de bucle na barra de reprodución para alternar entre marcas ou toda a pista.

---

## 🎤 Transcrición de letras

Wavoscope inclúe unha pista de letras interactiva que permite unha transcrición e aliñamento de alta velocidade.

![Transcrición de letras](docs/images/lyrics_track.png)

### Fluxo de traballo de transcrición
1. **Alternar pista:** Fai clic no botón "Letras" na cabeceira da forma de onda para mostrar a pista de transcrición.
2. **Engadir e escribir:** Preme `V` ou fai un **só clic** nun espazo baleiro na pista de letras para engadir unha palabra.
3. **Entrada de alta velocidade:** Mentres escribes nunha caixa de letra, preme **Espazo** ou **Guión (`-`)**. Isto fará automaticamente o seguinte:
    - Confirma a palabra actual.
    - Crea unha nova caixa de letra inmediatamente despois (na posición actual do cursor ou onde rematou a anterior).
    - Move o foco á nova caixa para que poidas seguir escribindo sen detener a música.
4. **Busca:** Usa `Shift + Esquerda/Dereita` para saltar entre os elementos da letra. Isto é perfecto para verificar o tempo.

### Edición e redimensión
- **Movemento:** **Arrastra** o centro (80%) dunha caixa de letra para movela.
- **Tempo:** **Arrastra** os bordos (limiar do 10%) dunha caixa de letra para axustar o seu tempo de inicio ou fin.
- **Precisión:** Usa as **teclas de frecha** cando unha letra está seleccionada para movela en intervalos de 0,1s. Usa as frechas **Arriba/Abaixo** para axustar a duración.
- **Formato:** As caixas de letras desvanécese e ocultan o texto automaticamente cando se fan demasiado pequenas con niveis de zoom baixos, mantendo a interface limpa.

---

## ⚙️ Axustes e personalización

![Diálogo de axustes](docs/images/settings_dialog.png)

Accede aos axustes a través da icona da engrenaxe na barra de reprodución:
- **Teclas de piano visibles:** Axusta cantas teclas se mostran no teclado de piano do espectro.
- **Volume do clic:** Controla o volume das subdivisións do metrónomo.

### Temas
Wavoscope é totalmente personalizable con temas. Escolle o estilo que mellor se adapte ao teu contorno:
- **Cosmic:** Púrpuras profundos e acentos nebulares.
- **Dark:** Modo escuro clásico, cómodo para a vista.
- **Doll:** Rosas enerxéticos e tons divertidos.
- **Hacker:** Verde terminal retro sobre negro.
- **Light:** Estilo profesional limpo e de alto brillo.
- **Neon:** Azuis eléctricos e vibración de alto contraste.
- **OLED:** Fondo negro puro para o máximo contraste.
- **Retrowave:** Estética synthwave dos anos 80.
- **Toy:** Cores primarias rechamantes.
- **Warm:** Tons terra, cómodos para sesións longas.


---

## 🌍 Localización

Wavoscope soporta varios idiomas. Podes cambiar o idioma na pestana **Axustes > Global**.

### Traducións personalizadas
Wavoscope está deseñado para ser impulsado pola comunidade. Podes engadir ou modificar traducións editando os ficheiros JSON no directorio `resources/locales`.
- Para engadir un novo idioma, crea un novo ficheiro JSON (p. ex., `fr.json`) e engade un campo `"meta": { "name": "Français" }`.
- A aplicación detectará e listará automaticamente calquera ficheiro de tradución válido no menú de axustes.

---

## ⌨️ Controis completos

### Atallos de teclado
| Acción | Tecla |
| :--- | :--- |
| **Reproducir / Pausa** | `Espazo` |
| **Deter reprodución** | `Maiús + Espazo` |
| **Alternar metrónomo** | `M` |
| **Alternar axustes** | `Esc` |
| **Avanzar/Retroceder** | `Esquerda` / `Dereita` |
| **Aumentar/Diminuír velocidade** | `Arriba` / `Abaixo` |
| **Subir/Baixar oitava** | `Maiús + Esquerda/Dereita` |
| **Tamaño de ventá FFT** | `Maiús + Arriba/Abaixo` |
| **Engadir marca de ritmo** | `B` |
| **Engadir marca de harmonía** | `C` |
| **Alternar corte de baixos** | `F` |
| **Alternar corte de agudos** | `Maiús + F` |
| **Engadir/Confirmar letra** | `V` |
| **Dividir e avanzar letra**| `Espazo` / `-` (Dentro da entrada) |
| **Alternar modos de bucle** | `Tab` |
| **Deseleccionar selección** | `Shift + V` |
| **Saltar entre letras** | `Shift + Esquerda/Dereita` |
| **Eliminar elemento seleccionado** | `Suprimir` / `Retroceso` |
| **Abrir ficheiro** | `Ctrl + O` |
| **Gardar proxecto** | `Ctrl + S` |
| **Exportar MusicXML** | `Ctrl + E` |

### Interaccións co rato
| Área | Acción | Interacción |
| :--- | :--- | :--- |
| **Liña de tempo** | Engadir marca de ritmo | `Clic esquerdo` |
| **Liña de tempo** | Autocolocar marca de ritmo | `Shift + Clic esquerdo` |
| **Liña de tempo** | Engadir marca de harmonía | `Clic dereito` |
| **Liña de tempo** | Mover marca | `Arrastrar co esquerdo` |
| **Liña de tempo** | Escoitar acorde | **Manter clic esquerdo** na marca de harmonía |
| **Liña de tempo** | Desprazar vista | **Roda do rato** |
| **Forma de onda** | Mover cursor de reprodución | `Clic esquerdo` |
| **Forma de onda** | Mover vista | `Arrastrar co esquerdo` |
| **Forma de onda** | Zoom | **Roda do rato** |
| **Espectro** | Tocar ton senoidal | `Clic/Arrastrar co esquerdo` |
| **Espectro** | Alternar corte | `Clic dereito` no controlador |
| **Espectro** | Colocar corte | `Clic dereito` en calquera lugar |
| **Espectro** | Axustar corte | `Arrastrar co esquerdo` o controlador |
