"""praproses.py: rangkaian praproses SIMUTEH (dipakai ulang mulai P5).

Dua cara pakai:
  praproses(img, p)           -> satu set parameter tetap untuk semua citra
  praproses_adaptif(img, cfg) -> kondisi cahaya dideteksi dari statistik
                                 histogram, lalu parameter disesuaikan
"""
import json
import cv2
import numpy as np

PARAM_BAWAAN = {
    "lebar": 640,            # sampling: lebar citra kerja (piksel)
    "gamma": 1.0,            # < 1 mencerahkan, > 1 menggelapkan
    "clahe_clip": 2.0,       # 0 berarti CLAHE tidak dipakai
    "clahe_tile": 8,
    "penapis": "median",     # "none", "rerata", "gaussian", "median"
    "kernel": 3,
    "sigma": 1.0,
    "tajam_k": 0.0,          # 0 berarti tanpa penajaman
}


def _gamma_lut(g):
    """Tabel pencarian s = 255 * (r / 255) ** g untuk r = 0..255."""
    lut = np.array([255 * (i / 255) ** g for i in range(256)])
    return lut.clip(0, 255).astype(np.uint8)


def praproses(img_bgr, p=None):
    """Urutan: ubah ukuran -> gamma -> CLAHE kanal V -> redam derau -> tajamkan."""
    p = {**PARAM_BAWAAN, **(p or {})}

    # TODO 1: ubah ukuran agar lebar = p["lebar"], rasio aspek tetap
    h, w = img_bgr.shape[:2]
    if w != p["lebar"]:
        tinggi = int(round(h * p["lebar"] / w))
        img = cv2.resize(img_bgr, (p["lebar"], tinggi),
                         interpolation=cv2.INTER_AREA)
    else:
        img = img_bgr.copy()

    # TODO 2: koreksi gamma dengan cv2.LUT
    if p["gamma"] != 1:
        img = cv2.LUT(img, _gamma_lut(p["gamma"]))

    # TODO 3: CLAHE pada kanal V saja (H dan S tidak diubah agar warna tetap)
    if p["clahe_clip"] > 0:
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        clahe = cv2.createCLAHE(clipLimit=p["clahe_clip"],
                                tileGridSize=(p["clahe_tile"], p["clahe_tile"]))
        hsv[:, :, 2] = clahe.apply(hsv[:, :, 2])
        img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    # TODO 4: redam derau
    k = int(p["kernel"])
    if p["penapis"] == "rerata":
        img = cv2.blur(img, (k, k))
    elif p["penapis"] == "gaussian":
        img = cv2.GaussianBlur(img, (k, k), p["sigma"])
    elif p["penapis"] == "median":
        img = cv2.medianBlur(img, k)
    elif p["penapis"] != "none":
        raise ValueError(f"penapis tidak dikenal: {p['penapis']}")

    # TODO 5: unsharp masking: hasil = (1 + k) * img - k * blur
    if p["tajam_k"] > 0:
        blur = cv2.GaussianBlur(img, (5, 5), 1.0)
        img = cv2.addWeighted(img, 1 + p["tajam_k"], blur, -p["tajam_k"], 0)

    return img


# ---------------------------------------------------------------------------
# Mode adaptif (usulan P3.5 dan P5.2): parameter dipilih dari statistik histogram
# ---------------------------------------------------------------------------
def fitur_cahaya(img_bgr):
    """Rerata, simpangan baku, dan selisih rerata seperempat kiri-kanan (keabuan)."""
    g = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY).astype(np.float64)
    w = g.shape[1] // 4
    return g.mean(), g.std(), abs(g[:, :w].mean() - g[:, -w:].mean())


def deteksi_kondisi(img_bgr, ambang=None):
    """Aturan sederhana dari Bagian 3 (akurasi 100% pada 60 citra SEED 1022)."""
    a = {"bayangan_lr": 40, "terang_rerata": 190,
         "kontras_std": 25, "gelap_rerata": 145, **(ambang or {})}
    m, s, lr = fitur_cahaya(img_bgr)
    if lr > a["bayangan_lr"]:
        return "bayangan"
    if m > a["terang_rerata"]:
        return "terang"
    if s < a["kontras_std"]:
        return "kontras_rendah"
    if m < a["gelap_rerata"]:
        return "gelap"
    return "normal"


def praproses_adaptif(img_bgr, cfg):
    """cfg = {"dasar": {...}, "per_kondisi": {kondisi: {...}}, "ambang": {...}}.
    Mengembalikan (citra hasil, kondisi terdeteksi)."""
    kondisi = deteksi_kondisi(img_bgr, cfg.get("ambang"))
    p = {**cfg.get("dasar", {}), **cfg.get("per_kondisi", {}).get(kondisi, {})}
    return praproses(img_bgr, p), kondisi


def simpan_param(p, path="../hasil/param_praproses.json"):
    with open(path, "w") as f:
        json.dump({**PARAM_BAWAAN, **p}, f, indent=2)


def simpan_cfg(cfg, path="../hasil/param_praproses.json"):
    """Menyimpan konfigurasi adaptif lengkap (parameter dasar terisi penuh)."""
    out = {**cfg, "dasar": {**PARAM_BAWAAN, **cfg.get("dasar", {})}}
    with open(path, "w") as f:
        json.dump(out, f, indent=2)


def muat_param(path="../hasil/param_praproses.json"):
    with open(path) as f:
        return json.load(f)
