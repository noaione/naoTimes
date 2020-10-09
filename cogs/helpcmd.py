import asyncio
import logging
import os
from typing import List

import discord
from discord.ext import commands

from nthelper.utils import HelpGenerator, get_current_time, read_files

simple_textdata = r"""```
<judul>: Judul garapan yang terdaftar, bisa disingkat sesingkat mungkin
```
"""  # noqa: E501

simple_textdata_fs = r"""```
<kode fansub>: Fansub yang didaftar ke list khusus secara manual (Cek dengan ketik "!tagihfs" saja)

<judul>: Judul garapan yang terdaftar, bisa disingkat sesingkat mungkin
```
"""  # noqa: E501

simpleplex_textdata = r"""```
<jumlah>: Jumlah episode yang mau dirilis (dari episode yang terakhir dirilis)
Misalkan lagi ngerjain Episode 4, terus mau rilis sampe episode 7
Total dari Episode 4 sampai 7 ada 4 (4, 5, 6, 7)
Maka tulis jumlahnya 4

<judul>: Judul garapan yang terdaftar, bisa disingkat sesingkat mungkin
```
"""  # noqa: E501

simplex_ubahdata = r"""```
Mengatur ulang isi data dari sebuah judul
Terdapat 5 mode:
    - Ubah Staff
    - Ubah Role
    - Tambah Episode
    - Hapus Episode
    - (!) Drop

Ubah data merupakan tipe command yang interaktif.
```"""  # noqa: E501

simpleplex_textdata2 = r"""```
<range>: Ranged number, bisa satu digit untuk 1 episode saja atau range dari episode x sampai y
Contoh: `4` untuk episode 4 || `4-6` untuk episode 4 sampai 6

<judul>: Judul garapan yang terdaftar, bisa disingkat sesingkat mungkin
```
"""  # noqa: E501

ubahstaff_textdata = r"""```
<id_staff>: Merupakan ID user discord per staff
Bisa diisi ID sendiri atau dirandom (ex: 123)
Cara ambilnya:
1. Nyalakan mode Developer di User Settings -> Appereance -> Developer Mode
2. Klik kanan nama usernya
3. Klik Copy ID
--> https://puu.sh/D3yTA/e11282996e.gif

<posisi>: tl, tlc, enc, ed, tm, ts, atau qc
(Translator, Translation Checker, Encoder, Editor, Timer, Typesetter, Quality Checker)

<judul>: Judul garapan yang terdaftar, bisa disingkat sesingkat mungkin
```
"""  # noqa: E501

ubahrole_textdata = r"""```
<id_role>: ID Role tanpa `@&` khusus babu yang ngerjain anime ini
(Mention role dengan tanda `\` ex: `\@Delayer`)
--> https://puu.sh/D3yVw/fd088611f3.gif

<judul>: Judul garapan yang terdaftar, bisa disingkat sesingkat mungkin
```
"""  # noqa: E501

animangavn_textdata = r"""```
<judul>: Judul anime ataupun manga yang ada di Anilist.co atau VN yang ada di vndb.org
```
"""  # noqa: E501

tanda_textdata = r"""```
<posisi>: tl, tlc, enc, ed, tm, ts, atau qc
(Translator, Translation Checker, Encoder, Editor, Timer, Typesetter, Quality Checker)

<judul>: Judul garapan yang terdaftar, bisa disingkat sesingkat mungkin
```
"""  # noqa: E501

link_textdata = r"""```
<link>: URL yang ingin diamankan atau dipendekan.
URL harus ada 'https://' atau 'http://' sebagai awalan atau akan dianggap tidak valid

Jika ingin memakai pengaman disarankan memakai pemendek agar link lebih mudah diingat
```
"""  # noqa: E501

complex_textdata = r"""```
<anilist_id>: ID/Angka yang ada pada URL dari web anilist.co
> https://anilist.co/anime/101386/Hitoribocchi-no-Marumaru-Seikatsu/
`101386` merupakan ID nya

<total_ep>: Perkiraan total episode (Bisa diubah manual, silakan PM N4O#8868)

<id_role>: ID Role tanpa `@&` khusus babu yang ngerjain anime ini
(Mention role dengan tanda `\` ex: `\@Delayer`)
--> https://puu.sh/D3yVw/fd088611f3.gif

<id_tlor sampai id_qcer>: Merupakan ID user discord per staff
Bisa diisi ID sendiri atau dirandom (ex: 123)
Cara ambilnya:
1. Nyalakan mode Developer di User Settings -> Appereance -> Developer Mode
2. Klik kanan nama usernya
3. Klik Copy ID
--> https://puu.sh/D3yTA/e11282996e.gif

Jika ada kesalahan PM N4O#8868
```
"""  # noqa: E501

tandakan_textdata = r"""```
<posisi>: tl, tlc, enc, ed, tm, ts, atau qc
(Translator, Translation Checker, Encoder, Editor, Timer, Typesetter, Quality Checker)

<episode>: Episode yang ingin diubah tandanya

<judul>: Judul garapan yang terdaftar, bisa disingkat sesingkat mungkin

Note: Akan otomatis terubah dari `beres` ke `belum beres` atau sebaliknya jika command ini dipakai
Command ini tidak akan mengannounce perubahan ke channel publik
```
"""  # noqa: E501


def find_user_server(user_id, js_data):
    srv_list = []

    for i, _ in js_data.items():
        srv_list.append(i)

    srv_list.remove("supermod")

    srv_on_list = []

    for srv in srv_list:
        for mod in js_data[srv]["serverowner"]:
            if mod == user_id:
                srv_on_list.append(srv)

    return int(srv_on_list[0])


async def fetch_json() -> dict:
    """
    Open local database
    """
    print("[@] Opening json file")
    if not os.path.isfile("nao_showtimes.json"):
        print("[@] naoTimes are not initiated, skipping.")
        return {}
    json_data = await read_files("nao_showtimes.json")

    return json_data


async def dm_only(ctx):
    return ctx.guild is None


class UsePrivateMessages(commands.CheckFailure):
    pass


def reverse_guild_only():
    async def predicate(ctx):
        if ctx.guild is not None:
            raise UsePrivateMessages("Gunakan DM!")
        return True

    return commands.check(predicate)


class Helper(commands.Cog):
    """Helper module or etcetera module to show help and useless stuff"""

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self._ver: str = bot.semver
        self._pre: str = bot.prefix
        self.logger = logging.getLogger("cogs.helpcmd.Helper")

    def is_msg_empty(self, msg: str, thr: int = 3) -> bool:
        split_msg: List[str] = msg.split(" ")
        split_msg = [m for m in split_msg if m != ""]
        if len(split_msg) < thr:
            return True
        return False

    @commands.command(aliases=["bantuan"])
    async def help(self, ctx):
        new_help_msg = "Dokumentasi telah dipindah ke website baru!\n"
        new_help_msg += "Silakan kunjungi untuk melihat bantuan\n"
        new_help_msg += "https://naotimes.n4o.xyz/\n\n"
        new_help_msg += "Untuk melihat bantuan lama, ketik "
        new_help_msg += f"`{self._pre}oldhelp` di DM Bot"
        await ctx.send(new_help_msg)

    @commands.group(aliases=["bantuanlama"])
    async def oldhelp(self, ctx):
        msg = ctx.message.content
        channel = ctx.message.channel
        is_nsfw = False
        if isinstance(channel, discord.TextChannel):
            is_nsfw = channel.is_nsfw()
        loaded_cogs = list(dict(self.bot.extensions).keys())
        if ctx.invoked_subcommand is None:
            if not self.is_msg_empty(msg, 2):
                return await ctx.send("Tidak dapat menemukan bantuan perintah tersebut.")
            is_owner = await self.bot.is_owner(ctx.author)
            helpcmd = HelpGenerator(self.bot, desc=f"Versi {self._ver}")
            await helpcmd.generate_field("help", desc="Memunculkan bantuan perintah")
            if "cogs.showtimes" in loaded_cogs:
                await helpcmd.generate_field(
                    "help showtimes", desc="Memunculkan bantuan perintah showtimes",
                )
            if "cogs.anilist" in loaded_cogs:
                await helpcmd.generate_field(
                    "help weebs", desc="Memunculkan bantuan perintah anilist/vndb",
                )
            if "cogs.peninjau" in loaded_cogs:
                await helpcmd.generate_field(
                    "help peninjau", desc="Memunculkan bantuan perintah yang " "mengambil data dari website",
                )
            if "cogs.fun" in loaded_cogs:
                await helpcmd.generate_field(
                    "help fun", desc='Melihat bantuan perintah yang "menyenangkan"',
                )
            if "cogs.gamesapi" in loaded_cogs:
                await helpcmd.generate_field(
                    "help games", desc="Melihat bantuan perintah games",
                )
            if is_owner:
                await helpcmd.generate_field("help admin", desc="Memunculkan bantuan perintah admin")
            if "cogs.vote" in loaded_cogs:
                await helpcmd.generate_field(
                    "help vote/votekick/voteban", desc="Melihat Informasi vote system",
                )
            if "cogs.saus" in loaded_cogs:
                await helpcmd.generate_field(
                    "help vote/votekick/voteban", desc="Melihat Informasi vote system",
                )
            if "cogs.nyaa" in loaded_cogs:
                await helpcmd.generate_field("help nyaa", desc="Melihat Informasi command nyaa.si")
            if "cogs.perpus" in loaded_cogs:
                await helpcmd.generate_field("help perpus", desc="Melihat Informasi command perpusindo")
            if "cogs.nh" in loaded_cogs and is_nsfw:
                await helpcmd.generate_field("help nh", desc="Melihat Informasi command nhentai")
            await helpcmd.generate_field("help ping", desc="Pong!")
            await helpcmd.generate_aliases()
            await ctx.send(embed=helpcmd.get())

    @oldhelp.error
    async def oldhelp_error(self, ctx, error):
        if isinstance(error, UsePrivateMessages):
            await ctx.send("Mohon gunakan perintah ini di Private Message/DM")

    @oldhelp.command()
    @commands.is_owner()
    async def admin(self, ctx):
        helpcmd = HelpGenerator(self.bot, "Admin[*]", desc=f"Versi {self._ver}")
        await helpcmd.generate_field(
            "supermotd", desc="Mengirimkan pesan berantai ke tiap " "admin fansub yang terdaftar di naoTimes",
        )
        await helpcmd.generate_field(
            "reload", [{"name": "module", "type": "r"}], desc="Mereload module tertentu",
        )
        await helpcmd.generate_field(
            "load", [{"name": "module", "type": "r"}], desc="Load module tertentu",
        )
        await helpcmd.generate_field(
            "unload", [{"name": "module", "type": "r"}], desc="Unload module tertentu",
        )
        await helpcmd.generate_aliases()
        await ctx.send(embed=helpcmd.get())

    @oldhelp.command()
    async def fun(self, ctx):
        is_nsfw = False
        channel = ctx.message.channel
        if isinstance(channel, discord.TextChannel):
            is_nsfw = channel.is_nsfw()
        helpcmd = HelpGenerator(self.bot, "Fun[*]", desc=f"Versi {self._ver}")
        await helpcmd.generate_field(
            "ui", [{"name": "user", "type": "o"}], desc="Melihat informasi user",
        )
        await helpcmd.generate_field(
            "avatar", [{"name": "user", "type": "o"}], desc="Melihat avatar user",
        )
        await helpcmd.generate_field(
            "f", [{"name": "pesan", "type": "o"}], desc="Berikan F saudara-saudara.",
        )
        await helpcmd.generate_field(
            "kerang", [{"name": "pertanyaan", "type": "r"}], desc="Bertanya kepada kerang ajaib.",
        )
        await helpcmd.generate_field(
            "pilih", [{"name": "...", "type": "r"}], desc="Berikan bot pilihan untuk dipilih.",
        )
        if is_nsfw:
            await helpcmd.generate_field(
                "kontol", desc="Periksa panjang kntl anda",
            )
        await helpcmd.generate_field(
            "8ball", [{"name": "pertanyaan", "type": "r"}], desc="Bertanya ke bola ajaib.",
        )
        await helpcmd.generate_aliases()
        await ctx.send(embed=helpcmd.get())

    @oldhelp.command(aliases=["user", "uinfo", "userinfo"])
    async def ui(self, ctx):
        helpcmd = HelpGenerator(self.bot, "ui", "Melihat informasi user")
        await helpcmd.generate_field(
            "ui",
            [
                {
                    "name": "user",
                    "type": "o",
                    "desc": "**[user]** merupakan ID/Username/" "Mention user orang lain",
                }
            ],
            examples=["", "N4O", "@N4O", "466469077444067372"],
        )
        await helpcmd.generate_aliases(["user", "uinfo", "userinfo"])
        await ctx.send(embed=helpcmd.get())

    @oldhelp.command(aliases=["pp", "profile", "bigprofile", "ava"])
    async def avatar(self, ctx):
        helpcmd = HelpGenerator(self.bot, "avatar", "Melihat profile picture user")
        await helpcmd.generate_field(
            "avatar",
            [
                {
                    "name": "user",
                    "type": "o",
                    "desc": "**[user]** merupakan ID/Username/" "Mention user orang lain",
                }
            ],
            examples=["", "N4O", "@N4O", "466469077444067372"],
        )
        await helpcmd.generate_aliases(["pp", "profile", "bigprofile", "ava"])
        await ctx.send(embed=helpcmd.get())

    @oldhelp.command()
    async def f(self, ctx):
        helpcmd = HelpGenerator(self.bot, "f", "Pencet F untuk memberikan respek")
        await helpcmd.generate_field(
            "f",
            [{"name": "pesan", "type": "o", "desc": "`[pesan]` bebas mau diisi apa aja."}],
            examples=["", "ketauan buka r18"],
        )
        await helpcmd.generate_aliases()
        await ctx.send(embed=helpcmd.get())

    @oldhelp.command(aliases=["kerangajaib"])
    async def kerang(self, ctx):
        helpcmd = HelpGenerator(self.bot, "kerang", "Bertanya kepada kerang ajaib.")
        await helpcmd.generate_field(
            "kerang",
            [{"name": "pertanyaan", "type": "r", "desc": "`<pertanyaan>` akan dijawab oleh kerang ajaib."}],
            examples=["apakah utang saya akan selesai?"],
        )
        await helpcmd.generate_aliases()
        await ctx.send(embed=helpcmd.get())

    @oldhelp.command()
    async def pilih(self, ctx):
        helpcmd = HelpGenerator(self.bot, "pilih", "Berikan bot pilihan untuk dipilih.")
        await helpcmd.generate_field(
            "pilih",
            [
                {
                    "name": "...",
                    "type": "r",
                    "desc": "`<...>` merupakan pilihan yang ingin dipilih.\n"
                    "pisah pilihan dengan `,` (koma).\n"
                    "pilihan yang diberikan tidak terbatas.",
                }
            ],
            examples=["makan, tidur, ngesub"],
        )
        await helpcmd.generate_aliases()
        await ctx.send(embed=helpcmd.get())

    @oldhelp.command(aliases=["penis", "dick", "kntl"])
    async def kontol(self, ctx):
        helpcmd = HelpGenerator(self.bot, "kontol", "Periksa panjang kntl anda.")
        await helpcmd.generate_field(
            "kontol",
            desc="Bot akan memberikan panjang kntl situ\n"
            "`cm` mendapatkan x1 multiplier\n"
            "`m` mendapatkan x2 multiplier\n"
            "`km` mendapatkan x5 multiplier",
        )
        await helpcmd.generate_aliases(["penis", "dick", "kntl"])
        await ctx.send(embed=helpcmd.get())

    @oldhelp.command(name="8ball")
    async def _8ball(self, ctx):
        helpcmd = HelpGenerator(self.bot, "8ball", "Bertanya kepada bola delapan ajaib.")
        await helpcmd.generate_field(
            "8ball",
            [{"name": "pertanyaan", "type": "r", "desc": "`<pertanyaan>` akan dijawab oleh bola delapan."}],
            examples=["apakah utang saya akan selesai?"],
        )
        await helpcmd.generate_aliases()
        await ctx.send(embed=helpcmd.get())

    @oldhelp.command()
    @commands.is_owner()
    async def reload(self, ctx):
        helpcmd = HelpGenerator(self.bot, "reload", "Mereload salah satu module bot.")
        await helpcmd.generate_field(
            "reload",
            [{"name": "module", "type": "r", "desc": "`<module>` yang akan direload."}],
            examples=["anilist", "cogs.anilist"],
        )
        await helpcmd.generate_aliases(add_note=False)
        await ctx.send(embed=helpcmd.get())

    @oldhelp.command()
    @commands.is_owner()
    async def load(self, ctx):
        helpcmd = HelpGenerator(self.bot, "load", "Load salah satu module bot.")
        await helpcmd.generate_field(
            "load",
            [{"name": "module", "type": "r", "desc": "`<module>` yang akan diload."}],
            examples=["anilist", "cogs.anilist"],
        )
        await helpcmd.generate_aliases(add_note=False)
        await ctx.send(embed=helpcmd.get())

    @oldhelp.command()
    @commands.is_owner()
    async def unload(self, ctx):
        helpcmd = HelpGenerator(self.bot, "unload", "Unload salah satu module bot.")
        await helpcmd.generate_field(
            "unload",
            [{"name": "module", "type": "r", "desc": "`<module>` yang akan unload."}],
            examples=["anilist", "cogs.anilist"],
        )
        await helpcmd.generate_aliases(add_note=False)
        await ctx.send(embed=helpcmd.get())

    @oldhelp.command(name="peninjau")
    async def peninjau_help(self, ctx):
        helpcmd = HelpGenerator(
            self.bot, "Peninjau[*]", desc="Bantuan untuk perintah yang mengambil data dari website",
        )
        await helpcmd.generate_field(
            "anibin",
            desc="Mencari resolusi asli anime melalui anibin.",
            opts=[{"name": "judul", "type": "r"}],
        )
        await helpcmd.generate_field(
            "speedsub", desc="Speedsub file bokong dengan GTL.", opts=[{"name": "target_lang", "type": "r"}],
        )
        await helpcmd.generate_field(
            "kurs",
            desc="Konversi nilai mata uang maupun cryptocurrency.",
            opts=[
                {"name": "dari", "type": "r"},
                {"name": "ke", "type": "r"},
                {"name": "jumlah", "type": "r"},
            ],
        )
        await helpcmd.generate_field(
            "kbbi", desc="Mencari kata di KBBI Daring.", opts=[{"name": "kata", "type": "r"}],
        )
        await helpcmd.generate_field(
            "sinonim", desc="Mencari sinonim sebuah kata.", opts=[{"name": "kata", "type": "r"}],
        )
        await helpcmd.generate_field(
            "antonim", desc="Mencari antonim sebuah kata.", opts=[{"name": "kata", "type": "r"}],
        )
        await helpcmd.generate_field(
            "jisho", desc="Mencari kata di Jisho.", opts=[{"name": "kata", "type": "r"}],
        )
        await helpcmd.generate_aliases()
        await ctx.send(embed=helpcmd.get())

    @oldhelp.command()
    async def anibin(self, ctx):
        helpcmd = HelpGenerator(self.bot, "anibin", "Mencari resolusi asli anime melalui anibin.")
        await helpcmd.generate_field(
            "anibin",
            [{"name": "judul", "type": "r", "desc": "`<judul>` merupakan kueri yang akan dicari nanti"}],
            examples=["私に天使が舞い降りた"],
        )
        await helpcmd.generate_aliases()
        await ctx.send(embed=helpcmd.get())

    @oldhelp.command()
    async def kbbi(self, ctx):
        helpcmd = HelpGenerator(self.bot, "kbbi", "Mencari kata di KBBI Daring.")
        await helpcmd.generate_field(
            "kbbi",
            [{"name": "kata", "type": "r", "desc": "`<kata>` merupakan kueri yang akan dicari nanti"}],
            examples=["tes", "contoh", "peladen"],
        )
        await helpcmd.generate_aliases()
        await ctx.send(embed=helpcmd.get())

    @oldhelp.command(aliases=["persamaankata", "persamaan"])
    async def sinonim(self, ctx):
        helpcmd = HelpGenerator(self.bot, "sinonim", "Mencari sinonim sebuah kata.")
        await helpcmd.generate_field(
            "sinonim",
            [{"name": "kata", "type": "r", "desc": "`<kata>` merupakan kueri yang akan dicari nanti"}],
            examples=["duduk", "makan"],
        )
        await helpcmd.generate_aliases(["persamaankata", "persamaan"])
        await ctx.send(embed=helpcmd.get())

    @oldhelp.command(aliases=["lawankata"])
    async def antonim(self, ctx):
        helpcmd = HelpGenerator(self.bot, "antonim", "Mencari antonim sebuah kata.")
        await helpcmd.generate_field(
            "antonim",
            [{"name": "kata", "type": "r", "desc": "`<kata>` merupakan kueri yang akan dicari nanti"}],
            examples=["berdiri", "hidup"],
        )
        await helpcmd.generate_aliases(["lawankata"])
        await ctx.send(embed=helpcmd.get())

    @oldhelp.command(aliases=["kanji"])
    async def jisho(self, ctx):
        helpcmd = HelpGenerator(self.bot, "jisho", "Mencari kata di Jisho.")
        await helpcmd.generate_field(
            "jisho",
            [{"name": "kata", "type": "r", "desc": "`<kata>` merupakan kueri yang akan dicari nanti"}],
            examples=["duduk", "makan"],
        )
        await helpcmd.generate_aliases(["kanji"])
        await ctx.send(embed=helpcmd.get())

    @oldhelp.command(aliases=["konversiuang", "currency"])
    async def kurs(self, ctx):
        helpcmd = HelpGenerator(self.bot, "kurs", "Konversi nilai mata uang maupun cryptocurrency.")
        await helpcmd.generate_field(
            "kurs",
            [
                {
                    "name": "dari",
                    "type": "r",
                    "desc": "`<dari>` merupakan kode mata uang asal negara"
                    " (3 huruf)\nataupun kode mata uang cryptocurrency",
                },
                {
                    "name": "ke",
                    "type": "r",
                    "desc": "`<ke>` merupakan kode mata uang tujuan negara"
                    " (3 huruf)\nataupun kode mata uang cryptocurrency",
                },
                {
                    "name": "jumlah",
                    "type": "o",
                    "desc": "`<jumlah>` yang ingin dikonversi\n"
                    "Jika ada koma, ganti dengan titik.\n"
                    "Jika tidak diberikan jumlah, akan otomatis pake angka 1",
                },
            ],
            examples=["jpy idr 490", "usd idr 4.99", "btc idr 1"],
        )
        await helpcmd.generate_aliases(["konversiuang", "currency"])
        await ctx.send(embed=helpcmd.get())

    @oldhelp.command(aliases=["fastsub", "gtlsub"])
    async def speedsub(self, ctx):
        helpcmd = HelpGenerator(self.bot, "kurs", "Speedsub file bokong dengan GTL.")
        extra_txt = "Tautkan/Tambahkan Attachments file .ass atau .srt "
        extra_txt += f"dan isi pesannya dengan `{self._pre}speedsub`\n\n"
        extra_txt += "`<kode_bahasa>` merupakan kode bahasa 2 huruf, silakan cari di google dengan query `ISO 639-1`"  # noqa: E501
        await helpcmd.generate_field(
            "kurs",
            [{"name": "kode_bahasa", "type": "o", "desc": extra_txt}],
            examples=["speedsub", "speedsub jv"],
        )
        await helpcmd.generate_aliases(["fastsub", "gtlsub"])
        await ctx.send(embed=helpcmd.get())

    @oldhelp.command(name="weebs")
    async def weebs_help(self, ctx):
        helpcmd = HelpGenerator(self.bot, "Weebs[*]", "Bantuan untuk perintah Anilist dan VNDB.")
        await helpcmd.generate_field(
            "anime", [{"name": "judul", "type": "r"}], desc="Cari informasi sebuah anime melalui Anilist.co",
        )
        await helpcmd.generate_field(
            "manga", [{"name": "judul", "type": "r"}], desc="Cari informasi sebuah manga melalui Anilist.co",
        )
        await helpcmd.generate_field(
            "tayang", desc="Melihat jadwal tayang anime musim sekarang.",
        )
        await helpcmd.generate_field(
            "vn", [{"name": "judul", "type": "r"}], desc="Melihat informasi sebuah VN melalui VNDB.",
        )
        await helpcmd.generate_field(
            "randomvn", desc="Melihat informasi VN random (dipilih oleh bot).",
        )
        await helpcmd.generate_aliases()
        await ctx.send(embed=helpcmd.get())

    @oldhelp.command(aliases=["animu", "kartun"])
    async def anime(self, ctx):
        helpcmd = HelpGenerator(self.bot, "anime", "Cari informasi sebuah anime melalui Anilist.co.",)
        await helpcmd.generate_field(
            "anime", [{"name": "judul", "type": "r", "desc": animangavn_textdata}], examples=["hitoribocchi"],
        )
        helpcmd.embed.add_field(
            name="*Tambahan*",
            value="⏪ **(Selanjutnya)** ⏩ **(Sebelumnya)** "
            "✅ **(Selesai melihat)**\n⏳ **(Waktu Episode selanjutnya)** "
            "👍 **(Melihat Info kembali)**\n"
            "📺 **(Melihat tempat streaming legal)**",
            inline=False,
        )
        await helpcmd.generate_aliases(["animu", "kartun"])
        await ctx.send(embed=helpcmd.get())

    @oldhelp.command(aliases=["mango", "komik"])
    async def manga(self, ctx):
        helpcmd = HelpGenerator(self.bot, "manga", "Cari informasi sebuah manga melalui Anilist.co.",)
        await helpcmd.generate_field(
            "manga",
            [{"name": "judul", "type": "r", "desc": animangavn_textdata}],
            examples=["yagate kimi ni naru"],
        )
        helpcmd.embed.add_field(
            name="*Tambahan*",
            value="⏪ **(Selanjutnya)** ⏩ **(Sebelumnya)** " "✅ **(Selesai melihat)**",
            inline=False,
        )
        await helpcmd.generate_aliases(["mango", "komik"])
        await ctx.send(embed=helpcmd.get())

    @oldhelp.command()
    async def tayang(self, ctx):
        helpcmd = HelpGenerator(self.bot, "tayang", "Melihat jadwal tayang anime musim sekarang.",)
        await helpcmd.generate_field(
            "tayang",
            desc="Melihat jadwal tayang dengan listing per sisa hari" " menuju episode selanjutnya.",
        )
        helpcmd.embed.add_field(
            name="*Tambahan*",
            value="0️⃣ - 🇭 **(Melihat listing per sisa hari)**\n" "✅ **(Selesai melihat)**",
            inline=False,
        )
        await helpcmd.generate_aliases()
        await ctx.send(embed=helpcmd.get())

    @oldhelp.command(name="vn", aliases=["vndb", "visualnovel", "eroge"])
    async def vn_help(self, ctx):
        helpcmd = HelpGenerator(self.bot, "vn", "Melihat informasi sebuah VN melalui VNDB.")
        await helpcmd.generate_field(
            "vn",
            [{"name": "judul", "type": "r", "desc": animangavn_textdata}],
            examples=["steins;gate", "ao no kana"],
        )
        helpcmd.embed.add_field(
            name="*Tambahan*",
            value="⏪ **(Selanjutnya)** ⏩ **(Sebelumnya)** 📸 "
            "**(Melihat screenshot)**\n✅ **(Melihat Info kembali)**",
            inline=False,
        )
        await helpcmd.generate_aliases(["vndb", "visualnovel", "eroge"])
        await ctx.send(embed=helpcmd.get())

    @oldhelp.command(aliases=["randomvisualnovel", "randomeroge", "vnrandom"])
    async def randomvn(self, ctx):
        helpcmd = HelpGenerator(self.bot, "vn", "Melihat informasi sebuah VN random.")
        await helpcmd.generate_field(
            "randomvn", desc="VN akan dicari dipilih secara " "random oleh bot menggunakan RNG.",
        )
        helpcmd.embed.add_field(
            name="*Tambahan*", value="📸 **(Melihat screenshot)** ✅ **(Melihat Info kembali)**", inline=False,
        )
        await helpcmd.generate_aliases(["randomvisualnovel", "randomeroge", "vnrandom"])
        await ctx.send(embed=helpcmd.get())

    @oldhelp.group()
    async def showtimes(self, ctx):
        msg = ctx.message.content
        if not ctx.invoked_subcommand:
            if not self.is_msg_empty(msg):
                return await ctx.send("Tidak dapat menemukan bantuan perintah tersebut.")
            helpcmd = HelpGenerator(self.bot, "Showtimes[*]", desc=f"Versi {self._ver}")
            await helpcmd.generate_field(
                "help showtimes user", desc="Memunculkan bantuan perintah showtimes untuk user biasa",
            )
            await helpcmd.generate_field(
                "help showtimes staff", desc="Memunculkan bantuan perintah showtimes untuk staff",
            )
            await helpcmd.generate_field(
                "help showtimes admin", desc="Memunculkan bantuan perintah showtimes untuk admin",
            )
            await helpcmd.generate_field(
                "help showtimes alias", desc="Memunculkan bantuan perintah showtimes alias",
            )
            await helpcmd.generate_field(
                "help showtimes kolaborasi", desc="Memunculkan bantuan perintah showtimes kolaborasi",
            )
            is_owner = await self.bot.is_owner(ctx.author)
            if is_owner:
                await helpcmd.generate_field(
                    "help showtimes owner", desc="Memunculkan bantuan perintah showtimes" " untuk owner bot",
                )
            await helpcmd.generate_aliases()
            await ctx.send(embed=helpcmd.get())

    def get_text(self, switch):
        judul_info = "`<judul>` adalah garapan yang "
        judul_info += "terdaftar di database naoTimes."
        judul_info += "\n`<judul>` dapat disingkat sesingkat mungkin."

        posisi_info = "`<posisi>` merupakan salah satu dari 7 posisi ini:\n"
        posisi_info += "```\ntl, tlc, enc, ed, tm, ts, atau qc\n"
        posisi_info += "(Translator, Translation Checker, Encoder, Editor, "
        posisi_info += "Timer, Typesetter, Quality Checker)\n```"

        jumlah_info = "`<jumlah>` adalah total episode yang mau dirilis (dari episode yang terakhir dirilis)\n"  # noqa: E501
        jumlah_info += "Misalkan lagi ngerjain Episode 4, terus mau rilis sampe episode 7\n"  # noqa: E501
        jumlah_info += "Total dari Episode 4 sampai 7 ada 4 (4, 5, 6, 7)\n"
        jumlah_info += "Maka tulis jumlahnya 4"

        switches = {
            "judul": judul_info,
            "posisi": posisi_info,
            "jumlah": jumlah_info,
        }

        return switches.get(switch, "")

    @showtimes.command(name="user", aliases=["pengguna"])
    async def showtimes_user(self, ctx):
        helpcmd = HelpGenerator(
            self.bot, "Showtimes User[*]", desc="Perintah-perintah yang dapat digunakan oleh semua user.",
        )
        await helpcmd.generate_field(
            "tagih", desc="Melihat progress garapan sebuah anime.", opts=[{"name": "judul", "type": "r"}],
        )
        await helpcmd.generate_field(
            "jadwal", desc="Melihat jadwal episode selanjutnya untuk garapan fansub.",
        )
        await helpcmd.generate_field(
            "staff", desc="Melihat staff garapan sebuah anime.", opts=[{"name": "judul", "type": "r"}],
        )
        await helpcmd.generate_aliases(["pengguna"])
        await ctx.send(embed=helpcmd.get())

    @oldhelp.command(aliases=["blame", "mana"])
    async def tagih(self, ctx):
        helpcmd = HelpGenerator(self.bot, "tagih", "Melihat progress garapan sebuah anime.")
        extra_info = self.get_text("judul") + "\n"
        extra_info += "Jika judul tidak diberikan, akan diberikan list"
        extra_info += " seluruh garapan fansub yang terdaftar."
        await helpcmd.generate_field(
            "tagih", [{"name": "judul", "type": "r", "desc": extra_info}], examples=["hitoribocchi", ""],
        )
        await helpcmd.generate_aliases(["blame", "mana"])
        await ctx.send(embed=helpcmd.get())

    @oldhelp.command(aliases=["airing"])
    async def jadwal(self, ctx):
        helpcmd = HelpGenerator(
            self.bot, "jadwal", "Melihat jadwal episode selanjutnya untuk garapan fansub.",
        )
        await helpcmd.generate_field(
            "jadwal", desc="Memberikan list jadwal episode selanjutnya " "untuk garapan fansub musim ini.",
        )
        await helpcmd.generate_aliases(["airing"])
        await ctx.send(embed=helpcmd.get())

    @oldhelp.command(aliases=["tukangdelay", "pendelay"])
    async def staff(self, ctx):
        helpcmd = HelpGenerator(self.bot, "staff", "Melihat staff garapan sebuah anime.")
        extra_info = "`<judul>` yang terdaftar di database naoTimes."
        await helpcmd.generate_field("staff", [{"name": "judul", "type": "r", "desc": extra_info}])
        await helpcmd.generate_aliases(["tukangdelay", "pendelay"])
        await ctx.send(embed=helpcmd.get())

    @showtimes.command(name="staff")
    async def showtimes_staff(self, ctx):
        helpcmd = HelpGenerator(
            self.bot, "Showtimes Staff[*]", desc="Perintah yang dapat digunakan oleh staff fansub.",
        )
        await helpcmd.generate_field(
            "beres",
            desc="Menandakan posisi garapan episode menjadi beres.",
            opts=[{"name": "posisi", "type": "r"}, {"name": "judul", "type": "r"}],
        )
        await helpcmd.generate_field(
            "gakjadi",
            desc="Menandakan posisi garapan episode menjadi belum beres.",
            opts=[{"name": "posisi", "type": "r"}, {"name": "judul", "type": "r"}],
        )
        await helpcmd.generate_field(
            "tandakan",
            desc="Mengubah status untuk posisi untuk episode tertentu"
            " dari belum ke sudah atau sebaliknya.",
            opts=[
                {"name": "posisi", "type": "r"},
                {"name": "episode", "type": "r"},
                {"name": "judul", "type": "r"},
            ],
        )
        await helpcmd.generate_field(
            "rilis",
            desc="Merilis garapan!\n" "*Hanya bisa dipakai oleh Admin atau tukang QC*",
            opts=[{"name": "...", "type": "r"}],
        )
        await helpcmd.generate_field(
            "batalrilis",
            desc="Membatalkan rilisan garapan!\n" "*Hanya bisa dipakai oleh Admin atau tukang QC*",
            opts=[{"name": "judul", "type": "r"}],
        )
        await helpcmd.generate_aliases()
        await ctx.send(embed=helpcmd.get())

    @oldhelp.command(aliases=["done"])
    async def beres(self, ctx):
        helpcmd = HelpGenerator(self.bot, "beres", "Menandakan posisi garapan episode menjadi beres.",)
        await helpcmd.generate_field(
            "beres",
            [
                {"name": "posisi", "type": "r", "desc": self.get_text("posisi")},
                {"name": "judul", "type": "r", "desc": self.get_text("judul")},
            ],
            examples=["enc hitoribocchi", "ts hitoribocchi"],
        )
        await helpcmd.generate_aliases(["done"])
        await ctx.send(embed=helpcmd.get())

    @oldhelp.command(aliases=["undone", "cancel"])
    async def gakjadi(self, ctx):
        helpcmd = HelpGenerator(
            self.bot, "gakjadi", "Menandakan posisi garapan episode menjadi belum beres.",
        )
        await helpcmd.generate_field(
            "gakjadi",
            [
                {"name": "posisi", "type": "r", "desc": self.get_text("posisi")},
                {"name": "judul", "type": "r", "desc": self.get_text("judul")},
            ],
            examples=["enc hitoribocchi", "ts hitoribocchi"],
        )
        await helpcmd.generate_aliases(["undone", "cancel"])
        await ctx.send(embed=helpcmd.get())

    @oldhelp.command(aliases=["release"])
    async def rilis(self, ctx):
        helpcmd = HelpGenerator(
            self.bot, "rilis", "Merilis garapan!\n" "*Hanya bisa dipakai oleh Admin atau tukang QC*",
        )
        await helpcmd.generate_field(
            "rilis",
            [{"name": "judul", "type": "r", "desc": self.get_text("judul")}],
            desc="Merilis episode yang telah selesai dikerjakan.",
            examples=["hitoribocchi"],
        )
        await helpcmd.generate_field(
            "rilis batch",
            [
                {"name": "jumlah", "type": "r", "desc": self.get_text("jumlah")},
                {"name": "judul", "type": "r", "desc": self.get_text("judul")},
            ],
            desc="Merilis beberapa episode sekaligus.",
            examples=["batch 4 hitoribocchi"],
        )
        await helpcmd.generate_field(
            "rilis semua",
            [{"name": "judul", "type": "r", "desc": self.get_text("judul")}],
            desc="Merilis semua episode sekaligus.",
            examples=["semua hitoribocchi"],
        )
        await helpcmd.generate_aliases(["release"])
        await ctx.send(embed=helpcmd.get())

    @oldhelp.command(aliases=["gakjadirilis", "revert"])
    async def batalrilis(self, ctx):
        helpcmd = HelpGenerator(
            self.bot,
            "batalrilis",
            "Membatalkan rilisan episode yang dirlis paling terakhir.\n"
            "*Hanya bisa dipakai oleh Admin atau tukang QC*",
        )
        await helpcmd.generate_field(
            "batalrilis",
            [{"name": "judul", "type": "r", "desc": self.get_text("judul")}],
            examples=["hitoribocchi"],
        )
        await helpcmd.generate_aliases(["gakjadirilis", "revert"])
        await ctx.send(embed=helpcmd.get())

    @oldhelp.command(aliases=["mark"])
    async def tandakan(self, ctx):
        helpcmd = HelpGenerator(
            self.bot,
            "tandakan",
            "Menandakan status garapan episode tertentu untuk "
            "posisi tertentu menjadi beres ataupun sebaliknya.",
        )
        await helpcmd.generate_field(
            "tandakan",
            [
                {"name": "posisi", "type": "r", "desc": self.get_text("posisi")},
                {"name": "episode", "type": "r", "desc": "Episode yang ingin ditandakan."},
                {"name": "judul", "type": "r", "desc": self.get_text("judul")},
            ],
            examples=["ts 4 tate", "enc 4 tate", "enc 5 tate"],
        )
        await helpcmd.generate_aliases(["mark"])
        await ctx.send(embed=helpcmd.get())

    @showtimes.command(name="alias")
    async def showtimes_alias(self, ctx):
        helpcmd = HelpGenerator(
            self.bot, "Showtimes Alias[*]", desc="Perintah yang dapat digunakan oleh admin/owner fansub.",
        )
        await helpcmd.generate_field(
            "alias", desc="Menambah alias baru untuk sebuah judul.",
        )
        await helpcmd.generate_field(
            "alias list", desc="Melihat alias untuk sebuah judul.", opts=[{"name": "judul", "type": "r"}],
        )
        await helpcmd.generate_field(
            "alias hapus", desc="Menghapus alias untuk sebuah judul.", opts=[{"name": "judul", "type": "r"}],
        )
        await helpcmd.generate_aliases()
        await ctx.send(embed=helpcmd.get())

    @oldhelp.group()
    async def alias(self, ctx):
        msg = ctx.message.content
        if ctx.invoked_subcommand is None:
            if not self.is_msg_empty(msg):
                return await ctx.send("Tidak dapat menemukan bantuan perintah tersebut.")
            helpcmd = HelpGenerator(self.bot, "alias", desc=f"Versi {self._ver}",)
            txt_help = "Menambah alias baru untuk sebuah judul.\n"
            txt_help += f"Command ini bersifat interaktif, cukup ketik {self._pre}alias"
            txt_help += " untuk memulai proses menambahkan alias baru"
            await helpcmd.generate_field("alias", desc=txt_help)
            await helpcmd.generate_aliases()
            await ctx.send(embed=helpcmd.get())

    @alias.command(name="list")
    async def alias_list_help(self, ctx):
        helpcmd = HelpGenerator(self.bot, "alias list", desc="Melihat alias untuk sebuah judul.",)
        await helpcmd.generate_field(
            "alias list", opts=[{"name": "judul", "type": "r", "desc": self.get_text("judul")}],
        )
        await helpcmd.generate_aliases()
        await ctx.send(embed=helpcmd.get())

    @alias.command(name="hapus")
    async def alias_hapus_help(self, ctx):
        helpcmd = HelpGenerator(self.bot, "alias hapus", desc="Menghapus alias untuk sebuah judul.",)
        await helpcmd.generate_field(
            "alias hapus", opts=[{"name": "judul", "type": "r", "desc": self.get_text("judul")}],
        )
        await helpcmd.generate_aliases()
        await ctx.send(embed=helpcmd.get())

    @showtimes.command(name="kolaborasi", aliases=["joint", "join", "koleb"])
    async def showtimes_kolaborasi(self, ctx):
        helpcmd = HelpGenerator(
            self.bot,
            "Showtimes Kolaborasi[*]",
            desc="Perintah yang dapat digunakan oleh admin/owner fansub.",
        )
        await helpcmd.generate_field(
            "kolaborasi dengan",
            desc="Memulai proses kolaborasi garapan dengan fansub lain.",
            opts=[{"name": "server id kolaborasi", "type": "r"}, {"name": "judul", "type": "r"}],
        )
        await helpcmd.generate_field(
            "kolaborasi konfirmasi",
            desc="Konfirmasi proses kolaborasi garapan.",
            opts=[{"name": "kode unik", "type": "r"}],
        )
        await helpcmd.generate_field(
            "kolaborasi putus",
            desc="Memutuskan hubungan kolaborasi suatu garapan.",
            opts=[{"name": "judul", "type": "r"}],
        )
        await helpcmd.generate_field(
            "kolaborasi batalkan",
            desc="Membatalkan proses kolaborasi.",
            opts=[{"name": "server id kolaborasi", "type": "r"}, {"name": "kode unik", "type": "r"}],
        )
        await helpcmd.generate_aliases(["joint", "join", "koleb"])
        await ctx.send(embed=helpcmd.get())

    @showtimes.command(name="admin")
    async def showtimes_admin(self, ctx):
        helpcmd = HelpGenerator(
            self.bot, "Showtimes Admin[*]", desc="Perintah yang dapat digunakan oleh admin/owner fansub.",
        )
        await helpcmd.generate_field(
            "tambahutang", desc="Menambah garapan baru ke database.",
        )
        await helpcmd.generate_field(
            "ubahdata", desc="Mengubah data internal suatu garapan.", opts=[{"name": "judul", "type": "r"}],
        )
        await helpcmd.generate_aliases()
        await ctx.send(embed=helpcmd.get())

    @oldhelp.command()
    async def ubahdata(self, ctx):
        helpcmd = HelpGenerator(
            self.bot,
            "ubahdata",
            "Mengubah data internal suatu garapan.\n" "*Hanya bisa dipakai oleh Admin.*",
        )
        await helpcmd.generate_field(
            "ubahdata",
            [{"name": "judul", "type": "r", "desc": self.get_text("judul")}],
            examples=["hitoribocchi"],
        )
        await helpcmd.generate_aliases()
        await ctx.send(embed=helpcmd.get())

    @oldhelp.command(aliases=["addnew"])
    async def tambahutang(self, ctx):
        helpcmd = HelpGenerator(
            self.bot, "tambahutang", f"Versi {self._ver}\n" "*Hanya bisa dipakai oleh Admin.*",
        )
        txt_help = "Menambah garapan baru ke database.\n"
        txt_help += f"Command ini bersifat interaktif, cukup ketik {self._pre}tambahutang"
        txt_help += " untuk memulai proses menambahkan utang/garapan baru"
        await helpcmd.generate_field("tambahutang", desc=txt_help)
        await helpcmd.generate_aliases(["addnew"])
        await ctx.send(embed=helpcmd.get())

    @showtimes.command(name="owner", aliases=["naotimesadmin", "naoadmin"])
    @commands.is_owner()
    async def showtimes_owner(self, ctx):
        helpcmd = HelpGenerator(
            self.bot, "Showtimes Owner[*]", desc="Perintah yang dapat digunakan oleh owner bot.",
        )
        await helpcmd.generate_field(
            "ntadmin initiate", desc="Menginisiasi showtimes.",
        )
        await helpcmd.generate_field(
            "ntadmin tambah",
            desc="Menambah server baru ke database naoTimes.",
            opts=[
                {"name": "server id", "type": "r"},
                {"name": "admin id", "type": "r"},
                {"name": "#progress channel", "type": "o"},
            ],
        )
        await helpcmd.generate_field(
            "ntadmin hapus",
            desc="Menghapus server dari database naoTimes.",
            opts=[{"name": "server id", "type": "r"}],
        )
        await helpcmd.generate_field(
            "ntadmin tambahadmin",
            desc="Menambah admin ke server baru yang terdaftar di database.",
            opts=[{"name": "server id", "type": "r"}, {"name": "admin id", "type": "r"}],
        )
        await helpcmd.generate_field(
            "ntadmin hapusadmin",
            desc="Menghapus admin dari server baru yang" " terdaftar di database.",
            opts=[{"name": "server id", "type": "r"}, {"name": "admin id", "type": "r"}],
        )
        await helpcmd.generate_field(
            "ntadmin fetchdb", desc="Mengambil database lokal dan kirim ke Discord.",
        )
        await helpcmd.generate_field(
            "ntadmin patchdb", desc="Update database dengan file yang dikirim user.",
        )
        await helpcmd.generate_field(
            "ntadmin forcepull", desc="Update paksa database lokal dengan database utama.",
        )
        await helpcmd.generate_field(
            "ntadmin forceupdate", desc="Update paksa database utama dengan database lokal.",
        )
        await helpcmd.generate_aliases(["naotimesadmin", "naoadmin"])
        await ctx.send(embed=helpcmd.get())

    @oldhelp.command()
    async def vote(self, ctx):
        helpmain = discord.Embed(
            title="Bantuan Perintah (!vote)", description=f"versi {self._ver}", color=0x00AAAA,
        )
        helpmain.set_thumbnail(url="https://image.ibb.co/darSzH/question_mark_1750942_640.png")
        helpmain.set_author(name="naoTimes", icon_url="https://p.n4o.xyz/i/naotimes_ava.png")
        helpmain.add_field(
            name="!vote <judul> <timer> <opsi>",
            value="```<judul>: Judul voting (Gunakan kutip dua)\n"
            "<timer>: Waktu pengumpulan vote sebelum proses "
            "(Default: 3 menit, minimum: 3 menit)\n"
            "<opsi>: Pilihan, dapat ditulis sampai 10 opsi "
            "(Gunakan kutip dua)```",
            inline=False,
        )
        helpmain.add_field(
            name="Contoh",
            value='!vote "Mi Instan Terbaik" 5 "Indomie" ' '"Mie Sedap" "Sarimi" "Lain-Lain"',
            inline=False,
        )
        helpmain.add_field(
            name="*Catatan*",
            value="Semua command bisa dilihat infonya " "dengan !help <nama command>",
            inline=False,
        )
        helpmain.set_footer(text="Dibawakan oleh naoTimes " f"|| Dibuat oleh N4O#8868 versi {self._ver}")
        await ctx.send(embed=helpmain)

    @oldhelp.command()
    async def votekick(self, ctx):
        helpmain = discord.Embed(
            title="Bantuan Perintah (!votekick)", description=f"versi {self._ver}", color=0x00AAAA,
        )
        helpmain.set_thumbnail(url="https://image.ibb.co/darSzH/question_mark_1750942_640.png")
        helpmain.set_author(name="naoTimes", icon_url="https://p.n4o.xyz/i/naotimes_ava.png")
        helpmain.add_field(
            name="!votekick <user> <limit> <timer>",
            value="```Melakukan votekick\n<user>: mention atau ketik IDnya"
            "\n<limit>: limit orang yang harus react (Default: 5, minimum: 5)"
            "\n<timer>: waktu pengumpulan vote sebelum proses "
            "(Default: 60 detik, minimum: 30 detik)```",
            inline=False,
        )
        helpmain.add_field(
            name="Contoh", value="!votekick @N4O\n!votekick 466469077444067372", inline=False,
        )
        helpmain.add_field(
            name="*Catatan*",
            value="Semua command bisa dilihat infonya " "dengan !help <nama command>",
            inline=False,
        )
        helpmain.set_footer(text="Dibawakan oleh naoTimes " f"|| Dibuat oleh N4O#8868 versi {self._ver}")
        await ctx.send(embed=helpmain)

    @oldhelp.command()
    async def voteban(self, ctx):
        helpmain = discord.Embed(
            title="Bantuan Perintah (!voteban)", description=f"versi {self._ver}", color=0x00AAAA,
        )
        helpmain.set_thumbnail(url="https://image.ibb.co/darSzH/question_mark_1750942_640.png")
        helpmain.set_author(name="naoTimes", icon_url="https://p.n4o.xyz/i/naotimes_ava.png")
        helpmain.add_field(
            name="!voteban <user> <limit> <timer>",
            value="```Melakukan voteban\n<user>: mention atau ketik IDnya"
            "\n<limit>: limit orang yang harus react (Default: 5, minimum: 5)"
            "\n<timer>: waktu pengumpulan vote sebelum proses "
            "(Default: 60 detik, minimum: 30 detik)```",
            inline=False,
        )
        helpmain.add_field(
            name="Contoh", value="!voteban @N4O\n!voteban 466469077444067372", inline=False,
        )
        helpmain.add_field(
            name="*Catatan*",
            value="Semua command bisa dilihat infonya " "dengan !help <nama command>",
            inline=False,
        )
        helpmain.set_footer(text="Dibawakan oleh naoTimes " f"|| Dibuat oleh N4O#8868 versi {self._ver}")
        await ctx.send(embed=helpmain)

    @oldhelp.group(name="nyaa")
    async def nyaahelp(self, ctx):
        if not ctx.invoked_subcommand:
            helpmain = discord.Embed(
                title="Bantuan Perintah (!nyaa)", description=f"versi {self._ver}", color=0x00AAAA,
            )
            helpmain.set_thumbnail(url="https://image.ibb.co/darSzH/question_mark_1750942_640.png")
            helpmain.set_author(
                name="naoTimes", icon_url="https://p.n4o.xyz/i/naotimes_ava.png",
            )
            helpmain.add_field(
                name="!nyaa", value="```Memunculkan bantuan perintah```", inline=False,
            )
            helpmain.add_field(
                name="!nyaa cari <argumen>",
                value="```Mencari torrent di nyaa.si " "(gunakan argumen -h untuk melihat bantuan)```",
                inline=False,
            )
            helpmain.add_field(
                name="!nyaa terbaru <argumen>",
                value="```Melihat 10 torrents terbaru " "(gunakan argumen -h untuk melihat bantuan)```",
                inline=False,
            )
            helpmain.add_field(
                name="!nyaa kategori <tipe>",
                value="```Melihat kategori apa aja yang bisa dipakai"
                "\n<tipe> ada 2 yaitu, normal dan sukebei```",
                inline=False,
            )
            helpmain.add_field(name="Aliases", value="Tidak ada", inline=False)
            helpmain.set_footer(text="Dibawakan oleh naoTimes " f"|| Dibuat oleh N4O#8868 versi {self._ver}")
            await ctx.send(embed=helpmain)

    @nyaahelp.command(aliases=["search"])
    async def cari(self, ctx):
        helpmain = discord.Embed(
            title="Bantuan Perintah (!nyaa cari)", description=f"versi {self._ver}", color=0x00AAAA,
        )
        helpmain.set_thumbnail(url="https://image.ibb.co/darSzH/question_mark_1750942_640.png")
        helpmain.set_author(name="naoTimes", icon_url="https://p.n4o.xyz/i/naotimes_ava.png")
        helpmain.add_field(
            name="!nyaa cari <opsi> <pencarian>",
            value="```Mencari sesuatu dari nyaa, opsi " "dapat dilihat dengan:\n!nyaa cari -h```",
            inline=False,
        )
        helpmain.add_field(
            name="Contoh",
            value="!nyaa cari -C anime --trusted -u " 'HorribleSubs "Hitoribocchi"',
            inline=False,
        )
        helpmain.add_field(name="Aliases", value="!nyaa cari, !nyaa search", inline=False)
        helpmain.add_field(
            name="*Catatan*",
            value="Semua command bisa dilihat infonya " "dengan !help <nama command>",
            inline=False,
        )
        helpmain.set_footer(text="Dibawakan oleh naoTimes " f"|| Dibuat oleh N4O#8868 versi {self._ver}")
        await ctx.send(embed=helpmain)

    @nyaahelp.command(aliases=["latest"])
    async def terbaru(self, ctx):
        helpmain = discord.Embed(
            title="Bantuan Perintah (!nyaa terbaru)", description=f"versi {self._ver}", color=0x00AAAA,
        )
        helpmain.set_thumbnail(url="https://image.ibb.co/darSzH/question_mark_1750942_640.png")
        helpmain.set_author(name="naoTimes", icon_url="https://p.n4o.xyz/i/naotimes_ava.png")
        helpmain.add_field(
            name="!nyaa terbaru <opsi>",
            value="```Melihat 10 torrent terbaru dari nyaa, opsi dapat "
            "dilihat dengan:\n!nyaa terbaru -h```",
            inline=False,
        )
        helpmain.add_field(
            name="Contoh", value="!nyaa terbaru -C anime --trusted -u HorribleSubs", inline=False,
        )
        helpmain.add_field(name="Aliases", value="!nyaa terbaru, !nyaa latest", inline=False)
        helpmain.add_field(
            name="*Catatan*",
            value="Semua command bisa dilihat infonya " "dengan !help <nama command>",
            inline=False,
        )
        helpmain.set_footer(text="Dibawakan oleh naoTimes " f"|| Dibuat oleh N4O#8868 versi {self._ver}")
        await ctx.send(embed=helpmain)

    @nyaahelp.command(aliases=["category"])
    async def kategori(self, ctx):
        helpmain = discord.Embed(
            title="Bantuan Perintah (!nyaa cari)", description=f"versi {self._ver}", color=0x00AAAA,
        )
        helpmain.set_thumbnail(url="https://image.ibb.co/darSzH/question_mark_1750942_640.png")
        helpmain.set_author(name="naoTimes", icon_url="https://p.n4o.xyz/i/naotimes_ava.png")
        helpmain.add_field(
            name="!nyaa katergori <tipe>",
            value="```Melihat kategori\n<tipe> ada 2 yaitu:" "\n- normal\n- sukebei```",
            inline=False,
        )
        helpmain.add_field(
            name="Contoh", value="!nyaa kategori normal\n!nyaa kategori sukebei", inline=False,
        )
        helpmain.add_field(
            name="Aliases", value="!nyaa kategori, !nyaa category", inline=False,
        )
        helpmain.add_field(
            name="*Catatan*",
            value="Semua command bisa dilihat infonya " "dengan !help <nama command>",
            inline=False,
        )
        helpmain.set_footer(text="Dibawakan oleh naoTimes " f"|| Dibuat oleh N4O#8868 versi {self._ver}")
        await ctx.send(embed=helpmain)

    @oldhelp.group(name="perpus", aliases=["pi", "perpusindo"])
    async def perpushelp(self, ctx):
        if not ctx.invoked_subcommand:
            helpmain = discord.Embed(
                title="Bantuan Perintah (!perpus)", description=f"versi {self._ver}", color=0x00AAAA,
            )
            helpmain.set_thumbnail(url="https://image.ibb.co/darSzH/question_mark_1750942_640.png")
            helpmain.set_author(
                name="naoTimes", icon_url="https://p.n4o.xyz/i/naotimes_ava.png",
            )
            helpmain.add_field(
                name="!perpus", value="```Memunculkan bantuan perintah```", inline=False,
            )
            helpmain.add_field(
                name="!perpus cari <argumen>",
                value="```Mencari berkas di perpusindo.info " "(gunakan argumen -h untuk melihat bantuan)```",
                inline=False,
            )
            helpmain.add_field(
                name="!perpus terbaru <argumen>",
                value="```Melihat 10 berkas terbaru " "(gunakan argumen -h untuk melihat bantuan)```",
                inline=False,
            )
            helpmain.add_field(
                name="!perpus kategori",
                value="```Melihat kategori apa aja yang bisa dipakai```",
                inline=False,
            )
            helpmain.add_field(name="Aliases", value="!perpus, !perpusindo, !pi", inline=False)
            helpmain.set_footer(text="Dibawakan oleh naoTimes " f"|| Dibuat oleh N4O#8868 versi {self._ver}")
            await ctx.send(embed=helpmain)

    @perpushelp.command(name="cari", aliases=["search"])
    async def perpus_cari(self, ctx):
        helpmain = discord.Embed(
            title="Bantuan Perintah (!perpus cari)", description=f"versi {self._ver}", color=0x00AAAA,
        )
        helpmain.set_thumbnail(url="https://image.ibb.co/darSzH/question_mark_1750942_640.png")
        helpmain.set_author(name="naoTimes", icon_url="https://p.n4o.xyz/i/naotimes_ava.png")
        helpmain.add_field(
            name="!perpus cari <opsi> <pencarian>",
            value="```Mencari sesuatu dari PerpusIndo, opsi dapat dilihat " "dengan:\n!perpus cari -h```",
            inline=False,
        )
        helpmain.add_field(
            name="Contoh", value='!perpus cari -C audio --trusted -u N4O "FLAC"', inline=False,
        )
        helpmain.add_field(name="Aliases", value="!perpus cari, !perpus search", inline=False)
        helpmain.add_field(
            name="*Catatan*",
            value="Semua command bisa dilihat infonya " "dengan !help <nama command>",
            inline=False,
        )
        helpmain.set_footer(text="Dibawakan oleh naoTimes " f"|| Dibuat oleh N4O#8868 versi {self._ver}")
        await ctx.send(embed=helpmain)

    @perpushelp.command(name="terbaru", aliases=["latest"])
    async def perpus_terbaru(self, ctx):
        helpmain = discord.Embed(
            title="Bantuan Perintah (!perpus terbaru)", description=f"versi {self._ver}", color=0x00AAAA,
        )
        helpmain.set_thumbnail(url="https://image.ibb.co/darSzH/question_mark_1750942_640.png")
        helpmain.set_author(name="naoTimes", icon_url="https://p.n4o.xyz/i/naotimes_ava.png")
        helpmain.add_field(
            name="!perpus terbaru <opsi>",
            value="```Melihat 10 berkas terbaru dari PerpusIndo, "
            "opsi dapat dilihat dengan:\n!nyaa terbaru -h```",
            inline=False,
        )
        helpmain.add_field(
            name="Contoh", value="!perpus terbaru -C audio --trusted -u N4O", inline=False,
        )
        helpmain.add_field(
            name="Aliases", value="!perpus terbaru, !perpus latest", inline=False,
        )
        helpmain.add_field(
            name="*Catatan*",
            value="Semua command bisa dilihat infonya " "dengan !help <nama command>",
            inline=False,
        )
        helpmain.set_footer(text="Dibawakan oleh naoTimes " f"|| Dibuat oleh N4O#8868 versi {self._ver}")
        await ctx.send(embed=helpmain)

    @perpushelp.command(name="kategori", aliases=["category"])
    async def perpus_kategori(self, ctx):
        helpmain = discord.Embed(
            title="Bantuan Perintah (!perpus kategori)", description=f"versi {self._ver}", color=0x00AAAA,
        )
        helpmain.set_thumbnail(url="https://image.ibb.co/darSzH/question_mark_1750942_640.png")
        helpmain.set_author(name="naoTimes", icon_url="https://p.n4o.xyz/i/naotimes_ava.png")
        helpmain.add_field(
            name="!perpus katergori", value="```Melihat kategori```", inline=False,
        )
        helpmain.add_field(name="Contoh", value="!perpus kategori", inline=False)
        helpmain.add_field(
            name="Aliases", value="!perpus kategori, !perpus category", inline=False,
        )
        helpmain.add_field(
            name="*Catatan*",
            value="Semua command bisa dilihat infonya " "dengan !help <nama command>",
            inline=False,
        )
        helpmain.set_footer(text="Dibawakan oleh naoTimes " f"|| Dibuat oleh N4O#8868 versi {self._ver}")
        await ctx.send(embed=helpmain)

    @oldhelp.group(name="nh")
    async def nh_help(self, ctx):
        if not ctx.invoked_subcommand:
            helpmain = discord.Embed(
                title="Bantuan Perintah (!nh)", description=f"versi {self._ver}", color=0x00AAAA,
            )
            helpmain.set_thumbnail(url="https://image.ibb.co/darSzH/question_mark_1750942_640.png")
            helpmain.set_author(
                name="naoTimes", icon_url="https://p.n4o.xyz/i/naotimes_ava.png",
            )
            helpmain.add_field(
                name="!nh atau !help nh", value="```Memunculkan bantuan perintah```", inline=False,
            )
            helpmain.add_field(
                name="!nh cari <query>", value="```Mencari kode nuklir.```", inline=False,
            )
            helpmain.add_field(
                name="!nh info <kode>", value="```Melihat informasi kode nuklir.```", inline=False,
            )
            helpmain.add_field(
                name="!nh baca <kode>", value="```Membaca langsung kode nuklir.```", inline=False,
            )
            helpmain.add_field(
                name="!nh unduh <kode>",
                value="```Mendownload kode nuklir dan dijadikan .zip file "
                "(limit file adalah 3 hari sebelum dihapus dari server).```",
                inline=False,
            )
            helpmain.add_field(name="Aliases", value="Tidak ada", inline=False)
            helpmain.set_footer(text="Dibawakan oleh naoTimes " f"|| Dibuat oleh N4O#8868 versi {self._ver}")
            await ctx.send(embed=helpmain)

    @nh_help.command(name="cari", aliases=["search"])  # noqa: F811
    async def nh_cari(self, ctx):
        helpmain = discord.Embed(
            title="Bantuan Perintah (!nh cari)", description=f"versi {self._ver}", color=0x00AAAA,
        )
        helpmain.set_thumbnail(url="https://image.ibb.co/darSzH/question_mark_1750942_640.png")
        helpmain.set_author(name="naoTimes", icon_url="https://p.n4o.xyz/i/naotimes_ava.png")
        helpmain.add_field(
            name="!nh cari <pencarian>",
            value="```Mencari <pencarian> di nHentai\nFitur pencarian"
            " 1:1 dengan fitur pencarian dari nHentainya langsung.```",
            inline=False,
        )
        helpmain.add_field(
            name="Contoh",
            value='!nh cari "females only"\n!nh cari "hibike euphonium"' "\n!nh cari metamorphosis",
            inline=False,
        )
        helpmain.add_field(name="Aliases", value="!nh cari, !nh search", inline=False)
        helpmain.add_field(
            name="*Catatan*",
            value="Semua command bisa dilihat infonya " "dengan !help <nama command>",
            inline=False,
        )
        helpmain.set_footer(text="Dibawakan oleh naoTimes " f"|| Dibuat oleh N4O#8868 versi {self._ver}")
        await ctx.send(embed=helpmain)

    @nh_help.command(name="info", aliases=["informasi"])
    async def nh_info(self, ctx):
        helpmain = discord.Embed(
            title="Bantuan Perintah (!nh info)", description=f"versi {self._ver}", color=0x00AAAA,
        )
        helpmain.set_thumbnail(url="https://image.ibb.co/darSzH/question_mark_1750942_640.png")
        helpmain.set_author(name="naoTimes", icon_url="https://p.n4o.xyz/i/naotimes_ava.png")
        helpmain.add_field(
            name="!nh info <kode_nuklir>",
            value="```Mencari informasi tentang <kode_nuklir> di nHentai```",
            inline=False,
        )
        helpmain.add_field(
            name="Contoh", value="!nh info 177013\n!nh info 290691", inline=False,
        )
        helpmain.add_field(name="Aliases", value="!nh info, !nh informasi", inline=False)
        helpmain.add_field(
            name="*Catatan*",
            value="Semua command bisa dilihat infonya " "dengan !help <nama command>",
            inline=False,
        )
        helpmain.set_footer(text="Dibawakan oleh naoTimes " f"|| Dibuat oleh N4O#8868 versi {self._ver}")
        await ctx.send(embed=helpmain)

    @nh_help.command(name="baca", aliases=["read"])
    async def nh_baca(self, ctx):
        helpmain = discord.Embed(
            title="Bantuan Perintah (!nh baca)", description=f"versi {self._ver}", color=0x00AAAA,
        )
        helpmain.set_thumbnail(url="https://image.ibb.co/darSzH/question_mark_1750942_640.png")
        helpmain.set_author(name="naoTimes", icon_url="https://p.n4o.xyz/i/naotimes_ava.png")
        helpmain.add_field(
            name="!nh baca <kode_nuklir>",
            value="```Membaca langsung dari Discord\n"
            "Gambar akan di proxy agar "
            "tidak kena efek blok internet positif\n"
            "Maka dari itu, gambar akan "
            "butuh waktu untuk di cache\n"
            "Semakin banyak gambar, semakin lama.```",
            inline=False,
        )
        helpmain.add_field(
            name="Contoh", value="!nh baca 177013\n!nh baca 290691", inline=False,
        )
        helpmain.add_field(name="Aliases", value="!nh baca, !nh read", inline=False)
        helpmain.add_field(
            name="*Catatan*",
            value="Semua command bisa dilihat infonya " "dengan !help <nama command>",
            inline=False,
        )
        helpmain.set_footer(text="Dibawakan oleh naoTimes " f"|| Dibuat oleh N4O#8868 versi {self._ver}")
        await ctx.send(embed=helpmain)

    @nh_help.command(name="unduh", aliases=["down", "dl", "download"])
    async def nh_unduh(self, ctx):
        helpmain = discord.Embed(
            title="Bantuan Perintah (!nh unduh)", description=f"versi {self._ver}", color=0x00AAAA,
        )
        helpmain.set_thumbnail(url="https://image.ibb.co/darSzH/question_mark_1750942_640.png")
        helpmain.set_author(name="naoTimes", icon_url="https://p.n4o.xyz/i/naotimes_ava.png")
        helpmain.add_field(
            name="!nh unduh <kode_nuklir>",
            value="```Mengunduh <kode_nuklir>\nJika gambar belum sempat di "
            "proxy, akan memakan waktu lebih lama\nDisarankan menggunakan "
            "command !nh baca baru !nh unduh```",
            inline=False,
        )
        helpmain.add_field(
            name="Contoh", value="!nh unduh 177013\n!nh unduh 290691", inline=False,
        )
        helpmain.add_field(
            name="Aliases", value="!nh unduh, !nh down, !nh dl, !nh download", inline=False,
        )
        helpmain.add_field(
            name="*Catatan*",
            value="Semua command bisa dilihat infonya " "dengan !help <nama command>",
            inline=False,
        )
        helpmain.set_footer(text="Dibawakan oleh naoTimes " f"|| Dibuat oleh N4O#8868 versi {self._ver}")
        await ctx.send(embed=helpmain)

    @oldhelp.command()
    async def info(self, ctx):
        helpmain = discord.Embed(
            title="Bantuan Perintah (!info)", description=f"versi {self._ver}", color=0x00AAAA,
        )
        helpmain.set_thumbnail(url="https://image.ibb.co/darSzH/question_mark_1750942_640.png")
        helpmain.set_author(name="naoTimes", icon_url="https://p.n4o.xyz/i/naotimes_ava.png")
        helpmain.add_field(name="!info", value="Melihat Informasi bot ini", inline=False)
        helpmain.add_field(
            name="*Catatan*",
            value="Semua command bisa dilihat infonya " "dengan !help <nama command>",
            inline=False,
        )
        helpmain.set_footer(text="Dibawakan oleh naoTimes " f"|| Dibuat oleh N4O#8868 versi {self._ver}")
        await ctx.send(embed=helpmain)

    @oldhelp.command()
    async def prefix(self, ctx):
        helpmain = discord.Embed(
            title="Bantuan Perintah (!prefix)", description=f"versi {self._ver}", color=0x00AAAA,
        )
        helpmain.set_thumbnail(url="https://image.ibb.co/darSzH/question_mark_1750942_640.png")
        helpmain.set_author(name="naoTimes", icon_url="https://p.n4o.xyz/i/naotimes_ava.png")
        helpmain.add_field(
            name="!prefix <prefix>",
            value="Menambah server custom prefix baru ke server ini"
            "\nLihat custom prefix server dengan ketik `!prefix`",
            inline=False,
        )
        helpmain.add_field(
            name="!prefix clear", value="Menghapus server custom prefix dari server ini", inline=False,
        )
        helpmain.add_field(name="Minimum Permission", value="- Manage Server")
        helpmain.add_field(
            name="Aliases", value="!prefix\n!prefix clear, !prefix hapus, !prefix bersihkan", inline=False,
        )
        helpmain.add_field(
            name="*Catatan*",
            value="Semua command bisa dilihat infonya " "dengan !help <nama command>",
            inline=False,
        )
        helpmain.set_footer(text="Dibawakan oleh naoTimes " f"|| Dibuat oleh N4O#8868 versi {self._ver}")
        await ctx.send(embed=helpmain)

    @oldhelp.command()
    async def ping(self, ctx):
        helpmain = discord.Embed(
            title="Bantuan Perintah (!ping)", description=f"versi {self._ver}", color=0x00AAAA,
        )
        helpmain.set_thumbnail(url="https://image.ibb.co/darSzH/question_mark_1750942_640.png")
        helpmain.set_author(name="naoTimes", icon_url="https://p.n4o.xyz/i/naotimes_ava.png")
        helpmain.add_field(
            name="!ping",
            value="Melihat cepat rambat koneksi dari " "server ke discord dan ke github",
            inline=False,
        )
        helpmain.add_field(
            name="*Catatan*",
            value="Semua command bisa dilihat infonya " "dengan !help <nama command>",
            inline=False,
        )
        helpmain.set_footer(text="Dibawakan oleh naoTimes " f"|| Dibuat oleh N4O#8868 versi {self._ver}")
        await ctx.send(embed=helpmain)

    @commands.command(aliases=["invite"])
    async def undang(self, ctx):
        invi = discord.Embed(
            title="Ingin invite Bot ini? Klik link di bawah ini!",
            description="[Invite](https://ihateani.me/andfansub)"
            f"\n[Support Server](https://discord.gg/7KyYecn) atau ketik `{self.bot.prefix}tiket` di DM Bot."
            "\n[Dukung Dev-nya](https://trakteer.id/noaione)",
            color=0x1,
        )
        invi.set_thumbnail(url="https://p.n4o.xyz/i/naotimes_ava.png")
        await ctx.send(embed=invi)

    @commands.command(aliases=["donate"])
    async def donasi(self, ctx):
        donatur = discord.Embed(
            title="Donasi ke Developer Bot-nya!",
            description="Bantu biar developer botnya masih mau tetap"
            " maintenance bot naoTimes!"
            "\n[Trakteer](https://trakteer.id/noaione)"
            "\n[KaryaKarsa](https://karyakarsa.com/noaione)",
            color=0x1,
        )
        donatur.set_thumbnail(url="https://p.n4o.xyz/i/naotimes_ava.png")
        await ctx.send(embed=donatur)

    @commands.command()
    async def support(self, ctx):
        invi = discord.Embed(
            title="Support!",
            description="Silakan Join [Support Server](https://discord.gg/7KyYecn)"
            "\ndan kunjungi #bantuan."
            f"\nATAU ketik `{self.bot.prefix}tiket` di DM Bot.",
            color=0x1,
        )
        invi.set_thumbnail(url="https://p.n4o.xyz/i/naotimes_ava.png")
        await ctx.send(embed=invi)

    @commands.command()
    @commands.guild_only()
    async def supermotd(self, ctx):
        if ctx.message.author.id != self.bot.owner.id:
            print("[@] Someone want to use supermotd " "but not the bot owner, ignoring...")
            print("[@] User that are trying to use it: " + str(ctx.message.author.id))
            return

        print("[@] Super MOTD Activated")
        json_data = await fetch_json()
        if not json_data:
            return

        mod_list = json_data["supermod"]

        starting_messages = await ctx.send(
            "**Initiated Super MOTD, please write" " the content below**\n*Type `cancel` to cancel*"
        )

        def check(m):
            return m.author == ctx.message.author

        motd_content = await self.bot.wait_for("message", check=check)

        if motd_content.content == ("cancel"):
            print("[@] MOTD Cancelled")
            return await ctx.send("**MOTD Message announcement cancelled.**")

        print("MOTD Content:\n{}".format(motd_content.content))
        await starting_messages.edit("**Initiated Super MOTD, please write the content below**")

        preview_msg = await ctx.send(
            "**MOTD Preview**\n"
            "```{}```\nAre you sure want to send this message?".format(motd_content.content)
        )
        to_react = ["✅", "❌"]
        for reaction in to_react:
            await preview_msg.add_reaction(reaction)

        def check_react(reaction, user):
            if reaction.message.id != preview_msg.id:
                return False
            if user != ctx.message.author:
                return False
            if str(reaction.emoji) not in to_react:
                return False
            return True

        try:
            res, user = await self.bot.wait_for("reaction_add", timeout=30.0, check=check_react)
        except asyncio.TimeoutError:
            await ctx.send("***Timeout!***")
            return await preview_msg.clear_reactions()
        if "✅" in str(res.emoji):
            print("[@] Sending MOTD")
            await preview_msg.clear_reactions()
            preview_msg = preview_msg.edit("**Sending to every admin...**")
            success_rate = 0
            failed_user = []
            for mod in mod_list:
                print("[@] Sending to: {}".format(mod))
                try:
                    server_mod = find_user_server(mod, json_data)
                    server_in = self.bot.get_guild(server_mod)
                    srv_mod = server_in.get_member(int(mod))
                    await srv_mod.send(
                        "**Announcement dari N4O#8868"
                        " (Bot Owner):**\n\n{}\n\n*Pada: {}*".format(motd_content.content, get_current_time())
                    )
                    success_rate += 1
                    print("[@] Success")
                except Exception:
                    failed_user.append(mod)
                    print("[@] Failed")
            await preview_msg.edit("**Done! {}/{} user get the message**".format(success_rate, len(mod_list)))
            if failed_user:
                print("Failed user list: {}".format(", ".join(failed_user)))
        elif "❌" in str(res.emoji):
            print("[@] MOTD Cancelled")
            await preview_msg.clear_reactions()
            await preview_msg.edit("**MOTD Message announcement cancelled.**")


def setup(bot):
    bot.add_cog(Helper(bot))
