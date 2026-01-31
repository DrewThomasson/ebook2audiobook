num2words library - Convert numbers to words in multiple languages
==================================================================

.. image:: https://img.shields.io/pypi/v/num2words.svg
   :target: https://pypi.python.org/pypi/num2words

.. image:: https://travis-ci.org/savoirfairelinux/num2words.svg?branch=master
    :target: https://travis-ci.org/savoirfairelinux/num2words

.. image:: https://coveralls.io/repos/github/savoirfairelinux/num2words/badge.svg?branch=master
    :target: https://coveralls.io/github/savoirfairelinux/num2words?branch=master


``num2words`` is a library that converts numbers like ``42`` to words like ``forty-two``.
It supports multiple languages (see the list below for full list
of languages) and can even generate ordinal numbers like ``forty-second``
(although this last feature is a bit buggy for some languages at the moment).

The project is hosted on GitHub_. Contributions are welcome.

.. _GitHub: https://github.com/savoirfairelinux/num2words

Installation
------------

The easiest way to install ``num2words`` is to use pip::

    pip install num2words

Otherwise, you can download the source package and then execute::

    python setup.py install

The test suite in this library is new, so it's rather thin, but it can be run with::

    python setup.py test

To run the full CI test suite which includes linting and multiple python environments::

    pip install tox
    tox

Usage
-----
Command line::

    $ num2words 10001
    ten thousand and one
    $ num2words 24,120.10
    twenty-four thousand, one hundred and twenty point one
    $ num2words 24,120.10 -l es
    veinticuatro mil ciento veinte punto uno
    $num2words 2.14 -l es --to currency
    dos euros con catorce céntimos

In code there's only one function to use::

    >>> from num2words import num2words
    >>> num2words(42)
    forty-two
    >>> num2words(42, to='ordinal')
    forty-second
    >>> num2words(42, lang='fr')
    quarante-deux

Besides the numerical argument, there are two main optional arguments, ``to:`` and ``lang:``

**to:** The converter to use. Supported values are:

* ``cardinal`` (default)
* ``ordinal``
* ``ordinal_num``
* ``year``
* ``currency``

**lang:** The language in which to convert the number. Supported values are:

* ``en`` (English, default)
* ``am`` (Amharic)
* ``ar`` (Arabic)
* ``az`` (Azerbaijani)
* ``be`` (Belarusian)
* ``bn`` (Bangladeshi)
* ``ca`` (Catalan)
* ``ce`` (Chechen)
* ``cs`` (Czech)
* ``cy`` (Welsh)
* ``da`` (Danish)
* ``de`` (German)
* ``en_GB`` (English - Great Britain)
* ``en_IN`` (English - India)
* ``en_NG`` (English - Nigeria)
* ``es`` (Spanish)
* ``es_CO`` (Spanish - Colombia)
* ``es_CR`` (Spanish - Costa Rica)
* ``es_GT`` (Spanish - Guatemala)
* ``es_VE`` (Spanish - Venezuela)
* ``eu`` (EURO)
* ``fa`` (Farsi)
* ``fi`` (Finnish)
* ``fr`` (French)
* ``fr_BE`` (French - Belgium)
* ``fr_CH`` (French - Switzerland)
* ``fr_DZ`` (French - Algeria)
* ``he`` (Hebrew)
* ``hi`` (Hindi)
* ``hu`` (Hungarian)
* ``hy`` (Armenian)
* ``id`` (Indonesian)
* ``is`` (Icelandic)
* ``it`` (Italian)
* ``ja`` (Japanese)
* ``kn`` (Kannada)
* ``ko`` (Korean)
* ``kz`` (Kazakh)
* ``mn`` (Mongolian)
* ``lt`` (Lithuanian)
* ``lv`` (Latvian)
* ``nl`` (Dutch)
* ``no`` (Norwegian)
* ``pl`` (Polish)
* ``pt`` (Portuguese)
* ``pt_BR`` (Portuguese - Brazilian)
* ``ro`` (Romanian)
* ``ru`` (Russian)
* ``sl`` (Slovene)
* ``sk`` (Slovak)
* ``sr`` (Serbian)
* ``sv`` (Swedish)
* ``te`` (Telugu)
* ``tet`` (Tetum)
* ``tg`` (Tajik)
* ``tr`` (Turkish)
* ``th`` (Thai)
* ``uk`` (Ukrainian)
* ``vi`` (Vietnamese)
* ``zh`` (Chinese - Traditional)
* ``zh_CN`` (Chinese - Simplified / Mainland China)
* ``zh_TW`` (Chinese - Traditional / Taiwan)
* ``zh_HK`` (Chinese - Traditional / Hong Kong)

You can supply values like ``fr_FR``; if the country doesn't exist but the
language does, the code will fall back to the base language (i.e. ``fr``). If
you supply an unsupported language, ``NotImplementedError`` is raised.
Therefore, if you want to call ``num2words`` with a fallback, you can do::

    try:
        return num2words(42, lang=mylang)
    except NotImplementedError:
        return num2words(42, lang='en')

Additionally, some converters and languages support other optional arguments
that are needed to make the converter useful in practice.

Wiki
----
For additional information on some localization please check the Wiki_.
And feel free to propose wiki enhancement.

.. _Wiki: https://github.com/savoirfairelinux/num2words/wiki

History
-------

``num2words`` is based on an old library, ``pynum2word``, created by Taro Ogawa
in 2003. Unfortunately, the library stopped being maintained and the author
can't be reached. There was another developer, Marius Grigaitis, who in 2011
added Lithuanian support, but didn't take over maintenance of the project.

I am thus basing myself on Marius Grigaitis' improvements and re-publishing
``pynum2word`` as ``num2words``.

Virgil Dupras, Savoir-faire Linux