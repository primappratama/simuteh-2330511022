# Teks siap salin: Problem Statement, Tabel Risiko, Rencana Akuisisi

## Problem statement
Bagi petugas sortir kelompok tani teh rakyat di Kabupaten Sukabumi yang menilai bercak daun secara manual dengan hasil yang lambat dan berbeda antarpetugas, terutama saat cahaya tidak merata dan bercak masih kecil, kami membangun SIMUTEH, sistem pemeriksaan mutu daun berbasis citra, yang menerima foto satu helai daun di atas nampan dari kamera telepon genggam dan menghasilkan kelas mutu (Sehat, Bercak Ringan, Bercak Berat) beserta persentase luas bercak, sehingga petugas memperoleh pertimbangan yang konsisten sementara keputusan akhir tetap di tangan petugas.

## Tabel 6. Risiko responsible computer vision SIMUTEH
| Aspek | Risiko pada SIMUTEH | Mitigasi awal |
|---|---|---|
| Privasi citra | Wajah petani ikut terfoto dan EXIF memuat koordinat GPS kebun | Bingkai hanya daun dan nampan, GPS kamera dimatikan, EXIF dihapus sebelum foto dibagikan, izin tertulis ketua kelompok tani |
| Bias dan keadilan | Data sintetis tidak mewakili klon, umur daun, dan penyakit lain, sehingga akurasi bisa timpang antarkondisi cahaya | Laporkan hasil per kondisi cahaya, uji pada foto nyata sebelum dipakai, tidak mengklaim akurat di luar kondisi uji |
| Transparansi | Petugas tidak tahu dasar penilaian sistem dan kapan sistem kurang yakin | Tampilkan persentase bercak dan mask-nya, beri peringatan bila cahaya di luar rentang uji, jelaskan batas sistem |
| Keamanan data | Foto dan lokasi kebun tersebar lewat repositori atau tautan terbuka | Repositori privat, data mentah tidak diunggah, akses hanya anggota tim dan dosen |
| Dampak sosial | Daun sehat dinilai berat merugikan petani (harga turun), daun berat dinilai sehat membiarkan penyakit menyebar | Sistem hanya alat bantu, keputusan akhir di petugas, sampel acak diperiksa ulang manual |
| Keterlacakan | Hasil tidak dapat diulang karena parameter dan data tidak tercatat | Parameter di JSON, SEED dicatat, commit bertahap, tag versi, requirements.txt |

## Rencana akuisisi citra
| Variabel | Ketentuan |
|---|---|
| Jarak dan sudut | Kamera tegak lurus di atas daun pada jarak 20 cm (batas maksimum 22,9 cm agar bercak 5 mm tetap >= 10 px setelah diperkecil ke lebar 640 px), memakai penyangga |
| Resolusi minimum | 4000 x 3000 piksel, disimpan penuh, baru diperkecil ke lebar 640 px saat praproses |
| Alas dan acuan ukuran | Nampan atau kertas polos matte, penggaris di tepi bingkai |
| Kondisi cahaya | Lima kondisi: normal, gelap, terang, kontras rendah, bayangan; tanpa lampu kilat |
| Jumlah citra | Minimal 20 per kelas (sehat, ringan, berat), merata di lima kondisi |
| Penamaan berkas | teh_[kelas]_[kondisi]_[nomor].jpg, contoh teh_berat_gelap_007.jpg |
| Perangkat | Satu jenis ponsel, JPEG, tanpa zoom digital, HDR, filter, atau mode kecantikan |
| Izin | Izin tertulis ketua kelompok tani, memuat tujuan, penyimpanan, dan hak menarik izin |
| Metadata dan wajah | GPS dimatikan, EXIF dibersihkan, foto yang memuat orang dihapus |
