# Phosor 🧠📸

**Photo Sorting Orchestrator for Faces**

Phosor adalah alat otomatis untuk **mengelompokkan foto berdasarkan wajah**.
Aplikasi ini memindai foto dari sebuah folder (misalnya SD card kamera), mendeteksi wajah, mengekstrak embedding, melakukan clustering, lalu mengelompokkan foto ke dalam folder per individu.

Tujuan utamanya:

> Menghemat waktu user dalam memilah foto per orang, terutama untuk fotografer, dokumentasi event, atau pengguna yang sering memotret banyak orang sekaligus.

---

## 1. Tujuan, Ruang Lingkup & Kriteria Sukses

### 1.1 Tujuan Utama

* Mengotomatisasi proses **sortir foto berdasarkan wajah**.
* Menyediakan sistem yang dapat:

  * Mengelompokkan wajah yang mirip dalam satu cluster.
  * Membuat **folder terpisah per orang/cluster**.
  * Mendukung **incremental update**, sehingga saat ada foto baru, sistem tinggal memperbarui hasil pengelompokan sebelumnya.
* Berjalan **secara lokal** (offline-capable) di laptop/PC tanpa perlu koneksi internet.

### 1.2 Ruang Lingkup Versi 1 (MVP)

Versi 1 Phosor akan fokus pada:

* Input:

  * Folder berisi file gambar (`.jpg`, `.jpeg`, `.png`, `.webp`).
* Proses:

  * Deteksi wajah, ekstraksi embedding, clustering, mapping cluster → folder.
* Output:

  * Struktur folder per cluster + metadata JSON.
* Mode operasi:

  * **Full scan** dan **dry run**.
* Antarmuka:

  * **CLI (Command Line Interface)** berbasis Python.

Yang **belum** jadi fokus versi 1 (masuk roadmap):

* Web dashboard (FastAPI + UI).
* Mode incremental yang kompleks (dengan database besar).
* GUI desktop.

### 1.3 Kriteria Sukses Teknis

* Mampu memproses minimal:

  * ± 1.000–3.000 foto di laptop kelas menengah **tanpa crash**.
* Error handling:

  * File rusak / non-image tidak menyebabkan proses berhenti total.
* Clustering:

  * Foto orang yang sama mayoritas masuk ke cluster yang sama.
  * Noise wajar ditampung di folder `unclustered/`.
* Penggunaan:

  * CLI cukup 1–2 perintah utama untuk menjalankan pipeline.

---

## 2. Target Pengguna & Use Case

### 2.1 Target Pengguna

* Fotografer event (wedding, wisuda, seminar, dll).
* Divisi dokumentasi organisasi/komunitas.
* User rumahan yang sering foto keluarga/teman.
* Mahasiswa / peneliti yang butuh contoh use case computer vision dan face recognition.

### 2.2 Use Case Contoh

1. **Fotografer wisuda**

   * Input: 1000+ foto dari SD card kamera.
   * Output:

     * Folder `Person_01` berisi semua foto mahasiswa A.
     * Folder `Person_02` berisi semua foto mahasiswa B.
     * Folder `unclustered` untuk wajah yang tidak cukup data atau noise.

2. **Album keluarga**

   * Input: Foto campuran keluarga selama beberapa tahun.
   * Output:

     * `Ayah/`, `Ibu/`, `Anak_1/`, `Anak_2/` (bisa direlabel manual setelah clustering awal).

3. **Dokumentasi organisasi**

   * Memudahkan tim dokumentasi untuk cari foto tiap pengurus/anggota.

---

## 3. Prinsip Desain & Non-Fungsional

### 3.1 Prinsip Desain

* **Local-first**: semua proses di device user.
* **Configurable**: parameter clustering & mode copy/move diatur via config file.
* **Composable**: modul dipisah dengan jelas (engine wajah, clustering, manajemen file).
* **Extensible**: mudah mengganti backend face recognition di masa depan.

### 3.2 Non-Functional Requirements

* **Portability**:

  * Support utama: Windows & Linux.
  * macOS didukung selama dependensi ONNX & OpenCV berjalan.
* **Reliability**:

  * Graceful handling untuk:

    * File rusak.
    * Folder kosong.
    * Tidak ada wajah terdeteksi.
* **Performance**:

  * Batch processing dan opsi multiprocess.
  * Menghindari loading model berulang (singleton pattern untuk `FaceEngine`).
* **Maintainability**:

  * Struktur modul rapi.
  * Testing dengan pytest.
  * Linting & formatting konsisten.

---

## 4. Arsitektur Sistem

Secara garis besar, arsitektur Phosor:

```text
Input Folder (foto)
        ↓
  File Scanner
        ↓
  Face Engine (UniFace)
  - Face Detection
  - Face Embedding
        ↓
  Embedding Store (in-memory + file metadata)
        ↓
  Clustering Engine (DBSCAN / KMeans / HDBSCAN)
        ↓
  Cluster Manager & Naming
        ↓
  Folder Writer (copy/move foto ke output)
        ↓
Output Folder (per orang / per cluster)
```

Untuk versi lebih lanjut:

```text
+ Optional: Metadata DB (SQLite)
        ↓
+ Optional: REST API (FastAPI)
        ↓
+ Optional: Web Dashboard (UI)
```

---

## 5. Alur Kerja (Flow) Phosor

### 5.1 High-Level Flow

1. User menentukan:

   * `input_dir`: lokasi foto (misalnya `D:/DCIM/`).
   * `output_dir`: lokasi hasil sortir (misalnya `E:/Phosor_Output/`).
   * Parameter konfigurasi:

     * Metode clustering.
     * Threshold / parameter DBSCAN.
     * Mode: `copy` / `move`.
     * Minimal jumlah wajah per cluster valid.

2. Phosor:

   * Memindai semua file gambar dari `input_dir`.
   * Untuk setiap foto:

     * Membaca gambar.
     * Mendeteksi wajah menggunakan UniFace.
     * Untuk setiap wajah:

       * Mengambil **face landmarks**.
       * Menghasilkan **embedding wajah** (vektor).
   * Menyimpan embedding beserta metadata foto dalam struktur data internal.

3. Clustering:

   * Seluruh embedding dikumpulkan.
   * Clustering dijalankan (mis. DBSCAN berbasis cosine distance).
   * Hasil:

     * Setiap embedding memiliki `cluster_id` (misal 0, 1, 2, … atau `-1` untuk noise).

4. Mapping cluster ke folder:

   * Cluster valid diberi nama seperti:

     * `Person_01`, `Person_02`, dst.
   * Cluster dengan label `-1` (noise) dimasukkan ke folder `unclustered/`.

5. Penulisan output:

   * Phosor membuat struktur folder di `output_dir`.
   * Foto disalin/dipindahkan ke folder sesuai cluster.
   * File metadata (misal `embeddings.json`, `clusters_summary.json`) disimpan.

### 5.2 Flow Detail per Foto

Untuk setiap file `image_path`:

1. Baca gambar dengan OpenCV (`cv2.imread`).

2. Deteksi wajah:

   * Menggunakan `RetinaFace` dari UniFace.
   * Mendapatkan bounding box dan landmarks.

3. Untuk setiap wajah:

   * Menggunakan `ArcFace` atau model lain dari UniFace.
   * Menghasilkan embedding normalisasi (mis. vektor 512 dimensi).

4. Menyimpan record:

   ```json
   {
     "image_path": "D:/DCIM/IMG_00123.JPG",
     "face_index": 0,
     "embedding": [...],
     "bbox": [x1, y1, x2, y2]
   }
   ```

5. Jika tidak ada wajah:

   * Foto bisa dimasukkan:

     * Ke folder `no_face/`, atau
     * Di-skip sesuai konfigurasi.

---

## 6. Komponen Sistem & Modul

### 6.1 Core / Engine Phosor

* Bentuk awal: **Command Line Interface (CLI)**.
* Tugas:

  * Membaca argumen (input, output, mode, config).
  * Mengatur proses scanning → embedding → clustering → penulisan output.
  * Menampilkan progress (via progress bar).
  * Menangani logging dan error.

### 6.2 Face Engine (UniFace)

* Library utama:

  * [`uniface`](https://github.com/yakhyo/uniface) sebagai backend deteksi & embedding wajah.
* Fungsi:

  * `detect_faces(image)`: mengembalikan daftar wajah (bbox, landmarks).
  * `get_embedding(image, landmarks)`: mengembalikan embedding normalized.
* Konsep:

  * Dibungkus dalam kelas `FaceEngine` supaya:

    * Model hanya di-load sekali.
    * Backend bisa diganti di masa depan (polymorphism).

### 6.3 Clustering Engine

* Menggunakan library **scikit-learn** (minimal).

* Opsi algoritma:

  * **DBSCAN (cosine metric)**:

    * Tidak perlu tentukan jumlah cluster di awal.
    * Cocok saat jumlah orang tidak diketahui.
  * **KMeans (opsional)**:

    * Dipakai jika user ingin paksa jumlah cluster tertentu.
  * (Opsional) **HDBSCAN**:

    * Untuk dataset lebih kompleks.

* Output:

  * Mapping `embedding_index → cluster_id`.

### 6.4 File Scanner & Folder Manager

* **File Scanner**:

  * Memindai semua file di `input_dir` dengan ekstensi tertentu: `.jpg`, `.jpeg`, `.png`, `.webp`, dll.
  * Menghasilkan list path foto.
  * Bisa filter:

    * Ukuran file minimum (hindari thumbnail).
    * Pilih recursive / non-recursive.

* **Folder Manager**:

  * Membuat struktur folder output.
  * Menentukan nama folder per cluster: `Person_01/`, `Person_02/`, dll.
  * Menangani mode:

    * `copy` (menyalin foto),
    * `move` (memindahkan foto),
    * Di masa depan: `symlink` (jika OS mendukung dan diinginkan).

### 6.5 Config & Logging

* Config:

  * Disimpan di file `config.toml` / `config.yaml`.
  * Memuat:

    * `input_dir`, `output_dir`.
    * `cluster_method` (DBSCAN / KMeans).
    * `eps`, `min_samples` (untuk DBSCAN).
    * `copy_mode` (copy/move).
    * `min_faces_per_cluster` (untuk memfilter cluster kecil).
    * Flag untuk:

      * Menangani foto tanpa wajah.
      * Menyimpan embedding ke JSON/DB.

* Logging:

  * Menggunakan `logging` Python.
  * Level: DEBUG/INFO/WARNING/ERROR.
  * Output ke:

    * Console.
    * File `logs/phosor.log`.

### 6.6 (Opsional) Web Dashboard / API

* Backend: **FastAPI**.
* Fungsi:

  * Menampilkan daftar cluster dan contoh foto per cluster.
  * Mengizinkan user merge/split cluster secara manual.
  * Rename cluster `Person_01` → `Andi`, dll.
* Frontend (opsional):

  * SPA sederhana dengan React / Vanilla JS.

---

## 7. Tech Stack Detail

### 7.1 Bahasa & Runtime

* **Python 3.10+** (disarankan 3.10 atau 3.11).

### 7.2 Library Aplikasi

* **Face Recognition & Vision**

  * `uniface`
  * `opencv-python`
  * (Opsional) `Pillow` untuk baca EXIF & manipulasi gambar.

* **Clustering & Statistik**

  * `scikit-learn`
  * (Opsional) `hdbscan`

* **Tools Pendukung**

  * `numpy`
  * `tqdm` untuk progress bar.
  * `typer` untuk CLI ergonomis (`phosor scan ...`).
  * `pydantic` / `pydantic-settings` untuk config terstruktur.
  * `rich` / `rich-click` (opsional) untuk tampilan CLI yang lebih enak.

* **(Opsional) Backend & Dashboard**

  * `fastapi`
  * `uvicorn`
  * `sqlalchemy` / `sqlmodel` untuk metadata DB (SQLite).

### 7.3 Tooling Pengembangan

* **Dependency & Packaging**

  * `uv` atau `poetry` / `pip + venv`.
  * `pyproject.toml` dengan entry point:

    * CLI command: `phosor`.

* **Quality**

  * `black` untuk formatting.
  * `ruff` untuk linting.
  * `mypy` / `pyright` untuk type checking (opsional).

* **Testing**

  * `pytest` sebagai unit/integration test framework.
  * Test coverage minimal untuk:

    * `FaceEngine` (mock model).
    * Clustering logic.
    * File scanner & folder manager.

---

## 8. Struktur Direktori Proyek

Contoh struktur proyek Phosor:

```text
phosor/
  ├─ phosor/
  │   ├─ __init__.py
  │   ├─ cli.py
  │   ├─ face_engine.py
  │   ├─ clustering.py
  │   ├─ file_scanner.py
  │   ├─ folder_manager.py
  │   ├─ config.py
  │   ├─ models.py        # pydantic/dataclasses untuk data record
  │   └─ utils.py
  │
  ├─ configs/
  │   └─ config.example.toml
  │
  ├─ data/
  │   ├─ input/        # contoh folder input
  │   └─ output/       # contoh folder output
  │
  ├─ logs/
  │   └─ phosor.log
  │
  ├─ scripts/
  │   └─ demo_phosor.py
  │
  ├─ tests/
  │   ├─ test_face_engine.py
  │   ├─ test_clustering.py
  │   ├─ test_file_scanner.py
  │   └─ test_integration.py
  │
  ├─ pyproject.toml
  ├─ README.md
  └─ LICENSE
```

---

## 9. Format Data & Metadata

### 9.1 Metadata Embedding

Untuk memudahkan debugging dan incremental update, Phosor dapat menyimpan file metadata, misalnya `embeddings.json`:

```json
[
  {
    "id": 1,
    "image_path": "D:/DCIM/IMG_00123.JPG",
    "face_index": 0,
    "embedding": [0.123, -0.045, "..."],
    "bbox": [120, 80, 300, 260],
    "cluster_id": 0
  }
]
```

### 9.2 File Cluster Summary

Phosor juga bisa menyimpan `clusters_summary.json`:

```json
{
  "clusters": [
    {
      "cluster_id": 0,
      "label": "Person_01",
      "num_faces": 145,
      "sample_images": [
        "D:/DCIM/IMG_00123.JPG",
        "D:/DCIM/IMG_00124.JPG"
      ]
    }
  ],
  "unclustered_count": 23
}
```

### 9.3 (Opsional) Penyimpanan ke Database

* Database: **SQLite** (file `phosor.db`).
* Tabel:

  * `images`: id, path, hash, created_at.
  * `faces`: id, image_id, face_index, bbox, embedding (bisa disimpan terkompres).
  * `clusters`: id, label, created_at.
  * `face_cluster_map`: face_id, cluster_id.

---

## 10. Contoh Konfigurasi (`config.toml`)

```toml
[input]
dir = "D:/DCIM"
recursive = true
min_file_size_kb = 50

[output]
dir = "E:/Phosor_Output"
mode = "copy" # copy | move

[face]
detector = "retinaface"
recognizer = "arcface"
max_faces_per_image = 10

[clustering]
method = "dbscan"     # dbscan | kmeans
eps = 0.5             # hanya untuk dbscan
min_samples = 3       # minimal titik dalam sebuah cluster
min_faces_per_cluster = 5

[handling]
include_no_face = false   # jika true, simpan di folder no_face
save_embeddings = true

[logging]
level = "INFO"
file = "logs/phosor.log"
```

---

## 11. Desain CLI

Menggunakan `typer`, contoh perintah:

```bash
# Full scan dengan config default
phosor scan --config configs/config.toml

# Override input/output via CLI
phosor scan --input "D:/DCIM" --output "E:/Phosor_Output"

# Dry run (tanpa copy/move file)
phosor scan --config configs/config.toml --dry-run

# Cek summary cluster setelah proses
phosor summary --metadata "E:/Phosor_Output/clusters_summary.json"
```

Sub-command yang direncanakan:

* `phosor scan` → jalankan pipeline penuh.
* `phosor summary` → tampilkan ringkasan cluster.
* `phosor clean` → hapus metadata/log/output tertentu (opsional).

---

## 12. Pertimbangan Performa

* **Batch Processing**:

  * Memproses foto dalam batch (misalnya 50–100 foto).
* **Multiprocessing / Multithreading**:

  * Opsi untuk memparallelkan:

    * Pembacaan gambar.
    * Face detection & embedding.
* **Caching Model**:

  * UniFace sudah meng-cache model ONNX di lokal.
  * `FaceEngine` bertanggung jawab memastikan model hanya di-load sekali.

---

## 13. Pertimbangan Privasi & Etika

* Semua proses dilakukan **secara lokal**.
* Tidak ada pengiriman data ke server eksternal.
* Pengguna bertanggung jawab terhadap:

  * Legalitas & etika penggunaan foto.
  * Izin terhadap subjek foto.

---

## 14. Roadmap Implementasi

### Fase 0 – Setup Proyek

* Setup repo Git.
* Setup `pyproject.toml` + virtualenv.
* Tambah dependency dasar:

  * `uniface`, `opencv-python`, `numpy`, `scikit-learn`, `tqdm`, `typer`, `pytest`, `black`, `ruff`.

### Fase 1 – Core Pipeline (MVP)

* Implementasi:

  * `file_scanner.py`
  * `face_engine.py`
  * `clustering.py`
  * `folder_manager.py`
* CLI dasar:

  * `phosor scan --input ... --output ...`.
* Output:

  * Folder per cluster.
  * `embeddings.json` dan `clusters_summary.json`.

### Fase 2 – Config & Quality

* Config dengan file TOML + `pydantic-settings`.
* Logging terstruktur.
* Unit test untuk modul utama.
* Dokumentasi dasar di README.

### Fase 3 – Mode Lanjutan

* Mode `dry-run`.
* Mode handling `no_face`.
* Filter cluster kecil (`min_faces_per_cluster`).

### Fase 4 – Ekstensi (Opsional / Skripsi)

* Incremental update (reuse embedding & cluster).
* Integrasi SQLite untuk metadata besar.
* Dashboard sederhana (FastAPI + UI).

---

## 15. Ringkasan

Phosor adalah **alat penyortir foto berbasis wajah** yang:

* Berjalan lokal & offline.
* Memanfaatkan UniFace sebagai engine deteksi & embedding.
* Menggunakan algoritma clustering untuk mengelompokkan wajah mirip.
* Menghasilkan struktur folder rapi per orang, plus metadata JSON/DB.

Dokumen ini mendefinisikan:

* Tujuan & ruang lingkup.
* Arsitektur & alur kerja.
* Tech stack yang lengkap (runtime, library, tooling).
* Desain modul & CLI.
* Roadmap implementasi.