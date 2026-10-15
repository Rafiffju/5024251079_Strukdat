# ======================================================================
# M1 - DATA PESANAN: ARRAY vs LINKED LIST
# ======================================================================
# Isi file ini:
#   1. Array
#   2. LinkList
#   3. baca_pesanan() dan isi_linklist() -> memuat file CSV ke kedua struktur
# ======================================================================

import csv

# Kalau pesanan belum selesai, kolom t_selesai kosong. saya isi angka
# sangat besar supaya tetap bisa dibandingkan/diurutkan (ditaruh paling akhir).
BELUM_SELESAI = 10 ** 12

# Satu pesanan disimpan sebagai TUPLE (mirip struct yang isinya tidak bisa diubah).
# Konstanta di bawah = nomor urut tiap kolom di dalam tuple itu.
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
    # rec = satu baris CSV berupa list of string, misal ["O-000001", "Rahmi", ...]
    # Saya ubah menjadi tuple, dan kolom angka diubah dari string ke int.
    selesai = rec[7]
    if selesai == "":
        nilai_selesai = BELUM_SELESAI
    else:
        nilai_selesai = int(selesai)
    return (rec[0], rec[1], rec[2], rec[3], int(rec[4]), int(rec[5]),
            int(rec[6]), nilai_selesai, rec[8])


def cek_indeks(i, batas):
    # Dipakai get() dan hapus(): indeks harus 0 .. batas-1
    if i < 0 or i >= batas:
        raise IndexError(f"indeks {i} di luar jangkauan (0..{batas - 1})")


# ======================================================================
# 1. ARRAY
# ======================================================================
class Array:
    def __init__(self, kapasitas=4):
        if kapasitas < 1:
            kapasitas = 1
        self.isi = [None] * kapasitas   # petak memorinya
        self.jumlah = 0                 # berapa elemen yang benar-benar terisi
        self.langkah_terakhir = 0       # untuk ditampilkan di UI
        self.total_salinan = 0          # total elemen yang pernah disalin saat membesar
        self.jumlah_tumbuh = 0          # sudah berapa kali membesar

    def __len__(self):
        # Fungsi khusus: supaya len(arr) bisa dipakai, seperti arr.size() di C++
        return self.jumlah

    def kapasitas(self):
        return len(self.isi)

    def tumbuh(self):
        # Petak penuh -> bikin petak baru 2x lebih besar, lalu salin satu per satu.
        petak_baru = [None] * (2 * len(self.isi))
        for i in range(self.jumlah):
            petak_baru[i] = self.isi[i]
        self.total_salinan += self.jumlah
        self.jumlah_tumbuh += 1
        self.isi = petak_baru

    def append(self, nilai):
        # Tambah di belakang. Hanya menyalin kalau petak penuh.
        if self.jumlah == len(self.isi):
            self.tumbuh()
        self.isi[self.jumlah] = nilai
        self.jumlah += 1
        self.langkah_terakhir = 0

    def insert(self, i, nilai):
        # Sisipkan di indeks i. Elemen i..akhir harus digeser 1 langkah ke kanan.
        # Makin dekat ke depan, makin banyak yang digeser -> O(n).
        if i < 0 or i > self.jumlah:
            raise IndexError(f"posisi sisip {i} di luar 0..{self.jumlah}")
        if self.jumlah == len(self.isi):
            self.tumbuh()
        geser = 0
        j = self.jumlah
        while j > i:                       # geser dari belakang supaya tidak menimpa
            self.isi[j] = self.isi[j - 1]
            j -= 1
            geser += 1
        self.isi[i] = nilai
        self.jumlah += 1
        self.langkah_terakhir = geser

    def get(self, i):
        # Ambil elemen ke-i. Alamatnya bisa dihitung langsung -> O(1).
        cek_indeks(i, self.jumlah)
        self.langkah_terakhir = 0
        return self.isi[i]

    def set(self, i, nilai):
        cek_indeks(i, self.jumlah)
        self.isi[i] = nilai

    def hapus(self, i):
        # Cabut elemen ke-i, lalu geser sisanya 1 langkah ke kiri -> O(n).
        cek_indeks(i, self.jumlah)
        nilai = self.isi[i]
        geser = 0
        for j in range(i + 1, self.jumlah):
            self.isi[j - 1] = self.isi[j]
            geser += 1
        self.jumlah -= 1
        self.isi[self.jumlah] = None       # kosongkan slot terakhir
        self.langkah_terakhir = geser
        return nilai

    def pop(self):
        # Cabut elemen paling belakang (tidak ada yang digeser -> O(1)).
        return self.hapus(self.jumlah - 1)

    def tambah_reguler(self, baris):
        # Pesanan REGULER: paling belakang. Mengembalikan indeks tempat masuk.
        indeks = self.jumlah
        self.append(baris)
        return indeks

    def tambah_prioritas(self, baris):
        # Pesanan PRIORITAS: di tengah barisan.
        indeks = self.jumlah // 2
        self.insert(indeks, baris)
        return indeks

    def tambah_vip(self, baris):
        # Pesanan VIP: paling depan (indeks 0).
        self.insert(0, baris)
        return 0

    def ke_larik(self):
        # Salinan isi sebagai list biasa berukuran pas (dipakai M3 untuk sorting).
        hasil = [None] * self.jumlah
        for i in range(self.jumlah):
            hasil[i] = self.isi[i]
        return hasil


# ======================================================================
# 2. LINKED LIST
# ======================================================================
# Tiap pesanan dibungkus satu Simpul: menyimpan nilai + alamat simpul berikutnya.
# Tidak ada yang perlu digeser saat menyisip, tapi untuk menuju posisi ke-i kita
# harus berjalan dari head satu per satu (tidak ada alamat yang bisa dihitung).
class Simpul:
    def __init__(self, nilai, berikut=None):
        self.nilai = nilai
        self.berikut = berikut     # None = akhir rantai (seperti nullptr)


class LinkList:
    def __init__(self):
        self.head = None           # simpul pertama
        self.tail = None           # simpul terakhir (disimpan agar append tetap O(1))
        self.jumlah = 0
        self.langkah_terakhir = 0

    def __len__(self):
        return self.jumlah

    def append(self, nilai):
        # Tambah di belakang lewat tail -> O(1), tidak perlu menelusuri.
        simpul = Simpul(nilai)
        if self.tail is None:      # list masih kosong
            self.head = simpul
        else:
            self.tail.berikut = simpul
        self.tail = simpul
        self.jumlah += 1
        self.langkah_terakhir = 0

    def prepend(self, nilai):
        # Tambah di depan -> O(1): cukup ubah satu penunjuk (head).
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
        # Kasus tengah: berjalan sampai simpul SEBELUM posisi i, lalu sambung.
        p = self.head
        for _ in range(i - 1):     # `_` = nama variabel yang tidak di pakai
            p = p.berikut          # setara p = p->next di C++
        p.berikut = Simpul(nilai, p.berikut)
        self.jumlah += 1
        self.langkah_terakhir = i

    def get(self, i):
        # Ambil simpul ke-i: harus berjalan dari head -> O(n).
        cek_indeks(i, self.jumlah)
        p = self.head
        for _ in range(i):
            p = p.berikut
        self.langkah_terakhir = i
        return p.nilai

    def hapus(self, i):
        cek_indeks(i, self.jumlah)
        if i == 0:                         # hapus head
            simpul = self.head
            self.head = simpul.berikut
            if self.head is None:          # list jadi kosong
                self.tail = None
            self.jumlah -= 1
            self.langkah_terakhir = 0
            return simpul.nilai
        # Jalan sampai simpul SEBELUM yang dihapus
        p = self.head
        for _ in range(i - 1):
            p = p.berikut
        simpul = p.berikut                 # simpul yang akan dicabut
        p.berikut = simpul.berikut         # lewati simpul itu
        if simpul is self.tail:            # kalau yang dihapus ujung belakang
            self.tail = p                  # tail harus mundur satu
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
        # Salin isi ke list biasa dengan SATU kali penelusuran.
        hasil = [None] * self.jumlah
        p = self.head
        i = 0
        while p is not None:
            hasil[i] = p.nilai
            p = p.berikut
            i += 1
        return hasil


# ======================================================================
# 3. MEMUAT FILE CSV
# ======================================================================
# Saya pakai modul csv (bukan split(",")) karena ada nama yang memuat koma
# di dalam tanda kutip, contoh: "Oskar Puspita, S.Sos".
def baca_pesanan(path):
    arr = Array(1024)
    with open(path, encoding="utf-8", newline="") as f:   # `with` = otomatis menutup file
        pembaca = csv.reader(f)
        next(pembaca)                  # lewati baris header (oid,pelanggan,...)
        for rec in pembaca:
            if len(rec) >= 9:          # lewati baris kosong/rusak
                arr.append(ke_baris(rec))
    return arr


def isi_linklist(arr):
    # Isi LinkList dengan data yang SAMA persis (urutan sama) dengan Array.
    ll = LinkList()
    for i in range(len(arr)):
        ll.append(arr.get(i))
    return ll
