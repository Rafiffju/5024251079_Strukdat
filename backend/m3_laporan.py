import time

from backend.m1_pesanan import K_OID, K_HARGA, K_SELESAI

BATAS_INSERTION = 20000


class DataTerlaluBesar(ValueError):
    pass


class Hitung:
    def __init__(self):
        self.perbandingan = 0
        self.pemindahan = 0


def indeks_kunci(nama):
    if nama == "oid":
        return K_OID
    if nama == "harga":
        return K_HARGA
    if nama == "selesai":
        return K_SELESAI
    raise ValueError("kunci harus salah satu dari: oid, harga, selesai")


def salin(A):
    B = [None] * len(A)
    for i in range(len(A)):
        B[i] = A[i]
    return B


def insertion_sort(A, kunci, hitung=None):
    if hitung is None:
        hitung = Hitung()
    for i in range(1, len(A)):
        x = A[i]
        kunci_x = x[kunci]
        j = i - 1
        while j >= 0:
            hitung.perbandingan += 1
            if A[j][kunci] > kunci_x:
                A[j + 1] = A[j]
                hitung.pemindahan += 1
                j -= 1
            else:
                break
        A[j + 1] = x
        hitung.pemindahan += 1
    return A


def gabung(A, bantu, awal, tengah, akhir, kunci, hitung):
    i = awal
    j = tengah
    t = awal

    while i < tengah and j < akhir:
        hitung.perbandingan += 1
        if A[i][kunci] <= A[j][kunci]:
            bantu[t] = A[i]
            i += 1
        else:
            bantu[t] = A[j]
            j += 1
        t += 1
        hitung.pemindahan += 1

    while i < tengah:
        bantu[t] = A[i]
        i += 1
        t += 1
        hitung.pemindahan += 1

    while j < akhir:
        bantu[t] = A[j]
        j += 1
        t += 1
        hitung.pemindahan += 1

    for t in range(awal, akhir):
        A[t] = bantu[t]
        hitung.pemindahan += 1


def urut_bagi(A, bantu, awal, akhir, kunci, hitung):
    if akhir - awal < 2:
        return
    tengah = (awal + akhir) // 2
    urut_bagi(A, bantu, awal, tengah, kunci, hitung)
    urut_bagi(A, bantu, tengah, akhir, kunci, hitung)
    gabung(A, bantu, awal, tengah, akhir, kunci, hitung)


def merge_sort(A, kunci, hitung=None):
    if hitung is None:
        hitung = Hitung()
    B = salin(A)
    bantu = [None] * len(B)
    urut_bagi(B, bantu, 0, len(B), kunci, hitung)
    return B


def linear_search(A, target, kunci, hitung=None):
    if hitung is None:
        hitung = Hitung()
    for i in range(len(A)):
        hitung.perbandingan += 1
        if A[i][kunci] == target:
            return i
    return -1


def binary_search(A, target, kunci, hitung=None):
    if hitung is None:
        hitung = Hitung()
    kiri = 0
    kanan = len(A) - 1
    while kiri <= kanan:
        tengah = (kiri + kanan) // 2
        hitung.perbandingan += 1
        nilai = A[tengah][kunci]
        if nilai == target:
            return tengah
        if nilai < target:
            kiri = tengah + 1
        else:
            kanan = tengah - 1
    return -1


def cek_terurut(A, kunci):
    for i in range(1, len(A)):
        if A[i - 1][kunci] > A[i][kunci]:
            return False
    return True


def cek_stabil(A, kunci):
    for i in range(1, len(A)):
        if A[i - 1][kunci] == A[i][kunci] and A[i - 1][K_OID] > A[i][K_OID]:
            return False
    return True


class LaporanHarian:
    def __init__(self, baris):
        self.baris = baris
        self.terurut_oid = None
        self.biaya_bangun = None

    def ambil(self, n):
        if n < 1 or n > len(self.baris):
            raise ValueError(f"jumlah harus 1..{len(self.baris)}")
        B = [None] * n
        for i in range(n):
            B[i] = self.baris[i]
        return B

    def urutkan(self, algoritma, n, nama_kunci):
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
