# Transcripción y alineación de letras

Wavoscope proporciona una pista de letras dedicada para la transcripción interactiva, la alineación a nivel de palabra y la exportación MusicXML. Esta función está diseñada para una entrada rápida y un ajuste preciso del tiempo.

## Conceptos fundamentales

### La pista de letras
La pista de letras es una pista especializada basada en canvas situada sobre la forma de onda principal. Muestra los elementos de la letra como cajas editables.
- **Visibilidad:** Alterna la pista usando el botón "Letras" en la cabecera de la forma de onda.
- **Escalado:** La altura de la pista es fija (32px), pero su contenido se escala con el zoom y el desplazamiento globales.
- **Selección:** Solo se puede seleccionar una letra a la vez. Al seleccionar una letra, esta se resalta y se activan atajos de teclado específicos.

### Flujo de trabajo de transcripción: "Escribir-Dividir-Avanzar"
La forma más eficiente de transcribir una canción es siguiendo este flujo de trabajo:
1.  **Inicio:** Presiona `V` o haz clic en un espacio vacío para crear la primera letra en la posición actual del cursor.
2.  **Escribir:** Introduce la primera palabra.
3.  **Dividir:** Presiona `Espacio` (para nuevas palabras) o `-` (para sílabas dentro de una palabra). Esto confirma el texto actual y crea inmediatamente una nueva caja de letra.
    - **Diferenciación visual:** Las palabras divididas por guiones (sílabas) se conectan visualmente mediante una línea horizontal en la línea de tiempo. El guion en sí se almacena en los datos pero se oculta en la interfaz de usuario cuando no se está editando, proporcionando un aspecto limpio.
4.  **Repetir:** El foco se transfiere automáticamente a la nueva caja, permitiéndote continuar transcribiendo mientras la música suena.
5.  **Confirmar:** Presiona `Enter` o haz clic en otro lugar para finalizar la edición.

## Interacción y atajos

### Control del ratón
- **Un solo clic (espacio vacío):** Añade una nueva letra en esa marca de tiempo y entra en el modo de edición.
- **Clic izquierdo (caja existente):** Selecciona la letra.
- **Un solo clic (caja seleccionada):** Deselecciona la letra.
- **Arrastrar (centro 80%):** Mueve el elemento de la letra a lo largo de la línea de tiempo.
- **Arrastrar (bordos 10%):** Redimensiona la letra. Arrastrar el borde izquierdo ajusta el tiempo de inicio; arrastrar el borde derecho ajusta la duración.
- **Doble clic:** Entra en el modo de edición para la letra pulsada.
- **Clic en el fondo:** Deselecciona la letra actual.

### Atajos de teclado

| Tecla | Acción | Contexto |
|-------|--------|----------|
| `V` | Añadir / Confirmar y Avanzar | Global |
| `Shift + V` | Deseleccionar todo | Global |
| `Tab` | Alternar modos de bucle | Global |
| `Enter` | Iniciar/Finalizar edición | Seleccionado |
| `Escape` | Cancelar edición / Deseleccionar | Seleccionado |
| `Flechas (Izquierda/Derecha)` | Ajustar posición (0.1s) | Seleccionado (Sin editar) |
| `Flechas (Arriba/Abaixo)` | Ajustar duración (0.1s) | Seleccionado (Sin editar) |
| `Shift + Flechas` | Saltar entre letras | Global / Seleccionado |
| `Espacio` / `-` | Confirmar y generar siguiente | Editando |

## Implementación técnica

### Frontend
- **`LyricsTimeline.tsx`**: Utiliza un sistema de gestión de estado basado en referencias para manejar interacciones de alta frecuencia (arrastrar) localmente antes de confirmar en el backend. Emplega un `ResizeObserver` para la renderización reactiva del canvas.
- **Gestión de estado**: Integrado en `projectSlice.ts`. Las operaciones CRUD están optimizadas para actualizar el estado local directamente desde las respuestas del backend, minimizando los viajes de ida y vuelta por la red.
- **Visualización**: Cuenta con un motor de renderización dinámico que gestiona el truncamiento y el desvanecimiento del texto para elementos pequeños.

### Backend
- **Estructura de datos**: Las letras se almacenan como una lista ordenada de objetos `{text, timestamp, duration}` en el archivo `.oscope`.
- **Motor de bucles**: El `LoopingEngine` soporta un modo `lyric`, que establece automáticamente el rango del bucle a la letra seleccionada actualmente.
- **Exportación MusicXML**: `session/export.py` divide los compases en segmentos en cada límite de letra y armonía. Esto garantiza que las etiquetas `<lyric>` estén perfectamente alineadas con la estructura rítmica en la partitura exportada.

## Consejos de alineación
- **Zoom alto:** Para la alineación a nivel de palabra, aumenta el zoom hasta que puedas ver claramente los transitorios en la forma de onda.
- **Bucles:** Usa el modo de bucle `lyric` (alterna con `Tab`) para repetir la palabra actual mientras ajustas sus puntos de inicio y fin.
- **Metrónomo:** Mantén los clics de subdivisión activados para garantizar que tus letras se alineen con las marcas de pulso subyacentes (Marcas de Ritmo).
