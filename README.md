# 📚 ebook2audiobook

CPU/GPU Converter from eBooks to audiobooks with chapters and metadata<br/>
using Calibre, ffmpeg, XTTSv2, Fairseq and more. Supports voice cloning and 1124 languages!
> [!IMPORTANT]
**This tool is intended for use with non-DRM, legally acquired eBooks only.** <br>
The authors are not responsible for any misuse of this software or any resulting legal consequences. <br>
Use this tool responsibly and in accordance with all applicable laws.


[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

Thanks to support ebook2audiobook developers!<br>
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 


#### New v2.0 Web GUI Interface!
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Click to see images of Web GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>


## README.md
- ara [العربية (Arabic)](./readme/README_AR.md)
- zho [中文 (Chinese)](./readme/README_CN.md)
- eng [English](README.md)
- swe [Svenska (Swedish)](./readme/README_SWE.md)
- fas [فارسی (Persian)](./readme/README_FA.md)

## Table of Contents

- [ebook2audiobook](#ebook2audiobook)
- [Features](#features)
- [New v2.0 Web GUI Interface](#new-v20-web-gui-interface)
- [Huggingface Space Demo](#huggingface-space-demo)
- [Free Google Colab](#free-google-colab)
- [Pre-made Audio Demos](#demos)
- [Supported Languages](#supported-languages)
- [Requirements](#requirements)
- [Installation Instructions](#installation-instructions)
- [Usage](#usage)
  - [Launching Gradio Web Interface](#launching-gradio-web-interface)
  - [Basic Headless Usage](#basic-headless-usage)
  - [Headless Custom XTTS Model Usage](#headless-custom-xtts-model-usage)
  - [Renting a GPU](#renting-a-gpu)
  - [Help command output](#help-command-output)
- [Fine Tuned TTS models](#fine-tuned-tts-models)
  - [For Collection of Fine-Tuned TTS Models](#fine-tuned-tts-collection)
- [Using Docker](#using-docker)
  - [Docker Run](#running-the-docker-container)
  - [Docker Build](#building-the-docker-container)
  - [Docker Compose](#docker-compose)
  - [Docker headless guide](#docker-headless-guide)
  - [Docker container file locations](#docker-container-file-locations)
  - [Common Docker issues](#common-docker-issues)
- [Supported eBook Formats](#supported-ebook-formats)
- [Output](#output)
- [Common Issues](#common-issues)
- [Special Thanks](#special-thanks)
- [Join Our  Server!](#join-our--server)
- [Legacy](#legacy-v10)
- [Glossary of Sections](#glossary-of-sections)

## Features

- 📖 Converts eBooks to text format with Calibre.
- 📚 Splits eBook into chapters for organized audio.
- 🎙️ High-quality text-to-speech with [Coqui XTTSv2](https://huggingface.co/coqui/XTTS-v2) and [Fairseq](https://github.com/facebookresearch/fairseq/tree/main/examples/mms).
- 🗣️ Optional voice cloning with your own voice file.
- 🌍 Supports 1107 languages (English by default). [List of Supported languages](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
- 🖥️ Designed to run on 4GB RAM.

## [Huggingface space demo](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)

- Huggingface space is running on free cpu tier so expect very slow or timeout lol, just don't give it giant files is all
- Best to duplicate space or run locally.

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
- [** + 1107 languages via Fairseq**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)


##  Requirements

- 4gb ram
- Virtualization enabled if running on windows (Docker only)

> [!IMPORTANT]
**Before to post an install or bug issue search carefully to the opened and closed issues TAB<br>
to be sure your issue does not exist already.**

### Installation Instructions

1. **Clone repo**
```bash
git clone https://github.com/DrewThomasson/ebook2audiobook.git
```

Specify the language code when running the script in  mode.


### Launching Gradio Web Interface

1. **Run ebook2audiobook**:
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.sh  # Run Launch script
     ```
   - **Windows**
     ```bash
     .\ebook2audiobook.cmd  # Run launch script or double click on it
     ```
2. **Open the Web App**: Click the URL provided in the terminal to access the web app and convert eBooks.
3. **For Public Link**: Add `--share` to the end of it like this: `python app.py --share`
- **[For More Parameters]**: use the `--help` parameter like this `python app.py --help`

### Basic  Usage
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.sh  -- --ebook <path_to_ebook_file> --voice [path_to_voice_file] --language [language_code]
     ```
   - **Windows**
     ```bash
     .\ebook2audiobook.cmd  -- --ebook <path_to_ebook_file> --voice [path_to_voice_file] --language [language_code]
     ```

- **<path_to_ebook_file>**: Path to your eBook file.
- **[path_to_voice_file]**: Optional for voice cloning.
- **[language_code]**: Optional to specify ISO-639-3 3+ letters language code (default is eng). ISO-639-1 2 letters code is also supported
- **[For More Parameters]**: use the `--help` parameter like this `python app.py --help`

###  Custom XTTS Model Usage
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.sh  -- --ebook <ebook_file_path> --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path> --custom_config <custom_config_path> --custom_vocab <custom_vocab_path>
     ```
   - **Windows**
     ```bash
     .\ebook2audiobook.cmd  -- --ebook <ebook_file_path> --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path> --custom_config <custom_config_path> --custom_vocab <custom_vocab_path>
     ```

- **<ebook_file_path>**: Path to your eBook file.
- **<target_voice_file_path>**: Optional for voice cloning.
- **<language>**: Optional to specify language.
- **<custom_model_path>**: Path to `model.pth`.
- **<custom_config_path>**: Path to `config.json`.
- **<custom_vocab_path>**: Path to `vocab.json`.
- **[For More Parameters]**: use the `--help` parameter like this `python app.py --help`

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
- This will output the following:
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

You can also use Docker to run the eBook to Audiobook converter. This method ensures consistency across different environments and simplifies setup.

#### Running the Docker Container

To run the Docker container and start the Gradio interface, use the following command:

 -Run with CPU only
```powershell
docker run -it --rm -p 7860:7860 --platform=linux/amd64 athomasson2/ebook2audiobook python app.py
```
 -Run with GPU Speedup (Nvida graphics cards only)
```powershell
docker run -it --rm --gpus all -p 7860:7860 --platform=linux/amd64 athomasson2/ebook2audiobook python app.py
```

#### Building the Docker Container

- You can build the docker image with the command:
'''powershell
docker build --platform linux/amd64 -t athomasson2/ebook2audiobook .
'''

This command will start the Gradio interface on port 7860.(localhost:7860)
- For more options like running the docker in  mode or making the gradio link public add the `--help` parameter after the `app.py` in the docker launch command

## Docker container file locations
All ebook2audiobooks will have the base dir of `/home/user/app/`
For example:
`tmp` = `/home/user/app/tmp`
`audiobooks` = `/home/user/app/audiobooks`

   
## Docker headless guide

first for a docker pull of the latest with
```bash 
docker pull athomasson2/ebook2audiobook
```

- Before you do run this you need to create a dir named "input-folder" in your current dir which will be linked, This is where you can put your input files for the docker image to see
```bash
mkdir input-folder && mkdir Audiobooks
```

- In the command below swap out **YOUR_INPUT_FILE.TXT** with the name of your input file 

```bash
docker run -it --rm \
    -v $(pwd)/input-folder:/home/user/app/input_folder \
    -v $(pwd)/audiobooks:/home/user/app/audiobooks \
    --platform linux/amd64 \
    athomasson2/ebook2audiobook \
    python app.py --headless --ebook /input_folder/YOUR_INPUT_FILE.TXT
```

- And that should be it! 

- The output Audiobooks will be found in the Audiobook folder which will also be located in your local dir you ran this docker command in


## To get the help command for the other parameters this program has you can run this 

```bash
docker run -it --rm \
    --platform linux/amd64 \
    athomasson2/ebook2audiobook \
    python app.py --help

```


and that will output this 

[Help command output](#help-command-output)

### Docker Compose

This project uses Docker Compose to run locally. You can enable or disable GPU support by setting either `*gpu-enabled` or `*gpu-disabled` in `docker-compose.yml`

#### Steps to Run

1. **Clone the Repository** (if you haven't already):
   ```bash
   git clone https://github.com/DrewThomasson/ebook2audiobook.git
   cd ebook2audiobook
   ```

2. **Set GPU Support (disabled by default)**
  To enable GPU support, modify `docker-compose.yml` and change `*gpu-disabled` to `*gpu-enabled`

3. **Start the service:**
    ```bash
    docker-compose up -d
    ```

4. **Access the service:**
  The service will be available at http://localhost:7860.

#### New v2.0 Docker Web GUI Interface!
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Click to see images of Web GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## Renting a GPU
Don't have the hardware to run it or you want to rent a GPU?
#### You can duplicate the hugginface space and rent a gpu for around $0.40 an hour
[Huggingface Space Demo](#huggingface-space-demo)

#### Or you can try using the google colab for free!
(Be aware it will time out after a bit of your not messing with the google colab)
[Free Google Colab](#free-google-colab)

## Common Docker Issues
- Docker gets stuck downloading Fine-Tuned models. (This does not happen for every computer but some appear to run into this issue)
Disabling the progress bar appears to fix the issue, as discussed [here in #191](https://github.com/DrewThomasson/ebook2audiobook/issues/191)
Example of adding this fix in the `docker run` command
```Dockerfile
docker run -it --rm --gpus all -e HF_HUB_DISABLE_PROGRESS_BARS=1 -e HF_HUB_ENABLE_HF_TRANSFER=0 -p 7860:7860 --platform=linux/amd64 athomasson2/ebook2audiobook python app.py
```





## Fine Tuned TTS models

You can fine-tune your own xtts model easily with this repo
[xtts-finetune-webui](https://github.com/daswer123/xtts-finetune-webui)

If you want to rent a GPU easily you can also duplicate this huggingface
[xtts-finetune-webui-space](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu)

A space you can use to de-noise the training data easily also
[denoise-huggingface-space](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit)

### Fine Tuned TTS Collection

To find our collection of already fine-tuned TTS models, visit [this Hugging Face link](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)
For an XTTS custom model a ref audio clip of the voice will also be needed:

## Demos

Rainy day voice

https://github.com/user-attachments/assets/8486603c-38b1-43ce-9639-73757dfb1031

David Attenborough voice

https://github.com/user-attachments/assets/47c846a7-9e51-4eb9-844a-7460402a20a8


## Supported eBook Formats

- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`, `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`, `.snb`, `.cbc`, `.rb`, `.tcr`
- **Best results**: `.epub` or `.mobi` for automatic chapter detection

## Output

- Creates an `.m4b` file with metadata and chapters.
- **Example Output**: ![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)

## Common Issues:
- "It's slow!" - On CPU only this is very slow, and you can only get speedups though a NVIDIA GPU. [Discussion about this](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846) For faster multilingual generation I would suggest my other [project that uses piper-tts](https://github.com/DrewThomasson/ebook2audiobookpiper-tts) instead(It doesn't have zero-shot voice cloning though, and is siri quality voices, but it is much faster on cpu.)
- "I'm having dependency issues" - Just use the docker, its fully self contained and has a headless mode, add `-h` parameter after the `app.py` in the docker run command for more information.
- "Im getting a truncated audio issue!" - PLEASE MAKE AN ISSUE OF THIS, I don't speak every language and I need advise from each person to fine tune my sentense splitting function on any other languages.😊

## What I need help with! 🙌 
## [Full list of things can be found here](https://github.com/DrewThomasson/ebook2audiobook/issues/32)
- Any help from people speaking any of the supported languages to help with proper sentence splitting methods
- Potentially creating readme Guides for Multiple languages(Becuase the only language I know is English 😔)

## Special Thanks

- **Coqui TTS**: [Coqui TTS GitHub](https://github.com/idiap/coqui-ai-TTS)
- **Calibre**: [Calibre Website](https://calibre-ebook.com)
- **FFmpeg**: [FFmpeg Website](https://ffmpeg.org)

- [@shakenbake15 for better chapter saving method](https://github.com/DrewThomasson/ebook2audiobook/issues/8) 

### [Legacy V1.0](legacy/v1.0)

You can view the code [here](legacy/v1.0).

## Join Our  Server!

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)
