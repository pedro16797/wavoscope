# Estructura del proyecto

Este documento describe la estructura de directorios y el propósito de cada componente en el repositorio de Wavoscope.

## Descripción de los directorios

-   **`audio/`**: Contiene el motor de audio principal.
    -   `audio_backend.py`: El motor principal de reproducción de audio, que gestiona la E/S de archivos, el control de velocidad y las transmisiones en tiempo real.
    -   `chord_analyzer.py`: Detección de acordes basada en chroma para marcas de armonía.
    -   `ringbuffer.py`: Implementación de un búfer circular sin bloqueos para datos de audio.
    -   `spectrum_analyzer.py`: Lógica para el cálculo de FFT y datos espectrales.
    -   `synth.py`: Síntesis sencilla para los clics del metrónomo.
    -   `waveform_cache.py`: Gestiona la generación y el almacenamiento en caché de los datos de la forma de onda para una visualización eficiente.
-   **`backend/`**: El backend web moderno basado en FastAPI.
    -   `main.py`: Punto de entrada para el servidor FastAPI, que sirve los endpoints de la API y los activos del frontend.
    -   `state.py`: Estado global compartido (la instancia activa del `Project`).
    -   `routers/`: Enrutadores modularizados de FastAPI para diferentes dominios de la API (audio, reproducción, proyecto, etc.).
-   **`cli/`**: Contiene utilidades de interfaz de línea de comandos.
    -   `flag_cli.py`: Utilidades para gestionar marcas a través de la terminal.
-   **`config/`**: Archivos de configuración y ajustes predeterminados para la aplicación.
-   **`docs/`**: Documentación del proyecto, incluyendo planes de trabajo y guías de estructura.
-   **`frontend/`**: La interfaz gráfica de usuario basada en React.
    -   `src/components/`: Componentes de React (Forma de onda, Espectro, Línea de tiempo, Barra de reproducción).
    -   `src/store/`: Gestión del estado del frontend (Zustand).
    -   `dist/`: Activos de producción compilados.
-   **`resources/`**: Activos estáticos como iconos (SVG), temas (JSON), traducciones (JSON) y recursos de la aplicación.
-   **`scripts/`**: Scripts de automatización y utilidades (p. ej., generación de capturas de pantalla).
-   **`session/`**: Gestiona la persistencia del proyecto y el estado de alto nivel.
    -   `project.py`: La clase `Project` que vincula el audio, los metadatos (marcas) y el caché.
-   **`utils/`**: Funciones de ayuda generales y utilidades compartidas.

## Archivos en la raíz

-   **`run.sh` / `run.bat`**: Scripts para configurar el entorno e iniciar la aplicación.
-   **`main.py`**: El punto de entrada para la aplicación. Ahora inicia FastAPI + pywebview.
-   **`AGENTS.md`**: Guía y plan de trabajo para los agentes de IA que trabajan en el proyecto.
-   **`Readme.md`**: Descripción general del proyecto e instrucciones de configuración.
-   **`LICENSE`**: Los términos de la licencia MIT del proyecto.
-   **`SECURITY.md`**: Política para informar de vulnerabilidades de seguridad.
-   **`requirements.txt`**: Dependencias de Python.
