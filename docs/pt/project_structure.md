# Estrutura do Projeto

Este documento descreve a estrutura de diretórios e o propósito de cada componente no repositório do Wavoscope.

## Descrição dos Diretórios

-   **`audio/`**: Contém o motor de áudio principal.
    -   `audio_backend.py`: Motor principal de reprodução, lidando com E/S de arquivos, velocidade e streaming em tempo real.
    -   `chord_analyzer.py`: Detecção de acordes baseada em chroma para marcadores de harmonia.
    -   `ringbuffer.py`: Implementação de buffer circular sem bloqueio para dados de áudio.
    -   `spectrum_analyzer.py`: Lógica para cálculo de FFT e dados espectrais.
    -   `synth.py`: Síntese simples para os cliques do metrônomo.
    -   `waveform_cache.py`: Gerencia a geração e cache de dados da forma de onda para visualização eficiente.
-   **`backend/`**: Backend web moderno baseado em FastAPI.
    -   `main.py`: Ponto de entrada do servidor FastAPI, servindo endpoints da API e arquivos do frontend.
    -   `state.py`: Estado global compartilhado (instância ativa do `Project`).
    -   `routers/`: Rotas modularizadas do FastAPI para diferentes domínios da API (áudio, reprodução, projeto, etc.).
-   **`cli/`**: Contém utilitários de interface de linha de comando.
    -   `flag_cli.py`: Utilitários para gerenciar marcadores via terminal.
-   **`config/`**: Arquivos de configuração e padrões do aplicativo.
-   **`docs/`**: Documentação do projeto, incluindo roteiros e guias de estrutura.
-   **`frontend/`**: Interface gráfica baseada em React.
    -   `src/components/`: Componentes React (Forma de Onda, Espectro, Linha do Tempo, Barra de Reprodução).
    -   `src/store/`: Gerenciamento de estado do frontend (Zustand).
    -   `dist/`: Arquivos de produção compilados.
-   **`resources/`**: Arquivos estáticos como ícones (SVG), temas (JSON), traduções (JSON) e recursos do app.
-   **`scripts/`**: Scripts de automação e utilitários (ex: geração de capturas de tela).
-   **`session/`**: Gerencia a persistência do projeto e estado de alto nível.
    -   `project.py`: Classe `Project` que une o áudio, metadados (marcadores) e cache.
-   **`utils/`**: Funções auxiliares gerais e utilitários compartilhados.

## Arquivos na Raiz

-   **`run.sh` / `run.bat`**: Scripts para configurar o ambiente e iniciar o aplicativo.
-   **`main.py`**: Ponto de entrada do aplicativo. Inicia o FastAPI + pywebview.
-   **`AGENTS.md`**: Guia e roteiro para agentes de IA trabalhando no projeto.
-   **`Readme.md`**: Visão geral do projeto e instruções de configuração.
-   **`LICENSE`**: Termos da licença MIT do projeto.
-   **`SECURITY.md`**: Política para relatar vulnerabilidades de segurança.
-   **`requirements.txt`**: Dependências do Python.
