# 📚 ebook2audiobook

مبدل CPU/GPU برای تبدیل کتاب‌های الکترونیکی به کتاب‌های صوتی همراه با فصول و اطلاعات متاداده
با استفاده از Calibre، ffmpeg، XTTSv2، Fairseq و دیگر ابزارها.
پشتیبانی از کپی‌برداری صدا از ۱۱۲۴ زبان!
> [!IMPORTANT]
**این ابزار فقط برای کتاب‌های الکترونیکی که غیر DRM هستند و به طور قانونی خریداری شده اند است.** <br>
سازندگان هیچ مسئولیتی در قبال استفاده نادرست ندارند.<br>
از این ابزار به طور مسئولانه و مطابق با تمام قوانین مربوطه استفاده کنید.


[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/bg5Kx43c6w)](https://discord.gg/bg5Kx43c6w)

از توسعه‌دهندگان ebook2audiobook حمایت کنید!<br>
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 


#### رابط کاربری وب جدید نسخه 2.0!
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>برای دیدن رابط کاربری جدید کلیک کنید</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>


## README.md
- ara [العربية (Arabic)](./readme/README_AR.md)
- zho [中文 (Chinese)](./readme/README_CN.md)
- eng [English](README.md)
- swe [Svenska (Swedish)](./readme/README_SWE.md)
- far [فارسی (persian)](./readme/README_FA.md)
## Table of Contents

- [اصلی](#ebook2audiobook)
- [ویژگی ها](#features)
- [رابط کاربری وب جدید نسخه 2.0](#new-v20-web-gui-interface)
- [Huggingface فصای نمونه](#huggingface-space-demo)
- [رایگان Google Colab](#free-google-colab)
- [نمونه‌های صوتی ازپیش ایجاد شده](#demos)
- [زبان های پشتیبانی شده](#supported-languages)
- [پیشنیاز ها](#requirements)
- [دستور‌العمل‌های نصب](#installation-instructions)
- [استفاده](#usage)
  - [راه‌اندازی رابط کاربری وب Gradio](#launching-gradio-web-interface)
  - [استفاده بدون رابط گرافیکی](#basic-headless-usage)
  - [استفاده از مدل سفارشی XTTS بدون رابط گرافیکی](#headless-custom-xtts-model-usage)
  - [اجاره GPU](#renting-a-gpu)
  - [خروجی دستور کمکی](#help-command-output)
- [مدل های TTS به دقت تنظیم شده](#fine-tuned-tts-models)
  - [برای مجموعه مدل‌های TTS به دقت تنظیم شده](#fine-tuned-tts-collection)
- [استفاده از Docker](#using-docker)
  - [Docker Run](#running-the-docker-container)
  - [Docker Build](#building-the-docker-container)
  - [Docker Compose](#docker-compose)
  - [Docker headless guide](#docker-headless-guide)
  - [Docker container file locations](#docker-container-file-locations)
  - [Common Docker issues](#common-docker-issues)
- [فرمت‌های پشتیبانی‌شده کتاب الکترونیکی](#supported-ebook-formats)
- [خروجی](#output)
- [مشکلات رایج](#common-issues)
- [تشکرات ویژه](#special-thanks)
- [ملحق شده به سرور دیسکورد !](#join-our-discord-server)
- [میراث](#legacy-v10)
- [واژه‌نامه بخش ها](#glossary-of-sections)

## Features

- 📖 تبدیل کردن کتاب الکترونیک به متن با Calibre.
- 📚 تقسیم کردن کتاب الکترونیک به فصل ها برای صدای سازمان یافته .
- 🎙️ تبدیل گفتار به متن با کیفیت بالا همراه با [Coqui XTTSv2](https://huggingface.co/coqui/XTTS-v2) و [Fairseq](https://github.com/facebookresearch/fairseq/tree/main/examples/mms).
- 🗣️ همزاد سازی صدای اختیاری همراه با صدای خودتان.
- 🌍 پشتیبانی از 1124 زبان (English by default). [List of Supported languages](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
- 🖥️ طراحی شده تا اجرابشود با 4GB RAM.

## [Huggingface space demo](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)

- فضای Huggingface بر روی لایه پردازنده رایگان اجرا می‌شود، بنابراین انتظار داشته باشید که بسیار کند یا با تایم‌اوت مواجه شوید، فقط کافی است که فایل‌های خیلی بزرگ ارسال نکنید!

- بهترین کار این است که فضای مورد نظر را تکثیر کنید یا به صورت محلی اجرا کنید..

## Free Google Colab 
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb)

## Supported Languages

- **Arabic (ara)**
- **Chinese (zho)**
- **Czech (ces)**
- **Dutch (nld)**
- **English (eng)**
- **French (fra)**
- **German (deu)**
- **Hindi (hin)**
- **Hungarian (hun)**
- **Italian (ita)**
- **Japanese (jpn)**
- **Korean (kor)**
- **Polish (pol)**
- **Portuguese (por)**
- **Russian (rus)**
- **Spanish (spa)**
- **Turkish (tur)**
- **Vietnamese (vie)**
- [** + 1124 languages via Fairseq**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)


##  Requirements

- 4GB ram
- مجازی‌سازی فعال است اگر بر روی ویندوز اجرا شود (فقط Docker).

> [!IMPORTANT]
**قبل از ارسال مشکل نصب یا باگ، به دقت در تب مسائل باز و بسته شده جستجو کنید.<br>
تا مطمئن شوید که این گزارش درحال حاضر وجود ندارد.**

### Installation Instructions

1. **همزاد سازی کردن مخزن**
```bash
git clone https://github.com/DrewThomasson/ebook2audiobook.git
```

کد زبان خود را در هنگام اجرای برنامه مشخص کنید.

### Launching Gradio Web Interface

1. **اجرای ebook2audiobook**:
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.sh  # Run Launch script
     ```
   - **Windows**
     ```bash
     .\ebook2audiobook.cmd  # Run launch script or double click on it
     ```
2. **برنامه وب را باز کنید**: برای دسترسی به برنامه وب و تبدیل کتاب‌های الکترونیکی، روی آدرس URL ارائه‌شده در ترمینال کلیک کنید.
3. **برای لینک عمومی**: `--share `را به انتهای آن اضافه کنید به این صورت: `python app.py --share`
- **[برای پارامتر های بیشتر]**:از پارامتر `--help` به این صورت استفاده کنید: `python app.py --help`
### Basic  Usage
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.sh  -- --ebook <path_to_ebook_file> --voice [path_to_voice_file] --language [language_code]
     ```
   - **Windows**
     ```bash
     .\ebook2audiobook.cmd  -- --ebook <path_to_ebook_file> --voice [path_to_voice_file] --language [language_code]
     ```

- **<path_to_ebook_file>**: محل قرارگیری کتاب الکترونیک.
- **[path_to_voice_file]**: همزاد سازی صدای خود‌(اختیاری).
- **[language_code]**: اختیاری است که کد زبان سه حرفی ISO-639-3 را مشخص کنید (کد پیش‌فرض "eng" است). کد دو حرفی ISO-639-1 نیز پشتیبانی می‌شود.
- **[For More Parameters]**:در صورت نیاز از `--help` استفاده کنید. مانند `python app.py --help`

###  Custom XTTS Model Usage
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.sh  -- --ebook <ebook_file_path> --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path> --custom_config <custom_config_path> --custom_vocab <custom_vocab_path>
     ```
   - **Windows**
     ```bash
     .\ebook2audiobook.cmd  -- --ebook <ebook_file_path> --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path> --custom_config <custom_config_path> --custom_vocab <custom_vocab_path>
     ```

- **<ebook_file_path>**: محل پرونده کتاب الکترونیک.
- **<target_voice_file_path>**: همزاد سازی صدا (اختیاری).
- **<language>**: مشخص کردن زبان‌(اختیاری).
- **<custom_model_path>**: مسیر فایل`model.pth`.
- **<custom_config_path>**: مسیر فایل `config.json`.
- **<custom_vocab_path>**: مسیر فایل `vocab.json`.
- **[For More Parame]**: use the `--help` parameter like this `python app.py --help`

### For Detailed Guide with list of all Parameters to use
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.sh  --help
     ```
   - **Windows**
     ```bash
     .\ebook2audiobook.cmd  --help
     ```
<a id="help-command-output"></a>
- این خروجی‌اش خواهد بود:
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

### Using Docker

همچنین شما میتوانید از Docker برای اجرای ebook2audiobook استفاده کنید. این روش تضمین می‌کند که در محیط‌های مختلف ثبات وجود داشته باشد و راه‌اندازی را ساده‌تر می‌کند.

#### Running the Docker Container

برای اجرای کانتینر Docker و راه‌اندازی رابط Gradio، از دستور زیر استفاده کنید:

 -اجرا فقط با استفاده از CPU
```powershell
docker run -it --rm -p 7860:7860 --platform=linux/amd64 athomasson2/ebook2audiobook python app.py
```
 -اجرا با استفاده از GPU (فقط کارت گرافیک های Nvidia)
```powershell
docker run -it --rm --gpus all -p 7860:7860 --platform=linux/amd64 athomasson2/ebook2audiobook python app.py
```

#### Building the Docker Container

- شما میتوناید با استفاده از دستور زیر یک نگه دارنده docker بسازید:
'''powershell
docker build --platform linux/amd64 -t athomasson2/ebook2audiobook .
'''

این دستور رابط کاربری Gradio  را در پورت 7860 اجرا می‌کند. (localhost:7860)
- برای گزینه‌های بیشتر مانند اجرای Docker در حالت یا عمومی کردن لینک Gradio، پارامتر `--help` را بعد از `app.py` در دستور راه‌اندازی Docker اضافه کنید.

## Docker container file locations
   تمام فایل های ebook2audio در سر‌پوشه  `/home/user/app/` قرار دارند.
برای مثال :
`tmp` = `/home/user/app/tmp`
`audiobooks` = `/home/user/app/audiobooks`

   
## Docker headless guide

اول برای دریافت docker pull را وارد کنید.
```bash 
docker pull athomasson2/ebook2audiobook
```

- قبل از اینکه این را اجرا کنید، باید یک پوشه به نام "input-folder" در دایرکتوری فعلی خود ایجاد کنید که به آن لینک خواهد شد. اینجا جایی است که می‌توانید فایل‌های ورودی خود را برای مشاهده توسط تصویر Docker قرار دهید.
```bash
mkdir input-folder && mkdir Audiobooks
```

- در دستور زیر **YOUR_INPUT_FILE.TXT** را با نام فایل ورودی خود جایگزین کنید. 

```bash
docker run -it --rm \
    -v $(pwd)/input-folder:/home/user/app/input_folder \
    -v $(pwd)/audiobooks:/home/user/app/audiobooks \
    --platform linux/amd64 \
    athomasson2/ebook2audiobook \
    python app.py --headless --ebook /input_folder/YOUR_INPUT_FILE.TXT
```

-و این باید تمامش باشد!

- خروجی کتاب‌های صوتی در پوشه Audiobook پیدا خواهد شد که همچنین در دایرکتوری محلی که این دستور Docker را در آن اجرا کردید، قرار دارد.


## برای دریافت دستور کمک برای سایر پارامترهایی که این برنامه دارد، می‌توانید این را اجرا کنید.

```bash
docker run -it --rm \
    --platform linux/amd64 \
    athomasson2/ebook2audiobook \
    python app.py --help

```


و این خروجی زیر را تولید خواهد کرد.
[Help command output](#help-command-output)

### Docker Compose

این پروژه از Docker Compose برای اجرای محلی استفاده می‌کند. می‌توانید با تنظیم `*gpu-enabled` یا `*gpu-disabled` در `docker-compose.yml` از پشتیبانی GPU استفاده کنید یا آن را غیرفعال کنید.

#### Steps to Run

1. **Clone the Repository** (if you haven't already):
   ```bash
   git clone https://github.com/DrewThomasson/ebook2audiobook.git
   cd ebook2audiobook
   ```

2. **Set GPU Support (disabled by default)**
  برای فعال‌سازی پشتیبانی GPU، فایل `docker-compose.yml` را ویرایش کرده و `*gpu-disabled` را به `*gpu-enabled` تغییر دهید.

3. **Start the service:**
    ```bash
    docker-compose up -d
    ```

4. **Access the service:**
  این سرویس در آدرس http://localhost:7860 در دسترس خواهد بود.

#### New v2.0 Docker Web GUI Interface!
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>برای مشاهده تصاویر رابط کاربری وب کلیک کنید.</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## Renting a GPU
آیا سخت‌افزار لازم برای اجرای آن را ندارید یا می‌خواهید یک GPU اجاره کنید؟
#### شما می‌توانید فضای Hugging Face را کپی کنید و یک GPU را به قیمت حدود ۰.۴۰ دلار در ساعت اجاره کنید.
[Huggingface Space Demo](#huggingface-space-demo)

#### یا می‌توانید از Google Colab به صورت رایگان استفاده کنید!
(به یاد داشته باشید که اگر با Google Colab کاری نکنید، بعد از مدتی زمان آن به پایان می‌رسد.)
[Free Google Colab](#free-google-colab)

## Common Docker Issues
- Docker در حین دانلود مدل‌های Fine-Tuned گیر می‌کند. (این مشکل برای هر کامپیوتری پیش نمی‌آید، اما برخی به این مشکل برخورد می‌کنند)  
غیرفعال کردن نوار پیشرفت به نظر می‌رسد که این مشکل را حل می‌کند، همانطور که در [اینجا در #191](https://github.com/DrewThomasson/ebook2audiobook/issues/191) بحث شده است.  
مثالی از افزودن این اصلاح در دستور `docker run`
```Dockerfile
docker run -it --rm --gpus all -e HF_HUB_DISABLE_PROGRESS_BARS=1 -e HF_HUB_ENABLE_HF_TRANSFER=0 -p 7860:7860 --platform=linux/amd64 athomasson2/ebook2audiobook python app.py
```





## Fine Tuned TTS models

شما می‌توانید به راحتی مدل xtts خود را با این مخزن (repo) تنظیم دقیق کنید.
[xtts-finetune-webui](https://github.com/daswer123/xtts-finetune-webui)

اگر می‌خواهید به راحتی یک GPU اجاره کنید، می‌توانید این Hugging Face را نیز کپی کنید.
[xtts-finetune-webui-space](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu)
فضایی که می‌توانید برای کاهش نویز داده‌های آموزشی به راحتی استفاده کنید نیز وجود دارد.
[denoise-huggingface-space](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit)

### Fine Tuned TTS Collection

برای پیدا کردن مجموعه‌ای از مدل‌های TTS که قبلاً تنظیم دقیق شده‌اند، به [این لینک Hugging Face](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main) مراجعه کنید.  
برای یک مدل XTTS سفارشی، همچنین به یک کلیپ صوتی مرجع از صدا نیاز خواهد بود:
## Demos

Rainy day صدای

https://github.com/user-attachments/assets/8486603c-38b1-43ce-9639-73757dfb1031

David Attenborough صدای

https://github.com/user-attachments/assets/47c846a7-9e51-4eb9-844a-7460402a20a8


## Supported eBook Formats

- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`, `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`, `.snb`, `.cbc`, `.rb`, `.tcr`
- **بهترین نتایج**: `.epub` یا `.mobi` برای تشخیص خودکار فصل‌ها

## Output

- فایلی با فرمت `.m4b` با متادیتا و فصل‌ها ایجاد می‌کند.
- **خروجی مثال**: ![مثال](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)

## Common Issues:
-"این کند است!" - فقط در CPU این بسیار کند است و تنها می‌توانید با یک GPU NVIDIA سرعت را افزایش دهید. [بحث در مورد این موضوع](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846) برای تولید چندزبانه سریع‌تر، من پروژه دیگری که از piper-tts استفاده می‌کند را پیشنهاد می‌کنم [این پروژه](https://github.com/DrewThomasson/ebook2audiobookpiper-tts) به جای آن. (این پروژه قابلیت کلونینگ صدای بدون نمونه را ندارد، و صداها کیفیت سیری دارند، اما در CPU بسیار سریع‌تر است.)
-"من با مشکلات وابستگی مواجه هستم" - فقط از Docker استفاده کنید، این کاملاً مستقل است و حالت بدون سر دارد. پارامتر `-h` را بعد از `app.py` در دستور اجرای Docker اضافه کنید برای اطلاعات بیشتر.
- "من با مشکل صدای بریده شده مواجه هستم!" - لطفاً یک مشکل (Issue) در این مورد ایجاد کنید، من به هر زبانی صحبت نمی‌کنم و به مشاوره از هر شخص نیاز دارم تا تابع تقسیم جملات خود را در زبان‌های دیگر تنظیم دقیق کنم. 😊
## What I need help with! 🙌 
## [فهرست کامل موارد را می‌توانید در اینجا پیدا کنید.](https://github.com/DrewThomasson/ebook2audiobook/issues/32)
- هر کمکی از افرادی که به یکی از زبان‌های پشتیبانی شده صحبت می‌کنند برای کمک به روش‌های صحیح تقسیم جملات مورد نیاز است.
- امکان ایجاد راهنماهای README برای چندین زبان وجود دارد.

## Special Thanks

- **Coqui TTS**: [Coqui TTS GitHub](https://github.com/idiap/coqui-ai-TTS)
- **Calibre**: [Calibre Website](https://calibre-ebook.com)
- **FFmpeg**: [FFmpeg Website](https://ffmpeg.org)

- [@shakenbake15 برای روش بهتر ذخیره‌سازی فصل‌ها](https://github.com/DrewThomasson/ebook2audiobook/issues/8) 

### [Legacy V1.0](legacy/v1.0)

شما می‌توانید کد را [اینجا](legacy/v1.0) مشاهده کنید.

## Join Our Discord Server!

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/bg5Kx43c6w)](https://discord.gg/bg5Kx43c6w)
