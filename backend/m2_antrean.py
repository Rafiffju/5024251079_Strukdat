from backend.m1_pesanan import Array, K_OID


class Tumpukan:
    def __init__(self):
        self.larik = Array(8)

    def push(self, x):
        self.larik.append(x)

    def pop(self):
        if self.larik.jumlah == 0:
            raise IndexError("tumpukan kosong")
        return self.larik.pop()

    def peek(self):
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
        hasil = [None] * self.larik.jumlah
        for i in range(self.larik.jumlah):
            hasil[i] = self.larik.get(i)
        return hasil


def adalah_digit(c):
    return c >= "0" and c <= "9"


def adalah_operator(c):
    return c == "+" or c == "-" or c == "*" or c == "/"


def prioritas(op):
    if op == "*" or op == "/":
        return 2
    return 1


def pecah_token(ekspresi):
    token = Array(16)
    angka = ""
    sebelum = ""
    for c in ekspresi:
        if adalah_digit(c):
            angka += c
            continue
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
    if angka != "":
        token.append(angka)
    if token.jumlah == 0:
        raise ValueError("ekspresi kosong")
    return token


def gabung_spasi(daftar):
    hasil = ""
    for x in daftar:
        if hasil != "":
            hasil += " "
        hasil += x
    return hasil


def ke_postfix_detail(ekspresi):
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

        else:
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
            b = stack.pop()
            a = stack.pop()
            if t == "+":
                r = a + b
            elif t == "-":
                r = a - b
            elif t == "*":
                r = a * b
            else:
                if b == 0:
                    raise ValueError("pembagian dengan nol")
                if a % b == 0:
                    r = a // b
                else:
                    r = a / b
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
    tanda = ""
    if x < 0:
        tanda = "-"
        x = -x
    if x == int(x):
        return f"{tanda}Rp {ribuan(int(x))}"
    total_sen = int(round(x * 100))
    return f"{tanda}Rp {ribuan(total_sen // 100)},{total_sen % 100:02d}"


class AntreanNaif:
    def __init__(self):
        self.larik = Array(16)
        self.total_geser = 0

    def __len__(self):
        return self.larik.jumlah

    def kosong(self):
        return self.larik.jumlah == 0

    def kapasitas(self):
        return self.larik.kapasitas()

    def enqueue(self, x):
        self.larik.append(x)

    def dequeue(self):
        if self.larik.jumlah == 0:
            return None
        x = self.larik.hapus(0)
        self.total_geser += self.larik.langkah_terakhir
        return x

    def masuk_depan(self, x):
        self.larik.insert(0, x)
        self.total_geser += self.larik.langkah_terakhir

    def hapus_belakang(self):
        if self.larik.jumlah == 0:
            return None
        return self.larik.pop()

    def get(self, i):
        return self.larik.get(i)

    def depan(self):
        if self.larik.jumlah == 0:
            return None
        return self.larik.get(0)


class AntreanMelingkar:
    def __init__(self, kapasitas=16):
        if kapasitas < 2:
            kapasitas = 2
        self.data = [None] * kapasitas
        self.K = kapasitas
        self.front = 0
        self.rear = 0
        self.count = 0
        self.total_geser = 0
        self.jumlah_tumbuh = 0

    def __len__(self):
        return self.count

    def kosong(self):
        return self.count == 0

    def kapasitas(self):
        return self.K

    def tumbuh(self):
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
        self.front = (self.front + 1) % self.K
        self.count -= 1
        return x

    def masuk_depan(self, x):
        if self.count == self.K:
            self.tumbuh()
        self.front = (self.front - 1) % self.K
        self.data[self.front] = x
        self.count += 1

    def hapus_belakang(self):
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


class Aksi:
    def __init__(self, jenis, antrean, data):
        self.jenis = jenis
        self.antrean = antrean
        self.data = data


class SistemAntrean:
    def __init__(self, baris_antre, kapasitas_awal=16):
        self.naif = AntreanNaif()
        self.melingkar = AntreanMelingkar(kapasitas_awal)
        for baris in baris_antre:
            self.naif.enqueue(baris)
            self.melingkar.enqueue(baris)
        self.undo = Tumpukan()
        self.redo = Tumpukan()
        self.hook_order_tambah = None
        self.hook_order_batal = None

    def pilih_antrean(self, nama):
        if nama == "naif":
            return self.naif
        return self.melingkar

    def order(self, baris):
        aksi = Aksi("ORDER", "-", baris)
        self.kerjakan(aksi)
        self.catat(aksi)

    def enqueue(self, baris):
        aksi = Aksi("ENQUEUE", "keduanya", baris)
        self.kerjakan(aksi)
        self.catat(aksi)

    def dequeue(self, nama, k):
        antrean = self.pilih_antrean(nama)
        geser_sebelum = antrean.total_geser
        keluar = Array(8)
        for _ in range(k):
            x = antrean.dequeue()
            if x is None:
                break
            keluar.append(x)
        if keluar.jumlah > 0:
            self.catat(Aksi("DEQUEUE", nama, keluar))
        return keluar, antrean.total_geser - geser_sebelum

    def catat(self, aksi):
        self.undo.push(aksi)
        self.redo.kosongkan()

    def kerjakan(self, aksi):
        if aksi.jenis == "ENQUEUE":
            self.naif.enqueue(aksi.data)
            self.melingkar.enqueue(aksi.data)
        elif aksi.jenis == "DEQUEUE":
            antrean = self.pilih_antrean(aksi.antrean)
            for _ in range(aksi.data.jumlah):
                antrean.dequeue()
        else:
            if self.hook_order_tambah is not None:
                self.hook_order_tambah(aksi.data)

    def balik(self, aksi):
        if aksi.jenis == "ENQUEUE":
            self.naif.hapus_belakang()
            self.melingkar.hapus_belakang()
        elif aksi.jenis == "DEQUEUE":
            antrean = self.pilih_antrean(aksi.antrean)
            i = aksi.data.jumlah - 1
            while i >= 0:
                antrean.masuk_depan(aksi.data.get(i))
                i -= 1
        else:
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
        self.kerjakan(aksi)
        self.undo.push(aksi)
        return aksi

    def deskripsi(self, aksi):
        if aksi.jenis == "DEQUEUE":
            return f"DEQUEUE x{aksi.data.jumlah} ({aksi.antrean})"
        return f"{aksi.jenis} {aksi.data[K_OID]}"

    def history(self):
        hasil = Array(8)
        for aksi in self.undo.ke_list():
            hasil.append(self.deskripsi(aksi))
        return hasil

    def stats(self):
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
