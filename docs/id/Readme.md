<p align="center">
  <img src="resources/icons/WavoscopeLogo.svg" alt="Wavoscope Logo" width="256">
</p>

# Wavoscope - Alat Analisis & Transkripsi Audio

Wavoscope adalah alat bantu visualisasi dan transkripsi audio rreal-time yang kuat, dirancang untuk musisi, transkriber, dan insinyur audio. Alat ini menyediakan bentuk gelombang dengan fidelitas tinggi, analisis spektral, dan sistem penanda yang kuat untuk membantu Anda mendekonstruksi audio yang kompleks.

![Antarmuka Utama](docs/images/main_view.png)

---

## 🚀 Memulai

### Menjalankan Wavoscope
Wavoscope dirancang untuk mandiri. Anda tidak perlu menginstal Python atau dependensi lainnya secara manual.
- **Windows:** Klik dua kali `run.bat`. Ini akan secara otomatis mengatur lingkungan dan membuat `Wavoscope.exe` di folder root untuk penggunaan di masa mendatang.
- **Linux/macOS:** Jalankan `bash run.sh` di terminal Anda. Ini akan membuat biner `Wavoscope` di folder root.

Pada peluncuran pertama, Wavoscope akan secara otomatis mengunduh runtime Python-nya sendiri dan mengatur lingkungan yang diperlukan. Ini mungkin memakan waktu beberapa menit tergantung pada koneksi internet Anda. Setelah dijalankan pertama kali, Anda cukup menggunakan executable `Wavoscope` yang dihasilkan (dengan ikon aplikasi).

### Manajemen Proyek & Simpan Otomatis
Wavoscope menggunakan sistem file "sidecar". Saat Anda membuka file audio, Wavoscope membuat atau memuat file `.oscope` di direktori yang sama untuk menyimpan penanda, loop, dan pengaturan Anda.
- **Buka:** Klik ikon folder di bilah pemutaran untuk memuat format audio umum apa pun (MP3, WAV, FLAC, dll.).
- **Simpan:** Klik ikon disket. Ikon akan menyala dengan warna aksen tema Anda jika ada perubahan yang belum disimpan.
- **Simpan Otomatis:** Wavoscope secara otomatis membuat snapshot dari pekerjaan Anda secara berkala. Anda dapat mengonfigurasi frekuensi simpan otomatis, jumlah maksimum snapshot yang akan disimpan, dan lokasi penyimpanan di tab **Pengaturan > Pemulihan**. Secara default, simpan otomatis hanya terjadi jika ada perubahan yang belum disimpan. Anda dapat mengaktifkan **Simpan Otomatis Paksa** untuk selalu membuat snapshot terlepas dari perubahan. Secara default, simpan otomatis disimpan di folder sementara sistem Anda.

---

## 🎵 Navigasi & Pemutaran

- **Zooming:** Gunakan **Roda Mouse** di atas bentuk gelombang atau spektrum untuk memperbesar/memperkecil.
- **Scrolling:** Gunakan **Roda Mouse** di atas **timeline** untuk menggulir waktu ke depan/belakang.
- **Panning:** **Klik dan Seret** bentuk gelombang atau spektrum untuk bergerak melalui timeline.
- **Subdivisi Adaptif:** Timeline secara otomatis menyesuaikan langkah gridnya (dari 0.01 detik hingga beberapa jam) saat Anda melakukan zoom, memastikan detail yang optimal tanpa terlihat terlalu padat.
- **Kursor Pemutaran:** **Klik Kiri** pada bentuk gelombang untuk memindahkan playhead.
- **Kontrol Kecepatan:** Gunakan slider di bilah bawah untuk menyesuaikan kecepatan dari 0.1x ke 2.0x. Wavoscope menggunakan perentangan waktu (time-stretching) berkualitas tinggi yang mempertahankan nada.
- **Volume & Overdrive:** Sesuaikan volume pemutaran keseluruhan dengan slider. Klik pada **ikon Volume** atau tekan `G` untuk mengalihkan **mode Overdrive**, yang memperluas rentang volume dari 100% hingga 400%. Aplikasi mengingat tingkat volume yang berbeda untuk mode normal dan overdrive.
- **Tempo & Tap Tempo:** Tempo saat ini (dalam BPM) ditampilkan di header waveform. Klik berulang kali untuk mengukur tempo secara manual (**Tap Tempo**). Secara otomatis akan kembali ke tempo birama yang dihitung setelah 3 detik tidak ada aktivitas.

---

## 🔍 Analisis Spektral & Pemfilteran

Setengah bagian bawah layar menampilkan spektrogram constant-Q transform (CQT), yang dipetakan ke piano roll. Anda dapat menyesuaikan **FFT Window** dan **Octave Shift** menggunakan kontrol di header penganalisis spektrum.

![Pemfilteran Spektral](docs/images/spectrum_filter.png)

### Pemfilteran Lanjut
Anda dapat mengisolasi instrumen atau nada tertentu menggunakan filter band-pass real-time. Pegangan filter (garis vertikal pada spektrum) selalu tersedia:
- **Alihkan Cutoff:** **Klik Kanan** pada pegangan filter untuk mengaktifkan atau menonaktifkan batas tersebut.
- **Penempatan Cepat:** **Klik Kanan** di mana saja pada spektrogram untuk memindahkan pegangan filter terdekat dan mengaktifkannya.
- **Umpan Balik Visual:** Saat cutoff diaktifkan, area di luar jangkauannya akan diredupkan untuk membantu Anda fokus. Jika keduanya dinonaktifkan, filter akan dilewati (bypass).

---

## 🚩 Penanda & Transkripsi

Wavoscope menggunakan sistem bendera ganda untuk membantu Anda memetakan struktur dan harmoni sebuah lagu.

### Bendera Ritme (Penanda Ritme/Birama)
- **Penempatan:** Tekan `B` (default) atau **Klik Kiri** pada timeline untuk meletakkan bendera ritme.
- **Subdivisi:** Buka dialog bendera (**Klik Kanan** pegangan bendera) untuk mengatur subdivisi (misalnya, 4 untuk nada seperempat). Ini muncul sebagai garis vertikal samar pada timeline.
- **Metronom:** Bendera ritme secara otomatis memicu klik metronom selama pemutaran jika klik subdivisi diaktifkan.
- **Shift-Klik:** Secara otomatis menempatkan bendera baru pada interval yang sama dengan bendera sebelumnya, sempurna untuk memetakan ketukan reguler dengan cepat.
- **Bagian:** Tandai bendera sebagai "Awal Bagian" untuk memberinya label (seperti "Verse" atau "Chorus").

![Dialog Bendera Ritme](docs/images/rhythm_dialog.png)

### Bendera Akord (Penanda Akord)
- **Penempatan:** Tekan `C` (default) atau **Klik Kanan** pada timeline untuk meletakkan bendera akord.
- **Editor Akord:** **Klik Kanan** bendera yang ada untuk membuka Dialog Akord. Anda dapat mengetik nama akord (misalnya, "Am7", "C/G") atau menggunakan pemilih.
- **Analisis Otomatis:** Gunakan tombol **Sarankan** agar Wavoscope menganalisis audio pada posisi tersebut dan merekomendasikan akord yang paling mungkin.
- **Mendengarkan:** **Tahan Klik Kiri** pada pegangan bendera akord atau klik tombol "Putar" di dialog untuk mendengar akord dimainkan melalui synthesizer internal.

![Dialog Bendera Akord](docs/images/harmony_dialog.png)

### Mengelola Bendera
- **Menyeret:** Anda dapat **Klik dan Seret** pegangan bendera apa pun di timeline untuk menyempurnakan posisinya.
- **Tumpang Tindih:** Saat bendera Ritme dan Akord menempati ruang yang sama, mereka ditampilkan dengan setengah tinggi (Akord di atas, Ritme di bawah) sehingga Anda tetap dapat berinteraksi dengan keduanya.
- **Looping:** Gunakan tombol Loop di bilah pemutaran untuk beralih di antara penanda atau seluruh trek.

---

## 🎤 Transkripsi Lirik

Wavoscope memiliki trek lirik interaktif yang memungkinkan transkripsi dan penyelarasan kecepatan tinggi.

![Transkripsi Lirik](docs/images/lyrics_track.png)

### Alur Kerja Transkripsi
1. **Alihkan Trek:** Klik tombol "Lirik" di header bentuk gelombang untuk menampilkan trek transkripsi.
2. **Tambah & Ketik:** Tekan `V` atau **Klik Sekali** pada tempat kosong di trek lirik untuk menambah kata.
3. **Entri Kecepatan Tinggi:** Saat mengetik di kotak lirik, tekan **Spasi** atau **Dash (`-`)**. Ini akan secara otomatis:
    - Menyelesaikan kata saat ini.
    - Membuat kotak lirik baru segera setelahnya (di playhead saat ini atau akhir sebelumnya).
    - Memindahkan fokus ke kotak baru sehingga Anda dapat terus mengetik tanpa menghentikan musik.
4. **Mencari:** Gunakan `Shift + Kiri/Kanan` / `Shift + A/D` untuk melompat antar elemen lirik. Ini sempurna untuk memverifikasi timing.

### Mengedit & Mengubah Ukuran
- **Gerakan:** **Seret** bagian tengah (80%) dari kotak lirik untuk memindahkannya.
- **Timing:** **Seret** bagian tepi (ambang batas 10%) dari kotak lirik untuk menyesuaikan waktu mulai atau berakhirnya.
- **Presisi:** Gunakan **Tombol Panah** saat lirik dipilih untuk menggesernya sebanyak 0.1 detik. Gunakan panah **Atas/Bawah** untuk menyesuaikan durasi.
- **Pemformatan:** Kotak lirik secara otomatis memudar dan menutupi teks saat menjadi terlalu kecil pada tingkat zoom rendah, menjaga antarmuka tetap bersih.

---

## ⚙️ Pengaturan & Kustomisasi

![Dialog Pengaturan](docs/images/settings_dialog.png)

Akses pengaturan melalui ikon gir di bilah pemutaran:
- **Tututs Piano Terlihat:** Sesuaikan berapa banyak tututs yang ditampilkan di piano roll spektrum.
- **Volume Klik:** Kontrol kenyaringan klik subdivisi metronom.

### Tema
Wavoscope sepenuhnya dapat diganti temanya. Pilih tampilan yang sesuai dengan lingkungan Anda:
- **Cosmic:** Ungu tua dan aksen nebular.
- **Dark:** Mode gelap klasik yang nyaman di mata.
- **Doll:** Merah muda berenergi tinggi dan nada ceria.
- **Hacker:** Hijau terminal retro di atas hitam.
- **Light:** Tampilan profesional yang bersih dan cerah.
- **Neon:** Biru elektrik dan semangat kontras tinggi.
- **OLED:** Latar belakang hitam murni untuk kontras maksimum.
- **Retrowave:** Estetika synthwave tahun 80-an.
- **Toy:** Warna primer yang berani.
- **Warm:** Nada bersahaja dan nyaman untuk sesi yang lama.

---

## 🌍 Lokalisasi

Wavoscope mendukung banyak bahasa. Anda dapat mengubah bahasa di tab **Pengaturan > Global**.

### Terjemahan Kustom
Wavoscope dirancang untuk digerakkan oleh komunitas. Anda dapat menambah atau mengubah terjemahan dengan mengedit file JSON di direktori `resources/locales`.
- Untuk menambah bahasa baru, buat file JSON baru (misalnya, `fr.json`) dan tambahkan bidang `"meta": { "name": "Français" }`.
- Aplikasi akan secara otomatis mendeteksi dan mencantumkan file terjemahan yang valid di menu pengaturan.

---

## ⌨️ Panduan Kontrol Komprehensif

### Pintasan Keyboard
| Tindakan | Tombol |
| :--- | :--- |
| **Putar / Jeda** | `Spasi` |
| **Hentikan Pemutaran** | `Shift + Spasi` |
| **Alihkan Metronom** | `M` |
| **Alihkan Pengaturan** | `Esc` |
| **Cari Maju/Mundur** | `Kiri` / `Kanan` / `A` / `D` |
| **Tambah/Kurangi Kecepatan** | `Atas` / `Bawah` / `W` / `S` |
| **Oktaf Naik/Turun** | `Shift + Kiri/Kanan` / `Shift + A/D` |
| **Ukuran Jendela FFT** | `Shift + Atas/Bawah` / `Shift + W/S` |
| **Tambah Bendera Ritme** | `B` |
| **Tambah Bendera Akord** | `C` |
| **Alihkan Low Cutoff** | `F` |
| **Alihkan High Cutoff** | `Shift + F` |
| **Tambah Bendera Lirik** | `V` |
| **Pisah & Majukan Lirik**| `Spasi` / `-` (Di Dalam Input) |
| **Siklus Mode Loop** | `Tab` |
| **Batalkan Pilihan** | `Shift + V` |
| **Cari di antara Lirik** | `Shift + Kiri/Kanan` / `Shift + A/D` |
| **Hapus Item Terpilih** | `Delete` / `Backspace` |
| **Buka File** | `Ctrl + O` |
| **Simpan Proyek** | `Ctrl + S` |
| **Ekspor MusicXML** | `Ctrl + E` |

### Interaksi Mouse
| Area | Tindakan | Interaksi |
| :--- | :--- | :--- |
| **Timeline** | Tambah Bendera Ritme | `Klik Kiri` |
| **Timeline** | Tempatkan Ritme Otomatis | `Shift + Klik Kiri` |
| **Timeline** | Tambah Bendera Akord | `Klik Kanan` |
| **Timeline** | Pindahkan Bendera | `Seret Kiri` |
| **Timeline** | Dengarkan Akord | `Tahan Klik Kiri` pada Bendera Akord |
| **Timeline** | Gulir Tampilan | `Roda Mouse` |
| **Waveform** | Pindahkan Playhead | `Klik Kiri` |
| **Waveform** | Geser Tampilan | `Seret Kiri` |
| **Waveform** | Zoom In/Out | `Roda Mouse` |
| **Spectrum** | Mainkan Nada Sine | `Klik / Seret Kiri` |
| **Spectrum** | Alihkan Cutoff | `Klik Kanan` pegangan |
| **Spectrum** | Tempatkan Cutoff | `Klik Kanan` di mana saja |
| **Spectrum** | Sesuaikan Cutoff | `Seret Kiri` pegangan |
