# Teks siap salin: Bagian 5 (SIMUTEH, SEED 1022)

> Semua angka berasal dari notebook B5_praproses.ipynb. Angka waktu bergantung perangkat, jadi salin dari hasil run-mu sendiri. Kanal evaluasi: **R** (kanal terbaik Bagian 2).

---

# BAGIAN 5. INTEGRASI: RANGKAIAN PRAPROSES SIMUTEH

## 5.1 Modul praproses

`src/praproses.py` melengkapi kelima TODO:
1. **Ubah ukuran** ke lebar 640 px dengan `cv2.INTER_AREA`, tinggi dihitung dari rasio aspek (foto 4000 × 3000 menjadi 640 × 480).
2. **Koreksi gamma** dengan tabel `cv2.LUT` bila gamma ≠ 1.
3. **CLAHE pada kanal V** (HSV) bila `clahe_clip` > 0; kanal H dan S tidak diubah agar warna bercak tetap.
4. **Redam derau** rerata, Gaussian, atau median sesuai parameter.
5. **Unsharp masking** bila `tajam_k` > 0.

Modul juga diberi **mode adaptif** (`praproses_adaptif`): kondisi cahaya dideteksi dari statistik histogram keabuan (aturan P3.5), lalu parameter dasar ditimpa parameter khusus kondisi itu. Seluruh parameter disimpan di `hasil/param_praproses.json`.

## 5.2 Pemilihan parameter

Parameter dipilih dengan *grid search* (gamma × CLAHE × penajaman) per kondisi pada kanal R dengan dua syarat:
1. Gamma tidak boleh menjauhkan kecerahan dari kondisi normal (citra gelap tidak boleh digelapkan, citra terang tidak boleh diterangkan). Tanpa syarat ini, grid memilih gamma 1,6 untuk citra gelap (KB 45,19) karena derau di daun gelap ikut tertekan, padahal citranya makin gelap.
2. Simpangan baku kanal R pada daun sehat tidak boleh naik (mencegah bercak palsu).

Agar tidak terlalu dicocok-cocokkan ke data, penapis dibuat sama untuk semua kondisi, dan parameter khusus hanya dipakai bila jelas bermanfaat. Contoh: pada kondisi gelap, CLAHE 1,0 hanya menaikkan KB dari 17,19 menjadi 17,39 tetapi menaikkan simpangan baku daun sehat dari 5,25 menjadi 5,79, sehingga tidak dipakai. Hasil grid lengkap: `hasil/b5_grid_parameter.csv`.

| Penapis | Rerata KB terbaik (5 kondisi, dengan syarat) |
|---|---|
| Median 3 | 11,85 |
| Gaussian 5 (σ 1,0) | 11,72 |

**Perbandingan tiga rangkaian (rerata KB kanal R, 40 citra berbercak):**

| Kondisi | Sebelum | Contoh modul (CLAHE 2,0 + median 3) | Tetap (median 3) | Adaptif (final) |
|---|---|---|---|---|
| normal | 8,63 | 10,47 | 13,91 | 13,91 |
| gelap | 9,89 | 16,70 | 17,19 | 17,19 |
| terang | 6,52 | **6,16** | 10,71 | 12,20 |
| kontras rendah | 3,93 | 4,94 | 8,17 | 8,17 |
| bayangan | 5,10 | 7,34 | 6,34 | 7,59 |
| **rerata** | **6,81** | **9,12** | **11,26** | **11,81** |

## Tabel 12. Evaluasi rangkaian praproses final (adaptif)

| Kondisi | KB sebelum | KB sesudah | Perubahan (%) | Catatan |
|---|---|---|---|---|
| normal | 8,63 | 13,91 | +61,2 | Hanya median 3; kenaikan berasal dari peredaman derau sensor |
| gelap | 9,89 | 17,19 | +73,8 | Tidak dicerahkan; gamma < 1 justru menurunkan KB (Bagian 3) |
| terang | 6,52 | 12,20 | +87,1 | Gamma 1,6 menurunkan sorot; CLAHE 2,0 justru menurunkan KB (6,16) |
| kontras_rendah | 3,93 | 8,17 | +108,0 | KB awal paling rendah; median 3 menekan derau yang menenggelamkan beda kecil |
| bayangan | 5,10 | 7,59 | +48,7 | Kenaikan terkecil; CLAHE 1,0 hanya memperbaiki sebagian cahaya tidak merata |

KB naik pada **40 dari 40 citra**. Per kelas: ringan dan berat sama-sama naik di semua kondisi (contoh bayangan: berat 4,74 → 8,05; ringan 5,46 → 7,13). Deteksi kondisi otomatis benar 40 dari 40. Waktu praproses rata-rata sekitar 4 ms per citra 640 × 480 (angka pastinya bergantung perangkat).

## 5.3 Uji bercak palsu pada kelas sehat (teh_001 s.d. teh_020)

Simpangan baku kanal R pada area daun (mask_daun), rata-rata per kondisi:

| Kondisi | Sebelum | Contoh modul | Adaptif (final) | Perubahan adaptif |
|---|---|---|---|---|
| normal | 11,31 | 10,13 | 6,93 | −38,7% |
| gelap | 9,13 | 6,38 | 5,25 | −42,5% |
| terang | 10,46 | **12,42** | 7,32 | −30,0% |
| kontras rendah | 11,36 | 10,71 | 5,05 | −55,5% |
| bayangan | 13,55 | 9,89 | 9,21 | −32,0% |

Pengamatan visual (`hasil/b5_uji_bercak_palsu.png` dan `hasil/b5_zoom_sehat_terang.png`): rangkaian adaptif tidak memunculkan titik atau area terang baru pada daun sehat; tulang daun tetap terlihat sebagai garis tipis (struktur asli). Rangkaian contoh modul pada kondisi terang memperjelas tulang daun cabang menjadi pola garis terang yang berisiko dikira bercak.

**Ablasi penajaman** (rangkaian adaptif dengan tajam_k berbeda):

| tajam_k | KB rerata 40 citra berbercak | Simp. baku daun sehat |
|---|---|---|
| 0,0 | 11,81 | 6,75 |
| 0,5 | 11,19 | 7,26 |
| 1,0 | 10,26 | 8,00 |

## Tabel 13. Justifikasi rangkaian praproses

| Langkah | Parameter final | Alasan dan bukti | Risiko bila salah atur |
|---|---|---|---|
| 1. Ubah ukuran | Lebar 640 px, INTER_AREA, rasio aspek tetap | Foto 4000 × 3000 butuh 300 juta perkalian untuk kernel 5 × 5, sedangkan 640 × 480 hanya 7,68 juta (P4.6); waktu praproses ±4 ms per citra (kebutuhan pengguna 4). Pada jarak 20 cm bercak 5 mm tetap ≥ 10 px setelah diperkecil (lembar hitung 2.1d). INTER_AREA merata-ratakan piksel sehingga tidak menimbulkan aliasing | Terlalu kecil: bercak ringan < 10 px dan hilang (Kode 2.2: fx 0,05 → KB 1,57). INTER_NEAREST: aliasing atau pola palsu |
| 2. Koreksi gamma | 1,6 hanya bila terang; 1,0 untuk kondisi lain | Terang: KB 10,71 → 12,20 (B5); gamma > 1 terpilih juga di Bagian 3 (Langkah 3.5). Gelap tidak dicerahkan karena gamma 0,5 menurunkan KB 3,80 → 2,96 (Bagian 3) | Gamma > 1 pada citra gelap menenggelamkan bercak dan KB naik semu; gamma < 1 pada citra terang membuat bercak pucat jenuh putih |
| 3. CLAHE kanal V | Clip 1,0, tile 8 × 8, hanya bila bayangan | Bayangan: KB 6,34 → 7,59 (B5); CLAHE adalah perbaikan lokal untuk cahaya tidak merata (Tabel 10: CLAHE 1,99 vs ekualisasi 0,95). Kanal V menjaga Hue (geser 0,02 vs 8,66 bila tiap kanal BGR, Kode 3.3). Tidak dipakai di kondisi lain karena CLAHE 2,0 menurunkan KB terang (6,52 → 6,16) dan menaikkan simpangan baku daun sehat terang (10,46 → 12,42) | Clip tinggi atau CLAHE pada semua kondisi: derau dan tulang daun diperkuat menjadi bercak palsu; CLAHE tiap kanal BGR: warna bercak bergeser |
| 4. Redam derau | Median 3 × 3, semua kondisi | Rerata KB kanal R adaptif median 3 = 11,85 vs Gaussian 5 = 11,72 (grid search B5, `hasil/b5_grid_parameter.csv`) dan tanpa perlu penajaman; median 3 terbaik untuk garam-merica (48,33 dB, 0,08 ms, Tabel 11) dan tidak mengikis bercak kecil (dI 26,47 vs 25,97 tanpa penapis, Kode 4.3). Gaussian 5 sedikit lebih tinggi PSNR-nya pada derau sensor (40,27 vs 38,75 dB, Langkah 4.6); ini trade-off yang diterima | Kernel ≥ 9: bercak ringan terkikis (dI 19,16 pada median 9; 7,90 pada median 15); tanpa penapis: derau menutupi bercak pada kontras rendah |
| 5. Tajamkan | Tidak dipakai (tajam_k = 0) | Ablasi: tajam_k 0,5 dan 1,0 menurunkan KB (11,81 → 11,19 → 10,26) dan menaikkan simpangan baku daun sehat (6,75 → 7,26 → 8,00); penajaman memperkuat derau (Kode 4.4) | Penajaman berlebih memperkuat derau dan tepi tulang daun sehingga muncul bercak palsu |

(Diagram rangkaian dengan parameter final: `hasil/b5_diagram_praproses.png`)

## 5.5 Reprodusibilitas

Seluruh notebook dijalankan ulang dengan Restart & Run All tanpa galat. SEED dataset 1022, SEED derau buatan 42, versi pustaka tercatat di `requirements.txt` dan sel terakhir B5, parameter di `hasil/param_praproses.json`, dan versi ditandai dengan tag `v0.1-praproses`.

## Jawaban pertanyaan analisis Bagian 5

**P5.1** Ya. Rangkaian adaptif menaikkan KB pada kelima kondisi (+48,7% sampai +108,0%) dan pada 40 dari 40 citra berbercak. Kondisi tersulit adalah **bayangan**: kenaikannya paling kecil (+48,7%), dan simpangan baku daun sehatnya tetap paling tinggi setelah praproses (9,21). Pada citra bayangan, satu helai daun terbentang dari bagian terang ke bagian teduh, sehingga intensitas daun sehat sendiri sudah sangat beragam. Selisih cahaya ini masuk ke penyebut KB. CLAHE hanya meratakan cahaya per ubin dan tidak dapat menghapus gradien sepenuhnya, sedangkan median 3 hanya meredam derau, bukan perbedaan cahaya. Kontras rendah memiliki KB awal paling rendah (3,93), tetapi naik paling besar (+108%) karena masalah utamanya derau yang menenggelamkan beda kecil, dan itu yang diatasi penapis.

**P5.2** Dengan rangkaian final tidak ada kondisi yang KB-nya turun. Namun dengan parameter contoh modul (CLAHE 2,0 + median 3 untuk semua kondisi), KB kondisi **terang turun** dari 6,52 menjadi 6,16 (−5,5%). Citra terang sudah mendekati jenuh (79,5% piksel > 205 pada teh_043); CLAHE memperkuat variasi kecil di daun sehat (derau dan tulang daun), sehingga simpangan baku daun sehat naik (10,46 → 12,42), sementara bercak pucat tidak bisa lebih terang lagi. Penyebut KB naik lebih cepat daripada pembilangnya. Perbaikan yang saya terapkan adalah **parameter otomatis berdasarkan statistik histogram**: kondisi dideteksi dari rerata, simpangan baku, dan selisih terang kiri–kanan (benar 60 dari 60 citra), lalu CLAHE hanya dipakai pada bayangan dan gamma 1,6 hanya pada terang. Hasilnya KB terang naik menjadi 12,20. Keterbatasan: ambang deteksi ditentukan dari data sintetis dan harus dikalibrasi ulang pada foto nyata.

**P5.3** Rangkaian final tidak menimbulkan bercak palsu: simpangan baku kanal R daun sehat turun di kelima kondisi (−30,0% sampai −55,5%), dan panel sebelum–sesudah tidak menunjukkan titik terang baru. Kondisi paling berisiko adalah **terang** bila memakai CLAHE: dengan parameter contoh modul, simpangan baku daun sehat naik 18,7% (10,46 → 12,42), dan potongan yang diperbesar memperlihatkan tulang daun cabang berubah menjadi pola garis terang. Bayangan juga berisiko karena di sana CLAHE tetap dipakai dan keragaman daun sehatnya masih tertinggi (9,21). Kaitannya dengan P11: pengklasifikasi belajar dari fitur warna dan tekstur. Bila praproses memperkuat tekstur daun sehat, daun sehat dapat diklasifikasikan sebagai "Bercak Ringan" (salah positif), sehingga petani dirugikan karena harga turun. Ini juga alasan segmentasi pada tahap berikutnya perlu membedakan tulang daun yang memanjang dari bercak yang membulat.

**P5.4** Model pada P11 mempelajari pola fitur (intensitas, kontras, tekstur, persentase bercak) dari citra yang sudah diprapros. Bila data uji diprapros berbeda, sebaran fiturnya bergeser dan batas keputusan model tidak lagi berlaku. Contoh dari data saya: pada kondisi normal, KB kanal R citra mentah 8,63 sedangkan setelah praproses 13,91, dan simpangan baku daun sehat 11,31 vs 6,93. Model yang dilatih dengan citra terprapros akan menganggap daun sehat mentah lebih "bertekstur", sehingga bisa salah menilainya berbercak. Akibatnya akurasi di lapangan turun dan tidak dapat diperkirakan dari hasil uji. Karena itu kode (`praproses.py`) dan parameternya (`param_praproses.json`) disimpan dan dipakai ulang persis sama. Selain itu, parameter dan ambang praproses harus ditentukan **hanya dari data latih**; pada evaluasi ini parameter dipilih dan dievaluasi pada 40 citra yang sama, dan hal ini harus diperbaiki pada P11 agar tidak terjadi kebocoran data.

**P5.5** *(Tulis ulang dengan pengalamanmu sendiri.)*
- **Jujur:** saya melaporkan angka apa adanya, termasuk yang tidak menguntungkan: gamma 0,5 menurunkan KB pada kondisi gelap, parameter contoh modul menurunkan KB terang, dan satu ukuran bercak palsu (persentase piksel ekstrem) saya buang beserta alasannya karena terbukti menyesatkan, bukan karena hasilnya kurang bagus. Saya juga menyebutkan keterbatasan (data sintetis, parameter dipilih pada data yang sama) dan mencantumkan bagian yang dikerjakan dengan bantuan AI.
- **Amanah:** saya menjaga data dan kepercayaan pengguna. Folder data tidak diunggah ke repository, rencana akuisisi mewajibkan izin tertulis kelompok tani, GPS dimatikan, dan EXIF dibersihkan. SEED, versi pustaka, dan parameter dicatat agar siapa pun dapat memeriksa ulang hasil, dan sistem dirancang sebagai alat bantu sehingga keputusan akhir tetap di tangan petugas.
