# 📚 ebook2audiobook

Конвертер CPU/GPU для перетворення електронних книг у аудіокниги з главами та метаданими
за допомогою Calibre, ffmpeg, XTTSv2, Fairseq тощо. Підтримує клонування голосу та 1124 мови!
> [!IMPORTANT]
**Цей інструмент призначений для використання лише з електронними книгами без DRM, отриманими законним шляхом.** <br>
Автори не несуть відповідальності за будь-яке неправомірне використання цього програмного забезпечення або за юридичні наслідки, що можуть виникнути.
Використовуйте цей інструмент відповідально та відповідно до чинного законодавства.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/bg5Kx43c6w)](https://discord.gg/bg5Kx43c6w)

Дякуємо за підтримку розробників ebook2audiobook!<br>
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 


#### Нове веб-інтерфейс середовище v2.0!
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Натисніть, щоб переглянути зображення веб-інтерфейсу!</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>


## README.md
- ara [العربية (Arabic)](./readme/README_AR.md)
- zho [中文 (Chinese)](./readme/README_CN.md)
- eng [English](README.md)
- swe [Svenska (Swedish)](./readme/README_SWE.md)
- ua [Ukrainian](./readme/README_UA.md)

## Table of Contents

- [ebook2audiobook](#ebook2audiobook)
- [Функції](#features)
- [Новий веб-інтерфейс v2.0](#new-v20-web-gui-interface)
- [Демо на Huggingface Space](#huggingface-space-demo)
- [Безкоштовний Google Colab](#free-google-colab)
- [Готові аудіо-демо](#demos)
- [Підтримувані мови](#supported-languages)
- [Вимоги](#requirements)
- [Інструкція з встановлення](#installation-instructions)
- [Використання](#usage)
  - [Запуск Gradio Web Interface](#launching-gradio-web-interface)
  - [Основне використання без GUI](#basic-headless-usage)
  - [Використання власних XTTS моделей без GUI](#headless-custom-xtts-model-usage)
  - [Оренда GPU](#renting-a-gpu)
  - [Вивід команди допомоги](#help-command-output)
- [Моделі TTS з Fine Tune](#fine-tuned-tts-models)
  - [Колекція моделей TTS з налаштуванням](#fine-tuned-tts-collection)
- [Використання Docker](#using-docker)
  - [Docker Run](#running-the-docker-container)
  - [Docker Build](#building-the-docker-container)
  - [Docker Compose](#docker-compose)
  - [Керівництво по headless Docker](#docker-headless-guide)
  - [Розташування файлів у Docker контейнері](#docker-container-file-locations)
  - [Типові проблеми Docker](#common-docker-issues)
- [Підтримувані формати електронних книг](#supported-ebook-formats)
- [Результат](#output)
- [Типові проблеми](#common-issues)
- [Особлива подяка](#special-thanks)
- [Приєднуйтесь до нашого Discord серверу!](#join-our-discord-server)
- [Legacy](#legacy-v10)
- [Глосарій секцій](#glossary-of-sections)

## Функції

- 📖 Конвертує електронні книги у текстовий формат за допомогою Calibre.
- 📚 Ділить електронну книгу на глави для організованого аудіо.
- 🎙️ Високоякісний текст-у-мову за допомогою [Coqui XTTSv2](https://huggingface.co/coqui/XTTS-v2) та [Fairseq](https://github.com/facebookresearch/fairseq/tree/main/examples/mms).
- 🗣️ Опційне клонування голосу за допомогою вашого власного звукового файлу.
- 🌍 Підтримує 1107 мов (за замовчуванням — англійська). [Список підтримуваних мов](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
- 🖥️ Розроблений для роботи на пристроях із 4 ГБ оперативної пам’яті.

## [Huggingface space demo](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)

- Huggingface Space працює на безкоштовному CPU-тарифі, тому очікуйте дуже повільну роботу або таймаут 😅. Просто не завантажуйте надто великі файли.
- Найкраще продублювати Space або запустити його локально.

## Free Google Colab 
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb)

## Supported Languages

- **Арабська (ara)**  
- **Китайська (zho)**  
- **Чеська (ces)**  
- **Нідерландська (nld)**  
- **Англійська (eng)**  
- **Французька (fra)**  
- **Німецька (deu)**  
- **Гінді (hin)**  
- **Угорська (hun)**  
- **Італійська (ita)**  
- **Японська (jpn)**  
- **Корейська (kor)**  
- **Польська (pol)**  
- **Португальська (por)**  
- **Російська (rus)**  
- **Іспанська (spa)**  
- **Турецька (tur)**  
- **В'єтнамська (vie)**  
- [**+ 1107 мов через Fairseq**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)


## Вимоги

- 4 ГБ оперативної пам'яті
- Увімкнена віртуалізація, якщо ви запускаєте на Windows (тільки Docker)

> [!IMPORTANT]
**Перед тим, як опублікувати питання про встановлення або помилку, ретельно перевірте вкладку відкритих та закритих питань,  
щоб переконатися, що ваша проблема вже не була вирішена.**

### Інструкція з встановлення

1. **Клонуйте репозиторій**
```bash
git clone https://github.com/DrewThomasson/ebook2audiobook.git
```


Вкажіть код мови під час запуску скрипта в режимі.

### Запуск веб-інтерфейсу Gradio

1. **Запустіть ebook2audiobook**:
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.sh  # Запустіть скрипт запуску
     ```
   - **Windows**:
     ```bash
     .\ebook2audiobook.cmd  # Запустіть скрипт запуску або двічі клацніть на ньому
     ```
2. **Відкрийте веб-додаток**: Клацніть на URL, який надається в терміналі, щоб отримати доступ до веб-додатку та конвертувати електронні книги.
3. **Для публічного посилання**: Додайте `--share` в кінець, ось так: `python app.py --share`
- **[Більше параметрів]**: використовуйте параметр `--help`, ось так: `python app.py --help`

### Основне використання

   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.sh  -- --ebook <шлях_до_файлу_книги> --voice [шлях_до_файлу_голосу] --language [код_мови]
     ```
   - **Windows**:
     ```bash
     .\ebook2audiobook.cmd  -- --ebook <шлях_до_файлу_книги> --voice [шлях_до_файлу_голосу] --language [код_мови]
     ```

- **<шлях_до_файлу_книги>**: Шлях до вашого файлу електронної книги.
- **[шлях_до_файлу_голосу]**: Опційно для клонування голосу.
- **[код_мови]**: Опційно для вказівки коду мови ISO-639-3 (за замовчуванням — eng). Також підтримуються коди мов ISO-639-1 (2 літери).
- **[Більше параметрів]**: використовуйте параметр `--help`, ось так: `python app.py --help`

### Використання кастомної моделі XTTS
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.sh  -- --ebook <шлях_до_файлу_книги> --voice <шлях_до_цільового_файлу_голосу> --language <мова> --custom_model <шлях_до_кастомної_моделі> --custom_config <шлях_до_кастомного_конфігу> --custom_vocab <шлях_до_кастомного_словника>
     ```
   - **Windows**:
     ```bash
     .\ebook2audiobook.cmd  -- --ebook <шлях_до_файлу_книги> --voice <шлях_до_цільового_файлу_голосу> --language <мова> --custom_model <шлях_до_кастомної_моделі> --custom_config <шлях_до_кастомного_конфігу> --custom_vocab <шлях_до_кастомного_словника>
     ```

- **<ebook_file_path>**: Шлях до вашого файлу електронної книги.
- **<target_voice_file_path>**: Опційно для клонування голосу.
- **<language>**: Опційно для вказівки мови.
- **<custom_model_path>**: Шлях до `model.pth`.
- **<custom_config_path>**: Шлях до `config.json`.
- **<custom_vocab_path>**: Шлях до `vocab.json`.
- **[For More Parameters]**: використовуйте `--help` параметр ось так `python app.py --help`

### Для детальної інструкції з усіма параметрами
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.sh  --help
     ```
   - **Windows**
     ```bash
     .\ebook2audiobook.cmd  --help
     ```
<a id="help-command-output"></a>
- Виведе наступне:
```bash
usage: app.py [-h] [--script_mode SCRIPT_MODE] [--share] [-- []]
              [--session SESSION] [--ebook EBOOK] [--ebooks_dir [EBOOKS_DIR]]
              [--voice VOICE] [--language LANGUAGE] [--device {cpu,gpu}]
              [--custom_model CUSTOM_MODEL] [--temperature TEMPERATURE]
              [--length_penalty LENGTH_PENALTY]
              [--repetition_penalty REPETITION_PENALTY] [--top_k TOP_K] [--top_p TOP_P]
              [--speed SPEED] [--enable_text_splitting] [--fine_tuned FINE_TUNED]
              [--version]

Convert eBooks to Audiobooks using a Text-to-Speech model. You can either launch the Gradio interface or run the script in  mode for direct conversion.

options:
  -h, --help            show this help message and exit
  --script_mode SCRIPT_MODE
                        Force the script to run in NATIVE or DOCKER_UTILS
  --share               Enable a public shareable Gradio link. Default to False.
  -- []
                        Run in  mode. Default to True if the flag is present without a value, False otherwise.
  --session SESSION     Session to reconnect in case of interruption ( mode only)
  --ebook EBOOK         Path to the ebook file for conversion. Required in  mode.
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
    :
    ebook2audiobook.cmd -- --ebook 'path_to_ebook'
    Graphic Interface:
    ebook2audiobook.cmd
Linux/Mac:
    :
    ./ebook2audiobook.sh -- --ebook 'path_to_ebook'
    Graphic Interface:
    ./ebook2audiobook.sh


```

### Використання Docker

Ви також можете використовувати Docker для запуску конвертера eBook в аудіокнигу. Цей метод забезпечує консистентність між різними середовищами та спрощує налаштування.

#### Запуск контейнера Docker

Щоб запустити контейнер Docker і почати роботу з інтерфейсом Gradio, використовуйте наступну команду:

- Запуск з використанням лише CPU
```powershell
docker run -it --rm -p 7860:7860 --platform=linux/amd64 athomasson2/ebook2audiobook python app.py
```
 - Запуск з прискоренням за допомогою GPU (тільки для відеокарт Nvidia)
```powershell
docker run -it --rm --gpus all -p 7860:7860 --platform=linux/amd64 athomasson2/ebook2audiobook python app.py
```

#### Побудова Docker контейнера

- Ви можете побудувати образ Docker за допомогою наступної команди:
'''powershell
docker build --platform linux/amd64 -t athomasson2/ebook2audiobook .
'''

Ця команда запустить інтерфейс Gradio на порту 7860 (localhost:7860).
- Для додаткових опцій, таких як запуск Docker у режимі чи створення публічного посилання на Gradio, додайте параметр --help після app.py у команді запуску Docker.

## Розташування файлів Docker контейнера
Усі файли ebook2audiobook будуть знаходитися в основній директорії `/home/user/app/`.
Наприклад:
`tmp` = `/home/user/app/tmp`
`audiobooks` = `/home/user/app/audiobooks`

   
## Docker headless guide

Перш за все, виконайте команду для завантаження останньої версії контейнера:
```bash
docker pull athomasson2/ebook2audiobook
```

- Перед тим як запустити контейнер, вам потрібно створити директорію з назвою "input-folder" у вашій поточній директорії, яка буде з'єднана з контейнером. Саме тут ви можете помістити свої вхідні файли, щоб Docker міг їх побачити.
```bash
mkdir input-folder && mkdir Audiobooks
```

- У наведеній нижче команді замініть **YOUR_INPUT_FILE.TXT** на назву вашого вхідного файлу.

```bash
docker run -it --rm \
    -v $(pwd)/input-folder:/home/user/app/input_folder \
    -v $(pwd)/audiobooks:/home/user/app/audiobooks \
    --platform linux/amd64 \
    athomasson2/ebook2audiobook \
    python app.py --headless --ebook /input_folder/YOUR_INPUT_FILE.TXT
```

- І на цьому все! 

- Аудіокниги на виході будуть зберігатися в папці "Audiobooks", яка також буде знаходитися у вашій локальній директорії, де ви виконали цю команду Docker.


## Щоб отримати команду допомоги для інших параметрів, які має ця програма, ви можете виконати наступне

```bash
docker run -it --rm \
    --platform linux/amd64 \
    athomasson2/ebook2audiobook \
    python app.py --help

```


І це виведе наступне:

[Help command output](#help-command-output)

### Docker Compose

Цей проєкт використовує Docker Compose для локального запуску. Ви можете увімкнути або вимкнути підтримку GPU, встановивши значення `*gpu-enabled` або `*gpu-disabled` у файлі `docker-compose.yml`.

#### Кроки для запуску

1. **Клонуйте репозиторій** (якщо ви ще цього не зробили):
   ```bash
   git clone https://github.com/DrewThomasson/ebook2audiobook.git
   cd ebook2audiobook
   ```

2. **Увімкнення підтримки GPU (вимкнено за замовчуванням)**
  Для активації підтримки GPU, змініть файл `docker-compose.yml`, замінивши `*gpu-disabled` на `*gpu-enabled`.

3. **Запустіть сервіс:**
    ```bash
    docker-compose up -d
    ```

4. **Отримайте доступ до сервісу:**
Сервіс буде доступний за адресою http://localhost:7860.

#### New v2.0 Docker Web GUI Interface!
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Click to see images of Web GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## Оренда GPU
Не маєте потрібного обладнання для запуску або хочете орендувати GPU?
#### Ви можете дублювати простір на Hugging Face та орендувати GPU за приблизно $0.40 на годину.
[Huggingface Space Demo](#huggingface-space-demo)

#### Або ви можете спробувати використовувати Google Colab безкоштовно!
(Зверніть увагу, що він може вийти з ладу, якщо ви не взаємодієте з ним певний час).
[Free Google Colab](#free-google-colab)

## Загальні проблеми з Docker
- Docker зависає при завантаженні точно налаштованих моделей. (Це не трапляється на кожному комп'ютері, але деякі користувачі стикаються з цією проблемою)
Вимкнення панелі прогресу, здається, вирішує цю проблему, як обговорюється [тут у #191](https://github.com/DrewThomasson/ebook2audiobook/issues/191)
Приклад додавання цього виправлення до команди `docker run`
```Dockerfile
docker run -it --rm --gpus all -e HF_HUB_DISABLE_PROGRESS_BARS=1 -e HF_HUB_ENABLE_HF_TRANSFER=0 -p 7860:7860 --platform=linux/amd64 athomasson2/ebook2audiobook python app.py
```





## Точно налаштовані моделі TTS

Ви можете легко точно налаштувати власну модель XTTS за допомогою цього репозиторію
[xtts-finetune-webui](https://github.com/daswer123/xtts-finetune-webui)

Якщо ви хочете легко орендувати GPU, ви також можете дублювати цей простір на Hugging Face
[xtts-finetune-webui-space](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu)

Простір, який ви можете використовувати для очищення даних для навчання
[denoise-huggingface-space](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit)

### Колекція точно налаштованих моделей TTS

Щоб знайти нашу колекцію вже налаштованих моделей TTS, відвідайте [це посилання на Hugging Face](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)
Для створення кастомної моделі XTTS також буде потрібен референсний аудіокліп голосу.

## Демонстрації

Голос дощового дня

[Посилання на демонстрацію](https://github.com/user-attachments/assets/8486603c-38b1-43ce-9639-73757dfb1031)

Голос Девіда Аттенборо

[Посилання на демонстрацію](https://github.com/user-attachments/assets/47c846a7-9e51-4eb9-844a-7460402a20a8)


## Підтримувані формати eBook

- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`, `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`, `.snb`, `.cbc`, `.rb`, `.tcr`
- **Найкращі результати**: `.epub` або `.mobi` для автоматичного виявлення розділів

## Вихідні дані

- Створює файл `.m4b` з метаданими та розділами.
- **Приклад виходу**: ![Приклад](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)

## Типові проблеми:
- "Це повільно!" - На процесорі (CPU) це дуже повільно, і прискорення можливе лише за допомогою графічних карт NVIDIA. [Обговорення про це](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846). Для швидшого мультимовного генерування я б порадив мій інший [проєкт, який використовує piper-tts](https://github.com/DrewThomasson/ebook2audiobookpiper-tts) (але він не має клонування голосу без навчання, і голоси мають якість Сірі, але працює набагато швидше на процесорі).
- "Маю проблеми з залежностями" - Просто використовуйте Docker, він повністю самодостатній і має безголовий режим, додайте параметр `-h` після `app.py` у команді запуску Docker для додаткової інформації.
- "Отримую проблему з обрізаним аудіо!" - БУДЬ ЛАСКА, СТВОРІТЬ ПИТАННЯ З ЦИМ, я не розумію кожну мову, і мені потрібно отримати поради від кожної людини для доопрацювання моєї функції розбиття речень на інші мови.😊


## Чим мені потрібна допомога! 🙌 
## [Повний список можна знайти тут](https://github.com/DrewThomasson/ebook2audiobook/issues/32)
- Будь-яка допомога від людей, які говорять на будь-яких підтримуваних мовах, для допомоги в налаштуванні методів розбиття речень.
- Можливо, створення посібників README для кількох мов (тому що єдина мова, яку я знаю, - це англійська 😔)

## Спеціальні подяки

- **Coqui TTS**: [Coqui TTS GitHub](https://github.com/idiap/coqui-ai-TTS)
- **Calibre**: [Calibre Website](https://calibre-ebook.com)
- **FFmpeg**: [FFmpeg Website](https://ffmpeg.org)

- [@shakenbake15 for better chapter saving method](https://github.com/DrewThomasson/ebook2audiobook/issues/8) 

### [Legacy V1.0](legacy/v1.0)

You can view the code [here](legacy/v1.0).

## Join Our Discord Server!

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/bg5Kx43c6w)](https://discord.gg/bg5Kx43c6w)
