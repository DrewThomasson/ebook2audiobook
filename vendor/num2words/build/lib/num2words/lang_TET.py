# -*- coding: utf-8 -*-Num2Word_TET
# Copyright (c) 2003, Taro Ogawa.  All Rights Reserved.
# Copyright (c) 2013, Savoir-faire Linux inc.  All Rights Reserved.

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


from num2words.currency import parse_currency_parts

from .lang_EU import Num2Word_EU

DOLLAR = ('dolar', 'dolar')
CENTS = ('sentavu', 'sentavu')


class Num2Word_TET(Num2Word_EU):

    CURRENCY_FORMS = {
        'AUD': (DOLLAR, CENTS),
        'CAD': (DOLLAR, CENTS),
        'EUR': (('euro', 'euros'), CENTS),
        'GBP': (('pound sterling', 'pound sterling'), ('pence', 'pence')),
        'USD': (DOLLAR, CENTS),
    }

    GIGA_SUFFIX = None
    MEGA_SUFFIX = "iliaun"

    def setup(self):
        super().setup()
        lows = ["kuatr", "tr", "b", "m"]
        self.high_numwords = self.gen_high_numwords([], [], lows)
        self.negword = "menus "
        self.pointword = "vírgula"
        self.exclude_title = ["resin", "vírgula", "menus"]
        self.count = 0

        self.mid_numwords = [
            (1000, "rihun"), (100, "atus"), (90, "sianulu"),
            (80, "ualunulu"), (70, "hitunulu"), (60, "neenulu"),
            (50, "limanulu"), (40, "haatnulu"), (30, "tolunulu"),
            (20, "ruanulu")
        ]
        self.low_numwords = [
            "sanulu",
            "sia", "ualu", "hitu", "neen", "lima", "haat", "tolu", "rua",
            "ida", "mamuk"
        ]
        self.hundreds = {
            1: "atus",
            2: "atus rua",
            3: "atus tolu",
            4: "atus haat",
            5: "atus lima",
            6: "atus neen",
            7: "atus hitu",
            8: "atus ualu",
            9: "atus sia",
        }

    def merge(self, curr, next):
        ctext, cnum, ntext, nnum = curr + next

        if cnum == 1 and nnum < 100:
            return next

        if nnum < cnum:
            if nnum < 10:
                value_str = str(cnum + nnum)
                if int(value_str) > 100:
                    zero_list = value_str[1:-1]
                    all_zero = all(element == '0' for element in zero_list)
                    if all_zero:
                        if self.count >= 1:
                            self.count += 0
                            return (
                                "ho %s %s" % (ctext, ntext),
                                cnum + nnum
                            )
                        self.count += 1
                        return ("%s %s" % (ctext, ntext), cnum + nnum)

                return ("%s resin %s" % (ctext, ntext), cnum + nnum)
            else:
                return ("%s %s" % (ctext, ntext), cnum + nnum)

        return (ntext + " " + ctext, cnum * nnum)

    def ho_result(self, result, value):
        index = result.find('ho')
        count_ho = result.count('ho')

        if index != -1 and count_ho >= 1:
            index_rihun = result.find('rihun')
            value_str = len(str(value))
            if index_rihun != -1 and value_str > 7:
                result = result.replace("rihun ho", "ho rihun")
            lows = ["kuatr", "tr", "b", "m"]
            MEGA_SUFFIX = "iliaun"
            for low in lows:
                result = result.replace(
                    low + MEGA_SUFFIX + " ho", "ho " + low + MEGA_SUFFIX)
            remove_first_ho = result.startswith('ho')
            if remove_first_ho:
                result = result[3:]
        return result

    def remove_ho(self, result, value):
        value_str = str(value)
        result = self.ho_result(result, value)
        end_value = value_str[:-4]
        end_true = end_value.endswith('0')
        if end_true is False:
            if value > 100:
                if value_str[-1] != '0' and value_str[-2] == '0':
                    result = result.replace("ho", "")
                    result = result.replace("  ", " ")

        return result

    def to_cardinal(self, value):
        result = super().to_cardinal(value)

        results = self.remove_ho(result, value)
        return results

    def to_ordinal(self, value):
        self.verify_ordinal(value)
        out = ""
        val = self.splitnum(value)
        outs = val
        while len(val) != 1:
            outs = []
            left, right = val[:2]
            if isinstance(left, tuple) and isinstance(right, tuple):
                outs.append(self.merge(left, right))
                if val[2:]:
                    outs.append(val[2:])
            else:
                for elem in val:
                    if isinstance(elem, list):
                        if len(elem) == 1:
                            outs.append(elem[0])
                        else:
                            outs.append(self.clean(elem))
                    else:
                        outs.append(elem)
            val = outs

        words, num = outs[0]

        words = self.remove_ho(words, value)

        if num in [90, 80, 70, 60, 50, 40, 30, 20, 10, 9, 8, 7, 5, 3, 2]:
            words = 'da'+words+'k'
        if num in [6, 4]:
            words = 'da'+words
        if num == 1:
            words = 'dahuluk'
        if num in [900, 800, 700, 500, 300, 200, 100]:
            words = 'dah'+words+'k'
        if num in [600, 400]:
            words = 'dah'+words

        words_split = words.split()
        if len(words_split) >= 3 and num < 100:
            first_word = 'da'+words_split[0]
            second_word = " ".join(words_split[1:])
            if 'haat' in second_word or 'neen' in second_word:
                words = first_word+" "+second_word
            else:
                words = first_word+" "+second_word+'k'

        word_first = 'dah'+words_split[0]
        if word_first == 'dahatus' and len(words_split) >= 3:
            word_second = " ".join(words_split[1:])
            if 'haat' in word_second or 'neen' in word_second:
                words = word_first+" "+word_second
            else:
                words = word_first+" "+word_second+'k'

        if len(str(num)) > 3:
            if 'haat' in words_split[-1:] or 'neen' in words_split[-1:]:
                words = 'da'+words
            else:
                words = 'da'+words+'k'

        result = self.title(out + words)

        return result

    def to_ordinal_num(self, value):
        self.verify_ordinal(value)
        return "%sº" % (value)

    def to_year(self, val, longval=True):
        if val < 0:
            return self.to_cardinal(abs(val)) + ' antes Kristu'
        return self.to_cardinal(val)

    def to_currency(self, val, currency='USD', cents=True):
        """
        Args:
            val: Numeric value
            currency (str): Currency code
            cents (bool): Verbose cents
            adjective (bool): Prefix currency name with adjective
        Returns:
            str: Formatted string

        """
        left, right, is_negative = parse_currency_parts(val)

        try:
            cr1, cr2 = self.CURRENCY_FORMS[currency]

        except KeyError:
            raise NotImplementedError(
                'Currency code "%s" not implemented for "%s"' %
                (currency, self.__class__.__name__))

        minus_str = "%s " % self.negword.strip() if is_negative else ""
        money_str = self._money_verbose(left, currency)
        cents_str = self._cents_verbose(right, currency) \
            if cents else self._cents_terse(right, currency)

        if right == 0:
            return u'%s%s %s' % (
                minus_str,
                self.pluralize(left, cr1),
                money_str
            )
        else:
            return u'%s%s %s %s %s' % (
                minus_str,
                self.pluralize(left, cr1),
                money_str,
                self.pluralize(right, cr2),
                cents_str
            )
