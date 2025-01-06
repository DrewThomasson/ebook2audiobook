# 📚 ebook2audiobook
محول من كتب إلكترونية (eBooks) إلى كتب صوتية باستخدام معالج CPU/GPU مع الفصول والبيانات الوصفية
باستخدام Calibre، ffmpeg، XTTSv2، Fairseq والمزيد. يدعم استنساخ الصوت و1124 لغة!
> [!IMPORTANT]
**أداة التحويل هذه مخصصة للاستخدام مع الكتب الإلكترونية غير المحمية بحقوق DRM، والتي تم الحصول عليها قانونيًا فقط.**

المؤلفون غير مسؤولين عن أي إساءة استخدام لهذه الأداة أو أي تبعات قانونية ناتجة عنها.
يرجى استخدام هذه الأداة بشكل مسؤول ووفقًا لجميع القوانين المعمول بها.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/bg5Kx43c6w)](https://discord.gg/bg5Kx43c6w)

#### واجهة المستخدم الجديدة v2.0 عبر الويب!
![demo_web_gui](../assets/demo_web_gui.gif)

<details>
  <summary>اضغط لرؤية صور واجهة المستخدم عبر الويب</summary>
  <img width="1728" alt="GUI Screen 1" src="../assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="../assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="../assets/gui_3.png">
</details>

## لغات أخرى README.md
- الإنجليزية [English](README.md)

## جدول المحتويات


- [المقدمة](#ebook2audiobook)
- [المميزات](#المميزات)
- [واجهة المستخدم الجديدة v2.0 عبر الويب](#واجهة-المستخدم-الجديدة-v2.0-عبر-الويب!)
- [عرض تجريبي على Huggingface Space](#عرض-تجريبي-على-Huggingface-Space)
- [Google Colab مجاني](#Google-Colab-مجاني)
- [عروض صوتية جاهزة](#عروض-صوتية-جاهزة)
- [اللغات المدعومة](#اللغات-المدعومة)
- [المتطلبات](#المتطلبات)
- [تعليمات التثبيت](#تعليمات-التثبيت)
  - [الاستخدام](#الاستخدام)
  - [تشغيل واجهة Gradio عبر الويب](#تشغيل-واجهة-Gradio-عبر-الويب)
  - [الاستخدام الأساسي بدون واجهة رسومية](#الاستخدام-الأساسي-بدون-واجهة-رسومية)
  - [الاستخدام بدون واجهة باستخدام نموذج XTTS مخصص](#الاستخدام-بدون-واجهة-باستخدام-نموذج-XTTS-مخصص)
  - [استئجار معالج GPU](#استئجار-معالج-GPU)
  - [نتائج أمر المساعدة](#نتائج-أمر-المساعدة)
- [نماذج TTS المحسنة](#نماذج-TTS-المحسنة)
  - [مجموعة النماذج المحسنة](#مجموعة-النماذج-المحسنة)
- [استخدام Docker](#استخدام-Docker)
  - [تجميع Docker](#تجميع-Docker)
  - [دليل الاستخدام بدون واجهة في Docker](#دليل-الاستخدام-بدون-واجهة-في-Docker)
  - [مواقع ملفات حاوية Docker](#مواقع-ملفات-حاوية-Docker)
- [تنسيقات الكتب الإلكترونية المدعومة](#تنسيقات-الكتب-الإلكترونية-المدعومة)
- [المخرجات](#المخرجات)
- [المشاكل الشائعة](#المشاكل-الشائعة)
- [شكر خاص](#شكر-خاص)
- [انضم إلى خادم Discord الخاص بنا!](#انضم-إلى-خادم-Discord-الخاص-بنا!)
- [الإصدار القديم](#الإصدار-القديم-v1.0)
- [مسرد الأقسام](#مسرد-الأقسام)

## المميزات

- 📖 يحول الكتب الإلكترونية إلى صيغة نص باستخدام Calibre.
- 📚 يقسم الكتاب الإلكتروني إلى فصول للحصول على صوتيات منظمة.
- 🎙️ يقدم تحويل النص إلى كلام بجودة عالية باستخدام [Coqui XTTSv2](https://huggingface.co/coqui/XTTS-v2) و [Fairseq](https://github.com/facebookresearch/fairseq/tree/main/examples/mms).
- 🗣️ يدعم استنساخ الصوت باستخدام ملف صوتي خاص بك.
- 🌍 يدعم 1107 لغة (الإنجليزية افتراضيًا). [قائمة اللغات المدعومة](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
- 🖥️ مصمم للعمل على أجهزة تحتوي على 4 جيجابايت من ذاكرة الوصول العشوائي (RAM).

## [عرض تجريبي على Huggingface Space](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
- مساحة Huggingface تعمل على الطبقة المجانية لوحدة المعالجة المركزية (CPU)، لذا توقع بطء الأداء أو انتهاء المهلة (timeout). فقط تجنب إدخال ملفات كبيرة للغاية.
- من الأفضل تكرار المساحة إلى حسابك الخاص أو تشغيلها محليًا لتحسين الأداء.

## Google Colab مجاني 
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb)

## اللغات المدعومة

- **العربية (ara)**
- **الصينية (zho)**
- **التشيكية (ces)**
- **الهولندية (nld)**
- **الإنجليزية (eng)**
- **الفرنسية (fra)**
- **الألمانية (deu)**
- **الهندية (hin)**
- **المجرية (hun)**
- **الإيطالية (ita)**
- **اليابانية (jpn)**
- **الكورية (kor)**
- **البولندية (pol)**
- **البرتغالية (por)**
- **الروسية (rus)**
- **الأسبانية (spa)**
- **التركية (tur)**
- **الفيتنامية (vie)**
- [**+ 1107 لغة عبر Fairseq**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)

##  المتطلبات

- 4 جيجابايت من الذاكرة العشوائية (RAM).
- تمكين المحاكاة الافتراضية إذا كنت تستخدم Windows (لـ Docker فقط).

### تعليمات التثبيت

1. **استنساخ المستودع**
```bash
git clone https://github.com/DrewThomasson/ebook2audiobook.git
```

حدد رمز اللغة عند تشغيل السكربت في الوضع.

### تشغيل واجهة Gradio عبر الويب

<div align='right'>
  
**1. تشغيل البرنامج**:
   - **لينكس/ماك (Linux/MacOS)**:
     ```bash
     ./ebook2audiobook.sh  # Run Launch script
     ```
   - **ويندوز (Windows)**
     ```bash
     .\ebook2audiobook.cmd  # Run launch script
     ```

**2. افتح التطبيق عبر الويب**: انقر على الرابط المقدم في الطرفية (terminal) للوصول إلى التطبيق وتحويل الكتب الإلكترونية.
**3. للحصول على الرابط العام**: أضف `share--` في نهاية الأمر مثل هذا: `python app.py --share`
- **[لمزيد من الأوامر]**: استخدم الأمر `help--` مثل هذا: `python app.py --help`

</div>

### الاستخدام الأساسي بدون واجهة رسومية

   - **لينكس/ماك (Linux/MacOS)**:
     ```bash
     ./ebook2audiobook.sh  -- --ebook <path_to_ebook_file> --voice [path_to_voice_file] --language [language_code]
     ```
   - **ويندوز (Windows)**
     ```bash
     .\ebook2audiobook.cmd  -- --ebook <path_to_ebook_file> --voice [path_to_voice_file] --language [language_code]
     ```
     

- **<path_to_ebook_file>**: مسار ملف الكتاب الإلكتروني.
- **[path_to_voice_file]**: اختياري لاستنساخ الصوت.
- **[language_code]**: اختياري لتحديد رمز لغة ISO-639-3 (افتراضيًا "eng"). يدعم أيضًا رموز ISO-639-1 ذات الحرفين.
- **[للمزيد من الخيارات]**: استخدم الأمر `help--` بهذا الشكل: `python app.py --help`


###  الاستخدام بدون واجهة باستخدام نموذج XTTS مخصص
   - **لينكس/ماك (Linux/MacOS)**:
     ```bash
     ./ebook2audiobook.sh  -- --ebook <ebook_file_path> --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path> --custom_config <custom_config_path> --custom_vocab <custom_vocab_path>
     ```
   - **ويندوز (Windows)**
     ```bash
     .\ebook2audiobook.cmd  -- --ebook <ebook_file_path> --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path> --custom_config <custom_config_path> --custom_vocab <custom_vocab_path>
     ```

- **<ebook_file_path>**: مسار ملف الكتاب الإلكتروني الخاص بك.
- **<target_voice_file_path>**: اختياري لاستنساخ الصوت.
- **< language >**: اختياري لتحديد اللغة.
- **<custom_model_path>**: مسار ملف `model.pth`.
- **<custom_config_path>**: مسار ملف `config.json`.
- **<custom_vocab_path>**: مسار ملف `vocab.json`.
- **[للمزيد من الخيارات]**: استخدم الأمر `help--` بهذا الشكل: `python app.py --help`

### للحصول على دليل مفصل مع قائمة بجميع المعلمات التي يجب استخدامها
   - **لينكس/ماك (Linux/MacOS)**:
     ```bash
     ./ebook2audiobook.sh  --help
     ```
   - **ويندوز (Windows)**
     ```bash
     .\ebook2audiobook.cmd  --help
     ```
<a id="help-command-output"></a>
- سيؤدي ذلك إلى إخراج النتيجة التالية.
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

### استخدام Docker

يمكنك أيضًا استخدام Docker لتشغيل محول الكتب الإلكترونية إلى كتب صوتية. يضمن هذا الأسلوب التوافق بين البيئات المختلفة ويبسّط عملية الإعداد.

#### تشغيل حاوية Docker

لتشغيل حاوية Docker وبدء واجهة Gradio، استخدم الأمر التالي:

 -تشغيل باستخدام المعالج المركزي (CPU) فقط.
```powershell
docker run -it --rm -p 7860:7860 --platform=linux/amd64 athomasson2/ebook2audiobook python app.py
```
 -تشغيل باستخدام تسريع GPU (لبطاقات الرسومات Nvida فقط).
```powershell
docker run -it --rm --gpus all -p 7860:7860 --platform=linux/amd64 athomasson2/ebook2audiobook python app.py
```

سيبدأ هذا الأمر واجهة Gradio على المنفذ 7860 (localhost:7860).
- للحصول على المزيد من الخيارات مثل تشغيل Docker في وضع معين أو جعل رابط Gradio عامًا، أضف معلمة `help--` بعد `app.py` في أمر تشغيل Docker.

## مواقع ملفات حاوية Docker
سيكون لجميع ملفات ebook2audiobook الدليل الأساسي في المسار `/home/user/app/`
كمثال:
`tmp` = `/home/user/app/tmp`
`audiobooks` = `/home/user/app/audiobooks`

## دليل الاستخدام بدون واجهة في Docker

لأول مرة، قم بسحب أحدث إصدار من Docker باستخدام الأمر:
```bash 
docker pull athomasson2/ebook2audiobook
```

- قبل تشغيل هذا، يجب عليك إنشاء مجلد باسم "input-folder" في الدليل الحالي، والذي سيتم ربطه. هذا هو المكان الذي يمكنك فيه وضع ملفات الإدخال ليتمكن Docker من رؤيتها.
```bash
mkdir input-folder && mkdir Audiobooks
```

- في الأمر أدناه، استبدل YOUR_INPUT_FILE.TXT باسم ملف الإدخال الخاص بك.
```bash
docker run -it --rm \
    -v $(pwd)/input-folder:/home/user/app/input_folder \
    -v $(pwd)/audiobooks:/home/user/app/audiobooks \
    --platform linux/amd64 \
    athomasson2/ebook2audiobook \
    python app.py --headless --ebook /input_folder/YOUR_INPUT_FILE.TXT
```

- وتلك هي الخطوات!

- سيتم العثور على الكتب الصوتية الناتجة في مجلد "Audiobook" الذي سيكون موجودًا أيضًا في الدليل المحلي الذي قمت بتشغيل أمر Docker فيه.

## للحصول على أمر المساعدة للمعلمات (الأوامر) الأخرى التي يحتوي عليها هذا البرنامج، يمكنك تشغيل هذا الأمر

```bash
docker run -it --rm \
    --platform linux/amd64 \
    athomasson2/ebook2audiobook \
    python app.py --help

```


وسيقوم ذلك بإخراج هذا
[أوامر المساعدة](#help-command-output)

### تجميع Docker

يستخدم هذا المشروع Docker Compose لتشغيله محليًا. يمكنك تمكين أو تعطيل دعم GPU من خلال تعيين `gpu-enabled*` أو `gpu-disabled*` في ملف `docker-compose.yml`.

#### خطوات التشغيل

1. **استنساخ المستودع** (إذا لم تكن قد قمت بذلك بالفعل):
   ```bash
   git clone https://github.com/DrewThomasson/ebook2audiobook.git
   cd ebook2audiobook
   ```

2. **تفعيل دعم GPU (مُعطل افتراضيًا)**
  لتفعيل دعم GPU، قم بتعديل ملف `docker-compose.yml` وغيّر `gpu-disabled*` إلى `gpu-enabled*`

3. **بدء الخدمة:**
    ```bash
    docker-compose up -d
    ```

4. **الوصول إلى الخدمة:**
  ستكون الخدمة متاحة على الرابط http://localhost:7860.

#### واجهة الويب الجديدة v2.0 عبر Docker!
![demo_web_gui](../assets/demo_web_gui.gif)

<details>
  <summary>Click to see images of Web GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="../assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="../assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="../assets/gui_3.png">
</details>

## استئجار معالج GPU
لا تملك الأجهزة اللازمة لتشغيله أو ترغب في استئجار وحدة معالجة رسومات (GPU)؟
#### يمكنك استنساخ مساحة Huggingface واستئجار وحدة معالجة رسومات (GPU) مقابل حوالي 0.40 دولار في الساعة.
[عرض تجريبي على Huggingface Space](#عرض-تجريبي-على-Huggingface-Space)

#### أو يمكنك تجربة استخدام Google Colab مجانًا!
(كن حذرًا، حيث سينتهي وقت الجلسة إذا لم تقم بالتفاعل مع Google Colab لفترة من الوقت.)
[Google Colab مجاني](#Google-Colab-مجاني)


## نماذج TTS المحسنة

يمكنك تخصيص نموذج XTTS الخاص بك بسهولة باستخدام هذا المستودع.
[xtts-finetune-webui](https://github.com/daswer123/xtts-finetune-webui)

إذا كنت ترغب في استئجار وحدة معالجة رسومات (GPU) بسهولة، يمكنك أيضًا استنساخ هذه المساحة على Huggingface.
[xtts-finetune-webui-space](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu)

يمكنك أيضًا استخدام المساحة لتقليل الضوضاء في بيانات التدريب بسهولة.
[denoise-huggingface-space](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit)


### مجموعة نماذج TTS المعدلة بدقة

للعثور على مجموعة نماذج TTS المعدلة بدقة، يمكنك زيارة [هذا الرابط](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)

لإنشاء نموذج XTTS مخصص، سيكون من الضروري أيضًا توفير مقطع صوتي مرجعي للصوت:

## عرض توضيحي

صوت يوم ممطر

https://github.com/user-attachments/assets/8486603c-38b1-43ce-9639-73757dfb1031

صوت ديفيد أتينبورو (David Attenborough)

https://github.com/user-attachments/assets/47c846a7-9e51-4eb9-844a-7460402a20a8


## صيغ الكتب الإلكترونية المدعومة

- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`, `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`, `.snb`, `.cbc`, `.rb`, `.tcr`
- **أفضل النتائج**: `.epub` أو `.mobi` للكشف التلقائي للفصول.

## المخرجات

- ينشئ ملف `.m4b` مع البيانات الوصفية والفصول.
- **مثال للمخرجات**: ![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)

## المشاكل الشائعة:
- "إنه بطيء!" - عند استخدام وحدة المعالجة المركزية فقط، يكون الأداء بطيئًا جدًا، ولا يمكن تحسين السرعة إلا من خلال استخدام وحدة معالجة رسومات (GPU) من نوع NVIDIA. [مناقشة حول هذا](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846) لتحقيق توليد متعدد اللغات بسرعة أكبر، أنصحك [بمشروعي الآخر الذي يستخدم piper-tts](https://github.com/DrewThomasson/ebook2audiobookpiper-tts) بدلاً من ذلك (على الرغم من أنه لا يحتوي على استنساخ صوتي بدون تدريب مسبق، والأصوات تكون بجودة سيري، إلا أنه أسرع بكثير على الـ CPU).
- "أواجه مشاكل في التبعيات" - فقط استخدم الـ Docker، فهو معزول بالكامل ويحتوي على وضع غير مرئي (headless). أضف معلمة `h-` بعد `app.py` في أمر تشغيل الـ Docker للحصول على مزيد من المعلومات.
- "أواجه مشكلة في الصوت المقتطع!" - من فضلك أنشئ مشكلة (issue) في هذا الشأن، فأنا لا أتكلم كل اللغات وأحتاج إلى نصائح من كل شخص لتحسين وظيفة تقسيم الجمل في لغات أخرى. 😊

## ما أحتاج المساعدة فيه! 🙌
## [يمكن العثور على القائمة الكاملة للأشياء هنا](https://github.com/DrewThomasson/ebook2audiobook/issues/32)
- أي مساعدة من الأشخاص الذين يتحدثون أي من اللغات المدعومة للمساعدة في طرق تقسيم الجمل بشكل صحيح ستكون مفيدة.
- إمكانية إنشاء أدلة README لعدة لغات (لأن اللغة الوحيدة التي أعرفها هي الإنجليزية 😔)

## شكر خاص

- **Coqui TTS**: [Coqui TTS GitHub](https://github.com/idiap/coqui-ai-TTS)
- **Calibre**: [Calibre Website](https://calibre-ebook.com)
- **FFmpeg**: [FFmpeg Website](https://ffmpeg.org)

- [@shakenbake15 لتحسين طريقة حفظ الفصول](https://github.com/DrewThomasson/ebook2audiobook/issues/8)
- [@wesam-1110111 إلى اللغة العربية README لترجمة ملف](https://github.com/Wesam-1110111)

### [الإصدار القديم v1.0](../legacy/v1.0)

يمكنك مشاهدة الكود [هنا](../legacy/v1.0).

## انضم إلى خادم Discord الخاص بنا!

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/bg5Kx43c6w)](https://discord.gg/bg5Kx43c6w)
