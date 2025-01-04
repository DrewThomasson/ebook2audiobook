# 📚 ebook2audiobook

CPU/GPU-omvandlare från eBöcker till ljudböcker med kapitel och metadata<br/>
använder Calibre, ffmpeg, XTTSv2, Fairseq och mer. Stöder röstkloning och 1124 språk!
> [!VIKTIGT]
**Detta verktyg är avsett för användning med icke-DRM-skyddade, lagligt förvärvade eBöcker endast.** <br>
Författarna ansvarar inte för missbruk av denna programvara eller några resulterande juridiska konsekvenser. <br>
Använd detta verktyg ansvarsfullt och i enlighet med alla tillämpliga lagar.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/bg5Kx43c6w)](https://discord.gg/bg5Kx43c6w)

#### Ny v2.0 Web GUI Interface!
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Klicka för att se bilder av Web GUI</summary>
  <img width="1728" alt="GUI Skärm 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Skärm 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Skärm 3" src="assets/gui_3.png">
</details>

## README.md
- ara [العربية (Arabisk)](./readme/README_AR.md)
- zho [中文 (Kinesiska)](./readme/README_CN.md)
- swe [Svenska](./readme/README_SWE.md)
- eng [Engelska](README.md)

## Innehållsförteckning

- [ebook2audiobook](#ebook2audiobook)
- [Funktioner](#funktioner)
- [Ny v2.0 Web GUI Interface](#ny-v20-web-gui-interface)
- [Huggingface Space Demo](#huggingface-space-demo)
- [Gratis Google Colab](#gratis-google-colab)
- [Förgjorda Ljuddemonstrationer](#demos)
- [Stödda Språk](#st%C3%B6dda-spr%C3%A5k)
- [Krav](#krav)
- [Installationsinstruktioner](#installationsinstruktioner)
- [Användning](#anv%C3%A4ndning)
  - [Starta Gradio Web Interface](#starta-gradio-web-interface)
  - [Grundläggande Headless Användning](#grundl%C3%A4ggande-headless-anv%C3%A4ndning)
  - [Headless Anpassad XTTS Modell Användning](#headless-anpassad-xtts-modell-anv%C3%A4ndning)
  - [Hyra en GPU](#hyra-en-gpu)
  - [Hjälp Kommando Utdata](#hj%C3%A4lp-kommando-udata)
- [Finjusterade TTS-modeller](#finjusterade-tts-modeller)
  - [För Samling av Finjusterade TTS-modeller](#finjusterade-tts-collection)
- [Använda Docker](#anv%C3%A4nda-docker)
  - [Docker Run](#docker-run)
  - [Docker Build](#docker-build)
  - [Docker Compose](#docker-compose)
  - [Docker Headless Guide](#docker-headless-guide)
  - [Docker Container Filplatser](#docker-container-filplatser)
- [Stödda eBoksformat](#st%C3%B6dda-eboksformat)
- [Utdata](#utdata)
- [Vanliga Problem](#vanliga-problem)
- [Särskilt Tack](#s%C3%A4rskt-tack)
- [Gå med i Vår Discord-server!](#g%C3%A5-med-i-v%C3%A5r-discord-server)
- [Äldre Version](#legacy-v10)
- [Ordlista över Sektioner](#ordlista-%C3%B6ver-sektioner)

## Funktioner

- 📖 Konverterar eBöcker till textformat med Calibre.
- 📚 Delar upp eBoken i kapitel för organiserat ljud.
- 🎙️ Högkvalitativ text-till-tal med [Coqui XTTSv2](https://huggingface.co/coqui/XTTS-v2) och [Fairseq](https://github.com/facebookresearch/fairseq/tree/main/examples/mms).
- 🗣️ Valfri röstkloning med din egen röstfil.
- 🌍 Stöder 1107 språk (Engelska som standard). [Lista över Stödda språk](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
- 🖥️ Designad för att köras med 4GB RAM.

## [Huggingface space demo](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)

- Huggingface space körs på gratis CPU-nivå så förvänta dig väldigt långsamt eller timeout lol, ge det bara inte jättestora filer är allt
- Bäst att duplicera space eller köra lokalt.

## Gratis Google Colab 
[![Gratis Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb)

## Stödda Språk

- **Arabiska (ara)**
- **Kinesiska (zho)**
- **Tjeckiska (ces)**
- **Holländska (nld)**
- **Engelska (eng)**
- **Franska (fra)**
- **Tyska (deu)**
- **Hindi (hin)**
- **Ungerska (hun)**
- **Italienska (ita)**
- **Japanska (jpn)**
- **Koreanska (kor)**
- **Polska (pol)**
- **Portugisiska (por)**
- **Ryska (rus)**
- **Spanska (spa)**
- **Turkiska (tur)**
- **Vietnamesiska (vie)**
- [** + 1107 språk via Fairseq**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)

##  Krav

- 4GB RAM
- Virtualisering aktiverad om du kör på Windows (endast Docker)

### Installationsinstruktioner

1. **Klona repot**
```bash
git clone https://github.com/DrewThomasson/ebook2audiobook.git
```

Ange språkkoden när du kör skriptet i  mode.

### Starta Gradio Web Interface

1. **Kör ebook2audiobook**:
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.sh  # Kör startskript
     ```
   - **Windows**
     ```bash
     .\ebook2audiobook.cmd  # Kör startskript
     ```

2. **Öppna Webbappen**: Klicka på URL:en som visas i terminalen för att komma åt webbappen och konvertera eBöcker.
3. **För Offentlig Länk**: Lägg till `--share` i slutet som detta: `python app.py --share`
- **[För Fler Parametrar]**: använd `--help` parametern som detta `python app.py --help`

### Grundläggande  Användning
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.sh  -- --ebook <path_to_ebook_file> --voice [path_to_voice_file] --language [language_code]
     ```
   - **Windows**
     ```bash
     .\ebook2audiobook.cmd  -- --ebook <path_to_ebook_file> --voice [path_to_voice_file] --language [language_code]
     ```

- **<path_to_ebook_file>**: Sökväg till din eBok-fil.
- **[path_to_voice_file]**: Valfritt för röstkloning.
- **[language_code]**: Valfritt för att specificera ISO-639-3 3+ bokstäver språkkod (standard är eng). ISO-639-1 2 bokstäver kod stöds också
- **[För Fler Parametrar]**: använd `--help` parametern som detta `python app.py --help`

###  Anpassad XTTS Modell Användning
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.sh  -- --ebook <ebook_file_path> --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path> --custom_config <custom_config_path> --custom_vocab <custom_vocab_path>
     ```
   - **Windows**
     ```bash
     .\ebook2audiobook.cmd  -- --ebook <ebook_file_path> --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path> --custom_config <custom_config_path> --custom_vocab <custom_vocab_path>
     ```

- **<ebook_file_path>**: Sökväg till din eBok-fil.
- **<target_voice_file_path>**: Valfritt för röstkloning.
- **<language>**: Valfritt för att specificera språk.
- **<custom_model_path>**: Sökväg till `model.pth`.
- **<custom_config_path>**: Sökväg till `config.json`.
- **<custom_vocab_path>**: Sökväg till `vocab.json`.
- **[För Fler Parametrar]**: använd `--help` parametern som detta `python app.py --help`

### För Detaljerad Guide med lista över alla Parametrar att använda
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.sh  --help
     ```
   - **Windows**
     ```bash
     .\ebook2audiobook.cmd  --help
     ```
<a id="help-command-output"></a>
- Detta kommer att visa följande:
```bash
usage: app.py [-h] [--script_mode SCRIPT_MODE] [--share] [-- []]
              [--session SESSION] [--ebook EBOOK] [--ebooks_dir [EBOOKS_DIR]]
              [--voice VOICE] [--language LANGUAGE] [--device {cpu,gpu}]
              [--custom_model CUSTOM_MODEL] [--temperature TEMPERATURE]
              [--length_penalty LENGTH_PENALTY]
              [--repetition_penalty REPETITION_PENALTY] [--top_k TOP_K] [--top_p TOP_P]
              [--speed SPEED] [--enable_text_splitting] [--fine_tuned FINE_TUNED]
              [--version]

Konvertera eBöcker till Ljudböcker med hjälp av en Text-till-Tal-modell. Du kan antingen starta Gradio-gränssnittet eller köra skriptet i  mode för direkt konvertering.

options:
  -h, --help            visa detta hjälpmeddelande och avsluta
  --script_mode SCRIPT_MODE
                        Tvinga skriptet att köra i NATIVE eller DOCKER_UTILS
  --share               Aktivera en offentlig delbar Gradio-länk. Standard är False.
  -- []
                        Kör i  mode. Standard till True om flaggan är närvarande utan ett värde, False annars.
  --session SESSION     Session för att återansluta vid avbrott ( mode endast)
  --ebook EBOOK         Sökväg till eBok-filen för konvertering. Obligatorisk i  mode.
  --ebooks_dir [EBOOKS_DIR]
                        Sökväg till katalogen som innehåller eBöcker för batchkonvertering. Standard till "ebooks" om "default" anges.
  --voice VOICE         Sökväg till mål röstfil för TTS. Valfritt, måste vara 24khz för XTTS och 16khz för fairseq-modeller, använder en standardröst om inget anges.
  --language LANGUAGE   Språk för ljudboksomvandlingen. Alternativ: eng, zho, spa, fra, por, rus, ind, hin, ben, yor, ara, jav, jpn, kor, deu, ita, fas, tam, tel, tur, pol, hun, nld, zzzz, abi, ace, aca, acn, acr, ach, acu, guq, ade, adj, agd, agx, agn, aha, aka, knj, ake, aeu, ahk, bss, alj, sqi, alt, alp, alz, kab, amk, mmg, amh, ami, azg, agg, boj, cko, any, arl, atq, luc, hyw, apr, aia, msy, cni, cjo, cpu, cpb, asm, asa, teo, ati, djk, ava, avn, avu, awb, kwi, awa, agr, agu, ayr, ayo, abp, blx, sgb, azj-script_cyrillic, azj-script_latin, azb, bba, bhz, bvc, bfy, bgq, bdq, bdh, bqi, bjw, blz, ban, bcc-script_latin, bcc-script_arabic, bam, ptu, bcw, bqj, bno, bbb, bfa, bjz, bak, eus, bsq, akb, btd, btx, bts, bbc, bvz, bjv, bep, bkv, bzj, bem, bng, bom, btt, bha, bgw, bht, beh, sne, ubl, bcl, bim, bkd, bjr, bfo, biv, bib, bis, bzi, bqp, bpr, bps, bwq, bdv, bqc, bus, bnp, bmq, bdg, boa, ksr, bor, bru, box, bzh, bgt, sab, bul, bwu, bmv, mya, tte, cjp, cbv, kaq, cot, cbc, car, cat, ceb, cme, cbi, ceg, cly, cya, che, hne, nya, dig, dug, bgr, cek, cfm, cnh, hlt, mwq, ctd, tcz, zyp, cco, cnl, cle, chz, cpa, cso, cnt, cuc, hak, nan, xnj, cap, cax, ctg, ctu, chf, cce, crt, crq, cac-dialect_sansebastiáncoatán, cac-dialect_sanmateoixtatán, ckt, ncu, cdj, chv, caa, asg, con, crn, cok, crk-script_latin, crk-script_syllabics, crh, hrv, cui, ces, dan, dsh, dbq, dga, dgi, dgk, dnj-dialect_gweetaawueast, dnj-dialect_blowowest, daa, dnt, dnw, dar, tcc, dwr, ded, mzw, ntr, ddn, des, dso, nfa, dhi, gud, did, mhu, dip, dik, tbz, dts, dos, dgo, mvp, jen, dzo, idd, eka, cto, emp, enx, sja, myv, mcq, ese, evn, eza, ewe, fal, fao, far, fij, fin, fon, frd, ful, flr, gau, gbk, gag-script_cyrillic, gag-script_latin, gbi, gmv, lug, pwg, gbm, cab, grt, krs, gso, nlg, gej, gri, kik, acd, glk, gof-script_latin, gog, gkn, wsg, gjn, gqr, gor, gux, gbo, ell, grc, guh, gub, grn, gyr, guo, gde, guj, gvl, guk, rub, dah, gwr, gwi, hat, hlb, amf, hag, hnn, bgc, had, hau, hwc, hvn, hay, xed, heb, heh, hil, hif, hns, hoc, hoy, hus-dialect_westernpotosino, hus-dialect_centralveracruz, huv, hui, hap, iba, isl, dbj, ifa, ifb, ifu, ifk, ife, ign, ikk, iqw, ilb, ilo, imo, inb, ipi, irk, icr, itv, itl, atg, ixl-dialect_sanjuancotzal, ixl-dialect_sangasparchajul, ixl-dialect_santamarianebaj, nca, izr, izz, jac, jam, jvn, kac, dyo, csk, adh, jun, jbu, dyu, bex, juy, gna, urb, kbp, cwa, dtp, kbr, cgc, kki, kzf, lew, cbr, kkj, keo, kqe, kak, kyb, knb, kmd, kml, ify, xal, kbq, kay, ktb, hig, gam, cbu, xnr, kmu, kne, kan, kby, pam, cak-dialect_santamaríadejesús, cak-dialect_southcentral, cak-dialect_yepocapa, cak-dialect_western, cak-dialect_santodomingoxenacoj, cak-dialect_central, xrb, krc, kaa, krl, pww, xsm, cbs, pss, kxf, kyz, kyu, txu, kaz, ndp, kbo, kyq, ken, ker, xte, kyg, kjh, kca, khm, kxm, kjg, nyf, kij, kia, kqr, kqp, krj, zga, kin, pkb, geb, gil, kje, kss, thk, klu, kyo, kog, kfb, kpv, bbo, xon, kma, kno, kxc, ozm, kqy, coe, kpq, kpy, kyf, kff-script_telugu, kri, rop, ktj, ted, krr, kdt, kez, cul, kle, kdi, kue, kum, kvn, cuk, kdn, xuo, key, kpz, knk, kmr-script_latin, kmr-script_arabic, kmr-script_cyrillic, xua, kru, kus, kub, kdc, kxv, blh, cwt, kwd, tnk, kwf, cwe, kyc, tye, kir, quc-dialect_north, quc-dialect_east, quc-dialect_central, lac, lsi, lbj, lhu, las, lam, lns, ljp, laj, lao, lat, lav, law, lcp, lzz, lln, lef, acf, lww, mhx, eip, lia, lif, onb, lis, loq, lob, yaz, lok, llg, ycl, lom, ngl, lon, lex, lgg, ruf, dop, lnd, ndy, lwo, lee, mev, mfz, jmc, myy, mbc, mda, mad, mag, ayz, mai, mca, mcp, mak, vmw, mgh, kde, mlg, zlm, pse, mkn, xmm, mal, xdy, div, mdy, mup, mam-dialect_central, mam-dialect_northern, mam-dialect_southern, mam-dialect_western, mqj, mcu, mzk, maw, mjl, mnk, mge, mbh, knf, mjv, mbt, obo, mbb, mzj, sjm, mrw, mar, mpg, mhr, enb, mah, myx, klv, mfh, met, mcb, mop, yua, mfy, maz, vmy, maq, mzi, maj, maa-dialect_sanantonio, maa-dialect_sanjerónimo, mhy, mhi, zmz, myb, gai, mqb, mbu, med, men, mee, mwv, meq, zim, mgo, mej, mpp, min, gum, mpx, mco, mxq, pxm, mto, mim, xta, mbz, mip, mib, miy, mih, miz, xtd, mxt, xtm, mxv, xtn, mie, mil, mio, mdv, mza, mit, mxb, mpm, soy, cmo-script_latin, cmo-script_khmer, mfq, old, mfk, mif, mkl, mox, myl, mqf, mnw, mon, mog, mfe, mor, mqn, mgd, mtj, cmr, mtd, bmr, moz, mzm, mnb, mnf, unr, fmu, mur, tih, muv, muy, sur, moa, wmw, tnr, miq, mos, muh, nas, mbj, nfr, kfw, nst, nag, nch, nhe, ngu, azz, nhx, ncl, nhy, ncj, nsu, npl, nuz, nhw, nhi, nlc, nab, gld, nnb, npy, pbb, ntm, nmz, naw, nxq, ndj, ndz, ndv, new, nij, sba, gng, nga, nnq, ngp, gym, kdj, nia, nim, nin, nko, nog, lem, not, nhu, nob, bud, nus, yas, nnw, nwb, nyy, nyn, rim, lid, nuj, nyo, nzi, ann, ory, ojb-script_latin, ojb-script_syllabics, oku, bsc, bdu, orm, ury, oss, ote, otq, stn, sig, kfx, bfz, sey, pao, pau, pce, plw, pmf, pag, pap, prf, pab, pbi, pbc, pad, ata, pez, peg, pcm, pis, pny, pir, pjt, poy, pps, pls, poi, poh-dialect_eastern, poh-dialect_western, prt, pui, pan, tsz, suv, lme, quy, qvc, quz, qve, qub, qvh, qwh, qvw, quf, qvm, qul, qvn, qxn, qxh, qvs, quh, qxo, qxr, qvo, qvz, qxl, quw, kjb, kek, rah, rjs, rai, lje, rnl, rkt, rap, yea, raw, rej, rel, ril, iri, rgu, rhg, rmc-script_latin, rmc-script_cyrillic, rmo, rmy-script_latin, rmy-script_cyrillic, ron, rol, cla, rng, rug, run, lsm, spy, sck, saj, sch, sml, xsb, sbl, saq, sbd, smo, rav, sxn, sag, sbp, xsu, srm, sas, apb, sgw, tvw, lip, slu, snw, sea, sza, seh, crs, ksb, shn, sho, mcd, cbt, xsr, shk, shp, sna, cjs, jiv, snp, sya, sid, snn, sri, srx, sil, sld, akp, xog, som, bmu, khq, ses, mnx, srn, sxb, suc, tgo, suk, sun, suz, sgj, sus, swh, swe, syl, dyi, myk, spp, tap, tby, tna, shi, klw, tgl, tbk, tgj, blt, tbg, omw, tgk, tdj, tbc, tlj, tly, ttq-script_tifinagh, taj, taq, tpm, tgp, tnn, tac, rif-script_latin, rif-script_arabic, tat, tav, twb, tbl, kps, twe, ttc, kdh, tes, tex, tee, tpp, tpt, stp, tfr, twu, ter, tew, tha, nod, thl, tem, adx, bod, khg, tca, tir, txq, tik, dgr, tob, tmf, tng, tlb, ood, tpi, jic, lbw, txa, tom, toh, tnt, sda, tcs, toc, tos, neb, trn, trs, trc, tri, cof, tkr, kdl, cas, tso, tuo, iou, tmc, tuf, tuk-script_latin, tuk-script_arabic, bov, tue, kcg, tzh-dialect_bachajón, tzh-dialect_tenejapa, tzo-dialect_chenalhó, tzo-dialect_chamula, tzj-dialect_western, tzj-dialect_eastern, aoz, udm, udu, ukr, ppk, ubu, urk, ura, urt, urd-script_devanagari, urd-script_arabic, urd-script_latin, upv, usp, uig-script_arabic, uig-script_cyrillic, uzb-script_cyrillic, vag, bav, vid, vie, vif, vun, vut, prk, wwa, rro, bao, waw, lgl, wlx, cou, hub, gvc, mfi, wap, wba, war, way, guc, cym, kvw, tnp, hto, huu, wal-script_latin, wal-script_ethiopic, wlo, noa, wob, kao, xer, yad, yka, sah, yba, yli, nlk, yal, yam, yat, jmd, tao, yaa, ame, guu, yao, yre, yva, ybb, pib, byr, pil, ycn, ess, yuz, atb, zne, zaq, zpo, zad, zpc, zca, zpg, zai, zpl, zam, zaw, zpm, zac, zao, ztq, zar, zpt, zpi, zas, zaa, zpz, zab, zpu, zae, zty, zav, zza, zyb, ziw, zos, gnd. Standard är Engelska (eng).
  --device {cpu,gpu}    Typ av processorenhet för ljudboksomvandlingen. Om inte specificerat: kontrollera först om GPU är tillgänglig, annars väljs CPU.
  --custom_model CUSTOM_MODEL
                        Sökväg till den anpassade modellen (.zip-fil som innehåller ['config.json', 'vocab.json', 'model.pth', 'ref.wav']). Obligatorisk om du använder en anpassad modell.
  --temperature TEMPERATURE
                        Temperatur för modellen. Standard är 0.65. Högre temperaturer leder till mer kreativa utgångar.
  --length_penalty LENGTH_PENALTY
                        En längdförstärkningspenalty som appliceras på den autoregressiva dekodern. Standard är 1.0. Inte applicerad på anpassade modeller.
  --repetition_penalty REPETITION_PENALTY
                        En penalty som förhindrar den autoregressiva dekodern från att upprepa sig själv. Standard är 2.5
  --top_k TOP_K         Top-k sampling. Lägre värden betyder mer sannolika utgångar och ökad ljudgenereringshastighet. Standard är 50
  --top_p TOP_P         Top-p sampling. Lägre värden betyder mer sannolika utgångar och ökad ljudgenereringshastighet. Standard är 0.8
  --speed SPEED         Hastighetsfaktor för talgenereringen. Standard är 1.0
  --enable_text_splitting
                        Aktivera delning av text i meningar. Standard är False.
  --fine_tuned FINE_TUNED
                        Namn på den finjusterade modellen. Valfritt, använder standardmodellen enligt TTS-motorn och språk.
  --version             Visa versionen av skriptet och avsluta

Exempel på användning:    
Windows:
    :
    ebook2audiobook.cmd -- --ebook 'path_to_ebook'
    Grafiskt Gränssnitt:
    ebook2audiobook.cmd
Linux/Mac:
    :
    ./ebook2audiobook.sh -- --ebook 'path_to_ebook'
    Grafiskt Gränssnitt:
    ./ebook2audiobook.sh


```

### Använda Docker

Du kan också använda Docker för att köra eBok till Ljudboksomvandlaren. Denna metod säkerställer konsistens över olika miljöer och förenklar installationen.

#### Köra Docker-containern

För att köra Docker-containern och starta Gradio-gränssnittet, använd följande kommando:

 -Kör endast med CPU
```powershell
docker run -it --rm -p 7860:7860 --platform=linux/amd64 athomasson2/ebook2audiobook python app.py
```
 -Kör med GPU-acceleration (endast Nvidia grafikkort)
```powershell
docker run -it --rm --gpus all -p 7860:7860 --platform=linux/amd64 athomasson2/ebook2audiobook python app.py
```

#### Bygga Docker-containern

- Du kan bygga Docker-avbildningen med kommandot:
'''powershell
docker build --platform linux/amd64 -t athomasson2/ebook2audiobook .
'''

Detta kommando kommer att starta Gradio-gränssnittet på port 7860 (localhost:7860).
- För fler alternativ som att köra Docker i  mode eller göra Gradio-länken offentlig, lägg till `--help` parametern efter `app.py` i Docker startkommandot.

## Docker Container Filplatser
Alla ebook2audiobooks kommer att ha baskatalogen `/home/user/app/`
Exempel:
`tmp` = `/home/user/app/tmp`
`audiobooks` = `/home/user/app/audiobooks`

   
## Docker Headless Guide

Först gör en docker pull av den senaste versionen med
```bash 
docker pull athomasson2/ebook2audiobook
```

- Innan du gör detta behöver du skapa en katalog som heter "input-folder" i din nuvarande katalog som kommer att länkas. Detta är där du kan lägga dina indatafiler så att Docker-avbildningen kan se dem
```bash
mkdir input-folder && mkdir Audiobooks
```

- I kommandot nedan, byt ut **YOUR_INPUT_FILE.TXT** med namnet på din indatafil 

```bash
docker run -it --rm \
    -v $(pwd)/input-folder:/home/user/app/input_folder \
    -v $(pwd)/audiobooks:/home/user/app/audiobooks \
    --platform linux/amd64 \
    athomasson2/ebook2audiobook \
    python app.py --headless --ebook /input_folder/YOUR_INPUT_FILE.TXT
```

- Och det borde vara allt! 

- De genererade Ljudböckerna kommer att finnas i Audiobook-katalogen som också kommer att finnas i din lokala katalog där du körde detta Docker-kommando.

## För att få hjälpkommandot för de andra parametrarna detta program har kan du köra detta 

```bash
docker run -it --rm \
    --platform linux/amd64 \
    athomasson2/ebook2audiobook \
    python app.py --help

```

och det kommer att visa detta 

[Help command output](#help-command-output)

### Docker Compose

Detta projekt använder Docker Compose för att köras lokalt. Du kan aktivera eller inaktivera GPU-stöd genom att sätta antingen `*gpu-enabled` eller `*gpu-disabled` i `docker-compose.yml`

#### Steg för att Köra

1. **Klon Repositoriet** (om du inte redan har gjort det):
   ```bash
   git clone https://github.com/DrewThomasson/ebook2audiobook.git
   cd ebook2audiobook
   ```

2. **Ställ in GPU-stöd (inaktiverat som standard)**
  För att aktivera GPU-stöd, ändra `docker-compose.yml` och ändra `*gpu-disabled` till `*gpu-enabled`

3. **Starta tjänsten:**
    ```bash
    docker-compose up -d
    ```

4. **Åtkomst till tjänsten:**
  Tjänsten kommer att vara tillgänglig på http://localhost:7860.

#### Ny v2.0 Docker Web GUI Interface!
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Klicka för att se bilder av Web GUI</summary>
  <img width="1728" alt="GUI Skärm 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Skärm 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Skärm 3" src="assets/gui_3.png">
</details>

## Hyra en GPU
Har du inte hårdvaran för att köra det eller vill du hyra en GPU?
#### Du kan duplicera Huggingface-space och hyra en GPU för cirka $0.40 per timme
[Huggingface Space Demo](#huggingface-space-demo)

#### Eller så kan du prova att använda Google Colab gratis!
(Vara medveten om att den kommer att timeouta efter ett tag om du inte aktivt arbetar med Google Colab)
[Gratis Google Colab](#gratis-google-colab)


## Finjusterade TTS-modeller

Du kan finjustera din egen XTTS-modell enkelt med detta repo
[xtts-finetune-webui](https://github.com/daswer123/xtts-finetune-webui)

Om du vill hyra en GPU enkelt kan du också duplicera denna Huggingface
[xtts-finetune-webui-space](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu)

Ett space du kan använda för att enkelt de-noisera träningsdata också
[denoise-huggingface-space](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit)

### Finjusterad TTS Samling

För att hitta vår samling av redan finjusterade TTS-modeller, besök [denna Hugging Face-länk](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)
För en XTTS anpassad modell behövs även ett referensljudklipp av rösten:

## Demos

Regnig dag röst

https://github.com/user-attachments/assets/8486603c-38b1-43ce-9639-73757dfb1031

David Attenborough röst

https://github.com/user-attachments/assets/47c846a7-9e51-4eb9-844a-7460402a20a8


## Stödda eBoksformat

- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`, `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`, `.snb`, `.cbc`, `.rb`, `.tcr`
- **Bästa resultat**: `.epub` eller `.mobi` för automatisk kapiteldetektion

## Utdata

- Skapar en `.m4b`-fil med metadata och kapitel.
- **Exempelutdata**: ![Exempel](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)

## Vanliga Problem:
- "Det är långsamt!" - Endast på CPU är detta väldigt långsamt, och du kan bara få hastighetsökningar genom en NVIDIA GPU. [Diskussion om detta](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846) För snabbare flerspråkig generering skulle jag föreslå mitt andra [projekt som använder piper-tts](https://github.com/DrewThomasson/ebook2audiobookpiper-tts) istället (Det har dock inte nollskotts röstkloning, och har Siri-kvalitetsröster, men det är mycket snabbare på CPU.)
- "Jag har beroendeproblem" - Använd bara Docker, det är helt självständigt och har ett headless-läge, lägg till `-h` parametern efter `app.py` i Docker run-kommandot för mer information.
- "Jag får ett avklippt ljudproblem!" - VAR GOD SKAPA ETT ÄRANDE AVDETTA, Jag talar inte varje språk och jag behöver råd från varje person för att finjustera min meningsdelningsfunktion på andra språk.😊

## Vad jag behöver hjälp med! 🙌 
## [Fullständig lista över saker kan hittas här](https://github.com/DrewThomasson/ebook2audiobook/issues/32)
- All hjälp från personer som talar något av de stödda språken för att hjälpa till med korrekta meningsdelningsmetoder
- Möjligtvis skapa readme-guider för flera språk (För att det enda språket jag kan är Engelska 😔)

## Särskilt Tack

- **Coqui TTS**: [Coqui TTS GitHub](https://github.com/idiap/coqui-ai-TTS)
- **Calibre**: [Calibre Webbplats](https://calibre-ebook.com)
- **FFmpeg**: [FFmpeg Webbplats](https://ffmpeg.org)

- [@shakenbake15 för bättre kapitel sparmetod](https://github.com/DrewThomasson/ebook2audiobook/issues/8) 

### [Äldre V1.0](legacy/v1.0)

Du kan se koden [här](legacy/v1.0).

## Gå med i Vår Discord-server!

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/bg5Kx43c6w)](https://discord.gg/bg5Kx43c6w)