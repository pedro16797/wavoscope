# Estrutura do proxecto

Este documento describe a estrutura de directorios e o propósito de cada compoñente no repositorio de Wavoscope.

## Descrición dos directorios

-   **`src/`**: Contén a lóxica central da aplicación e o código fonte.
    -   **`audio/`**: Contén o motor de audio principal.
        -   `audio_backend.py`: O motor principal de reprodución de audio, que xestiona a E/S de ficheiros, o control de velocidade e as transmisións en tempo real.
        -   `chord_analyzer.py`: Detección de acordes baseada en chroma para marcas de harmonía.
        -   `ringbuffer.py`: Implementación dun buffer circular sen bloqueos para datos de audio.
        -   `spectrum_analyzer.py`: Lóxica para o cálculo de FFT e datos espectrais.
        -   `synth.py`: Síntese sinxela para os clics do metrónomo.
        -   `waveform_cache.py`: Xestiona a xeración e o almacenamento en caché dos datos da forma de onda para unha visualización eficiente.
    -   **`backend/`**: O backend web moderno baseado en FastAPI.
        -   `main.py`: Punto de entrada para o servidor FastAPI, que serve os endpoints da API e os activos do frontend.
        -   `state.py`: Estado global compartido (a instancia activa do `Project`).
        -   `routers/`: Enrutadores modularizados de FastAPI para diferentes dominios da API (audio, reprodución, proxecto, etc.).
    -   **`cli/`**: Contén utilidades de interface de liña de comandos.
        -   `flag_cli.py`: Utilidades para xestionar marcas a través da terminal.
        -   `gui.py`: Lóxica `pywebview` para a interface gráfica de usuario.
        -   `launcher.py`: Lóxica de axuda para iniciar o backend e o frontend.
    -   **`frontend/`**: A interface gráfica de usuario baseada en React.
        -   `src/components/`: Compoñentes de React (Forma de onda, Espectro, Liña de tempo, Barra de reprodución).
        -   `src/store/`: Xestión do estado do frontend (Zustand).
        -   `dist/`: Activos de produción compilados.
        -   `tests/`: Probas unitarias para compoñentes do frontend e lóxica de store.
    -   **`scripts/`**: Scripts de automatización e utilidades (p. ex., xeración de capturas de pantalla, creación do lanzador).
    -   **`session/`**: Xestiona a persistencia do proxecto e o estado de alto nivel.
        -   `project.py`: A clase `Project` que vincula o audio, os metadatos (marcas) e a caché.
        -   `manager.py`: Xestiona a E/S de ficheiros sidecar `.oscope`.
        -   `flags.py`: Xestiona as listas de marcas de ritmo e acordes.
        -   `undo.py`: Xestión do historial de desuso baseada en deltas.
    -   **`tests/`**: Probas unitarias e integración para o backend e a lóxica central.
    -   **`utils/`**: Funcións de axuda xerais e utilidades compartidas (rexistro, configuración, etc.).
    -   `main.py`: O punto de entrada principal para a aplicación.
    -   `requirements.txt`: Dependencias de Python.

-   **`config/`**: Ficheiros de configuración e axustes predeterminados para a aplicación.
-   **`docs/`**: Documentación do proxecto, incluíndo plans de traballo e guías de estrutura.
-   **`resources/`**: Activos estáticos como iconas (SVG), temas (JSON), traducións (JSON) e recursos da aplicación.

## Ficheiros na raíz

-   **`run.sh` / `run.bat`**: Scripts para configurar o contorno e iniciar a aplicación.
-   **`Wavoscope` / `Wavoscope.exe`**: Executable do lanzador (xerado por scripts).
-   **`AGENTS.md`**: Guía e plan de traballo para os axentes de IA que traballan no proxecto.
-   **`CONTRIBUTING.md`**: Directrices para contribuír ao proxecto.
-   **`Readme.md`**: Descrición xeral do proxecto e instrucións de configuración.
-   **`LICENSE`**: Os termos da licenza MIT do proxecto.
-   **`SECURITY.md`**: Política para informar de vulnerabilidades de seguridade.
