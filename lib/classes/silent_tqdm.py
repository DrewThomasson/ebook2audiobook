import tqdm.auto
import io
from contextlib import contextmanager

class SilentTqdm(tqdm.auto.tqdm):
	def __init__(self, *args, **kwargs):
		kwargs['file'] = io.StringIO()
		super().__init__(*args, **kwargs)

	@staticmethod
	@contextmanager
	def suppress_bark():
		original = tqdm.auto.tqdm
		tqdm.auto.tqdm = SilentTqdm
		try:
			yield
		finally:
			tqdm.auto.tqdm = original
