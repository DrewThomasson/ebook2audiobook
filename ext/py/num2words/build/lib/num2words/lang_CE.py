# -*- coding: utf-8 -*-
# Copyright (c) 2023, Johannes Heinecke.  All Rights Reserved.

# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301 USA

from __future__ import unicode_literals

from .currency import parse_currency_parts
from .lang_EU import Num2Word_EU

# Chechen numbers inflect in case if without noun or
# use a special oblique ending when followed by a counted noun
# 4, 14, 40 and composites thereof agree in class (gender) with the
# noun. Chechen has 6 classes which are indicated by the initial
# letter of 4, 14 and 40. By default it is "д" but
# it can also be "б", "й" or "в".
# Indicate the needed class prefix as follows
#   num2words(4, lang='ce', case="abs", clazz="б")


CARDINALS = {
    "casenames": {
        "abs": "Им.",
        "gen": "Род.",
        "dat": "Дат.",
        "erg": "Эрг;",
        "instr": "Твор.",
        "mat": "Вещ.",
        "comp": "Сравнит.",
        "all": "Местн.",
    },
    "casesuffix_cons": {  # to be added to numerals with final consonant
        "gen": "аннан",
        "dat": "анна",
        "erg": "амма",
        "instr": "анца",
        "mat": "аннах",
        "comp": "аннал",
        "all": "анга",
        "obl": "ан",
        "ORD": "алгӀа",
    },
    "casesuffix_voc": {  # to be added to numerals with final vowel
        "gen": "ннан",
        "dat": "нна",
        "erg": "мма",
        "instr": "нца",
        "mat": "ннах",
        "comp": "ннал",
        "all": "нга",
        "obl": "н",
        "ORD": "лгӀа",
    },
    0: {
        "attr": "ноль",
        "abs": "ноль",
        "gen": "нолан",
        "dat": "нолана",
        "erg": "ноло",
        "instr": "ноланца",
        "mat": "ноланах",
        "comp": "ноланал",
        "all": "ноланга",
    },
    1: {
        "attr": "цхьа",  # in front of nouns in ABS
        "obl": "цхьана",  # with nouns in other cases than ABS
        "abs": "цхьаъ",
        "gen": "цхьаннан",
        "dat": "цхьанна",
        "erg": "цхьамма",
        "instr": "цхьаьнца",
        "mat": "цхьаннах",
        "comp": "цхьаннал",
        "all": "цхаьнга",
        "ORD": "цхьалгӀа",
    },
    2: {
        "attr": "ши",  # in front of 100, 1000
        "obl": "шина",
        "abs": "шиъ",
        "gen": "шиннан",
        "dat": "шинна",
        "erg": "шимма",
        "instr": "шинца",
        "mat": "шиннах",
        "comp": "шиннал",
        "all": "шинга",
        "ORD": "шолгӀа",
    },
    3: {
        "attr": "кхо",
        "obl": "кхона",
        "abs": "кхоъ",
        "gen": "кхааннан",
        "dat": "кхаанна",
        "erg": "кхаамма",
        "instr": "кхаанца",
        "mat": "кхааннах",
        "comp": "кхааннал",
        "all": "кхаанга",
        "ORD": "кхоалгӀа",
    },
    4: {
        "attr": "д*и",
        "obl": "д*еа",
        "abs": "д*иъ",
        "gen": "д*еаннан",
        "dat": "д*еанна",
        "erg": "д*еамма",
        "instr": "д*еанца",
        "mat": "д*еаннах",
        "comp": "д*еаннал",
        "all": "д*еанга",
        "ORD": "д*оьалгӀа",
    },
    5: {
        "attr": "пхи",
        "obl": "пхеа",
        "abs": "пхиъ",
        "gen": "пхеаннан",
        "dat": "пхеанна",
        "erg": "пхеамма",
        "instr": "нхеанца",
        "mat": "пхеаннах",
        "comp": "пхеаннал",
        "all": "пхеанга",
        "ORD": "пхоьалгӀа",
    },
    6: {
        "abs": "ялх",
        "attr": "ялх",
        "ORD": "йолхалгӀа",
    },
    7: {
        "abs": "ворхӀ",
        "attr": "ворхӀ",
        "ORD": "ворхӀалгӀа",
    },
    8: {
        "abs": "бархӀ",
        "attr": "бархӀ",
        "ORD": "борхӀалӀа",
    },
    9: {
        "abs": "исс",
        "attr": "исс",
        "ORD": "уьссалгӀа",
    },
    10: {
        "attr": "итт",
        "abs": "итт",
        "gen": "иттаннан",
        "dat": "иттанна",
        "erg": "иттамма",
        "instr": "иттанца",
        "mat": "иттаннах",
        "comp": "иттаннал",
        "all": "иттанга",
        "ORD": "уьтталгӀа",
    },
    11: {
        "abs": "цхьайтта",
        "attr": "цхьайтта",
        "ORD": "цхьайтталгӀа",
    },
    12: {
        "abs": "шийтта",
        "attr": "шийтта",
        "ORD": "шийтталга",
    },
    13: {
        "abs": "кхойтта",
        "attr": "кхойтта",
        "ORD": "кхойтталгӀа",
    },
    14: {
        "abs": "д*ейтта",
        "attr": "д*ейтта",
        "ORD": "д*ейтталгӀа",
    },
    15: {
        "abs": "пхийтта",
        "attr": "пхийтта",
        "ORD": "пхийтталгӀа",
    },
    16: {
        "abs": "ялхитта",
        "attr": "ялхитта",
        "ORD": "ялхитталгӀа",
    },
    17: {
        "abs": "вуьрхӀитта",
        "attr": "вуьрхӀитта",
        "ORD": "вуьрхӀитталгӀа",
    },
    18: {
        "abs": "берхӀитта",
        "attr": "берхӀитта",
        "ORD": "берхитталӀа",
    },
    19: {
        "abs": "ткъайесна",
        "attr": "ткъайесна",
        "ORD": "ткъаесналгӀа",
    },
    20: {
        "abs": "ткъа",
        "gen": "ткъаннан",
        "dat": "ткъанна",
        "erg": "ткъамма",
        "instr": "ткъанца",
        "mat": "ткъаннах",
        "comp": "ткъаннал",
        "all": "ткъанга",
        "attr": "ткъе",
        "ORD": "ткъолгӀа",
    },
    40: {
        "abs": "шовзткъа",
        "attr": "шовзткъе",
        "ORD": "шовзткъалгІа",
    },
    60: {
        "abs": "кхузткъа",
        "attr": "кхузткъе",
        "ORD": "кхузткъалгІа",
    },
    80: {
        "abs": "дезткъа",
        "attr": "дезткъе",
        "ORD": "дезткъалгІа",
    },
    100: {
        "attr": "бӀе",
        "abs": "бӀе",
        "obl": "бӀен",
        "gen": "бӀеннан",
        "dat": "бӀенна",
        "erg": "бӀемма",
        "instr": "бӀенца",
        "mat": "бӀеннах",
        "comp": "бӀеннал",
        "all": "бӀенга",
        "ORD": "бІолгІа",
    },
    1000: {
        "attr": "эзар",
        "abs": "эзар",
        "obl": "эзаран",
        "gen": "эзарнан",
        "dat": "эзарна",
        "erg": "эзарно",
        "instr": "эзарнаца",
        "mat": "эзарнах",
        "comp": "эзарнал",
        "all": "эзаранга",
        "ORD": "эзарлагІа",
    },
    1000000: {
        "attr": "миллион",
        "abs": "миллион",
        "ORD": "миллионалгІа",
    },
}

ILLIONS = {
    6: {
        "attr": "миллион",
        "abs": "миллион",
        "ORD": "миллионалгІа",
    },
    9: {
        "attr": "миллиард",
        "abs": "миллиард",
        "ORD": "миллиардалгІа",
    },
    12: {
        "attr": "биллион",
        "abs": "биллион",
        "ORD": "биллионалгІа",
    },
    15: {
        "attr": "биллиард",
        "abs": "биллиард",
        "ORD": "биллиардалгІа",
    },
    18: {
        "attr": "триллион",
        "abs": "триллион",
        "ORD": "триллионалгІа",
    },
    21: {
        "attr": "триллиард",
        "abs": "триллиард",
        "ORD": "триллиардалгІа",
    },
    24: {
        "attr": "квадриллион",
        "abs": "квадриллион",
        "ORD": "квадриллионалгІа",
    },
    27: {
        "attr": "квадриллиард",
        "abs": "квадриллиард",
        "ORD": "квадриллиардалгІа",
    },
    30: {
        "attr": "квинтиллион",
        "abs": "квинтиллион",
        "ORD": "квинтиллионалгІа",
    },
    33: {
        "attr": "квинтиллиард",
        "abs": "квинтиллиард",
        "ORD": "квинтиллиардалгІа",
    },
}


MINUS = "минус"
# DECIMALPOINT = "запятая"  # check !
DECIMALPOINT = "а"


class Num2Word_CE(Num2Word_EU):
    CURRENCY_FORMS = {
        # currency code: (sg, pl), (sg, pl)
        "EUR": (("Евро", "Евро"), ("Сент", "Сенташ")),
        "RUB": (("Сом", "Сомаш"), ("Кепек", "Кепекаш")),
        "USD": (("Доллар", "Доллараш"), ("Сент", "Сенташ")),
        "GBP": (("Фунт", "Фунташ"), ("Пенни", "Пенни")),
    }

    def setup(self):
        Num2Word_EU.setup(self)
        self.negword = "минус"
        self.pointword = "запятая"  # check !
        # self.errmsg_nonnum = (
        #    u"Seulement des nombres peuvent être convertis en mots."
        #    )
        # self.errmsg_toobig = (
        #    u"Nombre trop grand pour être converti en mots (abs(%s) > %s)."
        #    )
        # self.exclude_title = ["et", "virgule", "moins"]
        self.mid_numwords = []
        self.low_numwords = []
        self.ords = {}

    def to_ordinal(self, number, clazz="д"):
        # implement here your code. number is the integer to
        # be transformed into an ordinal as a word (str)
        # which is returned
        return self.to_cardinal(number, clazz=clazz, case="ORD")

    def to_cardinal(self, number, clazz="д", case="abs"):
        if isinstance(number, float):
            entires = self.to_cardinal(int(number))
            float_part = str(number).split(".")[1]
            postfix = " ".join(
                # Drops the trailing zero and comma
                [self.to_cardinal(int(c)) for c in float_part]
            )
            return entires + " " + DECIMALPOINT + " " + postfix

        elif number < 20:
            return self.makecase(number, case, clazz)
        elif number < 100:
            twens = number // 20
            units = number % 20
            base = twens * 20
            if units == 0:
                return self.makecase(number, case, clazz)
            else:
                twenties = self.makecase(base, "attr", clazz)
                rest = self.to_cardinal(units, clazz=clazz, case=case)
                return twenties + " " + rest.replace("д*", clazz)
        elif number < 1000:
            hundreds = number // 100
            tens = number % 100
            if hundreds > 1:
                hundert = (
                    CARDINALS[hundreds]["attr"].replace("д*", clazz) + " "
                )
            else:
                hundert = ""
            if tens != 0:
                rest = self.to_cardinal(tens, clazz=clazz, case=case)
                return hundert + CARDINALS[100]["abs"] + " " + rest
            else:
                return hundert + self.makecase(100, case, clazz)
        elif number < 1000000:
            thousands = number // 1000
            hundert = number % 1000
            if hundert > 0:
                tcase = "attr"
            else:
                tcase = case
            if thousands > 1:
                tausend = (
                    self.to_cardinal(thousands, clazz=clazz, case="attr")
                    + " "
                    + CARDINALS[1000][tcase]
                )
            else:
                tausend = self.makecase(1000, tcase, clazz)

            if hundert != 0:
                rest = " " + self.to_cardinal(hundert, clazz=clazz, case=case)
            else:
                rest = ""
            return tausend + rest

        elif number < 10**34:
            out = []
            for pot in reversed([6, 9, 12, 15, 18, 21, 24, 27, 30, 33]):
                # 3 digits of billion, trillion etc
                step = number // 10**pot % 1000
                if step > 0:
                    words = self.to_cardinal(step, clazz=clazz, case="attr")
                    out.append(words + " " + ILLIONS[pot]["attr"])
            rest = number % 10**6
            if rest:
                out.append(self.to_cardinal(rest, clazz=clazz, case=case))
            return " ".join(out)

        return "NOT IMPLEMENTED"

    def _money_verbose(self, number, currency, case):
        mcase = "attr"
        if case != "abs":
            mcase = "obl"
        return self.to_cardinal(number, case=mcase)

    def _cents_verbose(self, number, currency, case):
        mcase = "attr"
        if case != "abs":
            mcase = "obl"
        return self.to_cardinal(number, case=mcase)

    def to_currency(
        self,
        val,
        currency="RUB",
        cents=True,
        separator=",",
        adjective=False,
        case="abs",
    ):
        """
        Args:
            val: Numeric value
            currency (str): Currency code
            cents (bool): Verbose cents
            separator (str): Cent separator
            adjective (bool): Prefix currency name with adjective
        Returns:
            str: Formatted string

        """
        left, right, is_negative = parse_currency_parts(val)

        try:
            cr1, cr2 = self.CURRENCY_FORMS[currency]
            devise = cr1[0]
            centime = cr2[0]
        except KeyError:
            raise NotImplementedError(
                'Currency code "%s" not implemented for "%s"'
                % (currency, self.__class__.__name__)
            )

        minus_str = "%s " % self.negword.strip() if is_negative else ""
        money_str = self._money_verbose(left, currency, case)
        cents_str = (
            self._cents_verbose(right, currency, case)
            if cents
            else self._cents_terse(right, currency)
        )

        return "%s%s %s%s %s %s" % (
            minus_str,
            money_str,
            devise,  # always singular
            separator,
            cents_str,
            centime,
        )

    def to_ordinal_num(self, number):
        self.verify_ordinal(number)
        return str(number) + "-й"

    def to_year(self, year, case="abs"):
        return self.to_cardinal(year, case=case)

    def makecase(self, number, case, clazz):
        # print("ZZZZ", number, CARDINALS[number])
        if case in CARDINALS[number]:
            return CARDINALS[number][case].replace("д*", clazz)
        else:
            if CARDINALS[number]["abs"][-1] in "а":
                return (
                    CARDINALS[number]["abs"].replace("д*", clazz)
                    + CARDINALS["casesuffix_voc"][case]
                )
            else:
                return (
                    CARDINALS[number]["abs"].replace("д*", clazz)
                    + CARDINALS["casesuffix_cons"][case]
                )
