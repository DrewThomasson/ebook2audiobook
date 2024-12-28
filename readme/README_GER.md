# 📚 ebook2audiobook

CPU/GPU Konverter von eBook zu Hörbüchern mit Kapiteln und Metadaten durch Calibre, ffmpeg, XttSv2, Fairseq und mehr. Unterstützt das Klonen von stimmen und 1124 Sprachen!

**Dieses Tool ist nur für die Verwendung mit legal erworbenen eBooks ohne DRM vorgesehen.** 

Die Autoren sind nicht für den Missbrauch dieser Software oder daraus resultierende rechtliche Konsequenzen verantwortlich.  

Verwenden Sie dieses Tool verantwortungsbewusst und in Übereinstimmung mit allen geltenden Gesetzen.

[![Discord](https://img.shields.io/badge/Discord-%235865F2.svg?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/bg5Kx43c6w)

#### Neue v2.0 Weboberfläche
![demo_web_gui](../assets/demo_web_gui.gif)

<details>
  <summary>Klicken Sie hier, um Bilder der Weboberfläche zu sehen!</summary>
  <img width="1728" alt="GUI Screen 1" src="../assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="../assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="../assets/gui_3.png">
</details>

## README.md
- en [Englisch](README.md)

## Inhaltsverzeichnis

- [ebook2audiobook](#ebook2audiobook)
- [Funktionen](#funktionen)
- [Neue v2.0 Weboberfläche!](#neue-v2.0-weboberfläche)
- [Huggingface Space Demo](#huggingface-space-demo)
- [Kostenloses Google Colab](#kostenloses-google-colab)
- [Vorgefertigte Audio-Beispiele](#vorgefertigte-audio-beispiele)
- [Unterstützte Sprachen](#unterstützte-sprachen)
- [Systemanforderungen](#systemanforderungen)
- [Installationsanleitung](#installationsanleitung)
- [Verwendung](#verwendung)
  - [Gradio Weboberfläche starten](#gradio-weboberfläche-starten)
  - [Grundlegende Verwendung in der Konsole](#grundlegende-verwendung-in-der-konsole)
  - [Verwendung von besonderen XTTS Modellen](#verwendung-von-besonderen-xtts-modellen)
- [Sammlung von Fine-Tuned TTS Modellen](#sammlung-von-fine-tuned-tts-modellen)
- [Benutzung mit Docker](#benutzung-mit-docker)
- [Unterstützte eBook Formate](#unterstützte-ebook-formate)
- [Ausgabeformate](#ausgabeformate)
- [Häufige Probleme](#häufige-probleme)
- [Besonderer Dank](#besonderer-dank)
- [Trete unserem Discord Server bei](#trete-unserem-discord-server-bei)


## Funktionen

- 📖 Konvertiert eBooks mit Calibre ins Textformat.
- 📚 Teilt eBooks in Kapitel auf, um Audio zu organisieren.
- 🎙️ Hochwertige Text-to-Speech-Funktion mit [Coqui XTTSv2](https://huggingface.co/coqui/XTTS-v2) und [Fairseq](https://github.com/facebookresearch/fairseq/tree/main/examples/mms).
- 🗣️ Optionales klonen von Stimmen mit Ihrer eigenen Sprachdatei.
- 🌍 Unterstützt 1107 Sprachen (standardmäßig Englisch). [Liste der unterstützten Sprachen](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
- 🖥️ Entwickelt für die Ausführung auf 4 GB RAM.

## [Huggingface Space-Demo](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)

- Huggingface Space läuft auf der kostenlosen CPU-Stufe, also rechnen Sie mit sehr langsamer Leistung oder Timeouts. Daher am besten keine riesigen Dateien ausprobieren.
- Am besten duplizieren Sie den Bereich oder führen das Programm lokal aus.

## Kostenloses Google Colab
[![Kostenloses Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb)

## Unterstützte Sprachen

- **Arabisch (ara)**
- **Chinesisch (zho)**
- **Tschechisch (ces)**
- **Niederländisch (nld)**
- **Englisch (eng)**
- **Französisch (fra)**
- **Deutsch (deu)**
- **Hindi (hin)**
- **Ungarisch (hun)**
- **Italienisch (ita)**
- **Japanisch (jpn)**
- **Koreanisch (kor)**
- **Polnisch (pol)**
- **Portugiesisch (por)**
- **Russisch (rus)**
- **Spanisch (spa)**
- **Türkisch (tur)**
- **Vietnamesisch (vie)**
- [** + 1107 Sprachen über Fairseq**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)

## Systemanforderungen

- 4 GB RAM
- Virtualisierung aktiviert, wenn unter Windows ausgeführt (nur Docker)

### Installationsanleitung

1. **Klone das Git-Repository**
```bash
git clone https://github.com/DrewThomasson/ebook2audiobook.git
```

Geben Sie das Sprachkürzel an, wenn Sie das Skript in der Konsole ausführen ausführen.

## Verwendung

### Gradio-Weboberfläche starten

1. **ebook2audiobook ausführen**:
- **Linux/MacOS**:
```bash
./ebook2audiobook.sh # Startskript ausführen
```
- **Windows**
```bash
.\ebook2audiobook.cmd # Startskript ausführen
```

2. **Web-App öffnen**: Klicken Sie auf die im Terminal bereitgestellte URL, um auf die Web-App zuzugreifen und eBooks zu konvertieren.
3. **Für öffentliche Links**: Fügen Sie am Ende `--share` hinzu, wie folgt: `python app.py --share`
- **[Für weitere Parameter]**: Verwenden Sie den Parameter `--help` wie folgt: `python app.py --help`

### Grundlegende Verwendung in der Konsole
- **Linux/MacOS**:
```bash
./ebook2audiobook.sh --headless --ebook <Pfad_zur_E-Book-Datei> --voice [Pfad_zur_Sprachdatei] --language [Sprachkürzel]
```
- **Windows**
```bash
.\ebook2audiobook.cmd --headless --ebook <Pfad_zur_E-Book-Datei> --voice [Pfad_zur_Sprachdatei] --language [Sprachkürzel]
```

- **<Pfad_zur_E-Book-Datei>**: Pfad zu Ihrer E-Book-Datei.
- **[Pfad_zur_Sprachdatei]**: Optional für Stimmklonierung.
- **[Sprachkürzel]**: Optional zur Angabe des ISO-639-3-Sprachkürzel mit 3+ Buchstaben (Standard ist „eng“). ISO-639-1 2-Buchstaben-Code wird ebenfalls unterstützt
- **[Weitere Parameter]**: Verwenden Sie den Parameter `--help` wie folgt `python app.py --help`

### Verwendung von besonderen XTTS Modellen
- **Linux/MacOS**:
```bash
./ebook2audiobook.sh --headless --ebook <Pfad_zur_E-Book-Datei> --voice <Pfad_zur_Sprachdatei> --language <Sprachkürzel> --custom_model <Pfad_zum_Modell> --custom_config <Pfad_zur_Konfigdatei> --custom_vocab <Pfad_zur_benutzerdefinierten_Vokabeldatei>
```
- **Windows**
```bash
.\ebook2audiobook.cmd --headless --ebook <Pfad_zur_E-Book-Datei> --voice <Pfad_zur_Sprachdatei> --language <Sprachkürzel> --custom_model <Pfad_zum_Modell> --custom_config <Pfad_zur_Konfigdatei> --custom_vocab <Pfad_zur_benutzerdefinierten_Vokabeldatei>
```

- **<Pfad_zur_E-Book-Datei>**: Pfad zu Ihrer eBook-Datei.
- **<Pfad_zur_Sprachdatei>**: Optional für Stimmklonierung.
- **<Sprachkürzel>**: Optional zur Angabe der Sprache.
- **<Pfad_zum_Modell>**: Pfad zu `model.pth`.
- **<Pfad_zur_Konfigdatei>**: Pfad zu `config.json`.
- **<Pfad_zur_benutzerdefinierten_Vokabeldatei>**: Pfad zu `vocab.json`.
- **[Weitere Parameter]**: Verwenden Sie den Parameter `--help` wie folgt: `python app.py --help`

### Für eine ausführliche Anleitung mit einer Liste aller zu verwendenden Parameter
- **Linux/MacOS**:
```bash
./ebook2audiobook.sh --help
```
- **Windows**
```bash
.\ebook2audiobook.cmd --help
```

- Dies gibt Folgendes aus:
```bash
usage: app.py [-h] [--script_mode SCRIPT_MODE] [--share] [--headless [HEADLESS]]
[--session SESSION] [--ebook EBOOK] [--ebooks_dir [EBOOKS_DIR]]
[--voice VOICE] [--language LANGUAGE] [--device {cpu,gpu}]
[--custom_model CUSTOM_MODEL] [--temperature TEMPERATURE]
[--length_penalty LENGTH_PENALTY]
[--repetition_penalty REPETITION_PENALTY] [--top_k TOP_K] [--top_p TOP_P]
[--speed SPEED] [--enable_text_splitting] [--fine_tuned FINE_TUNED]
[--version]

Konvertieren Sie eBooks in Hörbücher mithilfe eines Text-to-Speech-Modells. Sie können entweder die Gradio-Schnittstelle starten oder das Skript im Headless-Modus für eine direkte Konvertierung ausführen.

Optionen:
-h, --help zeigt diese Hilfemeldung an und beendet
--script_mode SCRIPT_MODE
Erzwingt die Ausführung des Skripts in NATIVE oder DOCKER_UTILS
--share Aktiviert einen öffentlichen, gemeinsam nutzbaren Gradio-Link. Standardmäßig auf „False“ eingestellt.
--headless [HEADLESS]
Im Headless-Modus ausführen. Standardmäßig True, wenn das Flag ohne Wert vorhanden ist, andernfalls False.
--session SESSION Sitzung zur Wiederherstellung der Verbindung im Falle einer Unterbrechung (nur Headless-Modus)
--ebook EBOOK Pfad zur E-Book-Datei für die Konvertierung. Erforderlich im Headless-Modus.
--ebooks_dir [EBOOKS_DIR]
Pfad zum Verzeichnis mit den E-Books für die Stapelkonvertierung. Standardmäßig „ebooks“, wenn „default“ angegeben ist.
--voice VOICE Pfad zur Zielsprachdatei für TTS. Optional, muss 24 kHz für XTTS und 16 kHz für Fairseq-Modelle sein, verwendet eine Standardstimme, wenn nicht angegeben.
--language LANGUAGE Sprache für die Hörbuchkonvertierung. Optionen: eng, zho, spa, fra, por, rus, ind, hin, ben, yor, ara, jav, jpn, kor, deu, ita, fas, tam, tel, tur, pol, hun, nld, zzzz, abi, ace, aca, acn, acr, ach, acu, guq, ade, adj, agd, agx, agn, aha, aka, knj, ake, aeu, ahk, bss, alj, sqi, alt, alp, alz, kab, amk, mmg, amh, ami, azg, agg, boj, cko, any, arl, atq, luc, hyw, apr, aia, msy, cni, cjo, cpu, cpb, asm, asa, teo, ati, djk, ava, avn, avu, awb, kwi, awa, agr, agu, ayr, ayo, abp, blx, sgb, azj-script_cyrillic, azj-script_latin, azb, bba, bhz, bvc, bfy, bgq, bdq, bdh, bqi, bjw, blz, ban, bcc-script_latin, bcc-script_arabic, bam, ptu, bcw, bqj, bno, bbb, bfa, bjz, bak, eus, bsq, akb, btd, btx, bts, bbc, bvz, bjv, bep, bkv, bzj, bem, bng, bom, btt, bha, bgw, bht, beh, sne, ubl, bcl, bim, bkd, bjr, bfo, biv, bib, bis, bzi, bqp, bpr, bps, bwq, bdv, bqc, bus, bnp, bmq, bdg, boa, ksr, bor, bru, box, bzh, bgt, sab, bul, bwu, bmv, mya, tte, cjp, cbv, kaq, cot, cbc, car, cat, ceb, cme, cbi, ceg, cly, cya, che, hne, nya, dig, dug, bgr, cek, cfm, cnh, hlt, mwq, ctd, tcz, zyp, cco, cnl, cle, chz, cpa, cso, cnt, cuc, hak, nan, xnj, cap, cax, ctg, ctu, chf, cce, crt, crq, cac-dialect_sansebastiáncoatán, cac-dialect_sanmateoixtatán, ckt, ncu, cdj, chv, caa, asg, con, crn, cok, crk-script_latin, crk-script_syllabics, crh, hrv, cui, ces, dan, dsh, dbq, dga, dgi, dgk, dnj-dialect_gweetaawueast, dnj-dialect_blowowest, daa, dnt, dnw, dar, tcc, dwr, ded, mzw, ntr, ddn, des, dso, nfa, dhi, gud, did, mhu, dip, dik, tbz, dts, dos, dgo, mvp, jen, dzo, idd, eka, cto, emp, enx, sja, myv, mcq, ese, evn, eza, ewe, fal, fao, far, fij, fin, fon, frd, ful, flr, gau, gbk, gag-script_cyrillic, gag-script_latin, gbi, gmv, lug, pwg, gbm, cab, grt, krs, gso, nlg, gej, gri, kik, acd, glk, gof-script_latin, gog, gkn, wsg, gjn, gqr, gor, gux, gbo, ell, grc, guh, gub, grn, gyr, guo, gde, guj, gvl, guk, rub, dah, gwr, gwi, hat, hlb, amf, hag, hnn, bgc, had, hau, hwc, hvn, hay, xed, heb, heh, hil, hif, hns, hoc, hoy, hus-dialect_westernpotosino, hus-dialect_centralveracruz, huv, hui, hap, iba, isl, dbj, ifa, ifb, ifu, ifk, ife, ign, ikk, iqw, ilb, ilo, imo, inb, ipi, irk, icr, itv, itl, atg, ixl-dialect_sanjuancotzal, ixl-dialect_sangasparchajul, ixl-dialect_santamarianebaj, nca, izr, izz, jac, jam, jvn, kac, dyo, csk, adh, jun, jbu, dyu, bex, juy, gna, urb, kbp, cwa, dtp, kbr, cgc, kki, kzf, lew, cbr, kkj, keo, kqe, kak, kyb, knb, kmd, kml, ify, xal, kbq, kay, ktb, hig, gam, cbu, xnr, kmu, kne, kan, kby, pam, cak-dialect_santamaríadejesús, cak-dialect_southcentral, cak-dialect_yepocapa, cak-dialect_western, cak-dialect_santodomingoxenacoj, cak-dialect_central, xrb, krc, kaa, krl, pww, xsm, cbs, pss, kxf, kyz, kyu, txu, kaz, ndp, kbo, kyq, ken, ker, xte, kyg, kjh, kca, khm, kxm, kjg, nyf, kij, kia, kqr, kqp, krj, zga, kin, pkb, geb, gil, kje, kss, thk, klu, kyo, kog, kfb, kpv, bbo, xon, kma, kno, kxc, ozm, kqy, coe, kpq, kpy, kyf, kff-script_telugu, kri, rop, ktj, ted, krr, kdt, kez, cul, kle, kdi, kue, kum, kvn, cuk, kdn, xuo, key, kpz, knk, kmr-script_latin, kmr-script_arabic, kmr-script_cyrillic, xua, kru, kus, kub, kdc, kxv, blh, cwt, kwd, tnk, kwf, cwe, kyc, tye, kir, quc-dialect_north, quc-dialect_east, quc-dialect_central, lac, lsi, lbj, lhu, las, lam, lns, ljp, laj, lao, lat, lav, law, lcp, lzz, lln, lef, acf, lww, mhx, eip, lia, lif, onb, lis, loq, lob, yaz, lok, llg, ycl, lom, ngl, lon, lex, lgg, ruf, dop, lnd, ndy, lwo, lee, mev, mfz, jmc, myy, mbc, mda, mad, mag, ayz, mai, mca, mcp, mak, vmw, mgh, kde, mlg, zlm, pse, mkn, xmm, mal, xdy, div, mdy, mup, mam-dialect_central, mam-dialect_northern, mam-dialect_southern, mam-dialect_western, mqj, mcu, mzk, maw, mjl, mnk, mge, mbh, knf, mjv, mbt, obo, mbb, mzj, sjm, mrw, mar, mpg, mhr, enb, mah, myx, klv, mfh, met, mcb, mop, yua, mfy, maz, vmy, maq, mzi, maj, maa-dialect_sanantonio, maa-dialect_sanjerónimo, mhy, mhi, zmz, myb, gai, mqb, mbu, med, men, mee, mwv, meq, zim, mgo, mej, mpp, min, gum, mpx, mco, mxq, pxm, mto, mim, xta, mbz, mip, mib, miy, mih, miz, xtd, mxt, xtm, mxv, xtn, mie, mil, mio, mdv, mza, mit, mxb, mpm, soy, cmo-script_latin, cmo-script_khmer, mfq, old, mfk, mif, mkl, mox, myl, mqf, mnw, mon, mog, mfe, mor, mqn, mgd, mtj, cmr, mtd, bmr, moz, mzm, mnb, mnf, unr, fmu, mur, tih, muv, muy, sur, moa, wmw, tnr, miq, mos, muh, nas, mbj, nfr, kfw, nst, nag, nch, nhe, ngu, azz, nhx, ncl, nhy, ncj, nsu, npl, nuz, nhw, nhi, nlc, nab, gld, nnb, npy, pbb, ntm, nmz, naw, nxq, ndj, ndz, ndv, new, nij, sba, gng, nga, nnq, ngp, gym, kdj, nia, nim, nin, nko, nog, lem, not, nhu, nob, bud, nus, yas, nnw, nwb, nyy, nyn, rim, lid, nuj, nyo, nzi, ann, ory, ojb-script_latin, ojb-script_syllabics, oku, bsc, bdu, orm, ury, oss, ote, otq, stn, sig, kfx, bfz, sey, pao, pau, pce, plw, pmf, pag, pap, prf, pab, pbi, pbc, pad, ata, pez, peg, pcm, pis, pny, pir, pjt, poy, pps, pls, poi, poh-dialect_eastern, poh-dialect_western, prt, pui, pan, tsz, suv, lme, quy, qvc, quz, qve, qub, qvh, qwh, qvw, quf, qvm, qul, qvn, qxn, qxh, qvs, quh, qxo, qxr, qvo, qvz, qxl, quw, kjb, kek, rah, rjs, rai, lje, rnl, rkt, rap, yea, raw, rej, rel, ril, iri, rgu, rhg, rmc-script_latin, rmc-script_cyrillic, rmo, rmy-script_latin, rmy-script_cyrillic, ron, rol, cla, rng, rug, run, lsm, spy, sck, saj, sch, sml, xsb, sbl, saq, sbd, smo, rav, sxn, sag, sbp, xsu, srm, sas, apb, sgw, tvw, lip, slu, snw, sea, sza, seh, crs, ksb, shn, sho, mcd, cbt, xsr, shk, shp, sna, cjs, jiv, snp, sya, sid, snn, sri, srx, sil, sld, akp, xog, som, bmu, khq, ses, mnx, srn, sxb, suc, tgo, suk, sun, suz, sgj, sus, swh, swe, syl, dyi, myk, spp, tap, tby, tna, shi, klw, tgl, tbk, tgj, blt, tbg, omw, tgk, tdj, tbc, tlj, tly, ttq-script_tifinagh, taj, taq, tpm, tgp, tnn, tac, rif-script_latin, rif-script_arabic, tat, tav, twb, tbl, kps, twe, ttc, kdh, tes, tex, tee, tpp, tpt, stp, tfr, twu, ter, tew, tha, nod, thl, tem, adx, bod, khg, tca, tir, txq, tik, dgr, tob, tmf, tng, tlb, ood, tpi, jic, lbw, txa, tom, toh, tnt, sda, tcs, toc, tos, neb, trn, trs, trc, tri, cof, tkr, kdl, cas, tso, tuo, iou, tmc, tuf, tuk-script_latin, tuk-script_arabic, bov, tue, kcg, tzh-dialect_bachajón, tzh-dialect_tenejapa, tzo-dialect_chenalhó, tzo-dialect_chamula, tzj-dialect_western, tzj-dialect_eastern, aoz, udm, udu, ukr, ppk, ubu, urk, ura, urt, urd-script_devanagari, urd-script_arabic, urd-script_latin, upv, usp, uig-script_arabic, uig-script_cyrillic, uzb-script_cyrillic, vag, bav, vid, vie, vif, vun, vut, prk, wwa, rro, bao, waw, lgl, wlx, cou, hub, gvc, mfi, wap, wba, war, way, guc, cym, kvw, tnp, hto, huu, wal-script_latin, wal-script_ethiopic, wlo, noa, wob, kao, xer, yad, yka, sah, yba, yli, nlk, yal, yam, yat, jmd, tao, yaa, ame, guu, yao, yre, yva, ybb, pib, byr, pil, ycn, ess, yuz, atb, zne, zaq, zpo, zad, zpc, zca, zpg, zai, zpl, zam, zaw, zpm, zac, zao, ztq, zar, zpt, zpi, zas, zaa, zpz, zab, zpu, zae, zty, zav, zza, zyb, ziw, zos, gnd.  Standardmäßig Englisch (eng).
--device {cpu,gpu} Typ der Prozessoreinheit für die Hörbuchkonvertierung. Wenn nicht angegeben: Überprüft zuerst, ob GPU verfügbar ist, wenn nicht, wird CPU ausgewählt.
--custom_model CUSTOM_MODEL
Pfad zum benutzerdefinierten Modell (.zip-Datei mit ['config.json', 'vocab.json', 'model.pth', 'ref.wav']). Erforderlich bei Verwendung eines benutzerdefinierten Modells.
--temperature TEMPERATURE
Temperatur für das Modell. Standardmäßig 0,65. Höhere Temperaturen führen zu kreativeren Ergebnissen.
--length_penalty LENGTH_PENALTY
Eine Längenstrafe, die auf den autoregressiven Decoder angewendet wird. Standardmäßig 1,0. Wird nicht auf benutzerdefinierte Modelle angewendet.
--repetition_penalty REPETITION_PENALTY
Eine Strafe, die verhindert, dass sich der autoregressive Decoder wiederholt. Standardmäßig 2,5
--top_k TOP_K Top-k-Sampling. Niedrigere Werte bedeuten wahrscheinlichere Ausgaben und eine höhere Geschwindigkeit der Audiogenerierung. Standardmäßig 50
--top_p TOP_P Top-p-Sampling. Niedrigere Werte bedeuten wahrscheinlichere Ausgaben und eine höhere Geschwindigkeit der Audiogenerierung. Standardmäßig 0,8
--speed SPEED Geschwindigkeitsfaktor für die Sprachgenerierung. Standardmäßig 1,0
--enable_text_splitting
Aktiviert das Aufteilen von Text in Sätze. Standardmäßig False.
--fine_tuned FINE_TUNED
Name des fein abgestimmten Modells. Optional, verwendet das Standardmodell entsprechend der TTS-Engine und Sprache.
--version Zeigt die Version des Skripts an und beendet das Programm.

Beispielverwendung:
Windows:
    headless:
    ebook2audiobook.cmd --headless --ebook 'path_to_ebook'
    Grafische Schnittstelle:
    ebook2audiobook.cmd
Linux/Mac:
    headless:
    ./ebook2audiobook.sh --headless --ebook 'path_to_ebook'
    Grafische Schnittstelle:
    ./ebook2audiobook.sh

```

### Benutzung mit Docker

Sie können Docker auch verwenden, um den eBook-zu-Hörbuch-Konverter auszuführen. Diese Methode gewährleistet Konsistenz in verschiedenen Umgebungen und vereinfacht die Einrichtung.

#### Ausführen des Docker-Containers

Um den Docker-Container auszuführen und die Gradio-Weboberfläche zu starten, verwenden Sie den folgenden Befehl:

-Nur mit CPU ausführen
```powershell
docker run -it --rm -p 7860:7860 --platform=linux/amd64 athomasson2/ebook2audiobookxtts:huggingface python app.py
```
-Mit GPU-Beschleunigung ausführen (nur Nvida-Grafikkarten)
```powershell
docker run -it --rm --gpus all -p 7860:7860 --platform=linux/amd64 athomasson2/ebook2audiobookxtts:huggingface python app.py
```

Dieser Befehl startet die Gradio-Schnittstelle auf Port 7860.(localhost:7860)
- Für weitere Optionen, wie das Ausführen des Dockers im Konsolen-Modus oder das Aktivieren eines öffentlichen Gradio Links: Fügen Sie den Parameter „--help“ nach „app.py“ im Docker-Startbefehl hinzu.
<details>
    <summary><strong>Beispiel für die Verwendung von Docker im Konsolen-Modus oder für die Änderung von irgendetwas mit den zusätzlichen Parametern + Vollständige Anleitung</strong></summary>

## Beispiel für die Verwendung von Docker im Konsolen-Modus

Für zuerst einen Docker-Pull durch um die neuesten Version zu erhalten.
```bash
docker pull athomasson2/ebook2audiobook:huggingface
```

- Bevor Sie dies ausführen, müssen Sie in Ihrem aktuellen Verzeichnis ein Verzeichnis mit dem Namen „input-folder“ erstellen, das verknüpft wird. Hier können Sie Ihre Eingabedateien ablegen, damit das Docker-Image sie sehen kann
```bash
mkdir input-folder && mkdir Audiobooks
```

- Ersetzen Sie im folgenden Befehl **YOUR_INPUT_FILE.TXT** durch den Namen Ihrer Eingabedatei

```bash
docker run -it --rm \
-v $(pwd)/input-folder:/home/user/app/input_folder \
-v $(pwd)/Audiobooks:/home/user/app/Audiobooks \
--platform linux/amd64 \
athomasson2/ebook2audiobook:huggingface \
python app.py --headless --ebook /input_folder/IHRE_EINGABEDATEI.TXT
```

- Und das sollte es sein!

- Die ausgegebenen Hörbücher befinden sich im Ordner „Hörbücher“, der sich ebenfalls in Ihrem lokalen Verzeichnis befindet, in dem Sie diesen Docker-Befehl ausgeführt haben

## Um den Hilfebefehl für die anderen Parameter dieses Programms zu erhalten, können Sie Folgendes ausführen:

```bash
docker run -it --rm \
--platform linux/amd64 \
athomasson2/ebook2audiobook:huggingface \
python app.py --help

```

und das gibt Folgendes aus:

```bash
user/app/ebook2audiobook/input-folder -v $(pwd)/Audiobooks:/home/user/app/ebook2audiobook/Audiobooks --memory="4g" --network none --platform linux/amd64 athomasson2/ebook2audiobook:huggingface python app.py -h
usage: app.py [-h] [--script_mode SCRIPT_MODE] [--share] [--headless [HEADLESS]]
              [--session SESSION] [--ebook EBOOK] [--ebooks_dir [EBOOKS_DIR]]
              [--voice VOICE] [--language LANGUAGE] [--device {cpu,gpu}]
              [--custom_model CUSTOM_MODEL] [--temperature TEMPERATURE]
              [--length_penalty LENGTH_PENALTY]
              [--repetition_penalty REPETITION_PENALTY] [--top_k TOP_K] [--top_p TOP_P]
              [--speed SPEED] [--enable_text_splitting] [--fine_tuned FINE_TUNED]
              [--version]

Convert eBooks to Audiobooks using a Text-to-Speech model. You can either launch the Gradio interface or run the script in headless mode for direct conversion.

options:
  -h, --help            show this help message and exit
  --script_mode SCRIPT_MODE
                        Force the script to run in NATIVE or DOCKER_UTILS
  --share               Enable a public shareable Gradio link. Default to False.
  --headless [HEADLESS]
                        Run in headless mode. Default to True if the flag is present without a value, False otherwise.
  --session SESSION     Session to reconnect in case of interruption (headless mode only)
  --ebook EBOOK         Path to the ebook file for conversion. Required in headless mode.
  --ebooks_dir [EBOOKS_DIR]
                        Path to the directory containing ebooks for batch conversion. Default to "ebooks" if "default" is provided.
  --voice VOICE         Path to the target voice file for TTS. Optional, must be 24khz for XTTS and 16khz for fairseq models, uses a default voice if not provided.
  --language LANGUAGE   Language for the audiobook conversion. Options: eng, zho, spa, fra, por, rus, ind, hin, ben, yor, ara, jav, jpn, kor, deu, ita, fas, tam, tel, tur, pol, hun, nld, zzzz, abi, ace, aca, acn, acr, ach, acu, guq, ade, adj, agd, agx, agn, aha, aka, knj, ake, aeu, ahk, bss, alj, sqi, alt, alp, alz, kab, amk, mmg, amh, ami, azg, agg, boj, cko, any, arl, atq, luc, hyw, apr, aia, msy, cni, cjo, cpu, cpb, asm, asa, teo, ati, djk, ava, avn, avu, awb, kwi, awa, agr, agu, ayr, ayo, abp, blx, sgb, azj-script_cyrillic, azj-script_latin, azb, bba, bhz, bvc, bfy, bgq, bdq, bdh, bqi, bjw, blz, ban, bcc-script_latin, bcc-script_arabic, bam, ptu, bcw, bqj, bno, bbb, bfa, bjz, bak, eus, bsq, akb, btd, btx, bts, bbc, bvz, bjv, bep, bkv, bzj, bem, bng, bom, btt, bha, bgw, bht, beh, sne, ubl, bcl, bim, bkd, bjr, bfo, biv, bib, bis, bzi, bqp, bpr, bps, bwq, bdv, bqc, bus, bnp, bmq, bdg, boa, ksr, bor, bru, box, bzh, bgt, sab, bul, bwu, bmv, mya, tte, cjp, cbv, kaq, cot, cbc, car, cat, ceb, cme, cbi, ceg, cly, cya, che, hne, nya, dig, dug, bgr, cek, cfm, cnh, hlt, mwq, ctd, tcz, zyp, cco, cnl, cle, chz, cpa, cso, cnt, cuc, hak, nan, xnj, cap, cax, ctg, ctu, chf, cce, crt, crq, cac-dialect_sansebastiáncoatán, cac-dialect_sanmateoixtatán, ckt, ncu, cdj, chv, caa, asg, con, crn, cok, crk-script_latin, crk-script_syllabics, crh, hrv, cui, ces, dan, dsh, dbq, dga, dgi, dgk, dnj-dialect_gweetaawueast, dnj-dialect_blowowest, daa, dnt, dnw, dar, tcc, dwr, ded, mzw, ntr, ddn, des, dso, nfa, dhi, gud, did, mhu, dip, dik, tbz, dts, dos, dgo, mvp, jen, dzo, idd, eka, cto, emp, enx, sja, myv, mcq, ese, evn, eza, ewe, fal, fao, far, fij, fin, fon, frd, ful, flr, gau, gbk, gag-script_cyrillic, gag-script_latin, gbi, gmv, lug, pwg, gbm, cab, grt, krs, gso, nlg, gej, gri, kik, acd, glk, gof-script_latin, gog, gkn, wsg, gjn, gqr, gor, gux, gbo, ell, grc, guh, gub, grn, gyr, guo, gde, guj, gvl, guk, rub, dah, gwr, gwi, hat, hlb, amf, hag, hnn, bgc, had, hau, hwc, hvn, hay, xed, heb, heh, hil, hif, hns, hoc, hoy, hus-dialect_westernpotosino, hus-dialect_centralveracruz, huv, hui, hap, iba, isl, dbj, ifa, ifb, ifu, ifk, ife, ign, ikk, iqw, ilb, ilo, imo, inb, ipi, irk, icr, itv, itl, atg, ixl-dialect_sanjuancotzal, ixl-dialect_sangasparchajul, ixl-dialect_santamarianebaj, nca, izr, izz, jac, jam, jvn, kac, dyo, csk, adh, jun, jbu, dyu, bex, juy, gna, urb, kbp, cwa, dtp, kbr, cgc, kki, kzf, lew, cbr, kkj, keo, kqe, kak, kyb, knb, kmd, kml, ify, xal, kbq, kay, ktb, hig, gam, cbu, xnr, kmu, kne, kan, kby, pam, cak-dialect_santamaríadejesús, cak-dialect_southcentral, cak-dialect_yepocapa, cak-dialect_western, cak-dialect_santodomingoxenacoj, cak-dialect_central, xrb, krc, kaa, krl, pww, xsm, cbs, pss, kxf, kyz, kyu, txu, kaz, ndp, kbo, kyq, ken, ker, xte, kyg, kjh, kca, khm, kxm, kjg, nyf, kij, kia, kqr, kqp, krj, zga, kin, pkb, geb, gil, kje, kss, thk, klu, kyo, kog, kfb, kpv, bbo, xon, kma, kno, kxc, ozm, kqy, coe, kpq, kpy, kyf, kff-script_telugu, kri, rop, ktj, ted, krr, kdt, kez, cul, kle, kdi, kue, kum, kvn, cuk, kdn, xuo, key, kpz, knk, kmr-script_latin, kmr-script_arabic, kmr-script_cyrillic, xua, kru, kus, kub, kdc, kxv, blh, cwt, kwd, tnk, kwf, cwe, kyc, tye, kir, quc-dialect_north, quc-dialect_east, quc-dialect_central, lac, lsi, lbj, lhu, las, lam, lns, ljp, laj, lao, lat, lav, law, lcp, lzz, lln, lef, acf, lww, mhx, eip, lia, lif, onb, lis, loq, lob, yaz, lok, llg, ycl, lom, ngl, lon, lex, lgg, ruf, dop, lnd, ndy, lwo, lee, mev, mfz, jmc, myy, mbc, mda, mad, mag, ayz, mai, mca, mcp, mak, vmw, mgh, kde, mlg, zlm, pse, mkn, xmm, mal, xdy, div, mdy, mup, mam-dialect_central, mam-dialect_northern, mam-dialect_southern, mam-dialect_western, mqj, mcu, mzk, maw, mjl, mnk, mge, mbh, knf, mjv, mbt, obo, mbb, mzj, sjm, mrw, mar, mpg, mhr, enb, mah, myx, klv, mfh, met, mcb, mop, yua, mfy, maz, vmy, maq, mzi, maj, maa-dialect_sanantonio, maa-dialect_sanjerónimo, mhy, mhi, zmz, myb, gai, mqb, mbu, med, men, mee, mwv, meq, zim, mgo, mej, mpp, min, gum, mpx, mco, mxq, pxm, mto, mim, xta, mbz, mip, mib, miy, mih, miz, xtd, mxt, xtm, mxv, xtn, mie, mil, mio, mdv, mza, mit, mxb, mpm, soy, cmo-script_latin, cmo-script_khmer, mfq, old, mfk, mif, mkl, mox, myl, mqf, mnw, mon, mog, mfe, mor, mqn, mgd, mtj, cmr, mtd, bmr, moz, mzm, mnb, mnf, unr, fmu, mur, tih, muv, muy, sur, moa, wmw, tnr, miq, mos, muh, nas, mbj, nfr, kfw, nst, nag, nch, nhe, ngu, azz, nhx, ncl, nhy, ncj, nsu, npl, nuz, nhw, nhi, nlc, nab, gld, nnb, npy, pbb, ntm, nmz, naw, nxq, ndj, ndz, ndv, new, nij, sba, gng, nga, nnq, ngp, gym, kdj, nia, nim, nin, nko, nog, lem, not, nhu, nob, bud, nus, yas, nnw, nwb, nyy, nyn, rim, lid, nuj, nyo, nzi, ann, ory, ojb-script_latin, ojb-script_syllabics, oku, bsc, bdu, orm, ury, oss, ote, otq, stn, sig, kfx, bfz, sey, pao, pau, pce, plw, pmf, pag, pap, prf, pab, pbi, pbc, pad, ata, pez, peg, pcm, pis, pny, pir, pjt, poy, pps, pls, poi, poh-dialect_eastern, poh-dialect_western, prt, pui, pan, tsz, suv, lme, quy, qvc, quz, qve, qub, qvh, qwh, qvw, quf, qvm, qul, qvn, qxn, qxh, qvs, quh, qxo, qxr, qvo, qvz, qxl, quw, kjb, kek, rah, rjs, rai, lje, rnl, rkt, rap, yea, raw, rej, rel, ril, iri, rgu, rhg, rmc-script_latin, rmc-script_cyrillic, rmo, rmy-script_latin, rmy-script_cyrillic, ron, rol, cla, rng, rug, run, lsm, spy, sck, saj, sch, sml, xsb, sbl, saq, sbd, smo, rav, sxn, sag, sbp, xsu, srm, sas, apb, sgw, tvw, lip, slu, snw, sea, sza, seh, crs, ksb, shn, sho, mcd, cbt, xsr, shk, shp, sna, cjs, jiv, snp, sya, sid, snn, sri, srx, sil, sld, akp, xog, som, bmu, khq, ses, mnx, srn, sxb, suc, tgo, suk, sun, suz, sgj, sus, swh, swe, syl, dyi, myk, spp, tap, tby, tna, shi, klw, tgl, tbk, tgj, blt, tbg, omw, tgk, tdj, tbc, tlj, tly, ttq-script_tifinagh, taj, taq, tpm, tgp, tnn, tac, rif-script_latin, rif-script_arabic, tat, tav, twb, tbl, kps, twe, ttc, kdh, tes, tex, tee, tpp, tpt, stp, tfr, twu, ter, tew, tha, nod, thl, tem, adx, bod, khg, tca, tir, txq, tik, dgr, tob, tmf, tng, tlb, ood, tpi, jic, lbw, txa, tom, toh, tnt, sda, tcs, toc, tos, neb, trn, trs, trc, tri, cof, tkr, kdl, cas, tso, tuo, iou, tmc, tuf, tuk-script_latin, tuk-script_arabic, bov, tue, kcg, tzh-dialect_bachajón, tzh-dialect_tenejapa, tzo-dialect_chenalhó, tzo-dialect_chamula, tzj-dialect_western, tzj-dialect_eastern, aoz, udm, udu, ukr, ppk, ubu, urk, ura, urt, urd-script_devanagari, urd-script_arabic, urd-script_latin, upv, usp, uig-script_arabic, uig-script_cyrillic, uzb-script_cyrillic, vag, bav, vid, vie, vif, vun, vut, prk, wwa, rro, bao, waw, lgl, wlx, cou, hub, gvc, mfi, wap, wba, war, way, guc, cym, kvw, tnp, hto, huu, wal-script_latin, wal-script_ethiopic, wlo, noa, wob, kao, xer, yad, yka, sah, yba, yli, nlk, yal, yam, yat, jmd, tao, yaa, ame, guu, yao, yre, yva, ybb, pib, byr, pil, ycn, ess, yuz, atb, zne, zaq, zpo, zad, zpc, zca, zpg, zai, zpl, zam, zaw, zpm, zac, zao, ztq, zar, zpt, zpi, zas, zaa, zpz, zab, zpu, zae, zty, zav, zza, zyb, ziw, zos, gnd. Default to English (eng).
  --device {cpu,gpu}    Type of processor unit for the audiobook conversion. If not specified: check first if gpu available, if not cpu is selected.
  --custom_model CUSTOM_MODEL
                        Path to the custom model (.zip file containing ['config.json', 'vocab.json', 'model.pth', 'ref.wav']). Required if using a custom model.
  --temperature TEMPERATURE
                        Temperature for the model. Default to 0.65. Higher temperatures lead to more creative outputs.
  --length_penalty LENGTH_PENALTY
                        A length penalty applied to the autoregressive decoder. Default to 1.0. Not applied to custom models.
  --repetition_penalty REPETITION_PENALTY
                        A penalty that prevents the autoregressive decoder from repeating itself. Default to 2.5
  --top_k TOP_K         Top-k sampling. Lower values mean more likely outputs and increased audio generation speed. Default to 50
  --top_p TOP_P         Top-p sampling. Lower values mean more likely outputs and increased audio generation speed. Default to 0.8
  --speed SPEED         Speed factor for the speech generation. Default to 1.0
  --enable_text_splitting
                        Enable splitting text into sentences. Default to False.
  --fine_tuned FINE_TUNED
                        Name of the fine tuned model. Optional, uses the standard model according to the TTS engine and language.
  --version             Show the version of the script and exit

Example usage:    
Windows:
    headless:
    ebook2audiobook.cmd --headless --ebook 'path_to_ebook'
    Graphic Interface:
    ebook2audiobook.cmd
Linux/Mac:
    headless:
    ./ebook2audiobook.sh --headless --ebook 'path_to_ebook'
    Graphic Interface:
    ./ebook2audiobook.sh
```

</details>

#### Neue v2.0 Docker Weboberfäche!
![demo_web_gui](../assets/demo_web_gui.gif)

<details>
<summary>Klicken Sie, um Bilder der Weboberfläche anzuzeigen.</summary>
<img width="1728" alt="GUI-Bildschirm 1" src="../assets/gui_1.png">
<img width="1728" alt="GUI-Bildschirm 2" src="../assets/gui_2.png">
<img width="1728" alt="GUI-Bildschirm 3" src="../assets/gui_3.png">
</details>

## Sammlung von Fine-Tuned TTS Modellen

Um unsere Sammlung bereits fein abgestimmter TTS-Modelle zu finden, besuchen Sie [diesen Hugging Face-Link](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)
Für ein benutzerdefiniertes XTTS-Modell wird außerdem ein Referenz-Audioclip der Stimme benötigt:

## Vorgefertigte Audio-Beispiele

Rainy day Stimme

https://github.com/user-attachments/assets/8486603c-38b1-43ce-9639-73757dfb1031

David Attenborough Stimme

https://github.com/user-attachments/assets/47c846a7-9e51-4eb9-844a-7460402a20a8

## Unterstützte eBook Formate

- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`, `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`, `.snb`, `.cbc`, `.rb`, `.tcr`
- **Beste Ergebnisse**: `.epub` oder `.mobi` für automatische Kapitelerkennung

## Ausgabe

- Erstellt eine `.m4b`-Datei mit Metadaten und Kapiteln.
- **Beispielausgabe**: ![Beispiel](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)

## Häufige Probleme:
- „Es ist langsam!“ – Nur auf der CPU ist dies sehr langsam, und Sie können nur durch eine NVIDIA-GPU eine Beschleunigung erreichen. [Diskussion darüber](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846) Für eine schnellere Generierung mehrerer Sprachen würde ich stattdessen mein anderes [Projekt vorschlagen, das Piper-TTS verwendet](https://github.com/DrewThomasson/ebook2audiobookpiper-tts) (Es hat allerdings kein Zero-Shot-Voice-Cloning und hat Stimmen in Siri-Qualität, ist aber viel schneller auf der CPU.)
- „Ich habe Abhängigkeitsprobleme“ – Verwenden Sie einfach den Docker, er ist vollständig eigenständig und hat einen Headless-Modus. Fügen Sie für weitere Informationen den Parameter „-h“ nach „app.py“ im Docker-Run-Befehl hinzu.
- „Ich habe ein Problem mit abgeschnittenem Audio!“ - BITTE MACHEN SIE EIN ISSURE DARAUS, ich spreche nicht jede Sprache und brauche den Rat von jeder Person, um meine Satztrennungsfunktion in anderen Sprachen zu optimieren.😊

## Wobei ich Hilfe brauche! 🙌
## [Die vollständige Liste der Dinge finden Sie hier](https://github.com/DrewThomasson/ebook2audiobook/issues/32)
- Jede Hilfe von Leuten, die eine der unterstützten Sprachen sprechen, um bei der richtigen Satztrennung zu helfen
- Eventuell Erstellung von Readme-Anleitungen für mehrere Sprachen (weil die einzige Sprache, die ich kenne, Englisch ist 😔)

## Besonderer Dank

- **Coqui TTS**: [Coqui TTS GitHub](https://github.com/idiap/coqui-ai-TTS)
- **Calibre**: [Calibre-Website](https://calibre-ebook.com)
- **FFmpeg**: [FFmpeg-Website](https://ffmpeg.org)

- [@shakenbake15 für eine bessere Methode zum Speichern von Kapiteln](https://github.com/DrewThomasson/ebook2audiobook/issues/8)

### [Legacy V1.0](legacy/v1.0)

Sie können den Code [hier](legacy/v1.0) ansehen.

## Trete unserem Discord Server bei

[![Discord](https://img.shields.io/badge/Discord-%235865F2.svg?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/bg5Kx43c6w)