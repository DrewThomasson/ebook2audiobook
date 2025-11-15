import torch
from audiocraft.models import MusicGen

print("Running on:", "GPU" if torch.cuda.is_available() else "CPU")

model = MusicGen.get_pretrained('small')
model.set_generation_params(duration=8)
wav = model.generate(descriptions=["deep ambient soundscape with evolving textures"])
model.save_wav(wav, "/outputs/output.wav")

print("✅ Done! File saved to /outputs/output.wav")