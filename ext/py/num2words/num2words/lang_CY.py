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

# Welsh numerals differs to many other languages since the counted
# object does not follow the numeral but is inserted between
# e.g. "23 hours" is
#   tri awr ar hugain
#   3   hour on twenty
# in addition to that some numeral trigger a mutation on the following word
# either another numeral or the counted object
# (https://en.wikipedia.org/wiki/Consonant_mutation#Welsh)
# e.g. "23 dogs" (aspirated mutation, c -> ch)
#  tri chi ar hugain
#  3   dog on twenty
# but "22 dogs" (soft mutation, c -> g)
#  dau gi  ar hugain
#  2   dog on twenty
# and "24 dogs" (no mutation)
#  pedwar ci ar hugain
#  4      dog on twenty
# (BTW, the counted word is always in singular when following a numeral)
# numerals are mutated as well
# e.g. "300"
#    tri chant
#    3   hundred
# "200"
#    dau gant
#    2   hundred
# "500"
#    pump cant
#    5    hundreds
# the numerals for 2, 3 and 4 are different in function of gender (MASC, FEM)
#    2 cats
#    dwy gath

#    2 dogs
#    dau gi

#    2000
#    dwy fil

#    3000
#    tair mil

# to add the counted object in the correct position use
#   num2words(17, lang="cy", counted="ci", gender="masc")
#   num2words(17, lang="cy", counted="cath", gender="fem")
# if the number is > 99, use plural form of counted object
#   num2words(117, lang="cy", counted="cathod", gender="fem")


# Globals
# -------

OBJ = "__OBJECT__"

CARDINAL_WORDS = {
    # masc, fem, triggers mutation
    0: [("dim", None), (OBJ, None)],
    1: [("un", None), (OBJ, None)],
    2: [("dau", "SM"), (OBJ, None)],
    3: [("tri", "AM"), (OBJ, None)],
    4: [("pedwar", None), (OBJ, None)],
    5: [("pump", None), (OBJ, None)],
    6: [("chwech", "AM"), (OBJ, None)],
    7: [("saith", None), (OBJ, None)],
    8: [("wyth", None), (OBJ, None)],
    9: [("naw", None), (OBJ, None)],
    10: [("deg", None), (OBJ, None)],
    11: [("un", None), (OBJ, None), ("ar ddeg", None)],
    12: [("deuddeg", None), (OBJ, None)],
    13: [("tri", "AM"), (OBJ, None), ("ar ddeg", None)],
    14: [("pedwar", None), (OBJ, None), ("ar ddeg", None)],
    15: [("pymtheg", None), (OBJ, None)],
    16: [("un", None), (OBJ, None), ("ar bymtheg", None)],
    17: [("dau", "SM"), (OBJ, None), ("ar bymtheg", None)],
    18: [("deunaw", None), (OBJ, None)],
    19: [("pedwar", None), ("ar bymtheg", None)],
}

CARDINAL_WORDS_FEM = {
    # masc, fem, triggers mutation
    0: [("dim", None), (OBJ, None)],
    1: [("un", None), (OBJ, None)],
    2: [("dwy", "SM"), (OBJ, None)],
    3: [("tair", None), (OBJ, None)],
    4: [("pedair", None), (OBJ, None)],
    5: [("pump", None), (OBJ, None)],
    6: [("chwech", "AM"), (OBJ, None)],
    7: [("saith", None), (OBJ, None)],
    8: [("wyth", None), (OBJ, None)],
    9: [("naw", None), (OBJ, None)],
    10: [("deg", None), (OBJ, None)],
    11: [("un", None), (OBJ, None), ("ar ddeg", None)],
    12: [("deuddeg", None), (OBJ, None)],
    13: [("tair", None), (OBJ, None), ("ar ddeg", None)],
    14: [("pedair", None), (OBJ, None), ("ar ddeg", None)],
    15: [("pymtheg", None), (OBJ, None)],
    16: [("un", None), (OBJ, None), ("ar bymtheg", None)],
    17: [("dwy", "SM"), (OBJ, None), ("ar bymtheg", None)],
    18: [("deunaw", None), (OBJ, None)],
    19: [("pedair", None), ("ar bymtheg", None)],
}

MILLION_WORDS = {
    3: ("mil", None),
    6: ("miliwn", None),
    9: ("biliwn", None),
    12: ("triliwn", None),
    15: ("cwadriliwn", None),
    18: ("cwintiliwn", None),
    21: ("secsttiliwn", None),
    24: ("septiliwn", None),
    27: ("octiliwn", None),
    30: ("noniliwn", None),
    33: ("dengiliwn", None),
}

ORDINAL_WORDS = {
    0: [("dimfed", None), (OBJ, None)],
    1: [(OBJ, None), ("cyntaf", None)],
    2: [("ail", "SM"), (OBJ, None)],
    3: [("trydydd", None), (OBJ, None)],
    4: [("pedwerydd", None), (OBJ, None)],
    5: [("pumed", None), (OBJ, None)],
    6: [("chweched", None), (OBJ, None)],
    7: [("saithfed", None), (OBJ, None)],
    8: [("wythfed", None), (OBJ, None)],
    9: [("nawfed", None), (OBJ, None)],
    10: [("degfed", None), (OBJ, None)],
    11: [("unfed", "SM"), (OBJ, None), ("ar ddeg", None)],
    12: [("deuddegfed", None), (OBJ, None)],
    13: [("trydydd", None), (OBJ, None), ("ar ddeg", None)],
    14: [("pedwerydd", None), (OBJ, None), ("ar ddeg", None)],
    15: [("pymthegfed", None), (OBJ, None)],
    16: [("unfed", None), (OBJ, None), ("ar bymtheg", None)],
    17: [("ail", "SM"), (OBJ, None), ("ar bymtheg", None)],
    18: [("deunawfed", None), (OBJ, None)],
    19: [("pedwerydd", None), (OBJ, None), ("ar bymtheg", None)],
}
ORDINAL_WORDS_FEM = {
    0: [("dimfed", None), (OBJ, None)],
    1: [(OBJ, None), ("gyntaf", None)],
    2: [("ail", "SM"), (OBJ, None)],
    3: [("trydedd", "SM"), (OBJ, None)],
    4: [("pedwaredd", "SM"), (OBJ, None)],
    5: [("pumed", None), (OBJ, None)],
    6: [("chweched", None), (OBJ, None)],
    7: [("saithfed", None), (OBJ, None)],
    8: [("wythfed", None), (OBJ, None)],
    9: [("nawfed", None), (OBJ, None)],
    10: [("degfed", None), (OBJ, None)],
    11: [("unfed", "SM"), (OBJ, None), ("ar ddeg", None)],
    12: [("deuddegfed", None), (OBJ, None)],
    13: [("trydedd", "SM"), (OBJ, None), ("ar ddeg", None)],
    14: [("pedwaredd", "SM"), (OBJ, None), ("ar ddeg", None)],
    15: [("pymthegfed", None), (OBJ, None)],
    16: [("unfed", None), (OBJ, None), ("ar bymtheg", None)],
    17: [("ail", "SM"), (OBJ, None), ("ar bymtheg", None)],
    18: [("deunawfed", None), (OBJ, None)],
    19: [("pedwaredd", None), (OBJ, None), ("ar bymtheg", None)],
}

# The script can extrapolate the missing numbers from the base forms.
STR_TENS = {
    1: [("ugain", None), (OBJ, None)],
    2: [("deugain", None), (OBJ, None)],
    3: [("trigain", None), (OBJ, None)],
    4: [("pedwar ugain", None), (OBJ, None)],
}

ORD_STR_TENS = {
    1: [("ugainfed", None), (OBJ, None)],
    2: [("deugainfed", None), (OBJ, None)],
    3: [("trigainfed", None), (OBJ, None)],
    4: [("pedwar ugainfed", None), (OBJ, None)],
}

STR_TENS_INFORMAL = {
    1: ("undeg", None),
    2: ("dauddeg", None),
    3: ("trideg", None),
    4: ("pedwardeg", None),
    5: ("pumdeg", None),
    6: ("chwedeg", None),
    7: ("saithdeg", None),
    8: ("wythdeg", None),
    9: ("nawdeg", None),
}


GENERIC_DOLLARS = ("dolar", "dolarau")
GENERIC_CENTS = ("ceiniog", "ceiniogau")

CURRENCIES_FEM = ["GBP"]


class Num2Word_CY(Num2Word_EU):
    CURRENCY_FORMS = {
        # currency code: (sg, pl), (sg, pl)
        # in Welsh a noun after a numeral is ALWAYS in the singular
        "EUR": (("euro", "euros"), GENERIC_CENTS),
        "USD": (GENERIC_DOLLARS, GENERIC_CENTS),
        "GBP": (("punt", "punnoedd"), ("ceiniog", "ceiniogau")),
        "CNY": (("yuan", "yuans"), ("ffen", "ffens")),
    }

    MINUS_PREFIX_WORD = "meinws "
    FLOAT_INFIX_WORD = " pwynt "

#    def setup(self):
#        Num2Word_EU.setup(self)

    def __init__(self):
        pass

    def float_to_words(self, float_number):
        # if ordinal:
        #     prefix = self.to_ordinal(int(float_number))
        # else:
        prefix = self.to_cardinal(int(float_number))
        float_part = str(float_number).split(".")[1]
        postfix = " ".join(
            # Drops the trailing zero and comma
            [self.to_cardinal(int(c)) for c in float_part]
        )
        return prefix + Num2Word_CY.FLOAT_INFIX_WORD + postfix

    def hundred_group(
        self, number, informal=False, gender="masc", ordinal=False
    ):
        hundreds = number // 100
        until100 = number % 100  # 0 - 99
        # list group of number words and mutation info (for the following word)
        result = (
            []
        )
        if gender == "fem":
            CW = CARDINAL_WORDS_FEM
        else:
            if ordinal:
                CW = ORDINAL_WORDS
            else:
                CW = CARDINAL_WORDS

        if hundreds > 0:
            if hundreds > 1:
                result.extend((CARDINAL_WORDS[hundreds]))
            result.extend([("cant", None), (OBJ, None)])
            if until100:
                if until100 in [
                    1,
                    8,
                    11,
                    16,
                    20,
                    21,
                    31,
                    36,
                    41,
                    48,
                    61,
                    68,
                    71,
                    81,
                    88,
                    91,
                ]:
                    result.append(("ac", None))
                else:
                    result.append(("a", "AM"))
        if until100:
            # if informal:
            #    pass
            if not ordinal and until100 >= 50 and until100 <= 59:
                units = number % 10
                if hundreds > 0:
                    if units == 0:
                        result.append(("hanner", None))
                    elif units == 1:
                        result.extend([("hanner ac un", None), (OBJ, None)])
                    else:
                        result.append(("hanner a", "AM"))
                        result.extend(CW[units])
                else:
                    if units == 0:
                        result.extend([("hanner cant", None), (OBJ, None)])
                    elif units == 1:
                        result.extend(
                            [("hanner cant ac un", None), (OBJ, None)]
                        )
                    else:
                        result.append(("hanner cant a", "AM"))
                        result.extend(CW[units])
            else:
                if (number < 20 and number > 0) or (
                    number == 0 and hundreds == 0
                ):
                    if gender == "fem":
                        result.extend(CARDINAL_WORDS_FEM[int(number)])
                    else:
                        result.extend(CARDINAL_WORDS[int(number)])

                else:
                    tens = until100 // 20
                    units = number % 20
                    if ordinal and units == 0:
                        degau = ORD_STR_TENS.get(tens)
                    else:
                        degau = STR_TENS.get(tens)

                    if units != 0:
                        if tens > 1:
                            result.extend(CW[units])
                            if degau:
                                result.append(("a", "AM"))
                                result.extend(degau)
                        else:
                            result.extend(CW[units])
                            if degau:
                                result.append(("ar", "SM"))
                                result.extend(degau)
                    elif degau:
                        result.extend(degau)
        return result

    def to_ordinal(self, number, informal=False, gender="masc"):
        if number < 20:
            return makestring(ORDINAL_WORDS[number])
        if number == 100:
            return "canfed"
        elif number > 100:
            raise NotImplementedError("The given number is too large.")

        return self.to_cardinal(
            number, informal=False, gender=gender, ordinal=True
        )

    def to_cardinal(
        self,
        number,
        informal=False,
        gender="masc",
        ordinal=False,
        counted=None,
        raw=False,
    ):
        negative = False
        if number < 0:
            negative = True
            number = -1 * number
        if number == 0:
            if raw:
                return CARDINAL_WORDS[0]
            else:
                return makestring(CARDINAL_WORDS[0])
        elif not number < 999 * 10**33:
            raise NotImplementedError("The given number is too large.")

        elif isinstance(number, float):
            return self.float_to_words(number)

        # split in groups of 10**3
        # groups of three digits starting from right (units (1 - 999),
        # thousands, millions, ...)
        groups = (
            []
        )
        lowestgroup = (
            None  # find the lowest group of 3 digits > 0 for the ordinals
        )
        for pot in [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36]:
            gr = (number % 10**pot) // 10 ** (pot - 3)
            groups.append((gr, pot))
            if gr and not lowestgroup:
                lowestgroup = gr
        # print("groups", groups)

        result = []
        if negative:
            result.append(("meinws", None))

        for gr, pot in reversed(groups):
            if gr:
                # print("AAAA", gr, pot, gender)
                if pot == 6:
                    g = "fem"  # mil (1000) is feminine
                elif pot == 3:
                    g = gender  # units depend on the following noun
                else:
                    g = "masc"  # millions etc are masculine
                    # "mil" is feminine
                if gr > 1 or pot == 3:
                    words = self.hundred_group(
                        gr,
                        informal=informal,
                        gender=g,
                        ordinal=ordinal and (lowestgroup == gr),
                    )
                    result += words
                    # print(">>>> ", words)
                if pot > 3:
                    result.append(MILLION_WORDS[pot - 3])
        if raw:
            # need to be able trigger correct mutation on currencies
            return result
        else:
            if number < 100:
                return makestring(result, counted=counted)
            else:
                if counted:
                    result.extend([("o", "SM"), (counted, None)])
                return makestring(result)

    def to_currency(
        self, val, currency="EUR", cents=True, separator=",", adjective=False
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

        except KeyError:
            raise NotImplementedError(
                'Currency code "%s" not implemented for "%s"'
                % (currency, self.__class__.__name__)
            )

        # if adjective and currency in self.CURRENCY_ADJECTIVES:
        #     cr1 = prefix_currency(self.CURRENCY_ADJECTIVES[currency], cr1)

        minus_str = "%s " % self.negword.strip() if is_negative else ""
        money_str = self._money_verbose(left, currency)
        cents_str = (
            self._cents_verbose(right, currency)
            if cents
            else self._cents_terse(right, currency)
        )

        if right == 0:
            # no pence
            return "%s%s" % (
                minus_str,
                money_str,
                # self.pluralize(right, cr2)
            )
        elif left == 0:
            # no pounds
            return "%s%s" % (
                minus_str,
                cents_str,
                # self.pluralize(right, cr2)
            )

        return "%s%s%s %s" % (
            minus_str,
            money_str,
            # self.pluralize(left, cr1),
            separator,
            cents_str,
            # self.pluralize(right, cr2)
        )

    def _money_verbose(self, number, currency):
        # used in super().to_currency(), we need to add gender
        # here for feminine currencies
        # if currency in CURRENCIES_FEM:  # always true in this context
        if number > 100:
            m = self.to_cardinal(number, gender="fem", raw=True)
            # if currency in self.CURRENCY_FORMS:
            c = self.CURRENCY_FORMS[currency][0][1]
            m.append(("o", "SM"))
            m.append((c, None))
            # else:
            #    c = currency
            #    m.append((c, None))
            return makestring(m)
        else:
            # if number > 1:
            m = self.to_cardinal(number, gender="fem", raw=True)
            # elif number == 0:
            #    m = self.to_cardinal(number, gender="fem", raw=True)
            # else:
            #    m = [(OBJ, None)]
            # if currency in self.CURRENCY_FORMS:
            c = self.CURRENCY_FORMS[currency][0][0]
            # else:
            #    c = currency
            # print("eeeeeeeee", m)
            # m.append((c, None))
            # print("fffffffff", m)
            return makestring(m, counted=c)
        # else:
        #    return self.to_cardinal(number, raw=True)

    def _cents_verbose(self, number, currency):
        if number == 0:
            return ""
        # elif number > 100:
        #     m = self.to_cardinal(number, raw=True)
        #     # if currency in self.CURRENCY_FORMS:
        #     c = self.CURRENCY_FORMS[currency][0][1]
        #     m.append(("o", "SM"))
        #     m.append((c, None))
        #     # else:
        #     #    c = currency
        #     #    m.append((c, None))
        #     return makestring(m)
        else:
            if number > 1:
                m = self.to_cardinal(number, raw=True)
            else:
                m = [(OBJ, None)]
            # if currency in self.CURRENCY_FORMS:
            c = self.CURRENCY_FORMS[currency][1][0]
            # else:
            #    c = currency
            return makestring(m, counted=c)


def makestring(result, counted=None):
    # concatenate numberwords with correct mutation
    out = []
    lastmut = None
    for w, mut in result:
        if w == OBJ:
            if not counted:
                continue
            else:
                w = counted
                counted = None  # only first position
        if lastmut:
            out.append(mutate(w, lastmut))
        else:
            out.append(w)
        lastmut = mut
    return " ".join(out)


def mutate(word, mutation):
    # print("uuu", word, mutation)
    if mutation == "SM":
        return softmutation(word)
    elif mutation == "AM":
        return aspiratedmutation(word)
    # return word  # does not occur


def softmutation(word):
    # print("SM<<<<%s>" % word)
    if word[0] == "p" and word[1] != "h":
        return "b" + word[1:]
    elif word[0] == "t" and word[1] != "h":
        return "d" + word[1:]
    elif word[0] == "c" and word[1] != "h":
        return "g" + word[1:]
    elif word[0] == "b" or word[0] == "m":
        return "f" + word[1:]
    elif word[0] == "d" and word[1] != "d":
        return "d" + word
    elif word.startswith("ll"):
        return word[1:]
    elif word.startswith("rh"):
        return "r" + word[2:]
    elif word == "ugain":
        return "hugain"
    else:
        return word


def aspiratedmutation(word):
    if word[0] == "p" and word[1] != "h":
        return "ph" + word[1:]
    elif word[0] == "t" and word[1] != "h":
        return "th" + word[1:]
    elif word[0] == "c" and word[1] != "h":
        return "ch" + word[1:]
    else:
        return word
