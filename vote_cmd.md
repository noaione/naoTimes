# Sistem Voting

Lakukan voting di dalam server!<br>
Sistem voting menggunakan parser bernama argparse, jadi penulisan command sedikit berbeda.

## Perintah

| Nama Command | Penjelasan |  Contoh  | Alias |
|:------------:|:----------:|:--------:|:-----:|
| !vote -h | Melihat bantuan perintah untuk command vote | - | - |
| !votekick -h | Melihat bantuan perintah untuk command vote kick | - | - |
| !voteban -h | Melihat bantuan perintah untuk command vote ban | - | - |

### Penjelasan sistem argparse

Untuk `!vote` terdapat 3 optional params dan 1 required params
```
Gunakan: !vote [-h] [--satu-pilihan] [--timer DETIK] [--opsi OPSI] topik

Argumen yang diwajibkan:
  topik                 Hal yang ingin divote.

Argumen opsional:
  --satu-pilihan, -S    Gunakan tipe satu pilihan (ya/tidak) untuk reactions.
  --timer DETIK, -t DETIK
                        Waktu sebelum voting ditutup (Dalam menit, min 3 menit)
  --opsi OPSI, -O OPSI  Opsi voting (minimal 2, batas 10)
```

**`topik`**: adalah hal yang ingin di voting, mohon gunakan kutip dua.<br>
**`--satu-pilihan`** atau **`-S`**: cukup gunakan reaction centang dan silang, alias ya dan tidak<br>
**`--timer`** atau **`-t`**: waktu voting dalam menit, default adalah 3 menit<br>
**`--opsi`** atau **`-O`**: Opsi yang ingin diberikan didalam voting, gunakan kutip dua.

**Contoh**: `!vote -O "Python" -O "JavaScript" -O "Brainfuck" -t 5 "Bahasa program terbaik"`<br>
Command tersebut akan membuat voting dengan judul `Bahasa program terbaik` dan 3 pilihan yaitu: `Python`, `JavaScript`, dan `Brainfuck`<br>
`-t 5` akan membuat voting ini berjalan selama 5 menit sebelum ditutup.

`!vote -S "Apakah saya pintar?"`
Command tersebut akan membuat voting dengan judul `Apakah saya pintar?` dan 2 pilihan yaitu `Ya` dan `Tidak`.<br>
Waktu votingnya adalah default 3 menit.


Sementara untuk `!votekick` dan `!voteban` terdapat 2 optional params dan 1 required params
```
Gunakan: !votekick [-h] [--timer DETIK] [--limit BATAS] user

Argumen yang diwajibkan:
  user                  User yang ingin di ban/kick.

Argumen opsional:
  -h, --help            Perlihatkan bantuan perintah
  --timer DETIK, -t DETIK
                        Waktu sebelum voting ditutup (Dalam detik, min 30 detik)
  --limit BATAS, -l BATAS
                        Limit user untuk melaksanakan kick/ban (minimal 5 orang)
```

**`user`**: adalah user yang ingin di kick/ban, bisa di mention orangnya, ketik IDnya, atau tulis Usernamenya<br>
**`--timer`** atau **`-t`**: waktu voting dalam detik, default adalah 60 detik<br>
**`--limit`** atau **`-l`**: batas orang yang dibutuhkan didalam vote sebelum di kick/ban (tidak termasuk user yang buat vote, dan yang akan di kick/ban), default 5 user<br>

**Contoh**: `!votekick -l 10 -t 180 466469077444067372`<br>
Akan mengaktifkan votekick untuk user ID `466469077444067372`, voting dibuka untuk 180 detik atau 3 menit, dan dibutuhkan minimal 10 orang sebelum di tentukan.

## Dalam .gif
### !vote<br> {docsify-ignore}
![vote](https://p.ihateani.me/vgmbostu.gif)

Untuk !voteban dan !votekick tidak jauh beda dengan !vote