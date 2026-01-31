# -*- coding: utf-8 -*-
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

from __future__ import division, print_function, unicode_literals

from .base import Num2Word_Base
from .compat import strtype
from .currency import parse_currency_parts


class Num2Word_ZH(Num2Word_Base):
    CURRENCY_FLOATS = ["角", "分"]

    CURRENCY_FORMS = {
        "XXX": "元",  # Generic dollar
        "CNY": "人民幣",
        "NTD": "新台幣",
        "HKD": "港幣",
        "MOP": "澳門幣",
        "SGD": "新加坡元",
        "MYR": "馬來西亞令吉",
        "USD": "美元",
        "EUR": "歐元",
        "GBP": "英鎊",
        "JPY": "日元",
        "CHF": "瑞士法郎",
        "CAD": "加元",
        "AUD": "澳幣",
        "NZD": "紐西蘭元",
        "THB": "泰銖",
        "KRW": "韓元",
    }

    cheque_suffix = "正"
    year = "年"
    year_prefix = ("公元", "西元")
    year_bce = "前"
    ord_prefix = "第"

    def set_high_numwords(self, high):
        max = 4 * len(high)
        for word, n in zip(high, range(max, 0, -4)):
            self.cards[10 ** n] = word

    def to_cardinal(self, value, stuff_zero=2, reading=False, prefer=None):
        self.stuff_zero = stuff_zero
        self.set_str_selection(reading, prefer)

        out = super().to_cardinal(value).replace(" ", "")
        return self.zh_to_cap(out, reading == "capital")

    def to_cardinal_float(self, value):
        out = super().to_cardinal_float(value).replace(" ", "")
        return self.zh_to_cap(out, self.capital)

    def merge(self, lpair, rpair):
        ltext, lnum = lpair
        rtext, rnum = rpair
        ltext, rtext = self.select_text(ltext), self.select_text(rtext)
        # ignore lpair if lnum is 1 and rnum is less than 10
        if lnum == 1 and rnum < 10:
            return (rtext, rnum)
        # stuff_zero logic between discontinous numbers
        # http://www.hkame.org.hk/uploaded_files/magazine/15/271.pdf
        with_zero = ("%s%s%s" % (ltext, self.select_text(
            self.low_numwords[-1]), rtext), lnum + rnum)
        no_zero = ("%s%s" % (ltext, rtext), lnum + rnum)
        if len(str(lnum)) - len(str(rnum)) > 1:
            if self.stuff_zero == 1:  # 凡「零」必讀 All discontinous numbers
                return with_zero
            elif self.stuff_zero == 2:  # Discontinous high numbers
                if len(str(lnum)) - len(str(rnum)
                                        ) > 1 and len(str(rnum)) % 4 != 0:
                    return with_zero
                return no_zero
            elif self.stuff_zero == 3:  # 凡「零」不讀 No zeros
                return no_zero
        elif rnum > lnum:
            return ("%s%s" % (ltext, rtext), lnum * rnum)
        return no_zero

    def to_ordinal(self, value, counter="", reading=False, prefer=None):
        self.set_str_selection(reading, prefer)
        self.verify_ordinal(value)
        base = self.to_cardinal(value, reading=reading, prefer=prefer)
        return "%s%s%s" % (self.select_text(self.ord_prefix),
                           base, self.select_text(counter))

    def to_ordinal_num(self, value, counter="", reading=False, prefer=None):
        self.set_str_selection(reading, prefer)
        return "%s%s%s" % (self.select_text(self.ord_prefix),
                           value, self.select_text(counter))

    def to_year(self, value, reading=False, prefer=None):
        self.set_str_selection(reading, prefer)

        if not value == int(value):
            raise TypeError(self.errmsg_floatyear % value)

        out = []
        if value < 0:
            out += [self.year_prefix, self.year_bce]
        elif reading == "capital":
            out += [self.year_prefix]

        out += [self.cards[int(s)] for s in str(abs(int(value)))]
        out += [self.year]

        return "".join(self.select_text(s) for s in out)

    def to_currency(self, val, currency='XXX', cents=False, separator="",
                    adjective=False, reading=False, prefer=None):
        """
        Args:
            val: Numeric value
            currency (str): Currency code
            # cents (bool): Verbose cents
            # separator (str): Cent separator
            # adjective (bool): Prefix currency name with adjective
            capital (bool): Select the capital form of a Chinese numeral
        Returns:
            str: Formatted string

        Handles whole numbers and decimal numbers differently
        """
        self.set_str_selection(reading, prefer)
        left, right, is_negative = parse_currency_parts(
            val, is_int_with_cents=False)

        try:
            cr = self.CURRENCY_FORMS[currency]
            # Not Applicable: ValueError
            # CURRENCY_FLOATS are the generic terms for demicals
        except KeyError:
            raise NotImplementedError(
                'Currency code "%s" not implemented for "%s"' %
                (currency, self.__class__.__name__))

        # CURRENCY_ADJECTIVES are not implemented
        minus_str = self.negword if is_negative else ""
        money_str = self.to_cardinal(left, reading=reading, prefer=prefer)
        # has_decimal is not implemented

        if currency == "XXX":
            cr_pre, cr_post = ("", cr)
        else:
            cr_pre, cr_post = (cr, self.CURRENCY_FORMS["XXX"])
        cents_str = self.to_currency_float(
            right, reading=reading, prefer=prefer)
        # Only add "整" in capital format
        cheque = self.cheque_suffix if len(
            cents_str) == 0 and reading == "capital" else ""

        for c in [minus_str, money_str, cr_post, *cents_str, cheque]:
            cr_pre += self.zh_to_cap(self.select_text(c), reading == "capital")
        return cr_pre

    def to_currency_float(self, value, reading=False, prefer=None):
        cents = "%02d" % value
        out = []

        if int(cents) > 0:
            if not (int(cents[0]) == 0 and reading == "capital"):
                out += [self.cards[int(cents[0])]]
            if int(cents[0]) > 0:
                out += [self.CURRENCY_FLOATS[0]]
            if int(cents[1]) > 0:
                out += [self.cards[int(cents[1])], self.CURRENCY_FLOATS[1]]

        return out

    def zh_to_cap(self, value, capital):
        """
        Select the capital form of a Chinese numeral
        """
        out = value
        one, ten = self.select_text(
            self.cards[1]), self.select_text(
            self.cards[10])
        if capital:
            for cap_w in self.CAP_map:
                if cap_w[0] in out:
                    out = out.replace(cap_w[0], cap_w[1])
            return out
        elif out.startswith(one + ten):
            out = out[len(one):]
        return out

    def setup(self):
        self.precision = 2
        self.negword = "負"
        self.pointword = "點"
        self.exclude_title = [self.negword, self.pointword]
        self.errmsg_floatyear = "Cannot treat float %s as year."

        self.reading = None
        self.prefer = None

        self.high_numwords = [
            "萬",       # 10 ** 4
            "億",       # 10 ** 8
            "兆",       # 10 ** 12
            "京",       # 10 ** 16
            "垓",       # 10 ** 20
            "秭",       # 10 ** 24
            "穣",       # 10 ** 28
            "溝",       # 10 ** 32
            "澗",       # 10 ** 36
            "正",       # 10 ** 40
            "載",       # 10 ** 44
            "極",       # 10 ** 48
            "恆河沙",   # 10 ** 52
            "阿僧祇",   # 10 ** 56
            "那由他",   # 10 ** 60
            "不可思議",  # 10 ** 64
            "無量",     # 10 ** 68
            "不可說",   # 10 ** 72
        ]
        self.high_numwords.reverse()

        self.mid_numwords = [
            (1000, '千'),
            (100, '百'),
            (10, '十')
        ]
        self.low_numwords = [
            "九",
            "八",
            "七",
            "六",
            "五",
            "四",
            "三",
            "二",
            "一",
            ("零", "〇")
        ]

    CAP_map = [
        ("千", "仟"),
        ("百", "佰"),
        ("十", "拾"),
        ("九", "玖"),
        ("八", "捌"),
        ("七", "柒"),
        ("六", "陸"),
        ("五", "伍"),
        ("四", "肆"),
        ("三", "叁"),
        ("二", "貳"),
        ("一", "壹"),
        ("元", "圓"),
        ("正", "整"),
    ]

    def select_text(self, text):
        """Select the correct text from the Chinese, phonetic symbol (注音) or
            alternatives ('ㄧ' or '壹')"""
        if isinstance(text, strtype):
            return text
        if len(text) == 0:
            return ''
        # Check if reading is provided
        if all(isinstance(item, tuple) for item in text):
            if self.reading is True:
                text = text[1]
            else:
                text = text[0]

        # select the preferred one or the first one from multiple alternatives
        if not isinstance(text, strtype):
            common = set(text) & set(self.prefer or set())
            if len(common) == 1:
                text = common.pop()
            else:
                text = text[0]
        return text

    def set_str_selection(self, reading, prefer):
        self.reading = reading
        self.prefer = prefer
        self.capital = reading == "capital"
