# Web Script
Kumpulan script website sebagai penghubung antara database dengan website

* [Website Progress](#naotimes-website-progress)

## naoTimes Website Progress

Menghubungkan progress garapan dari database bot ke website.

### Instalasi {docsify-ignore}

1. Selipkan snippet html berikut:
    ```html
    <div id='naotimes' class="progress-wrapper">
        <script type="text/javascript" src="https://naoti.me/assets/js/naoTimes.js"></script>
        <script type="text/javascript">
            naoTimesProcess("MASUKAN ID SERVER DISCORD DI SINI"); // Ubah line ini
        </script>
        <h1 class="naotimes-header">Status Garapan</h1>
        <img id='naotimes-loading' width="40" height="40" src='https://puu.sh/DiJzU/6af20efe7e.gif'>
    </div>
    ```
2. Ubah bagian
    ```js
    naoTimesProcess("MASUKAN ID SERVER DISCORD DI SINI"); // Ubah line ini
    ```
    dengan ID server discord anda. Contoh:
    ```js
    naoTimesProcess("472705451117641729"); // Ubah line ini
    ```
2. Kustomisasi dengan css, listnya ada:
    - **naotimes-header**: teks header dengan tulisan `Status Garapan`
    - **naotimes-animetitle**: bagian judul garapan/anime
    - **naotimes-animeprogress**: bagian progress tiap garapan/anime

**Bisa diganti dengan versi minimal dengan mengganti `.js` ke `.min.js`**
