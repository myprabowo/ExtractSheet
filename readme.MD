# 📥 PDF Answer Sheet Reader (AcroForm Extractor)

[![Shiny Python](https://img.shields.io/badge/Shiny-Python-blue?logo=python&logoColor=white)](https://shiny.posit.co/py/) [![Pandas](https://img.shields.io/badge/Library-Pandas-150458?logo=pandas)](https://pandas.pydata.org/) [![Pikepdf](https://img.shields.io/badge/Library-Pikepdf-red)](https://pikepdf.readthedocs.io/)

Aplikasi berbasis web (Shiny for Python) yang dirancang untuk **mengekstrak data secara massal** dari lembar jawab ujian TOEFL interaktif (AcroForm) ke dalam format tabel (DataFrame) dan CSV.

------------------------------------------------------------------------

## ✨ Fitur Utama

-   **Bulk Upload**: Unggah banyak file PDF sekaligus untuk diproses dalam satu sesi.
-   **AcroForm Extraction**: Mengambil nilai dari field teks dan radio button tanpa menggunakan OCR, sehingga akurasi data mencapai 100%.
-   **Auto-Sorting**: Mengurutkan kolom jawaban secara cerdas berdasarkan nama section dan nomor soal (misal: `Listening_1`, `Listening_2`, dst.).
-   **Validation Alert**: Mendeteksi secara otomatis file yang **Flattened** (tidak memiliki form metadata) dan memberikan peringatan kepada pengguna.
-   **Export to CSV**: Unduh hasil ekstraksi seluruh peserta ke dalam satu file CSV yang siap diolah untuk skoring.

------------------------------------------------------------------------

## 🚀 Teknologi yang Digunakan

-   **Shiny for Python**: Framework untuk antarmuka web interaktif.
-   **Pikepdf**: Library *high-performance* untuk membaca dan memanipulasi struktur internal PDF.
-   **Pandas**: Digunakan untuk manajemen tabel data dan ekspor CSV.
-   **Regex**: Untuk logika pengurutan kolom jawaban yang kompleks.

------------------------------------------------------------------------

## 🛠️ Instalasi Lokal

1.  **Pastikan Python 3.9+ terinstal.**

2.  **Instal dependensi yang diperlukan:**

    ``` bash
    pip install shiny pandas pikepdf
    ```

3.  **Jalankan aplikasi:**

``` bash
shiny run app.py
```

------------------------------------------------------------------------

## 📖 Cara Kerja Skrip

1.  **Upload**: Pengguna memasukkan file PDF LJU yang telah diisi oleh peserta.
2.  **Extraction**: Skrip menelusuri `Root.AcroForm.Fields` pada setiap PDF.
3.  **Formatting**:

-   Nilai objek pikepdf dipaksa menjadi *string* untuk stabilitas data.
-   Nama kolom dibersihkan dari prefix `/` (objek Name).

4.  **Ordering**: Kolom disusun dengan urutan: `filename` -\> `Identitas Peserta` -\> `Jawaban Soal`.
5.  **Download**: Hasil akhir digabungkan menjadi satu tabel besar yang dapat diunduh.

------------------------------------------------------------------------

## ⚠️ Catatan Penting

-   **File "Flattened"**: Skrip ini mencari metadata form. Jika PDF disimpan dengan cara "Print to PDF" atau "Flatten", data form akan hilang dan skrip akan menandai file tersebut sebagai file yang gagal dibaca.
-   **Viewer PDF**: Peserta ujian disarankan menggunakan Adobe Acrobat atau browser modern agar data tersimpan dalam struktur AcroForm yang benar.

------------------------------------------------------------------------

## 🌐 Deployment (Shinyapps.io)

Aplikasi ini dapat diunggah ke *shinyapps.io* dengan bantuan `rsconnect-python`. Pastikan file `requirements.txt` Anda berisi:

``` text
shiny
pandas
pikepdf
```

------------------------------------------------------------------------

**Creator**: Muhammad Yoga Prabowo

**Institution**: Politeknik Keuangan Negara STAN
