import threading
import time
import tkinter as tk
from tkinter import ttk

from frontend.perintah import Mesin, MENU, fmt_waktu


class Aplikasi:
    def __init__(self, root, folder_data):
        self.root = root
        self.folder_data = folder_data
        self.mesin = None
        self.sibuk = True
        self.menu_aktif = None
        self.vars = []
        self._hasil = None
        self._nomor = 0

        root.title("2EZ4U APP - Delivery Engine (M1-M3)")
        root.geometry("1180x760")
        root.minsize(980, 640)
        root.columnconfigure(1, weight=1)
        root.rowconfigure(0, weight=3)
        root.rowconfigure(1, weight=2)

        self._bangun_menu()
        self._bangun_kanan()
        self._bangun_command()

        self.status = tk.StringVar(value="Memuat data CSV ...")
        ttk.Label(root, textvariable=self.status, anchor="w", relief="sunken").grid(
            row=2, column=0, columnspan=2, sticky="ew")

        self._jalankan_thread(self._muat_awal, self._selesai_muat)

    def _bangun_menu(self):
        kiri = ttk.Frame(self.root, padding=(6, 6, 3, 3))
        kiri.grid(row=0, column=0, sticky="ns")
        ttk.Label(kiri, text="MENU", font=("TkDefaultFont", 10, "bold")).grid(row=0, column=0, sticky="w")
        kiri.rowconfigure(1, weight=1)
        self.pohon = ttk.Treeview(kiri, show="tree", selectmode="browse", height=12)
        self.pohon.column("#0", width=320)
        sb = ttk.Scrollbar(kiri, orient="vertical", command=self.pohon.yview)
        self.pohon.configure(yscrollcommand=sb.set)
        self.pohon.grid(row=1, column=0, sticky="ns")
        sb.grid(row=1, column=1, sticky="ns")
        grup_sekarang = None
        node = ""
        for i in range(len(MENU)):
            grup, judul, _, _ = MENU[i]
            if grup != grup_sekarang:
                node = self.pohon.insert("", "end", text=grup, open=True)
                grup_sekarang = grup
            self.pohon.insert(node, "end", iid="m%d" % i, text=judul)
        self.pohon.bind("<<TreeviewSelect>>", self._pilih_menu)

    def _bangun_kanan(self):
        kanan = ttk.Frame(self.root, padding=(3, 6, 6, 3))
        kanan.grid(row=0, column=1, sticky="nsew")
        kanan.columnconfigure(0, weight=1)
        kanan.rowconfigure(3, weight=1)
        self.judul = tk.StringVar(value="Pilih menu di sebelah kiri")
        ttk.Label(kanan, textvariable=self.judul, font=("TkDefaultFont", 12, "bold")).grid(
            row=0, column=0, sticky="w")
        self.form = ttk.LabelFrame(kanan, text="Parameter", padding=6)
        self.form.grid(row=1, column=0, sticky="ew", pady=4)
        self.form.columnconfigure(1, weight=1)
        self.tombol = ttk.Button(kanan, text="Jalankan", command=self._jalankan, state="disabled")
        self.tombol.grid(row=2, column=0, sticky="w", pady=(0, 4))
        hasil = ttk.Frame(kanan)
        hasil.grid(row=3, column=0, sticky="nsew")
        hasil.columnconfigure(0, weight=1)
        hasil.rowconfigure(0, weight=1)
        self.teks = tk.Text(hasil, wrap="none", font=("Courier", 10), state="disabled")
        sy = ttk.Scrollbar(hasil, orient="vertical", command=self.teks.yview)
        sx = ttk.Scrollbar(hasil, orient="horizontal", command=self.teks.xview)
        self.teks.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        self.teks.grid(row=0, column=0, sticky="nsew")
        sy.grid(row=0, column=1, sticky="ns")
        sx.grid(row=1, column=0, sticky="ew")

    def _bangun_command(self):
        bawah = ttk.LabelFrame(self.root, text="COMMAND", padding=4)
        bawah.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=6, pady=3)
        bawah.columnconfigure(0, weight=1)
        bawah.rowconfigure(0, weight=1)
        kol = ("no", "jam", "perintah", "modul", "waktu")
        self.log = ttk.Treeview(bawah, columns=kol, show="headings", height=7)
        lebar = (40, 70, 560, 170, 100)
        judul = ("#", "jam", "perintah", "modul", "waktu")
        for i in range(len(kol)):
            self.log.heading(kol[i], text=judul[i])
            self.log.column(kol[i], width=lebar[i], anchor="w", stretch=(kol[i] == "perintah"))
        sy = ttk.Scrollbar(bawah, orient="vertical", command=self.log.yview)
        self.log.configure(yscrollcommand=sy.set)
        self.log.grid(row=0, column=0, sticky="nsew")
        sy.grid(row=0, column=1, sticky="ns")

    def _jalankan_thread(self, kerja, selesai):
        self.sibuk = True
        self._hasil = None

        def target():
            self._hasil = kerja()

        threading.Thread(target=target, daemon=True).start()
        self._tunggu(selesai)

    def _tunggu(self, selesai):
        if self._hasil is None:
            self.root.after(40, lambda: self._tunggu(selesai))
        else:
            self.sibuk = False
            selesai(self._hasil)

    def _muat_awal(self):
        self.mesin = Mesin(self.folder_data)
        return ("ok",)

    def _selesai_muat(self, _):
        self.status.set(self.mesin.ringkas_muat())
        self._atur_tombol()

    def _pilih_menu(self, _event=None):
        sel = self.pohon.selection()
        if not sel or sel[0][0] != "m":
            return
        self.menu_aktif = int(sel[0][1:])
        grup, judul, _, params = MENU[self.menu_aktif]
        self.judul.set("%s  -  %s" % (grup, judul))
        for w in self.form.winfo_children():
            w.destroy()
        self.vars = []
        if len(params) == 0:
            ttk.Label(self.form, text="(tidak ada parameter)").grid(row=0, column=0, sticky="w")
        for i in range(len(params)):
            label, default, pilihan = params[i]
            v = tk.StringVar(value=default)
            self.vars.append(v)
            ttk.Label(self.form, text=label).grid(row=i, column=0, sticky="w", padx=(0, 8), pady=2)
            if len(pilihan) > 0:
                w = ttk.Combobox(self.form, textvariable=v, values=pilihan, state="readonly", width=20)
                w.grid(row=i, column=1, sticky="w", pady=2)
            else:
                w = ttk.Entry(self.form, textvariable=v)
                w.grid(row=i, column=1, sticky="ew", pady=2)
                w.bind("<Return>", lambda e: self._jalankan())
        self._atur_tombol()

    def _atur_tombol(self):
        ok = (not self.sibuk) and self.menu_aktif is not None
        self.tombol.configure(state="normal" if ok else "disabled")

    def _tulis(self, teks):
        self.teks.configure(state="normal")
        self.teks.delete("1.0", "end")
        self.teks.insert("1.0", teks)
        self.teks.configure(state="disabled")

    def _jalankan(self):
        if self.sibuk or self.menu_aktif is None:
            return
        idx = self.menu_aktif
        kunci = MENU[idx][2]
        nilai = []
        for v in self.vars:
            nilai.append(v.get())
        perintah = kunci
        for x in nilai:
            perintah += " " + x
        self.tombol.configure(state="disabled")
        self.status.set("Menjalankan %s ..." % kunci)
        self._tulis("Menjalankan ...")
        mulai = time.perf_counter()

        def kerja():
            return self.mesin.jalankan(kunci, nilai) + (perintah, mulai)

        self._jalankan_thread(kerja, self._tampilkan)

    def _tampilkan(self, hasil):
        teks, modul, dt, perintah, mulai = hasil
        self._tulis(teks)
        self._nomor += 1
        self.log.insert("", "end", values=(self._nomor, time.strftime("%H:%M:%S"), perintah,
                                           modul, fmt_waktu(dt)))
        kids = self.log.get_children()
        self.log.see(kids[len(kids) - 1])
        total = time.perf_counter() - mulai
        self.status.set("%s | %s | algoritma %s (total + UI %s)" % (
            modul, perintah[:60], fmt_waktu(dt), fmt_waktu(total)))
        self._atur_tombol()


def mulai(folder_data):
    root = tk.Tk()
    Aplikasi(root, folder_data)
    root.mainloop()
