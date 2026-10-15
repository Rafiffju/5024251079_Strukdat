# ======================================================================
# M3 - SORT & SEARCH (laporan harian + cari pesanan)
# ======================================================================
# Empat algoritma, semuanya MENCATAT jumlah perbandingan lewat objek `Hitung`:
#
#   insertion_sort   stabil, di tempat          O(n^2)
#   merge_sort       stabil, butuh buffer       O(n log n)
#   linear_search    tidak butuh data terurut   O(n)
#   binary_search    data WAJIB terurut         O(log n)
#
# Kenapa menghitung perbandingan, bukan hanya waktu? Waktu tergantung komputer,
# tapi jumlah perbandingan SAMA di komputer siapa pun -> itulah bukti O(n^2)
# vs O(n log n).
#
# Data yang diurutkan = list biasa berisi tuple pesanan (lihat m1_pesanan.py).
# Parameter `kunci` = NOMOR kolom yang dijadikan patokan (K_OID, K_HARGA, K_SELESAI).
# ======================================================================

import time

from backend.m1_pesanan import K_OID, K_HARGA, K_SELESAI

BATAS_INSERTION = 20000   # insertion sort menolak data lebih dari ini (terlalu lambat)


class DataTerlaluBesar(ValueError):
    # Jenis error khusus supaya UI bisa menampilkan pesan penolakan dengan rapi.
    pass


class Hitung:
    # Papan skor sederhana yang "dititipkan" ke algoritma.
    def __init__(self):
        self.perbandingan = 0
        self.pemindahan = 0


def indeks_kunci(nama):
    # "harga" -> K_HARGA, dst. Dipakai saat nama kunci datang dari UI (berupa teks).
    if nama == "oid":
        return K_OID
    if nama == "harga":
        return K_HARGA
    if nama == "selesai":
        return K_SELESAI
    raise ValueError("kunci harus salah satu dari: oid, harga, selesai")


def salin(A):
    # Menyalin list ke list baru (elemen satu per satu).
    B = [None] * len(A)
    for i in range(len(A)):
        B[i] = A[i]
    return B


# ======================================================================
# INSERTION SORT - seperti merapikan kartu di tangan
# ======================================================================
# Ambil elemen berikutnya, geser ke kiri melewati semua elemen yang LEBIH BESAR,
# lalu letakkan di tempatnya. Data besar & acak -> lambat (O(n^2)).
# STABIL: syarat menggeser memakai ">" (bukan ">="), jadi dua data berkunci sama
# tidak pernah bertukar tempat.
def insertion_sort(A, kunci, hitung=None):
    if hitung is None:             # kalau pemanggil tidak memberi papan skor, bikin sendiri
        hitung = Hitung()
    for i in range(1, len(A)):
        x = A[i]                   # elemen yang mau disisipkan
        kunci_x = x[kunci]
        j = i - 1
        while j >= 0:
            hitung.perbandingan += 1
            if A[j][kunci] > kunci_x:      # lebih besar -> geser ke kanan
                A[j + 1] = A[j]
                hitung.pemindahan += 1
                j -= 1
            else:                           # sudah ketemu tempatnya
                break
        A[j + 1] = x
        hitung.pemindahan += 1
    return A


# ======================================================================
# MERGE SORT - belah dua terus-menerus, lalu gabungkan yang sudah rapi
# ======================================================================
# Kedalaman pembelahan = log n, tiap tingkat menggabung O(n) -> O(n log n).
# Dua kesalahan langganan:
#   1. lupa menyalin SISA salah satu bagian setelah loop utama -> data hilang
#   2. memakai "<" bukan "<=" saat membandingkan -> tidak stabil
def gabung(A, bantu, awal, tengah, akhir, kunci, hitung):
    # Menggabung dua bagian yang sudah terurut:
    #   bagian kiri  = A[awal .. tengah-1]
    #   bagian kanan = A[tengah .. akhir-1]
    # Hasil ditulis dulu ke list `bantu`, lalu disalin balik ke A.
    i = awal                   # penunjuk bagian kiri
    j = tengah                 # penunjuk bagian kanan
    t = awal                   # penunjuk tempat menulis di `bantu`

    while i < tengah and j < akhir:
        hitung.perbandingan += 1
        if A[i][kunci] <= A[j][kunci]:     # "<=" -> kiri didahulukan saat sama (stabil)
            bantu[t] = A[i]
            i += 1
        else:
            bantu[t] = A[j]
            j += 1
        t += 1
        hitung.pemindahan += 1

    while i < tengah:          # sisa bagian kiri
        bantu[t] = A[i]
        i += 1
        t += 1
        hitung.pemindahan += 1

    while j < akhir:           # sisa bagian kanan
        bantu[t] = A[j]
        j += 1
        t += 1
        hitung.pemindahan += 1

    for t in range(awal, akhir):           # salin hasil gabungan kembali ke A
        A[t] = bantu[t]
        hitung.pemindahan += 1


def urut_bagi(A, bantu, awal, akhir, kunci, hitung):
    # Mengurutkan A[awal .. akhir-1]. Fungsi ini memanggil DIRINYA SENDIRI (rekursi).
    if akhir - awal < 2:       # 0 atau 1 elemen: sudah terurut, berhenti
        return
    tengah = (awal + akhir) // 2
    urut_bagi(A, bantu, awal, tengah, kunci, hitung)     # urutkan separuh kiri
    urut_bagi(A, bantu, tengah, akhir, kunci, hitung)    # urutkan separuh kanan
    gabung(A, bantu, awal, tengah, akhir, kunci, hitung)


def merge_sort(A, kunci, hitung=None):
    # Mengembalikan list BARU yang terurut. List A asli tidak berubah.
    if hitung is None:
        hitung = Hitung()
    B = salin(A)
    bantu = [None] * len(B)
    urut_bagi(B, bantu, 0, len(B), kunci, hitung)
    return B


# ======================================================================
# PENCARIAN
# ======================================================================
def linear_search(A, target, kunci, hitung=None):
    # Cek satu per satu dari depan. Mengembalikan indeks, atau -1 kalau tidak ada.
    if hitung is None:
        hitung = Hitung()
    for i in range(len(A)):
        hitung.perbandingan += 1
        if A[i][kunci] == target:
            return i
    return -1


def binary_search(A, target, kunci, hitung=None):
    # Data A WAJIB sudah terurut menurut `kunci`.
    # Tiap langkah: lihat elemen tengah, buang separuh yang pasti bukan jawabannya.
    if hitung is None:
        hitung = Hitung()
    kiri = 0
    kanan = len(A) - 1
    while kiri <= kanan:                   # perhatikan: <= , bukan <
        tengah = (kiri + kanan) // 2
        hitung.perbandingan += 1           # 1 langkah = 1 perbandingan
        nilai = A[tengah][kunci]
        if nilai == target:
            return tengah
        if nilai < target:                 # target ada di sebelah kanan
            kiri = tengah + 1
        else:                              # target ada di sebelah kiri
            kanan = tengah - 1
    return -1


# ======================================================================
# PEMERIKSA HASIL (dipakai UI untuk menulis "terurut: ya / stabil: ya")
# ======================================================================
def cek_terurut(A, kunci):
    for i in range(1, len(A)):
        if A[i - 1][kunci] > A[i][kunci]:
            return False
    return True


def cek_stabil(A, kunci):
    # Data asli terurut menaik menurut oid (urutan file). Jadi pada kunci yang
    # sama, oid HARUS tetap menaik kalau pengurutannya stabil.
    for i in range(1, len(A)):
        if A[i - 1][kunci] == A[i][kunci] and A[i - 1][K_OID] > A[i][K_OID]:
            return False
    return True


# ======================================================================
# LAYANAN LAPORAN HARIAN
# ======================================================================
class LaporanHarian:
    def __init__(self, baris):
        self.baris = baris             # semua pesanan (urutan file)
        self.terurut_oid = None        # daftar KHUSUS terurut oid, dibangun sekali saja
        self.biaya_bangun = None       # (detik, jumlah perbandingan) saat membangunnya

    def ambil(self, n):
        # Salin n pesanan pertama ke list baru.
        if n < 1 or n > len(self.baris):
            raise ValueError(f"jumlah harus 1..{len(self.baris)}")
        B = [None] * n
        for i in range(n):
            B[i] = self.baris[i]
        return B

    def urutkan(self, algoritma, n, nama_kunci):
        # Mengembalikan (hasil terurut, papan skor Hitung, lama detik).
        kunci = indeks_kunci(nama_kunci)
        hitung = Hitung()
        A = self.ambil(n)
        if algoritma == "insertion":
            if n > BATAS_INSERTION:
                raise DataTerlaluBesar(
                    f"DITOLAK: batasnya {BATAS_INSERTION} baris, pakai merge sort untuk data penuh")
            mulai = time.perf_counter()
            insertion_sort(A, kunci, hitung)
        else:
            mulai = time.perf_counter()
            A = merge_sort(A, kunci, hitung)
        lama = time.perf_counter() - mulai
        return A, hitung, lama

    def siapkan_oid(self):
        # Membangun daftar terurut-oid SEKALI (pakai merge sort).
        # Mengembalikan True kalau baru dibangun, False kalau sudah ada.
        # Binary search baru "untung" kalau daftar ini dipakai mencari berkali-kali,
        # sebab membangunnya jauh lebih mahal daripada satu kali linear search.
        if self.terurut_oid is not None:
            return False
        hitung = Hitung()
        mulai = time.perf_counter()
        self.terurut_oid = merge_sort(self.baris, K_OID, hitung)
        lama = time.perf_counter() - mulai
        self.biaya_bangun = (lama, hitung.perbandingan)
        return True

    def cari_linear_oid(self, oid):
        hitung = Hitung()
        mulai = time.perf_counter()
        i = linear_search(self.baris, oid, K_OID, hitung)
        lama = time.perf_counter() - mulai
        return i, hitung, lama

    def cari_biner_oid(self, oid):
        hitung = Hitung()
        mulai = time.perf_counter()
        i = binary_search(self.terurut_oid, oid, K_OID, hitung)
        lama = time.perf_counter() - mulai
        return i, hitung, lama
