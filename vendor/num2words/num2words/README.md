# Add new language

for each new language you must create a file `lang_NN.py` where `NN` is the 
ISO 639-1 or ISO 639-3 [language code](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes).

This class must be a subclass of `Num2Word_EU` and implement at least the following methods

```
to_cardinal(self, number)
to_ordinal(self, number)
```

To integrate your language into the `num2words` module, add the name of  your file
to the import list in [num2words/__init__.py](num2words/__init__.py) (top of the file),
and `'nn': lang_NN.Num2Word_NN()` to the `CONVERTER_CLASSES` list in the same file.
Do not forget to remplace `NN` by the appropriate ISO 639 language code.

The following is a template for a new language class

```
from .lang_EU import Num2Word_EU

class Num2Word_CY(Num2Word_EU):
    def setup(self):
        Num2Word_EU.setup(self)

    def __init__(self):
        pass

    def to_ordinal(self, number):
	# implement here your code. number is the integer to be transformed into an ordinal
        # as a word (str)
	# which is returned
	return "NOT IMPLEMENTED"

    def to_cardinal(self, number):
	# implement here your code. number is the integer to be transformed into an cardinal
        # as a word (str)
	# which is returned
	return "NOT IMPLEMENTED"
```

You can use as manu auxiliary methods as you need to make your code efficient and readable.
If you need further options like Gender, Formal/Informal, add those parameters to the methods,
e.g.

```
    def to_ordinal(self, number, gender="fem", informal=True)
	# your code
	pass
```

More inspiration can be found in existing `num2words/lang_NN.py` files

## Code validation

In order to get your contribution merged into the main project, your code must test the validation tests.
For this install the packages needed to test

```
pip install -r requirements-test.txt
```

run `tox` and `coverage` to check that the code is well formated and all parts of the code are tested

```
tox
python3 -m coverage report -m
```

