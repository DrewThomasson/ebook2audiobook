# 📚 ebook2audiobook

从eBooks到有章节和元数据的音频书籍的CPU/GPU转换器<br/>
使用Calibre、ffmpeg、XTTSv2、Fairseq等。支持语音克隆和1124种语言！
> [!IMPORTANT]
> **此工具仅适用于非DRM、合法获取的eBooks。** <br>
> 作者不对任何滥用此软件或由此产生的法律后果负责。<br>
> 请负责任地使用此工具，并遵守所有适用的法律。


[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/bg5Kx43c6w)](https://discord.gg/bg5Kx43c6w)

感谢支持ebook2audiobook的开发者！<br>
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 


#### 新v2.0 Web GUI界面！
![demo_web_gui](../assets/demo_web_gui.gif)

<details>
  <summary>点击查看Web GUI的图片</summary>
  <img width="1728" alt="GUI Screen 1" src="../assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="../assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="../assets/gui_3.png">
</details>


## README.md
- ara [العربية (Arabic)](./readme/README_AR.md)
- eng [English](README.md)
- swe [Svenska (Swedish)](./readme/README_SWE.md)

## 目录

- [ebook2audiobook](#-ebook2audiobook)
- [功能](#功能)
- [Huggingface Space Demo](#hugging-face-space-演示)
- [免费Google Colab](#免费google-colab)
- [演示](#演示)
- [支持的语言](#支持的语言)
- [要求](#要求)
- [安装说明](#安装说明)
- [使用](#使用)
  - [启动Gradio Web界面](#启动gradio-web界面)
  - [基本用法](#基本用法)
  - [使用自定义XTTS模型](#使用自定义xtts模型)
  - [租用GPU](#租用gpu)
  - [详细指南，列出所有参数](#详细指南列出所有参数)
- [Fine Tuned TTS模型](#fine-tuned-tts模型)
  - [Fine Tuned TTS模型集合](#fine-tuned-tts模型集合)
- [使用Docker](#使用docker)
  - [运行Docker容器](#运行docker容器)
  - [构建Docker容器](#构建docker容器)
  - [Docker Compose](#docker-compose)
  - [Docker无头指南](#docker无头指南)
  - [Docker容器文件位置](#docker容器文件位置)
  - [常见Docker问题](#常见docker问题)
- [支持的电子书格式](#支持的电子书格式)
- [输出](#输出)
- [常见问题](#常见问题)
- [特别感谢](#特别感谢)
- [加入我们的Discord服务器！](#加入我们的discord服务器)
- [Legacy](#legacy-v10)

## 功能

- 📖 使用Calibre将eBooks转换为文本格式。
- 📚 将eBooks拆分为章节，以组织音频。
- 🎙️ 使用[Coqui XTTSv2](https://huggingface.co/coqui/XTTS-v2)和[Fairseq](https://github.com/facebookresearch/fairseq/tree/main/examples/mms)的高质量文本转语音。
- 🗣️ 可选的语音克隆，使用你自己的语音文件。
- 🌍 支持1107种语言（默认是英语）。[支持的语言列表](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
- 🖥️ 设计为在4GB RAM上运行。

## [Huggingface space演示](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)

- Huggingface space在免费cpu层上运行，所以预计会很慢或超时，只需不要给它太大的文件。
- 最好复制空间或本地运行。

## 免费Google Colab
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb)

## 支持的语言

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
- **[ + 1107 languages via Fairseq](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)**


## 要求

- 4gb ram
- 如果运行在windows上，则启用虚拟化（仅限Docker）

> [!IMPORTANT]
> **在发布安装或错误问题之前，仔细搜索已打开和已关闭的问题选项卡<br>
> 以确保你的问题不存在。**

### 安装说明

1. **克隆仓库**
```bash
git clone https://github.com/DrewThomasson/ebook2audiobook.git
```

在命令行下运行脚本时指定语言代码。


### 启动Gradio Web界面

1. **运行ebook2audiobook**:
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.sh  # 运行启动脚本
     ```
   - **Windows**
     ```bash
     .\ebook2audiobook.cmd  # 运行启动脚本或双击它
     ```
2. **打开Web App**: 点击终端中提供的URL访问Web App并转换eBooks。
3. **公开链接**: 在末尾添加 `--share` 像这样: `python app.py --share`
- **[更多参数]**: 使用 `--help` 参数像这样: `python app.py --help`

### 基本用法
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.sh  -- --ebook <path_to_ebook_file> --voice [path_to_voice_file] --language [language_code]
     ```
   - **Windows**
     ```bash
     .\ebook2audiobook.cmd  -- --ebook <path_to_ebook_file> --voice [path_to_voice_file] --language [language_code]
     ```

- **<path_to_ebook_file>**: 你的eBook文件路径。
- **[path_to_voice_file]**: 指定转换的语音文件，可选。
- **[language_code]**: 可选指定ISO-639-3 3+字母语言代码（默认是eng）。ISO-639-1 2字母代码也支持
- **[更多参数]**: 使用 `--help` 参数像这样: `python app.py --help`

### 使用自定义XTTS模型
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.sh  -- --ebook <ebook_file_path> --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path> --custom_config <custom_config_path> --custom_vocab <custom_vocab_path>
     ```
   - **Windows**
     ```bash
     .\ebook2audiobook.cmd  -- --ebook <ebook_file_path> --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path> --custom_config <custom_config_path> --custom_vocab <custom_vocab_path>
     ```

- **<ebook_file_path>**: 你的eBook文件路径。
- **<target_voice_file_path>**: 指定转换的语音文件，可选。
- **<language>**: 指定语言，可选。
- **<custom_model_path>**: 指定`model.pth`文件路径。
- **<custom_config_path>**: 指定`config.json`文件路径。
- **<custom_vocab_path>**: 指定`vocab.json`文件路径。
- **[更多参数]**: 使用 `--help` 参数像这样: `python app.py --help`

### 详细指南，列出所有参数
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.sh  --help
     ```
   - **Windows**
     ```bash
     .\ebook2audiobook.cmd  --help
     ```
<a id="help-command-output"></a>
- 这将输出以下内容:
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

### 使用Docker

你也可以使用Docker来运行电子书到有声读物的转换器。这种方法确保了不同环境之间的一致性，并简化了设置。

#### 运行Docker容器

要运行Docker容器并启动Gradio界面，请使用以下命令:

 - 仅使用CPU
```powershell
docker run -it --rm -p 7860:7860 --platform=linux/amd64 athomasson2/ebook2audiobook python app.py
```
 - 使用GPU加速（仅限Nvidia显卡）
```powershell
docker run -it --rm --gpus all -p 7860:7860 --platform=linux/amd64 athomasson2/ebook2audiobook python app.py
```

#### 构建Docker容器

- 你可以使用以下命令构建docker镜像:
'''powershell
docker build --platform linux/amd64 -t athomasson2/ebook2audiobook .
'''

此命令将在端口7860上启动Gradio界面（localhost:7860）。
- 要运行Docker容器，请使用以下命令:
```powershell
docker run -it --rm -p 7860:7860 --platform=linux/amd64 athomasson2/ebook2audiobook python app.py
```

## Docker容器文件位置
所有ebook2audiobooks将具有基础目录`/home/user/app/`
例如：
`tmp` = `/home/user/app/tmp`
`audiobooks` = `/home/user/app/audiobooks`

   
## Docker无头指南

首先，使用以下命令拉取最新版本的Docker镜像:
```bash 
docker pull athomasson2/ebook2audiobook
```

- 在运行此命令之前，你需要在当前目录中创建一个名为"input-folder"的目录，该目录将被链接，这是你可以放置输入文件的地方，以便Docker镜像可以看到它们。
```bash
mkdir input-folder && mkdir Audiobooks
```

- 在下面的命令中，将 **YOUR_INPUT_FILE.TXT** 替换为你的输入文件的名称

```bash
docker run -it --rm \
    -v $(pwd)/input-folder:/home/user/app/input_folder \
    -v $(pwd)/audiobooks:/home/user/app/audiobooks \
    --platform linux/amd64 \
    athomasson2/ebook2audiobook \
    python app.py --headless --ebook /input_folder/YOUR_INPUT_FILE.TXT
```

- 这样就可以了！

- 输出有声读物将位于Audiobook文件夹中，该文件夹也将位于你运行此Docker命令的本地目录中


## 要获取此程序的其他参数的帮助命令，请运行此命令

```bash
docker run -it --rm \
    --platform linux/amd64 \
    athomasson2/ebook2audiobook \
    python app.py --help

```


这将输出此帮助命令  

[Help command output](#help-command-output)

### Docker Compose

此项目使用Docker Compose在本地运行。你可以通过设置`docker-compose.yml`中的`*gpu-enabled`或`*gpu-disabled`来启用或禁用GPU支持。

#### 运行步骤

1. **克隆仓库**（如果还没有克隆）:
   ```bash
   git clone https://github.com/DrewThomasson/ebook2audiobook.git
   cd ebook2audiobook
   ```

2. **设置GPU支持（默认禁用）**
  要启用GPU支持，修改`docker-compose.yml`并将`*gpu-disabled`改为`*gpu-enabled`

3. **启动服务:**
    ```bash
    docker-compose up -d
    ```

4. **访问服务:**
  服务将通过'http://localhost:7860'访问。

#### 新v2.0 Docker Web GUI界面!
![demo_web_gui](../assets/demo_web_gui.gif)

<details>
  <summary>点击查看Web GUI的图片</summary>
  <img width="1728" alt="GUI Screen 1" src="../assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="../assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="../assets/gui_3.png">
</details>

## 租用GPU
没有硬件运行它或你想租用GPU？
#### 你可以复制huggingface空间并租用一个GPU，每小时大约$0.40
[Huggingface Space Demo](#huggingface-space-demo)

#### 或者你可以尝试使用免费的Google Colab！
（请注意，它会在一段时间后超时，如果你不处理Google Colab）
[Free Google Colab](#free-google-colab)

## 常见Docker问题
- Docker卡在下载Fine-Tuned模型。（这并不发生在每台计算机上，但有些计算机似乎会遇到这个问题）
禁用进度条似乎解决了这个问题，如[#191](https://github.com/DrewThomasson/ebook2audiobook/issues/191)中所讨论
在`docker run`命令中添加此修复的示例
```Dockerfile
docker run -it --rm --gpus all -e HF_HUB_DISABLE_PROGRESS_BARS=1 -e HF_HUB_ENABLE_HF_TRANSFER=0 -p 7860:7860 --platform=linux/amd64 athomasson2/ebook2audiobook python app.py
```





## Fine Tuned TTS模型

你可以轻松使用此仓库微调你的xtts模型
[xtts-finetune-webui](https://github.com/daswer123/xtts-finetune-webui)

如果你想轻松租用GPU，你也可以复制这个huggingface
[xtts-finetune-webui-space](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu)

您还可以使用一个空间轻松地对训练数据进行去噪处理
[denoise-huggingface-space](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit)

### Fine Tuned TTS模型集合

要找到我们已微调的TTS模型集合，请访问[这个Hugging Face链接](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)
对于XTTS自定义模型，还需要语音的参考音频片段：

## 演示

雨天声音

https://github.com/user-attachments/assets/8486603c-38b1-43ce-9639-73757dfb1031

大卫·阿滕伯勒的声音

https://github.com/user-attachments/assets/47c846a7-9e51-4eb9-844a-7460402a20a8


## 支持的电子书格式

- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`, `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`, `.snb`, `.cbc`, `.rb`, `.tcr`
- **最佳结果**: `.epub` 或 `.mobi` 用于自动章节检测

## 输出

- 创建一个带有元数据和章节的`.m4b`文件。
- **示例输出**: ![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)

## 常见问题:
- "它很慢！" - 在CPU上，这非常慢，您只能通过NVIDIA GPU获得加速。[关于此的讨论](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846) 对于更快的多语言生成，我建议使用我的其他[使用piper-tts的项目](https://github.com/DrewThomasson/ebook2audiobookpiper-tts)（它没有零样本语音克隆，但它是Siri质量的语音，但在CPU上更快。）
- "我遇到了依赖问题" - 只需使用Docker，它完全自包含，并且有headless模式，在docker run命令中添加`-h`参数以获取更多信息。
- "我遇到了截断音频问题！" - 请创建一个issue，我并不知道每种语言，我需要从每个人那里获得建议，以在任何其他语言上微调我的句子分割函数。😊

## 我需要帮助！ 🙌 
## [完整列表可以在这里找到](https://github.com/DrewThomasson/ebook2audiobook/issues/32)
- 任何来自说任何受支持语言的人的帮助，以帮助改进句子分割方法
- 可能为多种语言创建readme指南（因为我只懂英语😔）

## 特别感谢

- **Coqui TTS**: [Coqui TTS GitHub](https://github.com/idiap/coqui-ai-TTS)
- **Calibre**: [Calibre Website](https://calibre-ebook.com)
- **FFmpeg**: [FFmpeg Website](https://ffmpeg.org)

- [@shakenbake15 for better chapter saving method](https://github.com/DrewThomasson/ebook2audiobook/issues/8) 

### [Legacy V1.0](legacy/v1.0)

你可以在这里查看代码 [here](legacy/v1.0).

## 加入我们的Discord服务器！

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/bg5Kx43c6w)](https://discord.gg/bg5Kx43c6w)
