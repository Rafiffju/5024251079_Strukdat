import os
import time

from backend.m1_pesanan import (Array, baca_pesanan, isi_linklist, BELUM_SELESAI,
                                K_OID, K_HARGA, K_SELESAI, K_STATUS)
from backend.m2_antrean import (SistemAntrean, ke_postfix_detail, hitung_detail, rupiah, ribuan)
from backend.m3_laporan import (LaporanHarian, DataTerlaluBesar, BATAS_INSERTION, cek_terurut,
                                cek_stabil, indeks_kunci)

M1, M2, M3 = "M1 - Pesanan", "M2 - Stack & Queue", "M3 - Sort & Search"

_F_PESANAN = (("pelanggan", "Pelanggan Baru", ()), ("resto", "kantin-pusat", ()),
              ("menu", "nasi-goreng", ()), ("harga", "15000", ()))
_F_I = (("indeks i", "0", ()),)

MENU = (
    (M1, "ARRAY - LIHAT PESANAN", "array_lihat", _F_I),
    (M1, "ARRAY - TAMBAH PESANAN REGULER", "array_reguler", _F_PESANAN),
    (M1, "ARRAY - TAMBAH PESANAN PRIORITAS", "array_prioritas", _F_PESANAN),
    (M1, "ARRAY - TAMBAH PESANAN VIP", "array_vip", _F_PESANAN),
    (M1, "ARRAY - HAPUS PESANAN", "array_hapus", _F_I),
    (M1, "LINKED LIST - LIHAT PESANAN", "ll_lihat", _F_I),
    (M1, "LINKED LIST - TAMBAH PESANAN REGULER", "ll_reguler", _F_PESANAN),
    (M1, "LINKED LIST - TAMBAH PESANAN PRIORITAS", "ll_prioritas", _F_PESANAN),
    (M1, "LINKED LIST - TAMBAH PESANAN VIP", "ll_vip", _F_PESANAN),
    (M1, "LINKED LIST - HAPUS PESANAN", "ll_hapus", _F_I),
    (M1, "DATA - MUAT ULANG (RESET)", "reset", ()),
    (M2, "STACK - POSTFIX (MESIN KASIR)", "stack_postfix",
     (("struk (infix)", "( 3 * 12000 ) + ( 2 * 8500 ) - 5000", ()),)),
    (M2, "STACK - ORDER BARU (BISA UNDO)", "stack_order", _F_PESANAN),
    (M2, "STACK - UNDO", "stack_undo", ()),
    (M2, "STACK - REDO", "stack_redo", ()),
    (M2, "QUEUE - ENQUEUE", "queue_enqueue", _F_PESANAN),
    (M2, "QUEUE - DEQUEUE NAIF", "queue_naif", (("jumlah", "1", ()),)),
    (M2, "QUEUE - DEQUEUE CIRCULAR", "queue_circular", (("jumlah", "1", ()),)),
    (M2, "QUEUE - STATISTIK & RIWAYAT", "queue_stats", ()),
    (M3, "SORT - INSERTION SORT", "sort_insertion",
     (("jumlah baris", "2000", ()), ("kunci", "harga", ("oid", "harga", "selesai")))),
    (M3, "SORT - MERGE SORT", "sort_merge",
     (("jumlah baris", "2000", ()), ("kunci", "harga", ("oid", "harga", "selesai")))),
    (M3, "SORT - BANDINGKAN n vs PERBANDINGAN", "sort_banding",
     (("daftar n (koma)", "500,1000,2000,4000", ()),
      ("kunci", "harga", ("oid", "harga", "selesai")))),
    (M3, "SEARCH - LINEAR SEARCH", "search_linear", (("oid", "O-137442", ()),)),
    (M3, "SEARCH - BINARY SEARCH", "search_binary", (("oid", "O-137442", ()),)),
)


def jam(detik):
    if detik >= BELUM_SELESAI:
        return "-"
    return "%02d:%02d:%02d" % (detik // 3600, (detik % 3600) // 60, detik % 60)


def fmt_waktu(s):
    if s >= 1:
        return ("%.2f s" % s).replace(".", ",")
    return ("%.2f ms" % (s * 1000)).replace(".", ",")


def fmt_baris(r):
    return "%s | %s | %s | %s | %s | P%d | masuk %s | selesai %s | %s" % (
        r[0], r[1], r[2], r[3], rupiah(r[4]), r[5], jam(r[6]), jam(r[7]), r[8])


def _ke_int(teks, nama, minimum=None):
    try:
        v = int(teks.strip().replace(".", ""))
    except ValueError:
        raise ValueError("%s harus bilangan bulat" % nama)
    if minimum is not None and v < minimum:
        raise ValueError("%s minimal %d" % (nama, minimum))
    return v


class Mesin:
    def __init__(self, folder_data):
        self.folder = folder_data
        self.muat()

    def muat(self):
        t0 = time.perf_counter()
        self.arr = baca_pesanan(os.path.join(self.folder, "pesanan.csv"))
        t1 = time.perf_counter()
        self.ll = isi_linklist(self.arr)
        t2 = time.perf_counter()
        antre = Array(1024)
        for i in range(len(self.arr)):
            r = self.arr.get(i)
            if r[K_STATUS] == "ANTRE":
                antre.append(r)
        self.sistem = SistemAntrean(antre.ke_larik(), 16)
        self.sistem.hook_order_tambah = self._order_tambah
        self.sistem.hook_order_batal = self._order_batal
        self.laporan = LaporanHarian(self.arr.ke_larik())
        self._no_oid = 200000
        self.info_muat = (len(self.arr), t1 - t0, t2 - t1, len(antre))
        return self.info_muat

    def ringkas_muat(self):
        n, ta, tl, antre = self.info_muat
        return "%s pesanan dimuat (Array %s, LinkList %s) | %s berstatus ANTRE" % (
            ribuan(n), fmt_waktu(ta), fmt_waktu(tl), ribuan(antre))

    def _oid_baru(self):
        self._no_oid += 1
        return "O-%06d" % self._no_oid

    def _baris_baru(self, nilai, prioritas):
        harga = _ke_int(nilai[3], "harga", 0)
        t = time.localtime()
        masuk = t.tm_hour * 3600 + t.tm_min * 60 + t.tm_sec
        nama = nilai[0].strip() or "Pelanggan"
        return (self._oid_baru(), nama, nilai[1].strip(), nilai[2].strip(), harga,
                prioritas, masuk, BELUM_SELESAI, "ANTRE")

    def _order_tambah(self, baris):
        self.arr.tambah_reguler(baris)
        self.ll.tambah_reguler(baris)

    def _order_batal(self, baris):
        n = len(self.arr)
        if n > 0 and self.arr.get(n - 1)[K_OID] == baris[K_OID]:
            self.arr.hapus(n - 1)
        n = len(self.ll)
        if n > 0 and self.ll.get(n - 1)[K_OID] == baris[K_OID]:
            self.ll.hapus(n - 1)

    def jalankan(self, kunci, nilai):
        try:
            return self._jalankan(kunci, nilai)
        except DataTerlaluBesar as e:
            return str(e), "M3 - ditolak", 0.0
        except (ValueError, IndexError) as e:
            return "GALAT: %s" % e, "galat", 0.0

    def _jalankan(self, kunci, v):
        if kunci == "array_lihat" or kunci == "ll_lihat":
            struktur = self.arr if kunci == "array_lihat" else self.ll
            i = _ke_int(v[0], "indeks", 0)
            t0 = time.perf_counter()
            r = struktur.get(i)
            dt = time.perf_counter() - t0
            if kunci == "array_lihat":
                kata, modul = "alamat dihitung langsung, 0 langkah", "M1 - array"
            else:
                kata, modul = "%s simpul ditelusuri dari head" % ribuan(struktur.langkah_terakhir), "M1 - linked list"
            return "Pesanan ke-%d dari %s:\n%s\n%s" % (i, ribuan(len(struktur)), fmt_baris(r), kata), modul, dt

        if kunci in ("array_reguler", "array_prioritas", "array_vip",
                     "ll_reguler", "ll_prioritas", "ll_vip"):
            is_arr = kunci[:5] == "array"
            struktur = self.arr if is_arr else self.ll
            jenis = kunci.split("_")[1]
            prio = 3 if jenis == "reguler" else (2 if jenis == "prioritas" else 1)
            baris = self._baris_baru(v, prio)
            sebelum = len(struktur)
            t0 = time.perf_counter()
            if jenis == "reguler":
                idx = struktur.tambah_reguler(baris)
            elif jenis == "prioritas":
                idx = struktur.tambah_prioritas(baris)
            else:
                idx = struktur.tambah_vip(baris)
            dt = time.perf_counter() - t0
            kata = "elemen digeser" if is_arr else "simpul ditelusuri"
            teks = "%s (%s) masuk di indeks %s dari %s | %s %s\npanjang: %s -> %s" % (
                baris[0], jenis.upper(), ribuan(idx), ribuan(sebelum + 1),
                ribuan(struktur.langkah_terakhir), kata, ribuan(sebelum), ribuan(len(struktur)))
            return teks, "M1 - array" if is_arr else "M1 - linked list", dt

        if kunci == "array_hapus" or kunci == "ll_hapus":
            is_arr = kunci == "array_hapus"
            struktur = self.arr if is_arr else self.ll
            i = _ke_int(v[0], "indeks", 0)
            sebelum = len(struktur)
            t0 = time.perf_counter()
            if is_arr:
                r = struktur.hapus(i)
            else:
                r = struktur.hapus(i)
            dt = time.perf_counter() - t0
            kata = "elemen digeser" if is_arr else "simpul ditelusuri"
            return "Dicabut: %s\n%s %s | panjang: %s -> %s" % (
                fmt_baris(r), ribuan(struktur.langkah_terakhir), kata, ribuan(sebelum),
                ribuan(len(struktur))), "M1 - array" if is_arr else "M1 - linked list", dt

        if kunci == "reset":
            info = self.muat()
            return "Data dimuat ulang.\n" + self.ringkas_muat(), "M1 - data", info[1] + info[2]

        if kunci == "stack_postfix":
            t0 = time.perf_counter()
            post, l1 = ke_postfix_detail(v[0])
            total, l2 = hitung_detail(post)
            dt = time.perf_counter() - t0
            tt = "Tahap 1 - infix -> postfix\n"
            tt += "%-5s %-5s %-34s %-12s %s\n" % ("no", "token", "tindakan", "stack", "keluaran")
            for i in range(len(l1)):
                a = l1.get(i)
                tt += "1.%-3d %-5s %-34s %-12s %s\n" % (i + 1, a[0], a[1], a[2], a[3])
            tt += "\nTahap 2 - evaluasi postfix\n"
            tt += "%-5s %-5s %-46s %s\n" % ("no", "token", "tindakan", "stack nilai")
            for i in range(len(l2)):
                a = l2.get(i)
                tt += "2.%-3d %-5s %-46s %s\n" % (i + 1, a[0], a[1], a[2])
            ptxt = ""
            for x in post.ke_larik():
                ptxt += (" " if ptxt else "") + x
            tt += "\npostfix: %s\nTOTAL : %s" % (ptxt, rupiah(total))
            return tt, "M2 - stack", dt

        if kunci == "stack_order":
            baris = self._baris_baru(v, 3)
            t0 = time.perf_counter()
            self.sistem.order(baris)
            dt = time.perf_counter() - t0
            return ("%s masuk sebagai pesanan REGULER ke Array & Linked List (M1)\n"
                    "panjang Array %s, LinkList %s | undo %d, redo %d" % (
                        baris[0], ribuan(len(self.arr)), ribuan(len(self.ll)),
                        len(self.sistem.undo), len(self.sistem.redo))), "M2 - stack", dt

        if kunci == "stack_undo" or kunci == "stack_redo":
            t0 = time.perf_counter()
            aksi = self.sistem.undo_last() if kunci == "stack_undo" else self.sistem.redo_last()
            dt = time.perf_counter() - t0
            if aksi is None:
                pesan = ("tumpukan undo kosong, tidak ada yang dibatalkan" if kunci == "stack_undo"
                         else "tumpukan redo kosong, tidak ada yang diulang")
                return pesan, "M2 - stack", dt
            d = self.sistem.deskripsi(aksi)
            if kunci == "stack_undo":
                kata = "dibatalkan (kebalikannya dijalankan)"
                if aksi.jenis == "DEQUEUE":
                    kata = "%d pesanan dikembalikan ke DEPAN antrean %s" % (aksi.data.jumlah, aksi.antrean)
                elif aksi.jenis == "ENQUEUE":
                    kata = "%s dikeluarkan lagi dari BELAKANG kedua antrean" % aksi.data[0]
            else:
                kata = "dikerjakan ulang (aksi aslinya)"
            s = self.sistem
            return "%s: %s\nantrean naif %s, circular %s | tumpukan undo %d, redo %d" % (
                d, kata, ribuan(len(s.naif)), ribuan(len(s.melingkar)), len(s.undo), len(s.redo)), "M2 - stack", dt

        if kunci == "queue_enqueue":
            baris = self._baris_baru(v, 3)
            t0 = time.perf_counter()
            self.sistem.enqueue(baris)
            dt = time.perf_counter() - t0
            s = self.sistem
            return "%s masuk paling belakang KEDUA antrean\npanjang naif %s | circular %s" % (
                baris[0], ribuan(len(s.naif)), ribuan(len(s.melingkar))), "M2 - queue", dt

        if kunci == "queue_naif" or kunci == "queue_circular":
            k = _ke_int(v[0], "jumlah", 1)
            nama = "naif" if kunci == "queue_naif" else "circular"
            t0 = time.perf_counter()
            keluar, geser = self.sistem.dequeue(nama, k)
            dt = time.perf_counter() - t0
            if keluar.jumlah == 0:
                return "antrean %s kosong, tidak ada yang keluar (None)" % nama, "M2 - queue " + nama, dt
            ids = ""
            for i in range(min(keluar.jumlah, 5)):
                ids += (", " if ids else "") + keluar.get(i)[0]
            if keluar.jumlah > 5:
                ids += ", ..."
            teks = "%s pesanan keluar (%s) | %s elemen digeser" % (ribuan(keluar.jumlah), ids, ribuan(geser))
            if nama == "circular":
                q = self.sistem.melingkar
                teks += "\nfront=%s rear=%s count=%s kapasitas=%s" % (
                    ribuan(q.front), ribuan(q.rear), ribuan(q.count), ribuan(q.K))
            return teks, "M2 - queue " + nama, dt

        if kunci == "queue_stats":
            t0 = time.perf_counter()
            st = self.sistem.stats()
            h = self.sistem.history()
            dt = time.perf_counter() - t0
            tt = "stats():\n"
            for i in range(len(st)):
                a = st.get(i)
                tt += "  %-26s %s\n" % (a[0], ribuan(a[1]))
            tt += "\nhistory() (terlama -> terbaru):\n"
            if len(h) == 0:
                tt += "  (kosong)"
            for i in range(len(h)):
                tt += "  %d. %s\n" % (i + 1, h.get(i))
            return tt.rstrip(), "M2 - stats", dt

        if kunci == "sort_insertion" or kunci == "sort_merge":
            n = _ke_int(v[0], "jumlah baris", 1)
            algo = "insertion" if kunci == "sort_insertion" else "merge"
            A, h, dt = self.laporan.urutkan(algo, n, v[1])
            k = indeks_kunci(v[1])
            ok = cek_terurut(A, k)
            stabil = cek_stabil(A, k)
            tt = "%s pesanan terurut menurut %s | %s perbandingan | %s pemindahan\n" % (
                ribuan(n), v[1], ribuan(h.perbandingan), ribuan(h.pemindahan))
            tt += "terurut: %s | stabil: %s\n\n" % ("ya" if ok else "TIDAK", "ya" if stabil else "TIDAK")
            tt += "%-10s %-8s %-9s %-8s\n" % ("oid", "harga", "selesai", "status")
            for i in range(min(10, n)):
                r = A[i]
                tt += "%-10s %-8s %-9s %-8s\n" % (r[0], ribuan(r[4]), jam(r[7]), r[8])
            if n > 10:
                tt += "... (%s baris lainnya)" % ribuan(n - 10)
            return tt.rstrip(), "M3 - %s sort" % algo, dt

        if kunci == "sort_banding":
            daftar = v[0].split(",")
            tt = "%8s | %22s | %22s | %s\n" % ("n", "insertion (banding.)", "merge (banding.)", "rasio ins/merge")
            total = 0.0
            for teks_n in daftar:
                n = _ke_int(teks_n, "n", 2)
                _, hm, dm = self.laporan.urutkan("merge", n, v[1])
                total += dm
                if n <= BATAS_INSERTION:
                    _, hi, di = self.laporan.urutkan("insertion", n, v[1])
                    total += di
                    tt += "%8s | %22s | %22s | %.1fx\n" % (
                        ribuan(n), ribuan(hi.perbandingan), ribuan(hm.perbandingan),
                        hi.perbandingan / hm.perbandingan)
                else:
                    tt += "%8s | %22s | %22s | -\n" % (ribuan(n), "ditolak (> %s)" % ribuan(BATAS_INSERTION),
                                                       ribuan(hm.perbandingan))
            tt += "\nn dilipatduakan: insertion ~4x, merge ~2x."
            return tt, "M3 - banding", total

        if kunci == "search_linear" or kunci == "search_binary":
            oid = v[0].strip()
            if kunci == "search_linear":
                i, h, dt = self.laporan.cari_linear_oid(oid)
                teks = ""
                modul = "M3 - linear"
            else:
                baru = self.laporan.siapkan_oid()
                i, h, dt = self.laporan.cari_biner_oid(oid)
                modul = "M3 - binary"
                if baru:
                    wb, cb = self.laporan.biaya_bangun
                    teks = "daftar terurut oid dibangun sekali (merge sort, %s perbandingan) %s\n" % (
                        ribuan(cb), fmt_waktu(wb))
                else:
                    teks = "daftar terurut oid sudah ada (dibangun sebelumnya, biaya tidak dihitung lagi)\n"
            if i < 0:
                teks += "%s tidak ditemukan | %s perbandingan" % (oid, ribuan(h.perbandingan))
            else:
                src = self.laporan.baris if kunci == "search_linear" else self.laporan.terurut_oid
                teks += "ditemukan di indeks %s | %s perbandingan\n%s" % (
                    ribuan(i), ribuan(h.perbandingan), fmt_baris(src[i]))
            return teks, modul, dt

        raise ValueError("perintah tidak dikenal: %s" % kunci)
