# Struktur Proyek

Dokumen ini menguraikan struktur direktori dan tujuan dari setiap komponen dalam repositori Wavoscope.

## Ikhtisar Direktori

-   **`audio/`**: Berisi mesin audio inti.
    -   `audio_backend.py`: Fasad backend audio utama.
    -   `chord_analyzer.py`: Deteksi akord berbasis Chroma untuk bendera akord.
    -   `ringbuffer.py`: Buffer cincin yang aman untuk thread untuk streaming audio.
    -   `spectrum_analyzer.py`: Logika untuk menghitung FFT dan data spektral.
    -   `synth.py`: Sintesis real-time untuk klik metronom dan audisi akord.
    -   `waveform_cache.py`: Mengelola pembuatan dan caching data bentuk gelombang untuk tampilan yang efisien.
    -   **`engine/`**: Komponen pemrosesan audio tingkat rendah.
        -   `playback.py`: Logika pemutaran inti dan manajemen streaming.
        -   `processing.py`: Peregangan audio (TSM) dan manajemen buffer.
        -   `metronome.py`: Pengaturan waktu dan pembuatan klik metronom.
        -   `filters.py`: Pemfilteran biquad real-time (band-pass).
-   **`backend/`**: Backend web modern berbasis FastAPI.
    -   `main.py`: Titik masuk untuk server FastAPI, melayani endpoint API dan aset frontend.
    -   `state.py`: Status global bersama (instans `Project` yang aktif).
    -   `routers/`: Router FastAPI modular untuk domain API yang berbeda (audio, pemutaran, proyek, dll.).
-   **`cli/`**: Berisi utilitas antarmuka baris perintah.
    -   `flag_cli.py`: Utilitas untuk mengelola bendera melalui terminal.
-   **`config/`**: File konfigurasi dan pengaturan default untuk aplikasi.
-   **`docs/`**: Dokumentasi proyek, termasuk peta jalan tugas dan panduan struktur.
-   **`frontend/`**: Antarmuka pengguna grafis berbasis React.
    -   `src/components/`: Komponen React (Waveform, Spectrum, Timeline, PlaybackBar).
    -   `src/store/`: Manajemen status frontend (Zustand).
    -   `dist/`: Aset produksi yang dibangun.
-   **`resources/`**: Aset statis seperti ikon (SVG), tema (JSON), dan sumber daya aplikasi.
-   **`scripts/`**: Skrip otomatisasi dan utilitas (misalnya, pembuatan tangkapan layar).
-   **`session/`**: Menangani persistensi proyek dan status tingkat tinggi.
    -   `project.py`: Kelas `Project` yang mengikat audio, metadata (bendera), dan caching menjadi satu.
    -   `manager.py`: Menangani I/O file sidecar `.oscope` dan pembersihan data (scrubbing).
    -   `flags.py`: Mengelola daftar bendera ritme dan akord.
    -   `looping.py`: Logika untuk berbagai mode loop (semua, bagian, penanda, lirik).
    -   `export.py`: Pembuatan ekspor MusicXML.
    -   `chord_utils.py`: Pembantu untuk penguraian dan validasi nama akord.
-   **`utils/`**: Fungsi pembantu umum dan utilitas bersama.

## File Root

-   **`run.sh` / `run.bat`**: Skrip untuk mengatur lingkungan dan meluncurkan aplikasi.
-   **`main.py`**: Titik masuk untuk aplikasi. Sekarang meluncurkan FastAPI + pywebview.
-   **`AGENTS.md`**: Panduan dan peta jalan untuk agen AI yang bekerja pada proyek ini.
-   **`Readme.md`**: Ikhtisar proyek umum dan instruksi penyiapan.
-   **`LICENSE`**: Ketentuan lisensi MIT proyek.
-   **`SECURITY.md`**: Kebijakan untuk melaporkan kerentanan keamanan.
-   **`requirements.txt`**: Dependensi Python.
