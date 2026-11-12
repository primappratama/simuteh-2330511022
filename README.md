# SIMUTEH: Analisis Citra Daun Teh (v0.3-morfologi)

Evaluasi Praktikum P1–P4 dan UTS (Praktikum P5–P6) Computer Vision
**Prima Pratama Putra · NIM 2330511022 · Kelas 7A · SEED = 1022** <br>
Repository: https://github.com/primappratama/simuteh-2330511022

SIMUTEH membantu petugas sortir kelompok tani teh rakyat di Kabupaten Sukabumi menilai bercak daun teh dari foto telepon genggam. Keluarannya kelas mutu (Sehat, Bercak Ringan, Bercak Berat) dan persentase luas bercak; keputusan akhir tetap di tangan petugas. Versi ini mencakup tahap **akuisisi, praproses, deteksi tepi, dan analisis bercak berbasis morfologi** (jumlah, luas, persen bercak, dan kelas mutu).

## Struktur repository

```
simuteh-2330511022/
├── data/sintetis/          # dibangkitkan ulang, tidak diunggah (.gitignore)
├── notebook/
│   ├── B1_lingkungan.ipynb     # lingkungan kerja, problem statement, risiko
│   ├── B2_citra_warna.ipynb    # pembentukan citra, kanal warna, KB
│   ├── B3_histogram.ipynb      # histogram, perbaikan citra, CLAHE
│   ├── B4_penapisan.ipynb      # konvolusi, penapis, derau
│   ├── B5_praproses.ipynb      # rangkaian praproses dan evaluasinya
│   ├── P5_tepi.ipynb           # gradien, operator tepi, Canny, keputusan pemakaian tepi
│   └── P6_morfologi.ipynb      # morfologi, komponen terhubung, modul bercak.py
├── src/
│   ├── buat_dataset_sintetis.py  # Lampiran A (SEED = 1022)
│   ├── utils_cv.py               # Lampiran B
│   ├── praproses.py              # modul praproses (dipakai ulang mulai P5)
│   ├── utils_tepi.py             # kode awal P5-P6 (Lampiran A)
│   └── bercak.py                 # modul analisis bercak (dipakai ulang mulai P7)
├── hasil/                  # gambar, CSV, param_praproses.json, param_bercak.json
├── laporan/                # bahan laporan
├── requirements.txt
└── README.md
```

## Cara menjalankan

```bash
pip install -r requirements.txt
python src/buat_dataset_sintetis.py      # dari folder utama; membuat data/sintetis/ (60 citra)
cd notebook
python -m notebook                        # atau buka di VS Code
```

Jalankan B1 sampai B5 berurutan, lalu P5 dan P6, dengan **Restart & Run All** (P5 dan P6 memakai `hasil/param_praproses.json` dari B5; P6 membuat `hasil/param_bercak.json`). Notebook harus dijalankan dari dalam folder `notebook/` karena memakai path `../`. Tanpa antarmuka:

```bash
python -m jupyter nbconvert --to notebook --execute --inplace B5_praproses.ipynb
```

Memakai modul praproses di kode lain:

```python
from praproses import praproses_adaptif, muat_param
cfg = muat_param("../hasil/param_praproses.json")
hasil, kondisi = praproses_adaptif(img_bgr, cfg)
```

Mulai P5, `praproses(img, cfg)` juga menerima konfigurasi adaptif ini (berkas yang punya kunci `dasar`) dan meneruskannya ke `praproses_adaptif`, sehingga kode petunjuk `praproses(img, PARAM)` berjalan tanpa diubah.

Analisis bercak satu daun:

```python
import json, bercak
from praproses import praproses, muat_param
PARAM = muat_param("../hasil/param_praproses.json")
PB = json.load(open("../hasil/param_bercak.json"))
h = bercak.analisis_daun(praproses(img_bgr, PARAM), PB)
print(h["kelas"], h["persen_bercak"], h["jumlah_bercak"])   # mis. Bercak Berat 3.162 7
# h["mask_daun"], h["mask_bercak"]: mask biner; h["bercak"]: luas (px, mm²), keliling, kebulatan, rasio aspek, pusat
```

## Reprodusibilitas

| Hal | Nilai |
|---|---|
| SEED dataset | 1022 (4 digit terakhir NIM) |
| SEED derau buatan (B4) | 42 |
| Dataset | 60 citra 640 × 480 (20 sehat, 20 ringan, 20 berat; 5 kondisi cahaya) |
| Lingkungan uji | Python 3.13, OpenCV 5.0.0, NumPy 2.5.3, pandas 3.0.5, scikit-image 0.26.0, matplotlib 3.11.2 |
| Parameter praproses | `hasil/param_praproses.json` |

Angka KB dan PSNR deterministik; angka waktu (ms) bergantung pada perangkat.

## Rangkaian praproses final

`ubah ukuran (640 px, INTER_AREA)` → `deteksi kondisi cahaya` → `gamma (1,6 hanya bila terang)` → `CLAHE kanal V (clip 1,0, tile 8 × 8, hanya bila bayangan)` → `median 3 × 3` → `tanpa penajaman`

Kondisi cahaya dideteksi dari statistik histogram keabuan: selisih rerata seperempat kiri–kanan > 40 → bayangan; rerata > 190 → terang; simpangan baku < 25 → kontras rendah; rerata < 145 → gelap; selain itu normal (benar 60 dari 60 citra).

## Ringkasan hasil

- **Kanal terbaik:** R (rerata KB 7,26 pada kelas berat), disusul H (5,01); G paling buruk (0,90).
- **Akuisisi:** jarak kamera 20 cm agar bercak 5 mm tetap ≥ 10 px setelah foto diperkecil ke lebar 640 px (batas 22,9 cm).
- **Perbaikan citra:** operasi linear (negatif, cerah, kontras) tidak mengubah KB; ekualisasi global menurunkan KB pada bayangan (1,23 → 0,95), sedangkan CLAHE menaikkannya (1,99). KB dapat "tertipu" bila citra gelap digelapkan, sehingga perbaikan dipilih dengan syarat arah kecerahan.
- **Penapisan:** median 3 terbaik untuk garam-merica (48,33 dB, 0,08 ms); median 9 mulai mengikis bercak ringan (dI 25,97 → 19,16).
- **Praproses (40 citra berbercak, kanal R):**

| Kondisi | KB sebelum | KB sesudah | Perubahan |
|---|---|---|---|
| normal | 8,63 | 13,91 | +61,2% |
| gelap | 9,89 | 17,19 | +73,8% |
| terang | 6,52 | 12,20 | +87,1% |
| kontras rendah | 3,93 | 8,17 | +108,0% |
| bayangan | 5,10 | 7,59 | +48,7% |

  KB naik pada 40 dari 40 citra; simpangan baku daun sehat turun 30–56% (tidak ada indikasi bercak palsu). Waktu praproses sekitar 4 ms per citra 640 × 480.

## Deteksi tepi (P5)

Diuji pada 40 citra berbercak dengan tepi acuan dari mask daun dan mask bercak (toleransi 2 piksel).

| Operator (kanal R, sesudah praproses) | F1 |
|---|---|
| Sobel T = 100 | 0,919 |
| Prewitt T = 75 | 0,929 |
| LoG sigma 3 | 0,944 |
| Canny 30/90, sigma 2 | 0,981 |
| `canny_persentil` q = 98, sigma 2 | **0,993** |

- **Kanal R** lebih baik daripada Gray untuk semua operator. Di Gray, tulang daun ikut terdeteksi pada kondisi gelap dan bayangan; di kanal R tidak ada tepi palsu pada daun sehat.
- **Ambang otomatis dari median intensitas gagal** pada kontras rendah kanal Gray (F1 0), karena median intensitas tidak berkaitan dengan besar gradien. Ambang dari persentil ke-98 magnitudo stabil di semua kondisi (simpangan baku antarkondisi 0,005).
- **Keputusan:** tepi tidak dipakai untuk menghitung luas bercak (isi kontur Canny hanya IoU 0,28–0,29). Luas bercak berasal dari ambang + morfologi (P6), dan kontur bentuk diambil dari mask bercak. `canny_persentil` dipakai sebagai pemeriksa mutu batas bercak.

## Analisis bercak (P6)

`bercak_awal` (kanal R, median + 4·MAD) → opening elips 5 → closing elips 3 → komponen terhubung (konektivitas 8) → saring luas ≥ 40 px, kebulatan ≥ 0,4, rasio aspek ≤ 1,8 → persen = luas bercak / luas daun → kelas (Ringan ≥ 0,1%, Berat ≥ 2,0%). 1 piksel = 0,4375 mm.

| Ukuran (60 citra) | Parameter bawaan | Parameter final |
|---|---|---|
| Galat absolut rerata persen bercak | 0,268 | **0,229** |
| Korelasi persen prediksi vs acuan | 0,979 | **0,981** |
| Akurasi kelas | 0,917 | **0,983** (59/60) |
| Daun sehat dinilai berbercak | 4 | **0** |
| Daun berbercak dinilai sehat | 1 | 1 (teh_030, bayangan) |

- Opening membuang derau dan tepi daun; potongan tulang daun yang tebalnya ≥ 5 px dibuang oleh syarat bentuk (tulang daun memanjang, rasio aspek sampai 48).
- Closing dibuat kecil (3) karena closing besar menyambung bercak dengan potongan lain (lembar hitung 3.1).
- Kesalahan tersisa berasal dari **ambang global pada cahaya tidak rata** (bayangan) dan **mask daun Otsu kanal S pada kontras rendah**. Keduanya akan diganti pada P7; top-hat morfologi sudah terbukti menaikkan IoU bercak pada kondisi bayangan (0,62 → 0,70).
- Waktu `praproses` + `analisis_daun` ±9 ms per citra 640 × 480 di laptop.

## Keterbatasan

- Data sintetis; ambang deteksi kondisi dan parameter perlu dikalibrasi ulang pada foto nyata.
- Parameter dipilih dan dievaluasi pada 40 citra yang sama; pada P11 parameter harus ditentukan dari data latih saja.
- Bayangan sintetis selalu berupa gradien kiri–kanan; bayangan di lapangan bisa dari arah mana pun.
- Bercak sintetis berbentuk lingkaran sempurna; syarat kebulatan dan rasio aspek perlu diuji ulang pada bercak nyata yang tidak beraturan.
- Parameter `bercak.py` dan batas kelas dipilih dan dievaluasi pada 60 citra yang sama, sehingga akurasinya optimistis.

## Etika dan privasi

Data mentah tidak diunggah; repository privat; foto lapangan hanya memuat daun dan nampan, GPS dimatikan dan EXIF dibersihkan; keputusan akhir mutu tetap di tangan petugas.

## Versi

- `v0.1-praproses`: akuisisi dan praproses (P1–P4)
- `v0.2-tepi`: deteksi tepi dan keputusan pemakaiannya (P5)
- `v0.3-morfologi`: operasi morfologi, komponen terhubung, dan modul `bercak.py` (P6)
