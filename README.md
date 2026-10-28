# SIMUTEH: Praproses Citra Daun Teh (v0.1-praproses)

Evaluasi Praktikum P1–P4 Computer Vision, Teknik Informatika UMMI, TA 2026/2027
**Prima Pratama Putra · NIM 2330511022 · Kelas 7A · SEED = 1022**
Repository: https://github.com/primappratama/simuteh-2330511022 (privat)

SIMUTEH membantu petugas sortir kelompok tani teh rakyat di Kabupaten Sukabumi menilai bercak daun teh dari foto telepon genggam. Keluarannya kelas mutu (Sehat, Bercak Ringan, Bercak Berat) dan persentase luas bercak; keputusan akhir tetap di tangan petugas. Versi ini mencakup tahap **akuisisi dan praproses**.

## Struktur repository

```
simuteh-2330511022/
├── data/sintetis/          # dibangkitkan ulang, tidak diunggah (.gitignore)
├── notebook/
│   ├── B1_lingkungan.ipynb     # lingkungan kerja, problem statement, risiko
│   ├── B2_citra_warna.ipynb    # pembentukan citra, kanal warna, KB
│   ├── B3_histogram.ipynb      # histogram, perbaikan citra, CLAHE
│   ├── B4_penapisan.ipynb      # konvolusi, penapis, derau
│   └── B5_praproses.ipynb      # rangkaian praproses dan evaluasinya
├── src/
│   ├── buat_dataset_sintetis.py  # Lampiran A (SEED = 1022)
│   ├── utils_cv.py               # Lampiran B
│   └── praproses.py              # modul praproses (dipakai ulang mulai P5)
├── hasil/                  # gambar, CSV, dan param_praproses.json
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

Jalankan B1 sampai B5 berurutan dengan **Restart & Run All**. Notebook harus dijalankan dari dalam folder `notebook/` karena memakai path `../`. Tanpa antarmuka:

```bash
python -m jupyter nbconvert --to notebook --execute --inplace B5_praproses.ipynb
```

Memakai modul praproses di kode lain:

```python
from praproses import praproses_adaptif, muat_param
cfg = muat_param("../hasil/param_praproses.json")
hasil, kondisi = praproses_adaptif(img_bgr, cfg)
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

## Keterbatasan

- Data sintetis; ambang deteksi kondisi dan parameter perlu dikalibrasi ulang pada foto nyata.
- Parameter dipilih dan dievaluasi pada 40 citra yang sama; pada P11 parameter harus ditentukan dari data latih saja.
- Bayangan sintetis selalu berupa gradien kiri–kanan; bayangan di lapangan bisa dari arah mana pun.

## Etika dan privasi

Data mentah tidak diunggah; repository privat; foto lapangan hanya memuat daun dan nampan, GPS dimatikan dan EXIF dibersihkan; keputusan akhir mutu tetap di tangan petugas.

## Versi

- `v0.1-praproses`: akuisisi dan praproses (P1–P4)
