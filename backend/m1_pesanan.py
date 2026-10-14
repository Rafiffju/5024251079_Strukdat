import csv

BELUM_SELESAI = 10 ** 12

K_OID = 0
K_PELANGGAN = 1
K_RESTO = 2
K_MENU = 3
K_HARGA = 4
K_PRIORITAS = 5
K_MASUK = 6
K_SELESAI = 7
K_STATUS = 8


def ke_baris(rec):
    selesai = rec[7]
    if selesai == "":
        nilai_selesai = BELUM_SELESAI
    else:
        nilai_selesai = int(selesai)
    return (rec[0], rec[1], rec[2], rec[3], int(rec[4]), int(rec[5]),
            int(rec[6]), nilai_selesai, rec[8])


def cek_indeks(i, batas):
    if i < 0 or i >= batas:
        raise IndexError(f"indeks {i} di luar jangkauan (0..{batas - 1})")


class Array:
    def __init__(self, kapasitas=4):
        if kapasitas < 1:
            kapasitas = 1
        self.isi = [None] * kapasitas
        self.jumlah = 0
        self.langkah_terakhir = 0
        self.total_salinan = 0
        self.jumlah_tumbuh = 0

    def __len__(self):
        return self.jumlah

    def kapasitas(self):
        return len(self.isi)

    def tumbuh(self):
        petak_baru = [None] * (2 * len(self.isi))
        for i in range(self.jumlah):
            petak_baru[i] = self.isi[i]
        self.total_salinan += self.jumlah
        self.jumlah_tumbuh += 1
        self.isi = petak_baru

    def append(self, nilai):
        if self.jumlah == len(self.isi):
            self.tumbuh()
        self.isi[self.jumlah] = nilai
        self.jumlah += 1
        self.langkah_terakhir = 0

    def insert(self, i, nilai):
        if i < 0 or i > self.jumlah:
            raise IndexError(f"posisi sisip {i} di luar 0..{self.jumlah}")
        if self.jumlah == len(self.isi):
            self.tumbuh()
        geser = 0
        j = self.jumlah
        while j > i:
            self.isi[j] = self.isi[j - 1]
            j -= 1
            geser += 1
        self.isi[i] = nilai
        self.jumlah += 1
        self.langkah_terakhir = geser

    def get(self, i):
        cek_indeks(i, self.jumlah)
        self.langkah_terakhir = 0
        return self.isi[i]

    def set(self, i, nilai):
        cek_indeks(i, self.jumlah)
        self.isi[i] = nilai

    def hapus(self, i):
        cek_indeks(i, self.jumlah)
        nilai = self.isi[i]
        geser = 0
        for j in range(i + 1, self.jumlah):
            self.isi[j - 1] = self.isi[j]
            geser += 1
        self.jumlah -= 1
        self.isi[self.jumlah] = None
        self.langkah_terakhir = geser
        return nilai

    def pop(self):
        return self.hapus(self.jumlah - 1)

    def tambah_reguler(self, baris):
        indeks = self.jumlah
        self.append(baris)
        return indeks

    def tambah_prioritas(self, baris):
        indeks = self.jumlah // 2
        self.insert(indeks, baris)
        return indeks

    def tambah_vip(self, baris):
        self.insert(0, baris)
        return 0

    def ke_larik(self):
        hasil = [None] * self.jumlah
        for i in range(self.jumlah):
            hasil[i] = self.isi[i]
        return hasil


class Simpul:
    def __init__(self, nilai, berikut=None):
        self.nilai = nilai
        self.berikut = berikut


class LinkList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.jumlah = 0
        self.langkah_terakhir = 0

    def __len__(self):
        return self.jumlah

    def append(self, nilai):
        simpul = Simpul(nilai)
        if self.tail is None:
            self.head = simpul
        else:
            self.tail.berikut = simpul
        self.tail = simpul
        self.jumlah += 1
        self.langkah_terakhir = 0

    def prepend(self, nilai):
        simpul = Simpul(nilai, self.head)
        self.head = simpul
        if self.tail is None:
            self.tail = simpul
        self.jumlah += 1
        self.langkah_terakhir = 0

    def insert(self, i, nilai):
        if i < 0 or i > self.jumlah:
            raise IndexError(f"posisi sisip {i} di luar 0..{self.jumlah}")
        if i == 0:
            self.prepend(nilai)
            return
        if i == self.jumlah:
            self.append(nilai)
            return
        p = self.head
        for _ in range(i - 1):
            p = p.berikut
        p.berikut = Simpul(nilai, p.berikut)
        self.jumlah += 1
        self.langkah_terakhir = i

    def get(self, i):
        cek_indeks(i, self.jumlah)
        p = self.head
        for _ in range(i):
            p = p.berikut
        self.langkah_terakhir = i
        return p.nilai

    def hapus(self, i):
        cek_indeks(i, self.jumlah)
        if i == 0:
            simpul = self.head
            self.head = simpul.berikut
            if self.head is None:
                self.tail = None
            self.jumlah -= 1
            self.langkah_terakhir = 0
            return simpul.nilai
        p = self.head
        for _ in range(i - 1):
            p = p.berikut
        simpul = p.berikut
        p.berikut = simpul.berikut
        if simpul is self.tail:
            self.tail = p
        self.jumlah -= 1
        self.langkah_terakhir = i
        return simpul.nilai

    def tambah_reguler(self, baris):
        indeks = self.jumlah
        self.append(baris)
        return indeks

    def tambah_prioritas(self, baris):
        indeks = self.jumlah // 2
        self.insert(indeks, baris)
        return indeks

    def tambah_vip(self, baris):
        self.prepend(baris)
        return 0

    def ke_larik(self):
        hasil = [None] * self.jumlah
        p = self.head
        i = 0
        while p is not None:
            hasil[i] = p.nilai
            p = p.berikut
            i += 1
        return hasil


def baca_pesanan(path):
    arr = Array(1024)
    with open(path, encoding="utf-8", newline="") as f:
        pembaca = csv.reader(f)
        next(pembaca)
        for rec in pembaca:
            if len(rec) >= 9:
                arr.append(ke_baris(rec))
    return arr


def isi_linklist(arr):
    ll = LinkList()
    for i in range(len(arr)):
        ll.append(arr.get(i))
    return ll
