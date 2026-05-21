# StyleTTS 2: Towards Human-Level Text-to-Speech through Style Diffusion and Adversarial Training with Large Speech Language Models

### Yinghao Aaron Li, Cong Han, Vinay S. Raghavan, Gavin Mischler, Nima Mesgarani

> In this paper, we present StyleTTS 2, a text-to-speech (TTS) model that leverages style diffusion and adversarial training with large speech language models (SLMs) to achieve human-level TTS synthesis. StyleTTS 2 differs from its predecessor by modeling styles as a latent random variable through diffusion models to generate the most suitable style for the text without requiring reference speech, achieving efficient latent diffusion while benefiting from the diverse speech synthesis offered by diffusion models. Furthermore, we employ large pre-trained SLMs, such as WavLM, as discriminators with our novel differentiable duration modeling for end-to-end training, resulting in improved speech naturalness. StyleTTS 2 surpasses human recordings on the single-speaker LJSpeech dataset and matches it on the multispeaker VCTK dataset as judged by native English speakers. Moreover, when trained on the LibriTTS dataset, our model outperforms previous publicly available models for zero-shot speaker adaptation. This work achieves the first human-level TTS synthesis on both single and multispeaker datasets, showcasing the potential of style diffusion and adversarial training with large SLMs.

Paper: [https://arxiv.org/abs/2306.07691](https://arxiv.org/abs/2306.07691)

Audio samples: [https://styletts2.github.io/](https://styletts2.github.io/)

Online demo: [Hugging Face](https://huggingface.co/spaces/styletts2/styletts2) (thank [@fakerybakery](https://github.com/fakerybakery) for the wonderful online demo)

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yl4579/StyleTTS2/blob/main/) [![Discord](https://img.shields.io/discord/1197679063150637117?logo=discord&logoColor=white&label=Join%20our%20Community)](https://discord.gg/ha8sxdG2K4)

## TODO
- [x] Training and inference demo code for single-speaker models (LJSpeech)
- [x] Test training code for multi-speaker models (VCTK and LibriTTS)
- [x] Finish demo code for multispeaker model and upload pre-trained models
- [x] Add a finetuning script for new speakers with base pre-trained multispeaker models
- [ ] Fix DDP (accelerator) for `train_second.py` **(I have tried everything I could to fix this but had no success, so if you are willing to help, please see [#7](https://github.com/yl4579/StyleTTS2/issues/7))**

## Pre-requisites
1. Python >= 3.7
2. Clone this repository:
```bash
git clone https://github.com/yl4579/StyleTTS2.git
cd StyleTTS2
```
3. Install python requirements: 
```bash
pip install -r requirements.txt
```
On Windows add:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 -U
```
Also install phonemizer and espeak if you want to run the demo:
```bash
pip install phonemizer
sudo apt-get install espeak-ng
```
4. Download and extract the [LJSpeech dataset](https://keithito.com/LJ-Speech-Dataset/), unzip to the data folder and upsample the data to 24 kHz. The text aligner and pitch extractor are pre-trained on 24 kHz data, but you can easily change the preprocessing and re-train them using your own preprocessing. 
For LibriTTS, you will need to combine train-clean-360 with train-clean-100 and rename the folder train-clean-460 (see [val_list_libritts.txt](https://github.com/yl4579/StyleTTS/blob/main/Data/val_list_libritts.txt) as an example).

## Training
First stage training:
```bash
accelerate launch train_first.py --config_path ./Configs/config.yml
```
Second stage training **(DDP version not working, so the current version uses DP, again see [#7](https://github.com/yl4579/StyleTTS2/issues/7) if you want to help)**:
```bash
python train_second.py --config_path ./Configs/config.yml
```
You can run both consecutively and it will train both the first and second stages. The model will be saved in the format "epoch_1st_%05d.pth" and "epoch_2nd_%05d.pth". Checkpoints and Tensorboard logs will be saved at `log_dir`. 

The data list format needs to be `filename.wav|transcription|speaker`, see [val_list.txt](https://github.com/yl4579/StyleTTS2/blob/main/Data/val_list.txt) as an example. The speaker labels are needed for multi-speaker models because we need to sample reference audio for style diffusion model training. 

### Important Configurations
In [config.yml](https://github.com/yl4579/StyleTTS2/blob/main/Configs/config.yml), there are a few important configurations to take care of:
- `OOD_data`: The path for out-of-distribution texts for SLM adversarial training. The format should be `text|anything`.
- `min_length`: Minimum length of OOD texts for training. This is to make sure the synthesized speech has a minimum length.
- `max_len`: Maximum length of audio for training. The unit is frame. Since the default hop size is 300, one frame is approximately `300 / 24000` (0.0125) second. Lowering this if you encounter the out-of-memory issue. 
- `multispeaker`: Set to true if you want to train a multispeaker model. This is needed because the architecture of the denoiser is different for single and multispeaker models.
- `batch_percentage`: This is to make sure during SLM adversarial training there are no out-of-memory (OOM) issues. If you encounter OOM problem, please set a lower number for this. 

### Pre-trained modules
In [Utils](https://github.com/yl4579/StyleTTS2/tree/main/Utils) folder, there are three pre-trained models: 
- **[ASR](https://github.com/yl4579/StyleTTS2/tree/main/Utils/ASR) folder**: It contains the pre-trained text aligner, which was pre-trained on English (LibriTTS), Japanese (JVS), and Chinese (AiShell) corpus. It works well for most other languages without fine-tuning, but you can always train your own text aligner with the code here: [yl4579/AuxiliaryASR](https://github.com/yl4579/AuxiliaryASR).
- **[JDC](https://github.com/yl4579/StyleTTS2/tree/main/Utils/JDC) folder**: It contains the pre-trained pitch extractor, which was pre-trained on English (LibriTTS) corpus only. However, it works well for other languages too because F0 is independent of language. If you want to train on singing corpus, it is recommended to train a new pitch extractor with the code here: [yl4579/PitchExtractor](https://github.com/yl4579/PitchExtractor).
- **[PLBERT](https://github.com/yl4579/StyleTTS2/tree/main/Utils/PLBERT) folder**: It contains the pre-trained [PL-BERT](https://arxiv.org/abs/2301.08810) model, which was pre-trained on English (Wikipedia) corpus only. It probably does not work very well on other languages, so you will need to train a different PL-BERT for different languages using the repo here: [yl4579/PL-BERT](https://github.com/yl4579/PL-BERT). You can also use the [multilingual PL-BERT](https://huggingface.co/papercup-ai/multilingual-pl-bert) which supports 14 languages. 

### Common Issues
- **Loss becomes NaN**: If it is the first stage, please make sure you do not use mixed precision, as it can cause loss becoming NaN for some particular datasets when the batch size is not set properly (need to be more than 16 to work well). For the second stage, please also experiment with different batch sizes, with higher batch sizes being more likely to cause NaN loss values. We recommend the batch size to be 16. You can refer to issues [#10](https://github.com/yl4579/StyleTTS2/issues/10) and [#11](https://github.com/yl4579/StyleTTS2/issues/11) for more details.
- **Out of memory**: Please either use lower `batch_size` or `max_len`. You may refer to issue [#10](https://github.com/yl4579/StyleTTS2/issues/10) for more information.
- **Non-English dataset**: You can train on any language you want, but you will need to use a pre-trained PL-BERT model for that language. We have a pre-trained [multilingual PL-BERT](https://huggingface.co/papercup-ai/multilingual-pl-bert) that supports 14 languages. You may refer to [yl4579/StyleTTS#10](https://github.com/yl4579/StyleTTS/issues/10) and [#70](https://github.com/yl4579/StyleTTS2/issues/70) for some examples to train on Chinese datasets. 

## Finetuning
The script is modified from `train_second.py` which uses DP, as DDP does not work for `train_second.py`. Please see the bold section above if you are willing to help with this problem. 
```bash
python train_finetune.py --config_path ./Configs/config_ft.yml
```
Please make sure you have the LibriTTS checkpoint downloaded and unzipped under the folder. The default configuration `config_ft.yml` finetunes on LJSpeech with 1 hour of speech data (around 1k samples) for 50 epochs. This took about 4 hours to finish on four NVidia A100. The quality is slightly worse (similar to NaturalSpeech on LJSpeech) than LJSpeech model trained from scratch with 24 hours of speech data, which took around 2.5 days to finish on four A100. The samples can be found at [#65 (comment)](https://github.com/yl4579/StyleTTS2/discussions/65#discussioncomment-7668393). 

If you are using a **single GPU** (because the script doesn't work with DDP) and want to save training speed and VRAM, you can do (thank [@korakoe](https://github.com/korakoe) for making the script at [#100](https://github.com/yl4579/StyleTTS2/pull/100)):
```bash
accelerate launch --mixed_precision=fp16 --num_processes=1 train_finetune_accelerate.py --config_path ./Configs/config_ft.yml
```
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yl4579/StyleTTS2/blob/main/Colab/StyleTTS2_Finetune_Demo.ipynb)

### Common Issues
[@Kreevoz](https://github.com/Kreevoz) has made detailed notes on common issues in finetuning, with suggestions in maximizing audio quality: [#81](https://github.com/yl4579/StyleTTS2/discussions/81). Some of these also apply to training from scratch. [@IIEleven11](https://github.com/IIEleven11) has also made a guideline for fine-tuning: [#128](https://github.com/yl4579/StyleTTS2/discussions/128).

- **Out of memory after `joint_epoch`**: This is likely because your GPU RAM is not big enough for SLM adversarial training run. You may skip that but the quality could be worse. Setting `joint_epoch` a larger number than `epochs` could skip the SLM advesariral training.

## Inference
Please refer to [Inference_LJSpeech.ipynb](https://github.com/yl4579/StyleTTS2/blob/main/Demo/Inference_LJSpeech.ipynb) (single-speaker) and [Inference_LibriTTS.ipynb](https://github.com/yl4579/StyleTTS2/blob/main/Demo/Inference_LibriTTS.ipynb) (multi-speaker) for details. For LibriTTS, you will also need to download [reference_audio.zip](https://huggingface.co/yl4579/StyleTTS2-LibriTTS/resolve/main/reference_audio.zip) and unzip it under the `demo` before running the demo. 

- The pretrained StyleTTS 2 on LJSpeech corpus in 24 kHz can be downloaded at [https://huggingface.co/yl4579/StyleTTS2-LJSpeech/tree/main](https://huggingface.co/yl4579/StyleTTS2-LJSpeech/tree/main).

  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yl4579/StyleTTS2/blob/main/Colab/StyleTTS2_Demo_LJSpeech.ipynb)

- The pretrained StyleTTS 2 model on LibriTTS can be downloaded at [https://huggingface.co/yl4579/StyleTTS2-LibriTTS/tree/main](https://huggingface.co/yl4579/StyleTTS2-LibriTTS/tree/main). 

  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yl4579/StyleTTS2/blob/main/Colab/StyleTTS2_Demo_LibriTTS.ipynb)


You can import StyleTTS 2 and run it in your own code. However, the inference depends on a GPL-licensed package, so it is not included directly in this repository. A [GPL-licensed fork](https://github.com/NeuralVox/StyleTTS2) has an importable script, as well as an experimental streaming API, etc. A [fully MIT-licensed package](https://pypi.org/project/styletts2/) that uses gruut (albeit lower quality due to mismatch between phonemizer and gruut) is also available.  

***Before using these pre-trained models, you agree to inform the listeners that the speech samples are synthesized by the pre-trained models, unless you have the permission to use the voice you synthesize. That is, you agree to only use voices whose speakers grant the permission to have their voice cloned, either directly or by license before making synthesized voices public, or you have to publicly announce that these voices are synthesized if you do not have the permission to use these voices.*** 

### Common Issues
- **High-pitched background noise**: This is caused by numerical float differences in older GPUs. For more details, please refer to issue [#13](https://github.com/yl4579/StyleTTS2/issues/13). Basically, you will need to use more modern GPUs or do inference on CPUs.
- **Pre-trained model license**: You only need to abide by the above rules if you use **the pre-trained models** and the voices are **NOT** in the training set, i.e., your reference speakers are not from any open access dataset. For more details of rules to use the pre-trained models, please see [#37](https://github.com/yl4579/StyleTTS2/issues/37).

## References
- [archinetai/audio-diffusion-pytorch](https://github.com/archinetai/audio-diffusion-pytorch)
- [jik876/hifi-gan](https://github.com/jik876/hifi-gan)
- [rishikksh20/iSTFTNet-pytorch](https://github.com/rishikksh20/iSTFTNet-pytorch)
- [nii-yamagishilab/project-NN-Pytorch-scripts/project/01-nsf](https://github.com/nii-yamagishilab/project-NN-Pytorch-scripts/tree/master/project/01-nsf)

## License

Code: MIT License

Pre-Trained Models: Before using these pre-trained models, you agree to inform the listeners that the speech samples are synthesized by the pre-trained models, unless you have the permission to use the voice you synthesize. That is, you agree to only use voices whose speakers grant the permission to have their voice cloned, either directly or by license before making synthesized voices public, or you have to publicly announce that these voices are synthesized if you do not have the permission to use these voices.
