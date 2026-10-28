# Teks siap salin: Bagian 3 dan Bagian 4 (SIMUTEH, SEED 1022)

> Semua angka berasal dari notebook B3_histogram.ipynb dan B4_penapisan.ipynb. Angka **waktu (ms/s)** akan berbeda di laptopmu, jadi salin angka waktu dari hasil run-mu sendiri. Angka KB dan PSNR harus sama persis.

---

# BAGIAN 3. HISTOGRAM DAN PERBAIKAN CITRA

## 3.1 Lembar hitung manual

Citra M (3 bit, L = 8):
```
M = [[1, 2, 2, 3],
     [2, 2, 3, 3],
     [1, 2, 3, 4],
     [2, 3, 3, 2]]
```

**a) Histogram**

| r | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|---|
| n | 0 | 2 | 7 | 6 | 1 | 0 | 0 | 0 |

Total = 2 + 7 + 6 + 1 = 16 piksel. (Gambar diagram batang: `hasil/b3_hist_manual.png`)

**b) Peregangan kontras ke 0–7**

Rumus: s = (r − r_min) / (r_max − r_min) × (L − 1) = (r − 1) / (4 − 1) × 7

- r = 1 → 0/3 × 7 = 0
- r = 2 → 1/3 × 7 = 2,33 → **2**
- r = 3 → 2/3 × 7 = 4,67 → **5**
- r = 4 → 3/3 × 7 = **7**

```
Hasil = [[0, 2, 2, 5],
         [2, 2, 5, 5],
         [0, 2, 5, 7],
         [2, 5, 5, 2]]
```

**c) Ekualisasi histogram**

| r | n | PDF = n/16 | CDF | 7 × CDF | s |
|---|---|---|---|---|---|
| 1 | 2 | 0,1250 | 0,1250 | 0,8750 | 1 |
| 2 | 7 | 0,4375 | 0,5625 | 3,9375 | 4 |
| 3 | 6 | 0,3750 | 0,9375 | 6,5625 | 7 |
| 4 | 1 | 0,0625 | 1,0000 | 7,0000 | 7 |

```
Hasil = [[1, 4, 4, 7],
         [4, 4, 7, 7],
         [1, 4, 7, 7],
         [4, 7, 7, 4]]
```

**d) Operasi titik 8 bit**

- Negatif r = 60: s = 255 − 60 = **195**
- Kontras r = 120: s = 1,4 × 120 − 30 = **138**
- Kontras r = 210: s = 1,4 × 210 − 30 = 264 → di-*clip* menjadi **255**
- Gamma 0,6, r = 100: s = 255 × (100/255)^0,6 = 255 × 0,5703 = 145,42 → **145**
- Gamma 1,8, r = 100: s = 255 × (100/255)^1,8 = 255 × 0,1855 = 47,29 → **47**

## Tabel 9. Diagnosis mutu citra

| Citra | Rerata | Simp. baku | Min–maks | % gelap | % terang | Diagnosis | Usulan perbaikan |
|---|---|---|---|---|---|---|---|
| teh_041 (normal) | 167,7 | 38,0 | 72–220 | 0,0 | 0,5 | Mutu baik; histogram tersebar, hampir tanpa piksel jenuh | Tanpa perbaikan |
| teh_042 (gelap) | 107,8 | 37,2 | 8–159 | 19,8 | 0,0 | Terlalu gelap; histogram menumpuk di kiri, 19,8% piksel < 50 | Peregangan persentil 2–98 |
| teh_043 (terang) | 211,9 | 26,1 | 134–252 | 0,0 | 79,5 | Terlalu terang, nyaris jenuh; 79,5% piksel > 205 | Gamma 1,8 |
| teh_044 (kontras rendah) | 155,8 | 18,3 | 101–193 | 0,0 | 0,0 | Histogram sempit di tengah; simpangan baku paling kecil | Peregangan persentil 2–98 |
| teh_045 (bayangan) | 123,8 | 51,2 | 33–230 | 0,7 | 6,3 | Histogram dua puncak (sekitar 70 dan 195) akibat cahaya tidak merata kiri–kanan; simpangan baku besar **bukan** tanda kontras baik | CLAHE (perbaikan lokal) |
| teh_021 s.d. teh_025 (ringan, rerata) | 158,1 | 36,0 | 66–220 | 2,1 | 18,8 | Lima citra mewakili lima kondisi (normal, gelap, terang, kontras rendah, bayangan); pola histogram sama dengan kelas berat | Perbaikan per kondisi, sama seperti kelas berat |

## Tabel 10. Hasil perbaikan citra kondisi bayangan (teh_045)

| Metode | Parameter | KB | Simp. baku | Pengamatan visual |
|---|---|---|---|---|
| asli | – | 1,23 | 51,2 | Sisi kiri terang, sisi kanan teduh; bercak di sisi teduh samar |
| negatif | s = 255 − r | 1,23 | 51,2 | Hanya membalik terang–gelap; KB tidak berubah |
| cerah+50 | beta = +50 | 1,23 | 50,5 | Seluruh citra lebih terang, sisi kiri memutih; KB tetap |
| kontras | alpha 1,5; beta −40 | 1,23 | 74,0 | Kontras tampak naik tetapi sisi kiri jenuh; KB tetap |
| regang | persentil 2–98 (54–213) | 1,27 | 81,7 | Rentang penuh, tetapi gradien bayangan ikut diperkuat |
| gamma0.5 | gamma 0,5 | 1,10 | 36,9 | Sisi teduh lebih terang, tetapi bercak pucat kurang menonjol |
| gamma1.8 | gamma 1,8 | 1,45 | 54,5 | Citra makin gelap; KB naik karena derau daun gelap tertekan, bukan karena bercak makin jelas |
| ekualisasi | global | 0,95 | 73,4 | Histogram rata, tetapi beda kiri–kanan makin tajam; KB turun |
| CLAHE | clip 2,0; tile 8 × 8 | 1,99 | 44,7 | Bayangan berkurang, bercak di sisi teduh terlihat; latar tampak lebih berbintik |

**Catatan pengamatan:** negatif, cerah+50, dan kontras memberi KB yang **persis sama** (1,23). Ketiganya adalah transformasi linear s = a·r + b. Selisih rerata bercak–daun dan simpangan baku daun sama-sama dikali |a|, sehingga rasio KB tidak berubah. Operasi linear global tidak bisa menambah keterpisahan bercak; yang bisa hanya operasi non-linear (gamma) atau lokal (CLAHE).

## Langkah 3.4 Eksperimen CLAHE (KB, teh_045)

| clipLimit \ tile | 4 × 4 | 8 × 8 | 16 × 16 |
|---|---|---|---|
| 1,0 | 1,91 | 1,93 | 1,92 |
| 2,0 | **2,05** | 1,99 | 1,98 |
| 4,0 | 2,02 | 1,78 | 1,80 |

**CLAHE kanal V vs tiap kanal BGR (teh_045):**

| Cara | Rerata pergeseran Hue daun sehat | Rerata Hue daun (asli 50,2) | KB kanal H |
|---|---|---|---|
| CLAHE kanal V | 0,02 | 50,3 | 6,45 |
| CLAHE tiap kanal B, G, R | 8,66 | 53,0 | 0,34 |

## Langkah 3.5 Satu perbaikan per kondisi

**Aturan pemilihan:** (1) hasil perbaikan harus menggeser rerata intensitas mendekati rerata kondisi normal (173,9); (2) di antara kandidat yang lolos, pilih rerata KB tertinggi pada 8 citra per kondisi (4 berat + 4 ringan).

| Kondisi | KB asli | Perbaikan terpilih | KB sesudah (rerata 8 citra) | Kandidat yang ditolak |
|---|---|---|---|---|
| Gelap | 3,80 | Peregangan persentil 2–98 | 4,12 | Gamma 1,8 (KB 5,48) ditolak karena membuat citra makin gelap (rerata 66,5) |
| Terang | 2,98 | Gamma 1,8 | 3,25 | Gamma 0,5 dan 0,7 ditolak karena makin terang |
| Kontras rendah | 2,09 | Peregangan persentil 2–98 | 2,22 | CLAHE dan ekualisasi ditolak (menjauhkan rerata dan menurunkan KB) |
| Bayangan | 1,62 | CLAHE clip 1,0, tile 8 × 8 | 1,76 | Gamma 1,8 (KB 2,00) ditolak karena menggelapkan |

Hasil pada pasangan citra:

| Kondisi | Citra | Perbaikan | KB sebelum | KB sesudah |
|---|---|---|---|---|
| Gelap | teh_042 (berat) | regang 2–98 | 5,66 | 5,94 |
| Gelap | teh_022 (ringan) | regang 2–98 | 2,10 | 2,60 |
| Terang | teh_043 (berat) | gamma 1,8 | 4,23 | 4,64 |
| Terang | teh_023 (ringan) | gamma 1,8 | 2,15 | 2,33 |
| Kontras rendah | teh_044 (berat) | regang 2–98 | 2,93 | 3,07 |
| Kontras rendah | teh_024 (ringan) | regang 2–98 | 0,77 | 0,83 |
| Bayangan | teh_045 (berat) | CLAHE 1,0/8 | 1,23 | 1,93 |
| Bayangan | teh_025 (ringan) | CLAHE 1,0/8 | 1,35 | 1,53 |

## Jawaban pertanyaan analisis Bagian 3

**P3.1** Setelah ekualisasi, nilai 3 dan 4 sama-sama menjadi 7. Artinya, piksel yang semula berbeda (3 ≠ 4) kini tidak dapat dibedakan; informasi itu hilang dan tidak dapat dikembalikan. Ekualisasi adalah pemetaan satu nilai ke satu nilai (r → s) yang hanya bisa **mempertahankan atau menggabungkan** tingkat keabuan, tidak pernah memecahnya. Jumlah tingkat keabuan berbeda tidak dapat bertambah (pada M tetap 4 nilai: {1,2,3,4} menjadi {1,4,7}, malah tinggal 3). Ekualisasi hanya meratakan sebaran nilai yang sudah ada sehingga tampak lebih kontras; ia tidak menambah informasi baru. Untuk SIMUTEH, bila bercak pucat dan daun di sekitarnya kebetulan tergabung ke satu nilai, bercak itu justru hilang.

**P3.2** Histogram teh_045 berpuncak dua: sekitar 70 (sisi teduh) dan 195 (sisi terang). Ekualisasi global memakai satu fungsi CDF untuk seluruh citra, sehingga sebagian besar rentang keluaran dihabiskan untuk memisahkan kedua puncak itu, yaitu memperbesar beda **cahaya kiri–kanan**, bukan beda bercak–daun. Daun yang membentang dari sisi terang ke sisi teduh makin tidak seragam, sehingga simpangan baku daun sehat naik dan KB turun dari 1,23 menjadi 0,95. CLAHE bekerja per ubin 8 × 8. Di dalam satu ubin cahayanya hampir seragam, sehingga peregangan lokal memperkuat beda bercak dengan daun di sekitarnya (KB naik menjadi 1,99). Inilah yang terjadi pada foto kebun teh di lapangan: sebagian daun di bawah naungan pohon pelindung dan sebagian terkena matahari langsung; perbaikan global tidak dapat menangani dua kondisi cahaya sekaligus. *(Sesuaikan kalimat terakhir dengan contoh kebun teh di slide P3.)*

**P3.3** Peregangan min–maks gagal bila ada sedikit piksel ekstrem, misalnya derau atau pantulan. Contoh: daun bernilai 100–190, tetapi ada satu piksel derau bernilai 0 dan satu sorot pantulan bernilai 255. Min–maks memberi r_min = 0 dan r_max = 255, sehingga s = (r − 0)/(255 − 0) × 255 = r: **citra tidak berubah sama sekali**, padahal kontrasnya rendah. Dengan persentil 2–98, dua piksel ekstrem itu diabaikan, r_min ≈ 100 dan r_max ≈ 190, sehingga daun diregangkan ke 0–255. Pada data saya, teh_045 memiliki min–maks 33–230, sedangkan persentil 2–98 adalah 54–213. Faktor penguatan min–maks hanya 255/197 = 1,29 dibanding 255/159 = 1,60 dengan persentil.

**P3.4** CLAHE pada tiap kanal B, G, R menyamakan histogram setiap kanal secara terpisah, sehingga perbandingan B:G:R pada satu piksel berubah dan **warnanya bergeser**. Bukti dari Kode 3.3: pada daun sehat teh_045, CLAHE tiap kanal menggeser Hue rata-rata 8,66 unit (50,2 → 53,0), sedangkan CLAHE kanal V hanya 0,02 unit (50,2 → 50,3). Akibatnya, KB kanal H turun dari 6,45 (CLAHE kanal V) menjadi 0,34 (CLAHE tiap kanal). Untuk SIMUTEH ini berbahaya, karena warna kuning pucat bercak adalah ciri utamanya; CLAHE pada kanal V hanya memperbaiki kecerahan tanpa mengubah rona (H) dan kejenuhan (S).

**P3.5** Satu pengaturan tidak cukup. Bila CLAHE 2,0/8 diterapkan ke semua kondisi, KB rata-rata turun di keempat kondisi (gelap 3,80 → 1,98; terang 2,98 → 1,66; kontras rendah 2,09 → 1,47; bayangan 1,62 → 1,54). Perbaikan perlu dipilih menurut kondisi. Aturan sederhana yang saya usulkan berdasarkan statistik citra keabuan:
1. Jika selisih rerata seperempat kiri dan kanan citra > 40 → **bayangan** → CLAHE 1,0/8.
2. Jika rerata > 190 → **terang** → gamma 1,8.
3. Jika simpangan baku < 25 → **kontras rendah** → regang 2–98.
4. Jika rerata < 145 → **gelap** → regang 2–98.
5. Selain itu → **normal** → tanpa perbaikan.

Ambang diambil dari rentang data: rerata terang 206,6–216,3 vs normal maksimum 180,2; simpangan baku kontras rendah 13,0–18,3 vs terang minimum 22,5; selisih kiri–kanan bayangan 100,9–134,0 vs kondisi lain maksimum 18,5. Aturan ini mengenali kondisi 60 citra dengan benar 100%. Bila bayangan hanya dikenali dari simpangan baku > 47, akurasinya turun menjadi 98,3% karena satu citra gelap (simpangan baku 51,0) salah dikira bayangan. Keterbatasan: bayangan sintetis selalu berupa gradien kiri–kanan; di lapangan bayangan bisa dari arah mana pun, sehingga fitur ini perlu diperluas (misalnya beda rerata antarubin) sebelum dipakai pada foto nyata.

**P3.6** Contoh perbaikan berlebihan: CLAHE dengan clipLimit tinggi (misalnya 4,0) dan ubin kecil memperkuat derau dan tekstur tulang daun pada daun sehat, sehingga muncul bintik-bintik terang yang dapat terbaca sebagai bercak palsu, dan daun sehat tampak "ringan". Sebaliknya, gamma 1,8 berlebihan pada citra gelap menenggelamkan bercak pucat yang kecil ke dalam daun yang menggelap, sehingga daun ringan tampak sehat; pada data saya gamma 1,8 bahkan menaikkan KB sambil membuat citra makin gelap, yang berarti metrik KB pun dapat "tertipu". Pencegahan: batasi clipLimit ≤ 2,0; pilih perbaikan dengan syarat arah (rerata harus mendekati kondisi normal), bukan hanya KB tertinggi; uji bercak palsu pada kelas sehat (Langkah 5.3); kunci parameter di `param_praproses.json`; dan simpan citra asli agar petugas selalu dapat membandingkan.

---

# BAGIAN 4. KONVOLUSI DAN PENAPISAN SPASIAL

## 4.1 Lembar hitung manual

```
P = [[52,  55,  61, 58],
     [59, 255,  64, 60],
     [62,  60,   0, 57],
     [58,  61,  59, 63]]
```

**a) Keluaran 2 × 2 (posisi valid, tanpa padding)**

Penapis rerata 3 × 3 (jumlah jendela / 9):
- (0,0): (52+55+61+59+255+64+62+60+0)/9 = 668/9 = **74,22**
- (0,1): (55+61+58+255+64+60+60+0+57)/9 = 670/9 = **74,44**
- (1,0): (59+255+64+62+60+0+58+61+59)/9 = 678/9 = **75,33**
- (1,1): (255+64+60+60+0+57+61+59+63)/9 = 679/9 = **75,44**

Penapis Gaussian 1/16 [[1,2,1],[2,4,2],[1,2,1]]:
- (0,0): (52 + 2·55 + 61 + 2·59 + 4·255 + 2·64 + 62 + 2·60 + 0)/16 = 1671/16 = **104,44**
- (0,1): (55 + 2·61 + 58 + 2·255 + 4·64 + 2·60 + 60 + 2·0 + 57)/16 = 1238/16 = **77,38**
- (1,0): (59 + 2·255 + 64 + 2·62 + 4·60 + 2·0 + 58 + 2·61 + 59)/16 = 1236/16 = **77,25**
- (1,1): (255 + 2·64 + 60 + 2·60 + 4·0 + 2·57 + 61 + 2·59 + 63)/16 = 919/16 = **57,44**

Penapis median 3 × 3 (nilai ke-5 dari 9 setelah diurutkan):
- (0,0): [0, 52, 55, 59, **60**, 61, 62, 64, 255] → **60**
- (0,1): [0, 55, 57, 58, **60**, 60, 61, 64, 255] → **60**
- (1,0): [0, 58, 59, 59, **60**, 61, 62, 64, 255] → **60**
- (1,1): [0, 57, 59, 60, **60**, 61, 63, 64, 255] → **60**

| Penapis | Hasil 2 × 2 |
|---|---|
| Rerata | [[74,22; 74,44], [75,33; 75,44]] |
| Gaussian | [[104,44; 77,38], [77,25; 57,44]] |
| Median | [[60; 60], [60; 60]] |

**b) Kernel tajam pada piksel tengah Q**

s = 5 × 120 − (72 + 74 + 78 + 76) = 600 − 300 = 300 → di-*clip* menjadi **255**

**c) Padding baris [12, 30, 45, 70]**

| Cara | Hasil padding | Rerata 1 × 3 piksel pertama |
|---|---|---|
| Zero | [0, 12, 30, 45, 70, 0] | (0 + 12 + 30)/3 = **14,00** |
| Replicate | [12, 12, 30, 45, 70, 70] | (12 + 12 + 30)/3 = **18,00** |
| Reflect 101 | [30, 12, 30, 45, 70, 45] | (30 + 12 + 30)/3 = **24,00** |

## Langkah 4.2 Keluaran Kode 4.1

| Kernel | Selisih manual vs filter2D | Selisih konvolusi sejati vs filter2D | Waktu manual | Waktu filter2D |
|---|---|---|---|---|
| Rerata 3 × 3 | 0 | 0 | 1,461 s | 0,00484 s |
| Asimetris (Sobel) | 0 | 255 | 1,707 s | 0,00039 s |

Modifikasi: `cv2.filter2D` dengan kernel yang dibalik 180° (`cv2.flip(k, -1)`) menghasilkan konvolusi sejati (selisih maks = 0 terhadap `konvolusi_sejati`).

## Tabel 11. Perbandingan penapis (citra bersih teh_041 + derau buatan)

| Penapis | Gaussian 20: PSNR (dB) | Gaussian 20: waktu (ms) | Gaussian 20: KB | Garam-merica 4%: PSNR (dB) | Garam-merica 4%: waktu (ms) | Garam-merica 4%: KB |
|---|---|---|---|---|---|---|
| tanpa | 22,11 | 0,00 | 1,89 | 19,32 | 0,00 | 1,45 |
| rerata_3 | 31,45 | 0,28 | 4,31 | 28,51 | 0,30 | 3,68 |
| rerata_5 | 34,63 | 0,32 | 5,19 | 31,91 | 0,30 | 4,83 |
| gauss_5 | 32,60 | 0,07 | 4,63 | 29,66 | 0,06 | 4,08 |
| median_3 | 29,74 | 0,06 | 3,84 | **48,33** | 0,05 | 6,46 |
| median_5 | 33,50 | 0,89 | 4,98 | 45,71 | 0,93 | 6,59 |
| median_9 | **35,64** | 11,54 | 5,69 | 41,76 | 10,57 | 6,99 |

(Grafik seluruh hasil: `hasil/b4_grafik_penapis.png`; tabel lengkap: `hasil/b4_tabel_penapis.csv`)

## Langkah 4.4 Ukuran kernel median pada bercak kecil (20 citra kelas ringan)

| Kernel | dI | KB |
|---|---|---|
| 1 (tanpa) | 25,97 | 4,01 |
| 3 | 26,47 | 4,15 |
| 5 | 25,46 | 4,05 |
| 9 | 19,16 | 3,48 |
| 15 | 7,90 | 2,06 |

## Langkah 4.5 Keluaran Kode 4.4 (derau Gaussian 20)

| Penapis redam | Tajam → redam: PSNR | σ latar | Redam → tajam: PSNR | σ latar |
|---|---|---|---|---|
| Gaussian 5 × 5 | 30,36 | 7,8 | 30,20 | 8,1 |
| Median 5 | 30,17 | 8,0 | **31,13** | **7,1** |

## Langkah 4.6 PSNR 12 citra kondisi normal (derau sensor bawaan)

Penapis pilihan: Gaussian 5 × 5, sigma 1,0 (median 3 sebagai pembanding).

| Citra | Kelas | PSNR sebelum | PSNR Gaussian 5 | PSNR median 3 |
|---|---|---|---|---|
| teh_001 | sehat | 34,11 | 42,20 | 41,10 |
| teh_006 | sehat | 35,24 | 42,70 | 42,05 |
| teh_011 | sehat | 29,84 | 39,18 | 37,19 |
| teh_016 | sehat | 29,49 | 39,09 | 36,88 |
| teh_021 | ringan | 30,66 | 39,77 | 37,93 |
| teh_026 | ringan | 29,78 | 39,22 | 37,15 |
| teh_031 | ringan | 31,32 | 40,15 | 38,55 |
| teh_036 | ringan | 34,48 | 42,13 | 41,33 |
| teh_041 | berat | 32,49 | 40,75 | 39,50 |
| teh_046 | berat | 29,99 | 39,01 | 37,23 |
| teh_051 | berat | 32,38 | 40,52 | 39,46 |
| teh_056 | berat | 29,25 | 38,52 | 36,58 |
| **Rerata** | | **31,59** | **40,27** | **38,75** |

## Jawaban pertanyaan analisis Bagian 4

**P4.1** Keempat jendela 3 × 3 sama-sama memuat piksel 255 dan piksel 0. Setelah diurutkan, keduanya selalu berada di ujung daftar (posisi pertama dan terakhir), sehingga nilai tengah (ke-5) selalu diambil dari piksel daun normal, yaitu 60. Rerata dan Gaussian menjumlahkan semua piksel dengan bobot, sehingga nilai ekstrem ikut "menarik" hasilnya. Contoh: Gaussian di (0,0) bernilai 104,44 karena piksel 255 berada di tengah dengan bobot terbesar 4/16, sedangkan di (1,1) bernilai 57,44 karena piksel 0 yang berada di tengah. Artinya, untuk derau garam-merica, median membuang piksel rusak sepenuhnya selama jumlahnya kurang dari separuh jendela, sedangkan rerata dan Gaussian hanya menyebarkan kerusakan ke tetangganya menjadi noda.

**P4.2** Korelasi menggeser kernel di atas citra **apa adanya**, sedangkan konvolusi sejati **membalik kernel 180°** lebih dahulu. Fungsi `konvolusi` pada slide sebenarnya melakukan korelasi, begitu juga `cv2.filter2D`. Karena itu keduanya identik (selisih 0) bahkan untuk kernel asimetris, sedangkan `konvolusi_sejati` berbeda hingga 255 untuk kernel Sobel asimetris (tepi kiri dan kanan tertukar tanda). Pada kernel rerata dan Gaussian perbedaan tidak tampak karena kernelnya simetris: dibalik 180° pun hasilnya sama persis, sehingga korelasi = konvolusi.

**P4.3** Diukur dengan PSNR saja: untuk derau Gaussian 20 penapis terbaik adalah median_9 (35,64 dB), dan untuk garam-merica 4% adalah median_3 (48,33 dB). Keputusan berubah bila waktu dan bercak kecil diperhitungkan. Median_9 butuh 11,54 ms, sekitar 36 kali lebih lama daripada rerata_5 (0,32 ms) yang PSNR-nya hanya 1 dB lebih rendah (34,63 dB), dan sekitar 165 kali lebih lama daripada gauss_5 (0,07 ms). Selain itu, Kode 4.3 menunjukkan median 9 sudah mengikis bercak ringan (dI turun dari 25,97 menjadi 19,16). Tingginya PSNR median_9 juga dibantu oleh citra sintetis yang permukaannya rata; daun nyata bertekstur. Trade-off yang saya pilih: untuk derau Gaussian, **Gaussian 5 × 5 atau rerata 5** (PSNR cukup tinggi, sangat cepat, bercak kecil aman); untuk garam-merica, **median 3** (unggul di PSNR, waktu, dan KB sekaligus).

**P4.4** Bercak ringan mulai hilang pada kernel median **9**: dI turun dari 25,97 (tanpa penapis) menjadi 19,16 (turun sekitar 26%), dan pada kernel 15 tinggal 7,90 (bercak hampir lenyap, terlihat juga pada potongan bercak yang diperbesar). Bercak terkecil berukuran sekitar 197 piksel (diameter ±16 px termasuk tepinya), sehingga jendela 9 × 9 sudah mulai didominasi piksel daun di tepi bercak. KB dapat tetap tinggi pada kernel sedang (kernel 3–5: KB 4,05–4,15) karena KB adalah **rasio**: penapis menurunkan simpangan baku daun sehat (penyebut) bersamaan dengan atau lebih cepat daripada turunnya selisih bercak–daun (pembilang). Pelajarannya: satu ukuran evaluasi bisa menyesatkan. KB perlu didampingi ukuran absolut seperti dI, dan dicek secara visual pada bercak terkecil, karena bercak kecil itulah sasaran SIMUTEH.

**P4.5** Tidak selalu. Untuk penapis Gaussian, urutan hampir tidak berpengaruh (PSNR 30,36 vs 30,20 dB) karena Gaussian blur dan unsharp mask sama-sama operasi **linear dan invarian geser**, sehingga bersifat komutatif: A(B(x)) = B(A(x)). Perbedaan kecil yang tersisa hanya dari pembulatan dan *clipping* ke uint8. Median bersifat **non-linear**, sehingga urutannya penting. Bila citra ditajamkan dulu, derau ikut diperkuat menjadi nilai ekstrem yang lebih besar dan lebih sulit diredam median (PSNR 30,17 dB, σ latar 8,0). Bila diredam dulu, derau dibuang sebelum penajaman (PSNR 31,13 dB, σ latar 7,1). Jadi anjuran "redam dulu, lalu tajamkan" terbukti penting untuk penapis non-linear seperti median.

**P4.6** Kernel 5 × 5 memerlukan 25 perkalian per piksel.
- Foto asli 4000 × 3000: 12.000.000 × 25 = **300.000.000 perkalian**
- Citra 640 × 480: 307.200 × 25 = **7.680.000 perkalian**

Foto asli membutuhkan sekitar 39 kali lebih banyak operasi. Pada Kode 4.1, konvolusi manual dengan perulangan Python pada citra 640 × 480 (kernel 3 × 3) sudah memerlukan sekitar 1,5–1,7 s, sedangkan `cv2.filter2D` hanya 0,4–4,8 ms (ratusan sampai ribuan kali lebih cepat). Pada foto asli, konvolusi manual diperkirakan memakan waktu sekitar 39 × 1,6 ≈ 62 s, belum termasuk biaya kernel 5 × 5. Kebutuhan pengguna nomor 4 menuntut proses cukup cepat di telepon genggam kelas menengah, sehingga SIMUTEH harus (1) memperkecil citra ke lebar 640 px sebelum penapisan dan (2) memakai fungsi pustaka teroptimasi seperti `cv2.filter2D`/`cv2.GaussianBlur`, bukan perulangan manual.

**P4.7** Blur ringan tidak cukup untuk anonimisasi karena: (1) bentuk wajah, warna kulit, rambut, pakaian, dan latar masih dapat dikenali oleh orang yang mengenal petani tersebut; (2) sistem pengenalan wajah modern tetap andal pada citra beresolusi rendah atau sedikit kabur; (3) blur ringan sebagian dapat dibalik dengan teknik *deblurring*. Prosedur yang lebih aman: (a) cegah sejak akuisisi, dengan bingkai hanya daun dan nampan; (b) bila wajah terlanjur terfoto, segera hapus foto atau potong bagian yang memuat orang sebelum foto disimpan dan dibagikan; (c) bila foto harus dipertahankan, tutup wajah dengan blok warna pekat (bukan blur) lalu simpan ulang sebagai berkas baru tanpa EXIF, dan hapus versi aslinya; (d) tambahkan pemeriksaan deteksi wajah otomatis sebelum foto masuk dataset; (e) catat tindakan ini di log data.
