# Transcrición e aliñamento de letras

Wavoscope ofrece unha pista de letras dedicada para a transcrición interactiva, o aliñamento a nivel de palabra e a exportación MusicXML. Esta función está deseñada para unha entrada rápida e un axuste preciso do tempo.

## Conceptos fundamentais

### A pista de letras
A pista de letras é unha pista especializada baseada en canvas situada enriba da forma de onda principal. Mostra os elementos da letra como caixas editables.
- **Visibilidade:** Alterna a pista usando o botón "Letras" na cabeceira da forma de onda.
- **Escalado:** A altura da pista é fixa (32px), pero o seu contido escálase co zoom e o desprazamento globais.
- **Selección:** Só se pode seleccionar unha letra á vez. Ao seleccionar unha letra, esta resáltase e actívanse atallos de teclado específicos.

### Fluxo de traballo de transcrición: "Escribir-Dividir-Avanzar"
A forma máis eficiente de transcribir unha canción é seguindo este fluxo de traballo:
1.  **Inicio:** Preme `L` ou fai clic nun espazo baleiro para crear a primeira letra na posición actual do cursor.
2.  **Escribir:** Introduce a primeira palabra.
3.  **Dividir:** Preme `Espazo` (para novas palabras) ou `-` (para sílabas dentro dunha palabra). Isto confirma o texto actual e crea inmediatamente unha nova caixa de letra.
4.  **Repetir:** O foco transfírese automaticamente á nova caixa, permitíndoche continuar transcribindo mentres a música soa.
5.  **Confirmar:** Preme `Enter` ou fai clic noutro lugar para finalizar a edición.

## Interacción e atallos

### Control do rato
- **Un só clic (espazo baleiro):** Engade unha nova letra nesa marca de tempo e entra no modo de edición.
- **Clic esquerdo (caixa existente):** Selecciona a letra.
- **Un só clic (caixa seleccionada):** Deselecciona a letra.
- **Arrastrar (centro 80%):** Move o elemento da letra ao longo da liña de tempo.
- **Arrastrar (bordos 10%):** Redimensiona a letra. Arrastrar o bordo esquerdo axusta o tempo de inicio; arrastrar o bordo dereito axusta a duración.
- **Dobre clic:** Entra no modo de edición para a letra premida.
- **Clic no fondo:** Deselecciona a letra actual.

### Atallos de teclado

| Tecla | Acción | Contexto |
|-------|--------|----------|
| `L` | Engadir / Confirmar e Avanzar | Global |
| `Shift + L` | Deseleccionar todo | Global |
| `Tab` | Alternar modos de bucle | Global |
| `Enter` | Iniciar/Finalizar edición | Seleccionado |
| `Escape` | Cancelar edición / Deseleccionar | Seleccionado |
| `Frechas (Esquerda/Dereita)` | Axustar posición (0.1s) | Seleccionado (Sen editar) |
| `Frechas (Arriba/Abaixo)` | Axustar duración (0.1s) | Seleccionado (Sen editar) |
| `Shift + Frechas` | Saltar entre letras | Global / Seleccionado |
| `Espazo` / `-` | Confirmar e xerar seguinte | Editando |

## Implementación técnica

### Frontend
- **`LyricsTimeline.tsx`**: Utiliza un sistema de xestión de estado baseado en referencias para manexar interaccións de alta frecuencia (arrastrar) localmente antes de confirmar no backend. Emprega un `ResizeObserver` para a renderización reactiva do canvas.
- **Xestión de estado**: Integrado en `projectSlice.ts`. As operacións CRUD están optimizadas para actualizar o estado local directamente dende as respostas do backend, minimizando as viaxes de ida e volta pola rede.
- **Visualización**: Dispón dun motor de renderización dinámico que xestiona o truncamento e o desvanecemento do texto para elementos pequenos.

### Backend
- **Estrutura de datos**: As letras almacénanse como unha lista ordenada de obxectos `{text, timestamp, duration}` no ficheiro `.oscope`.
- **Motor de bucles**: O `LoopingEngine` soporta un modo `lyric`, que establece automaticamente o rango do bucle á letra seleccionada actualmente.
- **Exportación MusicXML**: `session/export.py` divide os compases en segmentos en cada límite de letra e harmonía. Isto garante que as etiquetas `<lyric>` estean perfectamente aliñadas coa estrutura rítmica na partitura exportada.

## Consellos de aliñamento
- **Zoom alto:** Para o aliñamento a nivel de palabra, aumenta o zoom ata que poidas ver claramente os transitorios na forma de onda.
- **Bucles:** Usa o modo de bucle `lyric` (alterna con `Tab`) para repetir a palabra actual mentres axustas os seus puntos de inicio e fin.
- **Metrónomo:** Mantén os clics de subdivisión activados para garantir que as túas letras se aliñen coas marcas de pulso subxacentes (Marcas de Ritmo).
