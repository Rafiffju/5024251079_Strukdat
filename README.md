# 2EZ4U APP - Mini Delivery Engine (M1-M3)

Muhammad Rafif Izzuddin - 5024251079

## 1. Cara menjalankan

```bash
python app.py
```

## 2. Struktur repositori

```
2ez4u/
|-- README.md
|-- app.py                     <- python app.py
|-- data/  pesanan.csv  peta.csv
|-- backend/
|   |-- m1_pesanan.py          Array (kapasitas x2) + LinkList (head/tail) + pemuat CSV
|   |-- m2_antrean.py          Tumpukan, kasir infix->postfix->total, AntreanNaif, AntreanMelingkar, SistemAntrean (undo/redo)
|   |-- m3_laporan.py          insertion_sort, merge_sort, linear_search, binary_search, Hitung, LaporanHarian
|-- frontend/
|   |-- ui.py                  jendela Tkinter (menu kiri, form+hasil kanan, panel COMMAND bawah)
|   |-- perintah.py            jembatan UI <-> backend (tanpa Tkinter, bisa diuji headless)
```

## 3. M1 - Array vs Linked List

Data yang sama disimpan pada `Array` dan `LinkList`, keduanya melayani lima operasi yang sama (`get`, `tambah_reguler/prioritas/vip`, `hapus`). Tiga jenis pesanan = tiga titik sisip: REGULER di belakang (`append`), PRIORITAS di tengah (`insert(n//2)`), VIP di depan (`insert(0)`).

* **Array**: petak `[None] * kapasitas`. Penuh -> petak baru **2x**, salin sekali. Biaya total salin `< 2n` (diuji di `test_tumbuh_dua_kali_dan_amortized`), jadi `append` amortized O(1).
* **LinkList**: simpul + `head` + **`tail`** (tanpa `tail`, REGULER jadi O(n)). `prepend` hanya mengubah satu penunjuk.
* Setiap operasi menyimpan `langkah_terakhir` (elemen digeser / simpul ditelusuri) sehingga yang ditampilkan angka, bukan hanya milidetik.
* Pemuat memakai `csv.reader` karena nama pelanggan bisa memuat koma di dalam tanda kutip (`"Oskar Puspita, S.Sos"`). `t_selesai` kosong disimpan sebagai sentinel `BELUM_SELESAI = 10**12` (tampil `-`).

Hasil pada 200.000 baris (lihat tabel M1 di bagian 8): PRIORITAS hampir seimbang (Array menggeser 100.000 elemen, LinkList menelusuri 100.000 simpul), VIP Array ~9 ms vs LinkList ~0,01 ms, LIHAT ke-i Array 0 langkah vs LinkList ke-i langkah.

## 4. M2 - Stack & Queue

**Kasir.** `pecah_token` -> `ke_postfix` (stack operator) -> `hitung` (stack angka). Angka multi-digit satu token; `(` hanya mengatur stack dan tidak pernah keluar; operator mengeluarkan operator puncak yang *lebih kuat atau sama kuat* (asosiatif kiri). Pada evaluasi, **`b = pop()` dulu, lalu `a = pop()`, hitung `a - b`** (diuji khusus `10 - 4 = 6`, `20 / 4 = 5`). `( 3 * 12000 ) + ( 2 * 8500 ) - 5000` -> `3 12000 * 2 8500 * + 5000 -` -> **Rp 48.000**. Ekspresi salah (kurung tak berpasangan, operand kurang, bagi nol, unary minus) menghasilkan `ValueError` dengan pesan, bukan crash.

**Dua antrean, isi identik** (19.850 pesanan `ANTRE`):

* `AntreanNaif` - larik + hapus indeks 0, menggeser seluruh sisa; `total_geser` dihitung.
* `AntreanMelingkar` - `data, front, rear, count`, indeks `(i+1) % K`; `dequeue` hanya memajukan `front`.

Keputusan yang diminta soal:

1. **Kosong vs penuh**: memakai pencacah **`count`** (bukan `front == rear`, yang bernilai benar pada kedua keadaan; ada tesnya).
2. **Enqueue saat penuh**: **tumbuh** (kapasitas x2, isi diluruskan dari indeks 0), bukan menolak. Dari kapasitas awal 16, 19.850 pesanan berakhir pada kapasitas 32.768.
3. **Dequeue saat kosong**: mengembalikan `None`.
4. Uji terpenting: kapasitas `K = 4`, masuk 3, keluar 2, masuk 3 lagi -> penunjuk berputar dan isi tetap benar (`test_melingkar_putar_K4`); ditambah uji acak 5.000 operasi naif vs circular vs referensi list.

**Undo/redo** (dua `Tumpukan`). Catatan menyimpan *yang dibutuhkan untuk membalik*, bukan hitungannya:

| Aksi        | Disimpan                                            | Kebalikan saat undo                                                                     |
| ----------- | --------------------------------------------------- | --------------------------------------------------------------------------------------- |
| `ORDER`   | baris pesanan                                       | pesanan dicabut dari Array & LinkList (M1)                                              |
| `ENQUEUE` | baris                                               | keluarkan dari **belakang** kedua antrean                                         |
| `DEQUEUE` | **daftar** pesanan yang keluar + nama antrean | kembalikan seluruhnya ke **depan** (dari yang terakhir keluar), urutan asli pulih |

`redo_last()` mengerjakan **aksi aslinya**; aksi baru apa pun **mengosongkan redo** (riwayat bercabang). `history()` mengembalikan isi tumpukan undo, jadi selalu konsisten dengan `undo_last()`. `stats()` memuat queue len kedua versi, capacity, total geser, undo depth, redo depth.

## 5. M3 - Sort & Search

| Algoritma          | Stabil                      | Kompleksitas         | Alasan dipilih                                                                                    |
| ------------------ | --------------------------- | -------------------- | ------------------------------------------------------------------------------------------------- |
| `insertion_sort` | ya (geser hanya bila `>`) | O(n^2), terbaik O(n) | sederhana, bagus untuk data kecil / hampir terurut; **ditolak > 20.000 baris** dengan pesan |
| `merge_sort`     | ya (ambil kiri bila `<=`) | O(n log n) selalu    | sanggup mengurutkan 200.000 baris; sisa kiri/kanan disalin setelah loop utama                     |
| `linear_search`  | -                           | O(n)                 | tanpa syarat; benar untuk pencarian sekali-dua kali                                               |
| `binary_search`  | -                           | O(log n)             | butuh data terurut menurut **kunci yang dicari**                                            |

* Semua algoritma menerima objek **`Hitung`** (pencacah perbandingan & pemindahan) yang dititipkan -> angka sama di komputer mana pun.
* Laporan harian terurut menurut `selesai` (pesanan belum selesai memakai sentinel sehingga berada di akhir). Karena itu **binary search oid memakai daftar terpisah terurut-oid**, dibangun **sekali** dengan merge sort; biayanya dilaporkan terang-terangan di menu (+/- 0,5 detik, 1.730.048 perbandingan) dan baru "untung" bila dicari berulang kali.
* Menu menampilkan `terurut: ya/tidak` dan `stabil: ya/tidak` (diperiksa otomatis).
* Menu "BANDINGKAN n vs PERBANDINGAN" menjalankan kedua sort pada beberapa n sekaligus.

Cek angka dengan contoh di soal: 10 baris kunci harga -> **24 perbandingan, 25 pemindahan**; n=2.000 -> **962.430** vs **19.240**; n=4.000 -> **3.831.520** vs **42.355**; n=200.000 merge -> **3.226.139**; search `O-137442` -> 137.442 vs 17.
