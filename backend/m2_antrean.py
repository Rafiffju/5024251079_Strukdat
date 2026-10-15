# ======================================================================
# M2 - STACK & QUEUE
# ======================================================================
# Isi file ini:
#   1. Tumpukan (stack)       -> LIFO: yang terakhir masuk, keluar duluan
#   2. Kasir                  -> infix -> postfix -> hitung total (pakai stack)
#   3. AntreanNaif            -> queue di atas larik biasa, dequeue menggeser semua (lambat)
#   4. AntreanMelingkar       -> queue melingkar, dequeue hanya memajukan penunjuk (cepat)
#   5. SistemAntrean          -> dua antrean + undo/redo (pakai dua stack)
#
# Keputusan desain (wajib ditulis di README):   
#   - Antrean melingkar memakai `count` untuk membedakan KOSONG vs PENUH.
#   - Kalau penuh, enqueue membuat antrean TUMBUH 2x (bukan menolak).
#   - dequeue pada antrean kosong mengembalikan None.
# ======================================================================

from backend.m1_pesanan import Array, K_OID


# ======================================================================
# 1. TUMPUKAN (STACK) - dibangun di atas Array buatan sendiri
# ======================================================================
class Tumpukan:
    def __init__(self):
        self.larik = Array(8)

    def push(self, x):
        # taruh di puncak
        self.larik.append(x)

    def pop(self):
        # ambil dan buang elemen puncak
        if self.larik.jumlah == 0:
            raise IndexError("tumpukan kosong")
        return self.larik.pop()

    def peek(self):
        # lihat elemen puncak tanpa membuangnya
        if self.larik.jumlah == 0:
            raise IndexError("tumpukan kosong")
        return self.larik.get(self.larik.jumlah - 1)

    def kosong(self):
        return self.larik.jumlah == 0

    def kosongkan(self):
        self.larik = Array(8)

    def __len__(self):
        return self.larik.jumlah

    def ke_list(self):
        # isi tumpukan sebagai list biasa, urutan: dasar -> puncak (untuk ditampilkan)
        hasil = [None] * self.larik.jumlah
        for i in range(self.larik.jumlah):
            hasil[i] = self.larik.get(i)
        return hasil


# ======================================================================
# 2. KASIR: infix -> postfix -> total
# ======================================================================
def adalah_digit(c):
    return c >= "0" and c <= "9"


def adalah_operator(c):
    return c == "+" or c == "-" or c == "*" or c == "/"


def prioritas(op):
    # * dan / lebih kuat daripada + dan -
    if op == "*" or op == "/":
        return 2
    return 1


def pecah_token(ekspresi):
    # "( 3 * 12000 )" -> ["(", "3", "*", "12000", ")"]
    # Angka berdigit banyak harus jadi SATU token (12000, bukan 1,2,0,0,0).
    token = Array(16)
    angka = ""                 # penampung angka yang sedang dibaca
    sebelum = ""               # token terakhir yang sudah dimasukkan
    for c in ekspresi:         # `for c in teks` = ulangi untuk tiap karakter
        if adalah_digit(c):
            angka += c
            continue           # lanjut ke karakter berikutnya
        # karakter ini bukan digit -> kalau ada angka tertampung, simpan dulu
        if angka != "":
            token.append(angka)
            sebelum = angka
            angka = ""
        if c == " ":
            continue
        if c == "(" or c == ")" or adalah_operator(c):
            if c == "-" and (sebelum == "" or sebelum == "(" or adalah_operator(sebelum)):
                raise ValueError("operator '-' di depan angka tidak didukung; tulis (0 - x)")
            token.append(c)
            sebelum = c
        else:
            raise ValueError(f"karakter tidak dikenal: '{c}'")
    if angka != "":            # angka terakhir di ujung ekspresi
        token.append(angka)
    if token.jumlah == 0:
        raise ValueError("ekspresi kosong")
    return token


def gabung_spasi(daftar):
    # ["3", "12000", "*"] -> "3 12000 *"
    hasil = ""
    for x in daftar:
        if hasil != "":
            hasil += " "
        hasil += x
    return hasil


def ke_postfix_detail(ekspresi):
    # Aturan konversi (infix -> postfix) memakai stack operator:
    #   angka     -> langsung ke keluaran
    #   (         -> push ke stack
    #   )         -> pop sampai ketemu (, lalu buang (
    #   operator  -> pop dulu operator di puncak yang lebih kuat/sama kuat, baru push
    #   selesai   -> pop semua sisa stack ke keluaran
    # Mengembalikan: (keluaran postfix, tabel langkah untuk ditampilkan)
    token = pecah_token(ekspresi)
    stack = Tumpukan()
    keluar = Array(16)
    langkah = Array(16)

    for i in range(token.jumlah):
        t = token.get(i)

        if adalah_digit(t[0]):
            keluar.append(t)
            aksi = "angka, langsung keluar"

        elif t == "(":
            stack.push(t)
            aksi = "push ("

        elif t == ")":
            ketemu_buka = False
            while not stack.kosong():
                x = stack.pop()
                if x == "(":
                    ketemu_buka = True
                    break
                keluar.append(x)
            if not ketemu_buka:
                raise ValueError("kurung tutup ')' tanpa pasangan")
            aksi = "pop sampai (, buang ("

        else:   # operator
            diambil = ""
            while (not stack.kosong()) and stack.peek() != "(" \
                    and prioritas(stack.peek()) >= prioritas(t):
                x = stack.pop()
                keluar.append(x)
                diambil += x
            if diambil != "":
                aksi = f"pop {diambil} (lebih/sama kuat), push {t}"
            else:
                aksi = f"push {t}"
            stack.push(t)

        isi_stack = gabung_spasi(stack.ke_list())
        if isi_stack == "":
            isi_stack = "kosong"
        langkah.append((t, aksi, isi_stack, gabung_spasi(keluar.ke_larik())))

    # token habis: keluarkan semua sisa stack
    while not stack.kosong():
        x = stack.pop()
        if x == "(":
            raise ValueError("kurung buka '(' tanpa pasangan")
        keluar.append(x)
    langkah.append(("akhir", "pop sisa stack", "kosong", gabung_spasi(keluar.ke_larik())))
    return keluar, langkah


def ke_postfix(ekspresi):
    keluar, langkah = ke_postfix_detail(ekspresi)
    return keluar


def hitung_detail(postfix):
    # Evaluasi postfix memakai stack angka:
    #   angka    -> push
    #   operator -> pop dua angka, hitung, push hasilnya
    # PENTING: yang keluar PERTAMA adalah operand KANAN.
    #   b = pop() dulu, baru a = pop(), lalu hitung  a (operator) b
    # Kalau dibalik, + dan * tetap benar tapi - dan / jadi salah.
    # Mengembalikan: (hasil akhir, tabel langkah)
    stack = Tumpukan()
    langkah = Array(16)

    for i in range(postfix.jumlah):
        t = postfix.get(i)

        if adalah_digit(t[0]):
            stack.push(int(t))
            aksi = f"push {t}"
        else:
            if len(stack) < 2:
                raise ValueError(f"ekspresi tidak valid (operand kurang untuk '{t}')")
            b = stack.pop()        # operand kanan
            a = stack.pop()        # operand kiri
            if t == "+":
                r = a + b
            elif t == "-":
                r = a - b
            elif t == "*":
                r = a * b
            else:                  # pembagian
                if b == 0:
                    raise ValueError("pembagian dengan nol")
                if a % b == 0:
                    r = a // b     # habis dibagi -> hasil bulat
                else:
                    r = a / b      # tidak habis -> hasil desimal
            stack.push(r)
            aksi = f"pop {b} dan {a} -> {a} {t} {b} = {r}"

        isi = ""
        for x in stack.ke_list():
            if isi != "":
                isi += " "
            isi += str(x)
        langkah.append((t, aksi, isi))

    if len(stack) != 1:
        raise ValueError(f"ekspresi tidak valid (sisa {len(stack)} nilai di stack)")
    return stack.pop(), langkah


def hitung(postfix):
    hasil, langkah = hitung_detail(postfix)
    return hasil


def ribuan(n):
    # 1979950 -> "1.979.950" (titik pemisah ribuan gaya Indonesia)
    if n < 0:
        return "-" + ribuan(-n)
    s = str(n)
    hasil = ""
    for i in range(len(s)):
        sisa = len(s) - i
        if i > 0 and sisa % 3 == 0:
            hasil += "."
        hasil += s[i]
    return hasil


def rupiah(x):
    # 48000 -> "Rp 48.000"; 12.5 -> "Rp 12,50"
    tanda = ""
    if x < 0:
        tanda = "-"
        x = -x
    if x == int(x):
        return f"{tanda}Rp {ribuan(int(x))}"
    total_sen = int(round(x * 100))
    return f"{tanda}Rp {ribuan(total_sen // 100)},{total_sen % 100:02d}"


# ======================================================================
# 3. ANTREAN NAIF (larik biasa)
# ======================================================================
# dequeue = ambil elemen indeks 0, lalu SEMUA sisa digeser 1 langkah ke kiri.
# Untuk 20.000 pesanan, satu kali layanan = 20.000 penggeseran -> O(n).
class AntreanNaif:
    def __init__(self):
        self.larik = Array(16)
        self.total_geser = 0       # jumlah semua penggeseran (ditampilkan di UI)

    def __len__(self):
        return self.larik.jumlah

    def kosong(self):
        return self.larik.jumlah == 0

    def kapasitas(self):
        return self.larik.kapasitas()

    def enqueue(self, x):
        self.larik.append(x)       # masuk di belakang

    def dequeue(self):
        if self.larik.jumlah == 0:
            return None
        x = self.larik.hapus(0)    # hapus indeks 0 -> semua sisa bergeser
        self.total_geser += self.larik.langkah_terakhir
        return x

    def masuk_depan(self, x):
        # dipakai undo: kembalikan x ke DEPAN antrean
        self.larik.insert(0, x)
        self.total_geser += self.larik.langkah_terakhir

    def hapus_belakang(self):
        # dipakai undo: cabut elemen paling belakang
        if self.larik.jumlah == 0:
            return None
        return self.larik.pop()

    def get(self, i):
        return self.larik.get(i)

    def depan(self):
        if self.larik.jumlah == 0:
            return None
        return self.larik.get(0)


# ======================================================================
# 4. ANTREAN MELINGKAR (circular queue)
# ======================================================================
# Elemen tidak pernah digeser. Yang bergerak hanya dua penunjuk:
#   front = indeks elemen terdepan, rear = indeks slot kosong berikutnya.
# Kalau penunjuk sampai ujung larik, ia kembali ke 0 memakai operator % (modulo):
#       rear = (rear + 1) % K
# Kenapa perlu `count`? Kalau hanya front & rear, keadaan KOSONG dan PENUH
# sama-sama membuat front == rear -> tidak bisa dibedakan. Maka kita simpan count.
class AntreanMelingkar:
    def __init__(self, kapasitas=16):
        if kapasitas < 2:
            kapasitas = 2
        self.data = [None] * kapasitas
        self.K = kapasitas
        self.front = 0
        self.rear = 0
        self.count = 0
        self.total_geser = 0       # selalu 0; ada supaya sejajar dengan versi naif
        self.jumlah_tumbuh = 0

    def __len__(self):
        return self.count

    def kosong(self):
        return self.count == 0     # BUKAN front == rear

    def kapasitas(self):
        return self.K

    def tumbuh(self):
        # Penuh -> kapasitas 2x. Isi disalin berurutan mulai dari indeks 0
        # (urutan antrean dijaga, front dan rear di-reset).
        data_baru = [None] * (2 * self.K)
        for i in range(self.count):
            data_baru[i] = self.data[(self.front + i) % self.K]
        self.data = data_baru
        self.K = 2 * self.K
        self.front = 0
        self.rear = self.count
        self.jumlah_tumbuh += 1

    def enqueue(self, x):
        if self.count == self.K:
            self.tumbuh()
        self.data[self.rear] = x
        self.rear = (self.rear + 1) % self.K
        self.count += 1

    def dequeue(self):
        if self.count == 0:
            return None
        x = self.data[self.front]
        self.data[self.front] = None
        self.front = (self.front + 1) % self.K     # cuma majukan penunjuk
        self.count -= 1
        return x

    def masuk_depan(self, x):
        # dipakai undo: front mundur satu langkah, taruh x di situ
        if self.count == self.K:
            self.tumbuh()
        self.front = (self.front - 1) % self.K
        self.data[self.front] = x
        self.count += 1

    def hapus_belakang(self):
        # dipakai undo: rear mundur satu langkah, ambil elemen di situ
        if self.count == 0:
            return None
        self.rear = (self.rear - 1) % self.K
        x = self.data[self.rear]
        self.data[self.rear] = None
        self.count -= 1
        return x

    def get(self, i):
        if i < 0 or i >= self.count:
            raise IndexError("indeks di luar antrean")
        return self.data[(self.front + i) % self.K]

    def depan(self):
        if self.count == 0:
            return None
        return self.data[self.front]


# ======================================================================
# 5. UNDO / REDO
# ======================================================================
# Setiap aksi dicatat sebagai objek Aksi berisi:
#   jenis   : "ORDER", "ENQUEUE", atau "DEQUEUE"
#   antrean : "naif" / "circular" (untuk DEQUEUE), "keduanya" (ENQUEUE), "-" (ORDER)
#   data    : bahan untuk MEMBALIKKAN aksi
#             ORDER/ENQUEUE -> baris pesanannya
#             DEQUEUE       -> Array berisi SEMUA pesanan yang keluar
#                              (bukan cuma jumlahnya, supaya bisa dikembalikan)
class Aksi:
    def __init__(self, jenis, antrean, data):
        self.jenis = jenis
        self.antrean = antrean
        self.data = data


class SistemAntrean:
    # Menyimpan dua antrean berisi data SAMA, plus dua tumpukan: undo dan redo.
    #   aksi baru  : push ke undo, KOSONGKAN redo
    #   undo       : pop dari undo, jalankan kebalikannya, push ke redo
    #   redo       : pop dari redo, kerjakan aksi ASLINYA, push kembali ke undo
    def __init__(self, baris_antre, kapasitas_awal=16):
        self.naif = AntreanNaif()
        self.melingkar = AntreanMelingkar(kapasitas_awal)
        for baris in baris_antre:
            self.naif.enqueue(baris)
            self.melingkar.enqueue(baris)
        self.undo = Tumpukan()
        self.redo = Tumpukan()
        # Dua "hook": tempat menyimpan FUNGSI dari luar (diisi oleh frontend)
        # supaya aksi ORDER bisa mengubah data M1 tanpa file ini mengenal UI.
        self.hook_order_tambah = None
        self.hook_order_batal = None

    def pilih_antrean(self, nama):
        if nama == "naif":
            return self.naif
        return self.melingkar

    # ---------------- aksi yang bisa di-undo ----------------
    def order(self, baris):
        aksi = Aksi("ORDER", "-", baris)
        self.kerjakan(aksi)
        self.catat(aksi)

    def enqueue(self, baris):
        aksi = Aksi("ENQUEUE", "keduanya", baris)
        self.kerjakan(aksi)
        self.catat(aksi)

    def dequeue(self, nama, k):
        # Keluarkan sampai k pesanan dari antrean `nama`.
        # Mengembalikan (Array pesanan yang keluar, jumlah geseran).
        antrean = self.pilih_antrean(nama)
        geser_sebelum = antrean.total_geser
        keluar = Array(8)
        for _ in range(k):
            x = antrean.dequeue()
            if x is None:          # antrean sudah habis
                break
            keluar.append(x)
        if keluar.jumlah > 0:      # kalau tidak ada yang keluar, tidak perlu dicatat
            self.catat(Aksi("DEQUEUE", nama, keluar))
        return keluar, antrean.total_geser - geser_sebelum

    def catat(self, aksi):
        self.undo.push(aksi)
        self.redo.kosongkan()      # aksi baru -> riwayat bercabang, redo lama tidak berlaku

    # ---------------- mengerjakan & membalik aksi ----------------
    def kerjakan(self, aksi):
        # Mengerjakan aksi apa adanya (dipakai aksi baru dan redo).
        if aksi.jenis == "ENQUEUE":
            self.naif.enqueue(aksi.data)
            self.melingkar.enqueue(aksi.data)
        elif aksi.jenis == "DEQUEUE":
            antrean = self.pilih_antrean(aksi.antrean)
            for _ in range(aksi.data.jumlah):
                antrean.dequeue()
        else:   # ORDER
            if self.hook_order_tambah is not None:
                self.hook_order_tambah(aksi.data)

    def balik(self, aksi):
        # Menjalankan KEBALIKAN aksi (dipakai undo).
        if aksi.jenis == "ENQUEUE":
            self.naif.hapus_belakang()
            self.melingkar.hapus_belakang()
        elif aksi.jenis == "DEQUEUE":
            antrean = self.pilih_antrean(aksi.antrean)
            # Kembalikan ke DEPAN, mulai dari yang paling akhir keluar,
            # supaya urutan awalnya pulih persis.
            i = aksi.data.jumlah - 1
            while i >= 0:
                antrean.masuk_depan(aksi.data.get(i))
                i -= 1
        else:   # ORDER
            if self.hook_order_batal is not None:
                self.hook_order_batal(aksi.data)

    def undo_last(self):
        if self.undo.kosong():
            return None
        aksi = self.undo.pop()
        self.balik(aksi)
        self.redo.push(aksi)
        return aksi

    def redo_last(self):
        if self.redo.kosong():
            return None
        aksi = self.redo.pop()
        self.kerjakan(aksi)        # aksi ASLI, bukan kebalikannya
        self.undo.push(aksi)
        return aksi

    # ---------------- tampilan ----------------
    def deskripsi(self, aksi):
        if aksi.jenis == "DEQUEUE":
            return f"DEQUEUE x{aksi.data.jumlah} ({aksi.antrean})"
        return f"{aksi.jenis} {aksi.data[K_OID]}"

    def history(self):
        # Riwayat aksi yang sedang berlaku (terlama -> terbaru).
        # Diambil dari tumpukan undo, jadi pasti konsisten dengan undo_last().
        hasil = Array(8)
        for aksi in self.undo.ke_list():
            hasil.append(self.deskripsi(aksi))
        return hasil

    def stats(self):
        # Mengembalikan Array berisi pasangan (label, nilai)
        s = Array(8)
        s.append(("queue len naif", len(self.naif)))
        s.append(("queue len circular", len(self.melingkar)))
        s.append(("queue capacity naif", self.naif.kapasitas()))
        s.append(("queue capacity circular", self.melingkar.kapasitas()))
        s.append(("total geser naif", self.naif.total_geser))
        s.append(("total geser circular", self.melingkar.total_geser))
        s.append(("undo depth", len(self.undo)))
        s.append(("redo depth", len(self.redo)))
        return s
