# 📚 ebook2audiobook

CPU/GPU转换器，将电子书转换为包含章节和元数据的有声读物<br/>
使用Calibre、ffmpeg、XTTSv2、Fairseq等。支持语音克隆和1124种语言！
> [!IMPORTANT]
**本工具仅适用于非DRM、合法获取的电子书。**
作者对软件的任何误用或由此产生的法律后果概不负责。
请负责任地使用本工具，并遵守所有适用法律。

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/bg5Kx43c6w)](https://discord.gg/bg5Kx43c6w)

#### 新的v2.0 Web GUI界面！
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>点击查看Web GUI的图片</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## README.md
- ar [العربية](./readme/README_AR.md)
- en [English](README.md)

## 目录

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
- [Supported eBook Formats](#supported-ebook-formats)
- [Output](#output)
- [Common Issues](#common-issues)
- [Special Thanks](#special-thanks)
- [Join Our Discord Server!](#join-our-discord-server)
- [Legacy](#legacy-v10)
- [Glossary of Sections](#glossary-of-sections)

## 🌟 特征

- 📖 使用Calibre将电子书转换为文本格式。
- 📚 将电子书拆分为章节，以获得有组织的音频。
- 🎙️ 使用[Coqui XTTSv2](https://huggingface.co/coqui/XTTS-v2)和[Fairseq](https://github.com/facebookresearch/fairseq/tree/main/examples/mms)实现高质量的文本到语音转换。
- 🗣️ 可选择使用您自己的语音文件进行语音克隆。
- 🌍 支持1107种语言（默认为英语）。[支持的语言列表](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)。
- 🖥️ 基于4GB RAM运行。

## [Huggingface space demo](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)

- Huggingface space运行在空闲cpu层上，所以预计会非常慢或超时，不要给它非常大的文件。
- 最好复制空间或在本地运行。

## 免费谷歌Colab
[![免费谷歌Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb)

## 🌐 支持的语言

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

##  必要条件

- 4gb 内存
- 如果在windows上运行，则启用虚拟化(仅限Docker)

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
     ./ebook2audiobook.sh  # Run Launch script
     ```
   - **Windows**
     ```bash
     .\ebook2audiobook.cmd  # Run launch script
     ```

2. **打开web应用程序**: 点击终端中提供的URL访问web应用程序并转换电子书.
3. **公共链接**: 在末尾添加“--share True”，如下所示：`python app.py--share True`
- **[更多参数]**: 使用`-h`参数，如`python app.py-h`

### 基本用法
    - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.sh  -- --ebook <path_to_ebook_file> --voice [path_to_voice_file] --language [language_code]
     ```
   - **Windows**
     ```bash
     .\ebook2audiobook.cmd  -- --ebook <path_to_ebook_file> --voice [path_to_voice_file] --language [language_code]
     ```

- **<path_to_ebook_file>**: 电子书文件的路径。
- **[path_to_voice_file]**: 指定转换的语音文件，可选。
- **[language_code]**: 指定转换的语言，可选。
- **[更多参数]**: 使用 `-h` 参数，如 `python app.py -h`

### 自定义XTTS模型用法
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.sh  -- --ebook <ebook_file_path> --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path> --custom_config <custom_config_path> --custom_vocab <custom_vocab_path>
     ```
   - **Windows**
     ```bash
     .\ebook2audiobook.cmd  -- --ebook <ebook_file_path> --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path> --custom_config <custom_config_path> --custom_vocab <custom_vocab_path>
     ```

- **<ebook_file_path>**: 电子书文件的路径。
- **<target_voice_file_path>**: 指定转换的语音文件，可选。
- **<language>**: 指定转换的语言，可选。
- **<custom_model_path>**: `model.pth`的路径。
- **<custom_config_path>**: `config.json`的路径。
- **<custom_vocab_path>**: `vocab.json`的路径。
- **[更多参数]**: 使用 `-h` 参数，如 `python app.py -h`

### 🧩 自定义XTTS Fine-Tune 模型的无头用法 🌐

```bash
python app.py --headless True --use_custom_model True --ebook <ebook_file_path> --voice <target_voice_file_path> --language <language> --custom_model_url <custom_model_URL_ZIP_path>
```

- **<ebook_file_path>**: 电子书文件的路径。
- **<target_voice_file_path>**: 指定转换的语音文件，可选。
- **<language>**: 指定转换的语言，可选。
- **<custom_model_URL_ZIP_path>**: 模型文件夹压缩包的URL路径。例如
 [xtts_David_Attenborough_fine_tune](https://huggingface.co/drewThomasson/xtts_David_Attenborough_fine_tune/tree/main) `https://huggingface.co/drewThomasson/xtts_David_Attenborough_fine_tune/resolve/main/Finished_model_files.zip?download=true`
- **[更多参数]**: 使用 `-h` 参数，如 `python app.py -h`

### 详细指南，包括所有要使用的参数列表
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
usage: app.py [-h] [--share] [--headless [HEADLESS]] [--ebook EBOOK]
              [--ebooks_dir [EBOOKS_DIR]] [--voice VOICE] [--language LANGUAGE]
              [--device {cpu,gpu}] [--use_custom_model] [--custom_model CUSTOM_MODEL]
              [--custom_config CUSTOM_CONFIG] [--custom_vocab CUSTOM_VOCAB]
              [--custom_model_url CUSTOM_MODEL_URL] [--temperature TEMPERATURE]
              [--length_penalty LENGTH_PENALTY]
              [--repetition_penalty REPETITION_PENALTY] [--top_k TOP_K] [--top_p TOP_P]
              [--speed SPEED] [--enable_text_splitting]

使用文本到语音模型将电子书转换为有声读物。您可以启动Gradio界面，也可以在命令行运行脚本进行直接转换。

options:
  -h, --help            显示此帮助消息并退出
  --script_mode SCRIPT_MODE
                        强制脚本在NATIVE或DOCKER_UTILS中运行
  --share               启用可公开共享的Gradio链接。默认为False
  -- []
                        以模式运行。如果标志不带值，则默认为True，否则为False
  --session SESSION     中断时重新连接的会话（仅命令行模式）
  --ebook EBOOK         转换电子书文件的路径。命令行中需要。
  --ebooks_dir [EBOOKS_DIR]
                        包含用于批量转换的电子书的目录的路径。如果提供“默认”，则默认为“电子书”。
  --voice VOICE         TTS目标语音文件的路径。可选，XTTS必须为24khz，fairseq型号必须为16khz，如果没有提供，则使用默认语音。
  --language LANGUAGE  有声读物转换的语言。 Options: eng, zho, spa, fra, por, rus, ind, hin, ben, yor, ara, jav, jpn, kor, deu, ita, fas, tam, tel, tur, pol, hun, nld, zzzz, abi, ace, aca, acn, acr, ach, acu, guq, ade, adj, agd, agx, agn, aha, aka, knj, ake, aeu, ahk, bss, alj, sqi, alt, alp, alz, kab, amk, mmg, amh, ami, azg, agg, boj, cko, any, arl, atq, luc, hyw, apr, aia, msy, cni, cjo, cpu, cpb, asm, asa, teo, ati, djk, ava, avn, avu, awb, kwi, awa, agr, agu, ayr, ayo, abp, blx, sgb, azj-script_cyrillic, azj-script_latin, azb, bba, bhz, bvc, bfy, bgq, bdq, bdh, bqi, bjw, blz, ban, bcc-script_latin, bcc-script_arabic, bam, ptu, bcw, bqj, bno, bbb, bfa, bjz, bak, eus, bsq, akb, btd, btx, bts, bbc, bvz, bjv, bep, bkv, bzj, bem, bng, bom, btt, bha, bgw, bht, beh, sne, ubl, bcl, bim, bkd, bjr, bfo, biv, bib, bis, bzi, bqp, bpr, bps, bwq, bdv, bqc, bus, bnp, bmq, bdg, boa, ksr, bor, bru, box, bzh, bgt, sab, bul, bwu, bmv, mya, tte, cjp, cbv, kaq, cot, cbc, car, cat, ceb, cme, cbi, ceg, cly, cya, che, hne, nya, dig, dug, bgr, cek, cfm, cnh, hlt, mwq, ctd, tcz, zyp, cco, cnl, cle, chz, cpa, cso, cnt, cuc, hak, nan, xnj, cap, cax, ctg, ctu, chf, cce, crt, crq, cac-dialect_sansebastiáncoatán, cac-dialect_sanmateoixtatán, ckt, ncu, cdj, chv, caa, asg, con, crn, cok, crk-script_latin, crk-script_syllabics, crh, hrv, cui, ces, dan, dsh, dbq, dga, dgi, dgk, dnj-dialect_gweetaawueast, dnj-dialect_blowowest, daa, dnt, dnw, dar, tcc, dwr, ded, mzw, ntr, ddn, des, dso, nfa, dhi, gud, did, mhu, dip, dik, tbz, dts, dos, dgo, mvp, jen, dzo, idd, eka, cto, emp, enx, sja, myv, mcq, ese, evn, eza, ewe, fal, fao, far, fij, fin, fon, frd, ful, flr, gau, gbk, gag-script_cyrillic, gag-script_latin, gbi, gmv, lug, pwg, gbm, cab, grt, krs, gso, nlg, gej, gri, kik, acd, glk, gof-script_latin, gog, gkn, wsg, gjn, gqr, gor, gux, gbo, ell, grc, guh, gub, grn, gyr, guo, gde, guj, gvl, guk, rub, dah, gwr, gwi, hat, hlb, amf, hag, hnn, bgc, had, hau, hwc, hvn, hay, xed, heb, heh, hil, hif, hns, hoc, hoy, hus-dialect_westernpotosino, hus-dialect_centralveracruz, huv, hui, hap, iba, isl, dbj, ifa, ifb, ifu, ifk, ife, ign, ikk, iqw, ilb, ilo, imo, inb, ipi, irk, icr, itv, itl, atg, ixl-dialect_sanjuancotzal, ixl-dialect_sangasparchajul, ixl-dialect_santamarianebaj, nca, izr, izz, jac, jam, jvn, kac, dyo, csk, adh, jun, jbu, dyu, bex, juy, gna, urb, kbp, cwa, dtp, kbr, cgc, kki, kzf, lew, cbr, kkj, keo, kqe, kak, kyb, knb, kmd, kml, ify, xal, kbq, kay, ktb, hig, gam, cbu, xnr, kmu, kne, kan, kby, pam, cak-dialect_santamaríadejesús, cak-dialect_southcentral, cak-dialect_yepocapa, cak-dialect_western, cak-dialect_santodomingoxenacoj, cak-dialect_central, xrb, krc, kaa, krl, pww, xsm, cbs, pss, kxf, kyz, kyu, txu, kaz, ndp, kbo, kyq, ken, ker, xte, kyg, kjh, kca, khm, kxm, kjg, nyf, kij, kia, kqr, kqp, krj, zga, kin, pkb, geb, gil, kje, kss, thk, klu, kyo, kog, kfb, kpv, bbo, xon, kma, kno, kxc, ozm, kqy, coe, kpq, kpy, kyf, kff-script_telugu, kri, rop, ktj, ted, krr, kdt, kez, cul, kle, kdi, kue, kum, kvn, cuk, kdn, xuo, key, kpz, knk, kmr-script_latin, kmr-script_arabic, kmr-script_cyrillic, xua, kru, kus, kub, kdc, kxv, blh, cwt, kwd, tnk, kwf, cwe, kyc, tye, kir, quc-dialect_north, quc-dialect_east, quc-dialect_central, lac, lsi, lbj, lhu, las, lam, lns, ljp, laj, lao, lat, lav, law, lcp, lzz, lln, lef, acf, lww, mhx, eip, lia, lif, onb, lis, loq, lob, yaz, lok, llg, ycl, lom, ngl, lon, lex, lgg, ruf, dop, lnd, ndy, lwo, lee, mev, mfz, jmc, myy, mbc, mda, mad, mag, ayz, mai, mca, mcp, mak, vmw, mgh, kde, mlg, zlm, pse, mkn, xmm, mal, xdy, div, mdy, mup, mam-dialect_central, mam-dialect_northern, mam-dialect_southern, mam-dialect_western, mqj, mcu, mzk, maw, mjl, mnk, mge, mbh, knf, mjv, mbt, obo, mbb, mzj, sjm, mrw, mar, mpg, mhr, enb, mah, myx, klv, mfh, met, mcb, mop, yua, mfy, maz, vmy, maq, mzi, maj, maa-dialect_sanantonio, maa-dialect_sanjerónimo, mhy, mhi, zmz, myb, gai, mqb, mbu, med, men, mee, mwv, meq, zim, mgo, mej, mpp, min, gum, mpx, mco, mxq, pxm, mto, mim, xta, mbz, mip, mib, miy, mih, miz, xtd, mxt, xtm, mxv, xtn, mie, mil, mio, mdv, mza, mit, mxb, mpm, soy, cmo-script_latin, cmo-script_khmer, mfq, old, mfk, mif, mkl, mox, myl, mqf, mnw, mon, mog, mfe, mor, mqn, mgd, mtj, cmr, mtd, bmr, moz, mzm, mnb, mnf, unr, fmu, mur, tih, muv, muy, sur, moa, wmw, tnr, miq, mos, muh, nas, mbj, nfr, kfw, nst, nag, nch, nhe, ngu, azz, nhx, ncl, nhy, ncj, nsu, npl, nuz, nhw, nhi, nlc, nab, gld, nnb, npy, pbb, ntm, nmz, naw, nxq, ndj, ndz, ndv, new, nij, sba, gng, nga, nnq, ngp, gym, kdj, nia, nim, nin, nko, nog, lem, not, nhu, nob, bud, nus, yas, nnw, nwb, nyy, nyn, rim, lid, nuj, nyo, nzi, ann, ory, ojb-script_latin, ojb-script_syllabics, oku, bsc, bdu, orm, ury, oss, ote, otq, stn, sig, kfx, bfz, sey, pao, pau, pce, plw, pmf, pag, pap, prf, pab, pbi, pbc, pad, ata, pez, peg, pcm, pis, pny, pir, pjt, poy, pps, pls, poi, poh-dialect_eastern, poh-dialect_western, prt, pui, pan, tsz, suv, lme, quy, qvc, quz, qve, qub, qvh, qwh, qvw, quf, qvm, qul, qvn, qxn, qxh, qvs, quh, qxo, qxr, qvo, qvz, qxl, quw, kjb, kek, rah, rjs, rai, lje, rnl, rkt, rap, yea, raw, rej, rel, ril, iri, rgu, rhg, rmc-script_latin, rmc-script_cyrillic, rmo, rmy-script_latin, rmy-script_cyrillic, ron, rol, cla, rng, rug, run, lsm, spy, sck, saj, sch, sml, xsb, sbl, saq, sbd, smo, rav, sxn, sag, sbp, xsu, srm, sas, apb, sgw, tvw, lip, slu, snw, sea, sza, seh, crs, ksb, shn, sho, mcd, cbt, xsr, shk, shp, sna, cjs, jiv, snp, sya, sid, snn, sri, srx, sil, sld, akp, xog, som, bmu, khq, ses, mnx, srn, sxb, suc, tgo, suk, sun, suz, sgj, sus, swh, swe, syl, dyi, myk, spp, tap, tby, tna, shi, klw, tgl, tbk, tgj, blt, tbg, omw, tgk, tdj, tbc, tlj, tly, ttq-script_tifinagh, taj, taq, tpm, tgp, tnn, tac, rif-script_latin, rif-script_arabic, tat, tav, twb, tbl, kps, twe, ttc, kdh, tes, tex, tee, tpp, tpt, stp, tfr, twu, ter, tew, tha, nod, thl, tem, adx, bod, khg, tca, tir, txq, tik, dgr, tob, tmf, tng, tlb, ood, tpi, jic, lbw, txa, tom, toh, tnt, sda, tcs, toc, tos, neb, trn, trs, trc, tri, cof, tkr, kdl, cas, tso, tuo, iou, tmc, tuf, tuk-script_latin, tuk-script_arabic, bov, tue, kcg, tzh-dialect_bachajón, tzh-dialect_tenejapa, tzo-dialect_chenalhó, tzo-dialect_chamula, tzj-dialect_western, tzj-dialect_eastern, aoz, udm, udu, ukr, ppk, ubu, urk, ura, urt, urd-script_devanagari, urd-script_arabic, urd-script_latin, upv, usp, uig-script_arabic, uig-script_cyrillic, uzb-script_cyrillic, vag, bav, vid, vie, vif, vun, vut, prk, wwa, rro, bao, waw, lgl, wlx, cou, hub, gvc, mfi, wap, wba, war, way, guc, cym, kvw, tnp, hto, huu, wal-script_latin, wal-script_ethiopic, wlo, noa, wob, kao, xer, yad, yka, sah, yba, yli, nlk, yal, yam, yat, jmd, tao, yaa, ame, guu, yao, yre, yva, ybb, pib, byr, pil, ycn, ess, yuz, atb, zne, zaq, zpo, zad, zpc, zca, zpg, zai, zpl, zam, zaw, zpm, zac, zao, ztq, zar, zpt, zpi, zas, zaa, zpz, zab, zpu, zae, zty, zav, zza, zyb, ziw, zos, gnd. Default to English (eng).
  --device {cpu,gpu}    有声读物转换的处理器单元类型。如果没有指定：首先检查gpu是否可用，如果没有选择cpu。
  --custom_model CUSTOM_MODEL
                        自定义模型的路径（包含[“config.json”、“vocab.json”、“model.pth”、“ref.wav”]的.zip文件）。如果使用自定义模型，则需要。
  --temperature TEMPERATURE
                        模型的温度。默认值为0.65。更高的温度会带来更有创意的输出。
  --length_penalty LENGTH_PENALTY
                        应用于自回归解码器的长度惩罚。默认值为1.0。不适用于自定义模型。
  --repetition_penalty REPETITION_PENALTY
                        防止自回归解码器重复自身的惩罚。默认值为2.5
  --top_k TOP_K         Top-k采样。较低的值意味着更可能的输出和更高的音频生成速度。默认值为50
  --top_p TOP_P         Top-p采样。较低的值意味着更可能的输出和更高的音频生成速度。默认值为0.8
  --speed SPEED         语音生成的速度因素。默认值为1.0
  --enable_text_splitting
                        允许将文本拆分为句子。默认为False
  --fine_tuned FINE_TUNED
                        微调模型的名称。可选，根据TTS引擎和语言使用标准型号。
  --version             显示脚本版本并退出

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

### 使用 Docker

您还可以使用Docker运行电子书到有声读物的转换器。这种方法确保了不同环境之间的一致性，并简化了设置。

#### 运行Docker容器

要运行Docker容器并启动Gradio接口，请使用以下命令：

 -只用CPU运行
```powershell
docker run -it --rm -p 7860:7860 --platform=linux/amd64 athomasson2/ebook2audiobook python app.py
```
 -使用GPU加速运行（仅限Nvida显卡）
```powershell
docker run -it --rm --gpus all -p 7860:7860 --platform=linux/amd64 athomasson2/ebook2audiobook python app.py
```

#### 构建Docker容器

- 您可以使用以下命令构建docker镜像:
'''powershell
docker build --platform linux/amd64 -t athomasson2/ebook2audiobook .
'''

此命令将启动端口7860上的Gradio接口。（localhost:7860）
- 对于更多选项，如以模式运行docker或公开gradio链接，请在docker启动命令中的`app.py`后添加`--help`参数

### 🖥️ Web界面

1. **运行脚本**:
   ```bash
   python custom_model_ebook2audiobookXTTS_gradio.py
   ```

2. **打开web应用程序**: 单击终端中提供的URL以访问web应用程序并转换电子书。

### 📝 基础用法

```bash
python ebook2audiobook.py <path_to_ebook_file> [path_to_voice_file] [language_code]
```

- **<path_to_ebook_file>**: 电子书文件的路径。
- **[path_to_voice_file]**: 指定转换的语音文件，可选。
- **[language_code]**: 指定转换的语言，可选。

### 🧩 自定义XTTS模型

```bash
python custom_model_ebook2audiobookXTTS.py <ebook_file_path> <target_voice_file_path> <language> <custom_model_path> <custom_config_path> <custom_vocab_path>
```

- **<ebook_file_path>**: 电子书文件的路径。
- **<target_voice_file_path>**: 指定转换的语音文件，可选。
- **<language>**: 指定转换的语言，可选。
- **<custom_model_path>**: `model.pth`的路径。
- **<custom_config_path>**: `config.json`的路径。
- **<custom_vocab_path>**: `vocab.json`的路径。
</details>

### 🐳 使用Docker

您还可以使用Docker运行电子书到有声读物的转换器。这种方法确保了不同环境之间的一致性，并简化了设置。

#### 🚀 运行Docker容器

要运行Docker容器并启动Gradio接口，请使用以下命令：

 -仅使用CPU运行
```powershell
docker run -it --rm -p 7860:7860 --platform=linux/amd64 athomasson2/ebook2audiobookxtts:huggingface python app.py
```
 -使用GPU加速运行（仅限Nvida显卡）
```powershell
docker run -it --rm --gpus all -p 7860:7860 --platform=linux/amd64 athomasson2/ebook2audiobookxtts:huggingface python app.py
```

此命令将启动7860端口上的Gradio接口(localhost:7860)
- 对于更多选项，如以无头模式运行docker或公开gradio链接，请在docker启动命令中的`app.py`后添加`-h`参数


## Docker容器文件位置
所有ebook2audiobooks的基本目录为 `/home/user/app/`
例如:
`tmp` = `/home/user/app/tmp`
`audiobooks` = `/home/user/app/audiobooks`

## Docker无头指南

首先是docker pull的最新版本
```bash
docker pull athomasson2/ebook2audiobook
```

- 在运行此命令之前，您需要在当前目录中创建一个名为“input folder”的目录，该目录将被链接，您可以在此处放置docker镜像的输入文件
```bash
mkdir input-folder && mkdir Audiobooks
```

- 在下面的命令中将 **YOUR_INPUT_FILE.TXT** 替换为您的输入文件的名称

```bash
docker run -it --rm \
    -v $(pwd)/input-folder:/home/user/app/input_folder \
    -v $(pwd)/audiobooks:/home/user/app/audiobooks \
    --platform linux/amd64 \
    athomasson2/ebook2audiobook \
    python app.py --headless --ebook /input_folder/YOUR_INPUT_FILE.TXT
```

- 应该就是这样了!

- 输出Audiobooks将在Audiobook文件夹中找到，该文件夹也位于您运行此docker命令的本地目录中

## 要获取此程序中其他参数的帮助命令，可以运行以下命令

```bash
docker run -it --rm \
    --platform linux/amd64 \
    athomasson2/ebook2audiobook \
    python app.py --help

```


这将输出以下内容

[帮助命令输出](#help-command-output)

### Docker编写

这个项目使用Docker Compose在本地运行。您可以通过在“docker-compose.yml”中设置“*GPU enabled”或“*gpudisabled”来启用或禁用GPU支持`

#### 启动步骤

1. **克隆存储库** (如果你还没有):
   ```bash
   git clone https://github.com/DrewThomasson/ebook2audiobook.git
   cd ebook2audiobook
   ```

2. **设置GPU支持（默认禁用）**
  要启用GPU支持，请修改“docker compose.yml”并将“*GPU disabled”更改为“*GPU-enabled”`

3. **开启服务:**
    ```bash
    docker-compose up -d
    ```

4. **访问服务:**
  该服务将在http://localhost:7860.

#### 新的2.0 Docker Web GUI界面！
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>点击查看Web GUI的图像</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## 租用GPU
没有运行它的硬件，或者你想租一个GPU？
#### 你可以复制hugginface空间，并以每小时约0.40美元的价格租用一台gpu
[Huggingface Space Demo](#huggingface-space-demo)

#### 或者你可以尝试免费使用谷歌的colab！
(请注意，在您不使用谷歌colab后，它将超时)
[免费的Google Colab](#free-google-colab)


## 微调TTS型号

您可以使用此仓库轻松微调自己的xtts模型
[xtts-finetune-webui](https://github.com/daswer123/xtts-finetune-webui)

如果你想轻松租用GPU，你也可以复制这个huggingface
[xtts-finetune-webui-space](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu)

您还可以使用一个空间轻松地对训练数据进行去噪处理
[denoise-huggingface-space](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit)

### 微调TTS系列

要查找我们已经微调的TTS型号集合，请访问[这个Hugging Face链接](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)
对于XTTS自定义模型，还需要语音的参考音频片段：

## Demos

雨天的声音

https://github.com/user-attachments/assets/8486603c-38b1-43ce-9639-73757dfb1031

大卫·爱登堡配音

https://github.com/user-attachments/assets/47c846a7-9e51-4eb9-844a-7460402a20a8

## 支持的电子书格式

- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`, `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`, `.snb`, `.cbc`, `.rb`, `.tcr`
-**最佳结果**：“.epub”或“.mobi”可以自动章节检测

## 输出

- 创建一个包含元数据和章节的“.m4b”文件。
- **输出示例**: ![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)

## 常见问题:
-“太慢了！”-仅在CPU上，这非常慢，而且你只能通过NVIDIA GPU获得加速。[关于此的讨论](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846）为了更快地生成多语言，我建议我的另一个[使用piper-tts的项目](https://github.com/DrewThomasson/ebook2audiobookpiper-tts)相反（它没有零样本语音克隆，而且是siri质量的语音，但在cpu上速度要快得多。）
-“我有依赖问题”-只需使用docker，它完全独立，有一个无头模式，在docker run命令中的`app.py`后添加`-h`参数以获取更多信息。
-“我遇到了一个截断的音频问题！”-请提出这个问题，我不会说每种语言，我需要每个人的建议来微调我在任何其他语言上的句子分割功能。😊

## 我需要帮助！ 🙌
##[完整列表可以在这里找到](https://github.com/DrewThomasson/ebook2audiobook/issues/32)
-说任何支持语言的人提供的帮助，以帮助正确的句子分割方法
-可能为多种语言创建自述指南（因为我只知道英语😔)

## 特别感谢

- **Coqui TTS**: [Coqui TTS GitHub](https://github.com/idiap/coqui-ai-TTS)
- **Calibre**: [Calibre Website](https://calibre-ebook.com)
- **FFmpeg**: [FFmpeg Website](https://ffmpeg.org)

- [@shakenbake15 for better chapter saving method](https://github.com/DrewThomasson/ebook2audiobook/issues/8)

### [Legacy V1.0](legacy/v1.0)

你能预览这个代码 [here](legacy/v1.0).

## 加入我们的Discord服务器！

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/bg5Kx43c6w)](https://discord.gg/bg5Kx43c6w)