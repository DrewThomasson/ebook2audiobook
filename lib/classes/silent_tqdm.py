import tqdm
import io

# Redirect all tqdm output to null stream for Bark
class SilentTqdm(tqdm.tqdm):
	def __init__(self, *args, **kwargs):
		kwargs['file'] = io.StringIO()
		super().__init__(*args, **kwargs)