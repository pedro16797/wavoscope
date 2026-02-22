# 项目结构

本文档描述了 Wavoscope 代码库的目录结构及各组件的用途。

## 目录说明

-   **`audio/`**: 包含核心音频引擎。
    -   `audio_backend.py`: 主音频播放引擎，处理文件 I/O、速度控制和实时流。
    -   `chord_analyzer.py`: 用于和声标记的基于色度图的和弦检测。
    -   `ringbuffer.py`: 音频数据的无锁环形缓冲区实现。
    -   `spectrum_analyzer.py`: FFT 计算和频谱数据逻辑。
    -   `synth.py`: 用于节拍器点击音的简单合成器。
    -   `waveform_cache.py`: 管理波形数据的生成与缓存，实现高效可视化。
-   **`backend/`**: 基于 FastAPI 的现代 Web 后端。
    -   `main.py`: FastAPI 服务器入口点，提供 API 终端和前端资产。
    -   `state.py`: 全局共享状态（活跃的 `Project` 实例）。
    -   `routers/`: 用于不同 API 领域（音频、播放、项目等）的模块化 FastAPI 路由。
-   **`cli/`**: 包含命令行界面工具。
    -   `flag_cli.py`: 用于通过终端管理标记的工具。
-   **`config/`**: 应用程序的配置文件和默认设置。
-   **`docs/`**: 项目文档，包括路线图和结构指南。
-   **`frontend/`**: 基于 React 的图形用户界面。
    -   `src/components/`: React 组件（波形、频谱、时间轴、播放栏）。
    -   `src/store/`: 前端状态管理 (Zustand)。
    -   `dist/`: 编译后的生产资产。
-   **`resources/`**: 静态资产，如图标 (SVG)、主题 (JSON)、翻译 (JSON) 和应用程序资源。
-   **`scripts/`**: 自动化脚本和实用工具（例如截图生成）。
-   **`session/`**: 管理项目持久化和高级状态。
    -   `project.py`: 连接音频、元数据（标记）和缓存的 `Project` 类。
-   **`utils/`**: 通用辅助函数和共享工具。

## 根目录文件

-   **`run.sh` / `run.bat`**: 用于配置环境并启动应用程序的脚本。
-   **`main.py`**: 应用程序入口点。现在启动 FastAPI + pywebview。
-   **`AGENTS.md`**: 针对项目中工作的 AI 代理的指南和路线图。
-   **`Readme.md`**: 项目概述和设置说明。
-   **`LICENSE`**: 项目的 MIT 许可证条款。
-   **`SECURITY.md`**: 报告安全漏洞的政策。
-   **`requirements.txt`**: Python 依赖项。
