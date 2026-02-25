# Transkripsi & Penyelarasan Lirik

Wavoscope menyediakan trek lirik khusus untuk transkripsi interaktif, penyelarasan tingkat kata, dan ekspor MusicXML. Fitur ini dirancang untuk entri cepat dan penyesuaian timing yang tepat.

## Konsep Inti

### Trek Lirik
Trek lirik adalah trek berbasis kanvas khusus yang terletak di atas bentuk gelombang utama. Trek ini menampilkan elemen lirik sebagai kotak yang dapat diedit.
- **Visibilitas:** Alihkan trek menggunakan tombol "Lyrics" di header bentuk gelombang.
- **Penskalaan:** Tinggi trek tetap (32px), tetapi isinya diskalakan dengan zoom dan offset global.
- **Seleksi:** Hanya satu lirik yang dapat dipilih dalam satu waktu. Memilih lirik akan menyorotnya dan mengaktifkan pintasan keyboard tertentu.

### Alur Kerja Transkripsi: "Ketik-Pisah-Maju"
Cara paling efisien untuk mentranskripsi lagu adalah menggunakan alur kerja berikut:
1.  **Mulai:** Tekan `V` atau klik tempat kosong untuk membuat lirik pertama di playhead saat ini.
2.  **Ketik:** Masukkan kata pertama.
3.  **Pisah:** Tekan **Spasi** (untuk kata baru) atau **Strip** (`-`, untuk suku kata dalam satu kata). Ini akan menyelesaikan teks saat ini dan segera memunculkan kotak lirik baru.
    - **Diferensiasi Visual:** Kata-kata yang dipisahkan oleh tanda hubung (suku kata) dihubungkan secara visual oleh garis horizontal di timeline. Tanda hubung itu sendiri disimpan dalam data tetapi disembunyikan di UI saat tidak mengedit, memberikan tampilan yang bersih.
4.  **Ulangi:** Fokus secara otomatis dipindahkan ke kotak baru, memungkinkan Anda untuk terus mentranskripsi saat musik diputar.
5.  **Selesaikan:** Tekan `Enter` atau klik di tempat lain untuk selesai mengedit.

## Interaksi & Pintasan

### Kontrol Mouse
- **Klik Sekali (Ruang Kosong):** Menambahkan lirik baru pada stempel waktu tersebut dan masuk ke mode edit.
- **Klik Kiri (Kotak yang Ada):** Memilih lirik.
- **Klik Sekali (Kotak yang Dipilih):** Membatalkan pilihan lirik.
- **Seret (Tengah 80%):** Memindahkan elemen lirik di sepanjang timeline.
- **Seret (Tepi 10%):** Mengubah ukuran lirik. Menyeret tepi kiri menyesuaikan waktu mulai; menyeret tepi kanan menyesuaikan durasi.
- **Klik Dua Kali:** Masuk ke mode edit untuk lirik yang diklik.
- **Klik Latar Belakang:** Membatalkan pilihan lirik saat ini.

### Pintasan Keyboard

| Tombol | Tindakan | Konteks |
|-----|--------|---------|
| `V` | Tambah / Selesaikan & Maju | Global |
| `Shift + V` | Batalkan Pilihan Semua | Global |
| `Tab` | Siklus Mode Loop | Global |
| `Enter` | Mulai/Selesai Mengedit | Terpilih |
| `Escape` | Batalkan Pengeditan / Batalkan Pilihan | Terpilih |
| `Panah / `A` / `D`` | Geser Posisi (0.1 detik) | Terpilih (Tidak mengedit) |
| `Panah / `W` / `S`` | Sesuaikan Durasi (0.1 detik) | Terpilih (Tidak mengedit) |
| `Shift + Panah` | Cari di antara Lirik | Global / Terpilih |
| `Spasi / -` | Selesaikan & Buat Selanjutnya | Sedang Mengedit |

## Implementasi Teknis

### Frontend
- **`LyricsTimeline.tsx`**: Menggunakan sistem manajemen status berbasis Ref untuk menangani interaksi frekuensi tinggi (menyeret) secara lokal sebelum mengirimkan ke backend. Ini menggunakan `ResizeObserver` untuk rendering kanvas yang responsif.
- **Manajemen Status**: Terintegrasi ke dalam `projectSlice.ts`. Operasi CRUD dioptimalkan untuk memperbarui status lokal secara langsung dari respons backend, meminimalkan perjalanan pulang pergi jaringan.
- **Visual:** Menampilkan mesin rendering dinamis yang menangani pemotongan teks dan pemudaran untuk elemen kecil.

### Backend
- **Struktur Data:** Lirik disimpan sebagai daftar objek `{text, timestamp, duration}` yang diurutkan dalam file sidecar `.oscope`.
- **Mesin Looping:** `LoopingEngine` mendukung mode `lyric`, yang secara otomatis mengatur rentang loop ke lirik yang dipilih saat ini.
- **Ekspor MusicXML:** `session/export.py` membagi birama menjadi segmen-segmen di setiap batas lirik dan akord. Ini memastikan bahwa tag `<lyric>` selaras sempurna dengan struktur ritme dalam skor yang diekspor.

## Tips Penyelarasan
- **Zoom Tinggi:** Untuk penyelarasan tingkat kata, perbesar hingga Anda dapat melihat transien dalam bentuk gelombang dengan jelas.
- **Looping:** Gunakan mode loop `lyric` (siklus dengan `Tab`) untuk mengulang kata saat ini saat Anda menyempurnakan titik awal dan akhirnya.
- **Metronom:** Biarkan klik subdivisi aktif untuk memastikan lirik Anda selaras dengan penanda ketukan (Bendera Ritme) yang mendasarinya.
