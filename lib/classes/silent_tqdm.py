import tqdm.auto
import io
from contextlib import contextmanager

class SilentTqdm(tqdm.auto.tqdm):
	"""A silent tqdm progress bar that writes nothing to the console."""
	def __init__(self, *args, **kwargs):
		kwargs['file'] = io.StringIO()
		super().__init__(*args, **kwargs)

	@staticmethod
	@contextmanager
	def suppress_bark():
		"""Suppress Bark's internal tqdm.auto.tqdm bars without affecting standard tqdm."""
		original = tqdm.auto.tqdm
		tqdm.auto.tqdm = SilentTqdm
		try:
			yield
		finally:
			tqdm.auto.tqdm = original