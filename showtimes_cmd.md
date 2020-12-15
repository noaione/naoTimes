# Showtimes

Ini merupakan module utama yang membantu tracking garapan Fansub.<br>
Untuk menyiapkannya, tolong liat bagian [Invite Bot](README#invite-bot)<br>
Jika sudah, mari kita mulai melihat list perintahnya

#### Table of Contents: {docsify-ignore}
* [Perintah Utama](#perintah-utama)
    * [Perintah User](#perintah-utama-user)
    * [Perintah Staff](#perintah-utama-staff)
    * [Perintah Admin](#perintah-utama-admin)
    * [Dalam .gif](#dalam-gif)
        * [Pengguna](#pengguna)
        * [Staff](#staff-2)
        * [Admin](#admin)
* [Perintah Alias](#perintah-alias)
    * [Dalam .gif](#dalam-gif-1)
* [Perintah Kolaborasi](#perintah-kolaborasi)
    * [Penjelasan](#penjelasan-koleb)
    * [Dalam .gif](#dalam-gif-2)
* [Perintah Bot Owner](#perintah-owner)
    * [Dalam .gif](#dalam-gif-3)

## Perintah Utama

Perintah utama dibagi menjadi 3 tier, yaitu pengujung/user, staff, dan admin.
* [Perintah User](#perintah-utama-user)
* [Perintah Staff](#perintah-utama-staff)
* [Perintah Admin](#perintah-utama-admin)
* [Dalam .gif](showtimes_cmd#dalam-gif)

### Perintah Utama: User

| Nama Command | Penjelasan |  Contoh  | Alias |
|:------------:|:----------:|:--------:|:-----:|
| !tagih **[judul]** | Menagih garapan suatu fansub yang terdaftar di database.<br><br>**[judul]**: Judul garapan yang terdaftar, bisa disingkat sesingkat mungkin | !tagih kyuuketsuki | !blame<br>!mana |
| !jadwal | Melihat jadwal tayang anime musiman yang di ambil. | !jadwal | !airing |
| !staff **[judul]** | Melihat ~~tukang delay~~ staff yang mengerjakan suatu garapan.<br><br>**[judul]**: Judul garapan yang terdaftar, bisa disingkat sesingkat mungkin | !staff kyuuketsuki |! tukangdelay<br>!pendelay |

### Perintah Utama: Staff

| Nama Command | Penjelasan |  Contoh  | Alias |
|:------------:|:----------:|:--------:|:-----:|
| !beres **[posisi]** **[judul]** | Menandakan posisi garapan episode yang telah dikerjakan.<br><br>**[posisi]**: tl, tlc, enc, ed, tm, ts, atau qc <br>(Translator, Translation Checker, Encoder, Editor, Timer, Typesetter, Quality Checker)<br><br>**[judul]**: Judul garapan yang terdaftar, bisa disingkat sesingkat mungkin | !beres enc hitoribocchi | !done |
| !gakjadi **[posisi]** **[judul]** | Menandakan posisi garapan episode yang telah dikerjakan tetapi ada kesalahan dan ingin diulang.<br><br>**[posisi]**: tl, tlc, enc, ed, tm, ts, atau qc <br>(Translator, Translation Checker, Encoder, Editor, Timer, Typesetter, Quality Checker)<br><br>**[judul]**: Judul garapan yang terdaftar, bisa disingkat sesingkat mungkin | !gakjadi enc hitoribocchi | !undone<br>!cancel |
| !tandakan **[posisi]** **[episode]** **[judul]** | Mengubah status posisi untuk episode tertentu dari belum ke sudah atau sebaliknya.<br><br>**[posisi]**: tl, tlc, enc, ed, tm, ts, atau qc <br>(Translator, Translation Checker, Encoder, Editor, Timer, Typesetter, Quality Checker)<br><br>**[episode]**: Episode yang ingin diubah tandanya<br><br>**[judul]**: Judul garapan yang terdaftar, bisa disingkat sesingkat mungkin<br><br>Note: Akan otomatis terubah dari ``beres`` ke ``belum beres`` atau sebaliknya jika perintah ini dipakai<br>perintah ini tidak akan mengannounce perubahan ke channel publik | !tandakan enc 3 hitoribocchi | !mark |
| !rilis <...> | Merilis garapan!<br>***Hanya bisa dipakai oleh Admin atau tukang QC***<br>Penjelasan ada di bawah ini. | !rilis kyuuketsuki<br><br>!rilis batch 3 kyuuketsuki<br><br>!rilis semua kyuuketsuki | !release |

**!rilis \<judul>**<br>
Merilis episode dari judul yang dikerjakan<br>
<br>
**!rilis batch \<jumlah> \<judul>**<br>
Merilis jumlah episode tertentu dari judul yang dikerjakan<br>
<br>
**!rilis semua \<judul>**<br>
Merilis semua episode dari judul yang dikerjakan

<p class="tip">
<strong>Note:</strong> Untuk perintah !rilis batch, terdapat <strong>[jumlah]</strong> episode yang mau dirilis.
Penghitungannya adalah <strong>Episode terakhir yang sedang dikerjakan ditambah jumlah</strong>.<br>
Misalkan lagi <strong>ngerjain Episode 4</strong>, terus mau <strong>rilis sampai episode 7</strong><br>
Total dari <strong>Episode 4 sampai 7 ada 4</strong> (4, 5, 6, dan 7)<br>
Maka tulis <strong>jumlahnya 4</strong>
</p>

### Perintah Utama: Admin

| Nama Command | Penjelasan |  Contoh  | Alias |
|:------------:|:----------:|:--------:|:-----:|
| !tambahutang | Menambah garapan baru ke database.<br>Anda akan dibantu melewati proses penambahan utang<br>silakan melihat [.gif ini](https://p.ihateani.me/ifQMCsOt.gif) jika kurang mengerti | !tambahutang | !add<br>!tambah |
| !ubahdata **[judul]** | Mengubah informasi data suatu garapan.<br>Penjelasan lebih lengkap ada di bawah ini.<br><br>**[judul]**: Judul garapan yang terdaftar, bisa disingkat sesingkat mungkin | !ubahdata kyuuketsuki | - |

**!ubahdata** memiliki 5 mode interaktif, yaitu:
- Ubah Staff
- Ubah Role
- Tambah Episode
- Hapus Episode
- (!) Drop

**Ubah Staff** akan membawa anda dalam proses mengubah posisi tertentu dengan staff lain (jikalau ada kesalahan, atau memang ada perubahan.)<br>
**Ubah Role** akan mengubah role yang dipakai untuk garapan tersebut, role dipakai untuk pengecekan agar garapan tersebut hanya dapat diubah statusnya oleh role tersebut.<br>
**Tambah Episode** akan menambah episode dengan jumlah tertentu, instruksi lengkap ada di mode tersebut.<br>
**Hapus Episode** akan menghapus episode dengan range tertentu, instruksi lengkap ada di mode tersebut.<br>
**Drop (!!!)** akan menghapus garapan dari database untuk selamanya.

### Dalam .gif

#### Pengguna

##### !tagih<br> {docsify-ignore}
![tagih](https://p.ihateani.me/sicktytu.gif)

##### !jadwal<br> {docsify-ignore}
![jadwal](https://p.ihateani.me/swbfwhls.gif)

##### !staff<br> {docsify-ignore}
![staff](https://p.ihateani.me/hjzkoxuw.gif)

#### Staff

##### !beres<br> {docsify-ignore}
![beres](https://p.ihateani.me/rodtjtfv.gif)

##### !gakjadi<br> {docsify-ignore}
![gakjadi](https://p.ihateani.me/vzeaykii.gif)

##### !tandakan {docsify-ignore}
![tandakan](https://p.ihateani.me/epvlcgyr.gif)

##### !rilis | !rilis batch | !rilis semua<br> {docsify-ignore}
![rilis](https://p.ihateani.me/tdiyikja.gif)

#### Admin

##### !tambahutang<br> {docsify-ignore}
![tambahutang](https://p.ihateani.me/ysnjlvfl.gif)

##### !ubahdata<br> {docsify-ignore}
![ubahdata](https://p.ihateani.me/qbjpsbok.gif)

## Perintah Alias

| Nama Command | Penjelasan |  Contoh  | Alias |
|:------------:|:----------:|:--------:|:-----:|
| !alias | Tambahkan alias baru dengan command ini, cukup jalankan `!alias` untuk memulai proses.<br>Anda akan dibantu melewati proses penambahan utang<br>silakan melihat [.gif ini](https://p.ihateani.me/ifQMCsOt.gif) jika kurang mengerti | !alias | - |
| !alias list **[judul]** | Melihat daftar alias dari suatu **[judul]**.<br><br>**[judul]**: Judul garapan yang terdaftar, bisa disingkat sesingkat mungkin | !alias list kyuuketsuki | - |
| !alias hapus **[judul]** | Menghapus alias dari suatu **[judul]**.<br><br>**[judul]**: Judul garapan yang terdaftar, bisa disingkat sesingkat mungkin | !alias hapus kyuuketsuki | !alias remove |

### Dalam .gif

##### !alias<br> {docsify-ignore}
![alias](https://p.ihateani.me/cvvshlcy.gif)

##### !alias list<br> {docsify-ignore}
![alias list](https://p.ihateani.me/opfcmfnz.gif)

##### !alias hapus<br> {docsify-ignore}
![alias hapus](https://p.ihateani.me/hbpnbafw.gif)

## Perintah Kolaborasi

| Nama Command | Penjelasan |  Contoh  | Alias |
|:------------:|:----------:|:--------:|:-----:|
| !kolaborasi | Memunculkan bantuan perintah kolaborasi | !kolaborasi | !joint<br>!join<br>!koleb |
| !kolaborasi dengan **[server_id_kolaborasi]** **[judul]** | Memulai proses kolaborasi dengan server/fansub lain, berikan kode unik yang diberikan bot ke admin server/fansub sebelah.<br><br>**[server_id_kolaborasi]**: Merupakan ID server yang ingin diajak kolaborasi (Harus teedaftar di database naoTimes)<br><br>**[judul]**: Judul garapan yang terdaftar, bisa disingkat sesingkat mungkin | !kolaborasi dengan 472705451117641729 kyuuketsuki | - |
| !kolaborasi konfirmasi **[kode]** | Konfirmasi kolaborasi garapan dengan **[kode]** unik | !kolaborasi konfirmasi eyasd123hnbbq | - |
| !kolaborasi putus **[judul]** | Memutuskan hubungan sinkronisasi data dengan semua fansub yang diajak kolaborasi<br><br>**[judul]**: Judul garapan yang terdaftar, bisa disingkat sesingkat mungkin | !kolaborasi putus kyuuketsuki | - |
| !kolaborasi batalkan **[server_id_kolaborasi]** **[kode]** | Membatalkan kode konfirmasi kolaborasi dengan fansub lain<br><br>**[server_id_kolaborasi]**: Merupakan ID server yang ingin diajak kolaborasi (Harus teedaftar di database naoTimes)<br><br>**[kode]** merupakan kode unik yang dibuat saat melakukan `!konfirmasi dengan` | !kolaborasi batalkan 472705451117641729 eyasd123hnbbq | - |

### Penjelasan :id=penjelasan-koleb
**Kegunaan:**<br>
Mengsinkronasikan proses garapan dengan server lain yang terdaftar pada database naoTimes.<br>
Kolaborasi bisa lebih dari 2 server.

!> Jika salah satu server meng-update data untuk anime yang melakukan kolaborasi, maka akan meng-update data server lainnya juga dan akan di announce juga ke semua server yang berkolaborasi

**Penjelasan perintah**<br>
- !kolaborasi dengan **[server_id_kolaborasi]** **[judul]**<br>
Memulai proses kolaborasi dengan server/fansub lain, berikan kode unik yang diberikan bot ke admin server/fansub sebelah<br>
Proses ini akan membuat kode unik yang hanya bisa dipakai oleh server yang ditarget.
- !kolaborasi konfirmasi **[kode]**<br>
Melakukan konfirmasi kolaborasi.<br>
Jika anime sudah didaftar, maka akan di overwrite dari data yang mengajak kolaborasi.<br>
Role akan dibuat otomatis dan tinggal diberikan ke staff.
- !kolaborasi putus **[judul]**<br>
Memutuskan hubungan sinkronisasi dengan semua fansub yang diajak kolaborasi<br>
Server lain akan tetap tersinkronisasi (jika ada) dan tidak akan terpengaruh.
- !kolaborasi batalkan **[server_id_kolaborasi]** **[kode]**<br>
Menghanguskan kode yang telah dibuat<br>
Jika terjadi kesalahan dan lain sebagainya.

### Dalam .gif

##### !kolaborasi dengan | !kolaborasi konfirmasi<br> {docsify-ignore}
![kolaborasi dengan dan konfirmasi](https://p.ihateani.me/bkmjftha.gif)

##### !kolaborasi putus<br> {docsify-ignore}
![kolaborasi putus](https://p.ihateani.me/xihrjfbw.gif)

##### !kolaborasi batalkan<br> {docsify-ignore}
![kolaborasi batalkan](https://p.ihateani.me/vxxwzefe.gif)

## Perintah Bot Owner (Admin) :id=perintah-owner

| Nama Command | Penjelasan |  Contoh  | Alias |
|:------------:|:----------:|:--------:|:-----:|
| !ntadmin | Memunculkan bantuan perintah owner | !ntadmin | !naotimesadmin<br>!naoadmin |

WIP

### Dalam .gif

WIP
