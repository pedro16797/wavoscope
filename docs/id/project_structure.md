# Struktur Proyek

Dokumen ini menguraikan struktur direktori dan tujuan dari setiap komponen dalam repositori Wavoscope.

## Ikhtisar Direktori

-   **`src/`**: Berisi logika aplikasi inti dan kode sumber.
    -   **`audio/`**: Berisi mesin audio inti.
        -   `audio_backend.py`: Fasad backend audio utama.
        -   `chord_analyzer.py`: Deteksi akord berbasis Chroma untuk bendera akord.
        -   `ringbuffer.py`: Buffer cincin yang aman untuk thread untuk streaming audio.
        -   `spectrum_analyzer.py`: Logika untuk menghitung FFT dan data spektral.
        -   `synth.py`: Sintesis real-time untuk klik metronom dan audisi akord.
        -   `waveform_cache.py`: Mengelola pembuatan dan caching data bentuk gelombang untuk tampilan yang efisien.
    -   **`backend/`**: Backend web modern berbasis FastAPI.
        -   `main.py`: Titik masuk untuk server FastAPI, melayani endpoint API dan aset frontend.
        -   `state.py`: Status global bersama (instans `Project` yang aktif).
        -   `routers/`: Router FastAPI modular untuk domain API yang berbeda (audio, pemutaran, proyek, dll.).
    -   **`cli/`**: Berisi utilitas antarmuka baris perintah.
        -   `flag_cli.py`: Utilitas untuk mengelola bendera melalui terminal.
        -   `gui.py`: Logika `pywebview` untuk antarmuka pengguna grafis.
        -   `launcher.py`: Logika pembantu untuk meluncurkan backend dan frontend.
    -   **`frontend/`**: Antarmuka pengguna grafis berbasis React.
        -   `src/components/`: Komponen React (Waveform, Spectrum, Timeline, PlaybackBar).
        -   `src/store/`: Manajemen status frontend (Zustand).
        -   `dist/`: Aset produksi yang dibangun.
        -   `tests/`: Tes unit untuk komponen frontend dan logika store.
    -   **`scripts/`**: Skrip otomatisasi dan utilitas (misalnya, pembuatan tangkapan layar, pembuatan peluncur).
    -   **`session/`**: Menangani persistensi proyek dan status tingkat tinggi.
        -   `project.py`: Kelas `Project` yang mengikat audio, metadata (bendera), dan caching menjadi satu.
        -   `manager.py`: Menangani I/O file sidecar `.oscope`.
        -   `flags.py`: Mengelola daftar bendera ritme dan akord.
        -   `undo.py`: Manajemen riwayat pembatalan berbasis delta.
    -   **`tests/`**: Tes unit dan integrasi untuk backend dan logika inti.
    -   **`utils/`**: Fungsi pembantu umum dan utilitas bersama (logging, konfigurasi, dll.).
    -   `main.py`: Titik masuk utama untuk aplikasi.
    -   `requirements.txt`: Dependensi Python.

-   **`config/`**: File konfigurasi dan pengaturan default untuk aplikasi.
-   **`docs/`**: Dokumentasi proyek, termasuk peta jalan tugas dan panduan struktur.
-   **`resources/`**: Aset statis seperti ikon (SVG), tema (JSON), dan sumber daya aplikasi.

## File Root

-   **`run.sh` / `run.bat`**: Skrip untuk mengatur lingkungan dan meluncurkan aplikasi.
-   **`Wavoscope` / `Wavoscope.exe`**: Peluncur yang dapat dieksekusi (dihasilkan oleh skrip).
-   **`AGENTS.md`**: Panduan dan peta jalan untuk agen AI yang bekerja pada proyek ini.
-   **`CONTRIBUTING.md`**: Panduan untuk berkontribusi pada proyek.
-   **`Readme.md`**: Ikhtisar proyek umum dan instruksi penyiapan.
-   **`LICENSE`**: Ketentuan lisensi MIT proyek.
-   **`SECURITY.md`**: Kebijakan untuk melaporkan kerentanan keamanan.
