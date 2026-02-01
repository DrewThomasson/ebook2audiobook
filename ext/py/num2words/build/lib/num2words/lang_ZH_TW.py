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

from .compat import to_s
from .lang_ZH import Num2Word_ZH


class Num2Word_ZH_TW(Num2Word_ZH):
    CURRENCY_FORMS_CHILD = {
        "XXX": (("元",), ("ㄩㄢˊ",)),  # Generic dollar
    }

    cheque_suffix = (("正",), ("ㄓㄥˋ",))
    year = (("年",), ("ㄋㄧㄢˊ",))
    year_prefix = (("公元", "西元"), ("ㄍㄨㄥ ㄩㄢˊ", "ㄒㄧㄩㄢˊ"))
    year_bce = (("前",), ("ㄑㄧㄢˊ",))
    ord_prefix = (("第",), ("ㄉㄧˋ",))
    ROC_era = (("民國",), ("ㄇㄧㄣˊㄍㄨㄛˊ",))

    def __init__(self):
        super().__init__()
        self.CURRENCY_FORMS = self.CURRENCY_FORMS.copy()

        for k, v in self.CURRENCY_FORMS_CHILD.items():
            self.CURRENCY_FORMS[k] = v

    # Get reading for negword
    def to_cardinal(self, value, stuff_zero=2, reading=False, prefer=None):
        self.stuff_zero = stuff_zero
        self.set_str_selection(reading, prefer)

        try:
            assert int(value) == value
        except (ValueError, TypeError, AssertionError):
            return self.to_cardinal_float(value, reading, prefer)

        out = ""
        if value < 0:
            value = abs(value)
            out = "%s " % self.select_text(self.negword).strip()

        if value >= self.MAXVAL:
            raise OverflowError(self.errmsg_toobig % (value, self.MAXVAL))

        val = self.splitnum(value)
        words, num = self.clean(val)
        out = self.title(out + words)

        out = self.zh_to_cap(out, reading == "capital")
        return out.replace(" ", "")

    # Get reading for pointword
    def to_cardinal_float(self, value, reading=False, prefer=None):
        try:
            float(value) == value
        except (ValueError, TypeError, AssertionError, AttributeError):
            raise TypeError(self.errmsg_nonnum % value)

        pre, post = self.float2tuple(float(value))

        post = str(post)
        post = '0' * (self.precision - len(post)) + post

        out = [self.to_cardinal(pre, reading=reading, prefer=prefer)]
        if value < 0 and pre == 0:
            out = [self.select_text(self.negword).strip()] + out

        if self.precision:
            out.append(self.select_text(self.title(self.pointword)))

        for i in range(self.precision):
            curr = int(post[i])
            out.append(
                to_s(
                    self.to_cardinal(
                        curr,
                        reading=reading,
                        prefer=prefer)))

        out = self.zh_to_cap(" ".join(out), self.capital)
        return out.replace(" ", "")

    def to_ordinal(self, value, counter="", reading=False, prefer=None):
        self.set_str_selection(reading, prefer)
        if reading is True:
            if counter not in self.counters and counter:
                raise NotImplementedError(
                    f"Reading not implemented for {counter}")
            counter = self.counters.get(counter, "")
        return super().to_ordinal(
            value, counter=counter, reading=reading, prefer=prefer)

    def to_ordinal_num(self, value, counter="", reading=False, prefer=None):
        self.set_str_selection(reading, prefer)
        if self.reading is True:
            if counter not in self.counters and counter:
                raise NotImplementedError(
                    f"Reading not implemented for {counter}")
            counter = self.counters.get(counter, "")
        return super().to_ordinal_num(
            value, counter=counter, reading=reading, prefer=prefer)

    def to_year(self, value, era=False, reading=False, prefer=None):
        self.set_str_selection(reading, prefer)
        if not era:
            return super().to_year(value, reading=reading, prefer=prefer)

        if not value == int(value):
            raise TypeError(self.errmsg_floatyear % value)

        min_year = 1912
        if value < min_year:
            raise ValueError(
                "Can't convert years less than %s to ROC era" %
                min_year)
        era_year = abs(int(value - min_year + 1))

        if reading == "arabic":
            era_year_words = era_year
        elif era_year == 1:
            era_year_words = self.select_text((("元",), ("ㄩㄢˊ",)))
        elif era_year < 101:
            era_year_words = self.to_cardinal(era_year)
        else:
            era_year_words = "".join(
                [self.select_text(self.cards[int(s)]) for s in str(era_year)])

        return "%s%s%s" % (self.select_text(self.ROC_era),
                           era_year_words, self.select_text(self.year))

    def setup(self):
        super().setup()
        self.negword = (("負",), ("ㄈㄨˋ",))
        self.pointword = (("點",), ("ㄉㄧㄢˇ",))
        self.exclude_title = [self.negword, self.pointword]

        self.high_numwords = [
            (("萬",), ("ㄨㄢˋ",)),                  # 10**4
            (("億",), ("ㄧˋ",)),                    # 10**8
            (("兆",), ("ㄓㄠˋ",)),                  # 10**12
            (("京",), ("ㄐㄧㄥ",)),                 # 10**16
            (("垓",), ("ㄍㄞ",)),                   # 10**20
            (("秭",), ("ㄗˇ",)),                    # 10**24
            (("穣",), ("ㄖㄤ",)),                   # 10**28
            (("溝",), ("ㄍㄡ",)),                   # 10**32
            (("澗",), ("ㄐㄧㄢˋ",)),                # 10**36
            (("正",), ("ㄓㄥˋ",)),                  # 10**40
            (("載",), ("ㄗㄞˇ",)),                  # 10**44
            (("極",), ("ㄐㄧˊ",)),                  # 10**48
            (("恆河沙",), ("ㄏㄥˊㄏㄜˊㄕㄚ",)),     # 10**52
            (("阿僧祇",), ("ㄚㄙㄥㄑㄧˊ",)),        # 10**56
            (("那由他",), ("ㄋㄚˋㄧㄡˊㄊㄚ",)),     # 10**60
            (("不可思議",), ("ㄅㄨˋㄎㄜˇㄙㄧˋ",)),  # 10**64
            (("無量",), ("ㄨˊㄌㄧㄤˋ",)),           # 10**68
            (("不可說",), ("ㄅㄨˋㄎㄜˇㄕㄨㄛ",))    # 10**72
        ]
        self.high_numwords.reverse()

        self.counters = {
            "個": "˙ㄍㄜ",
            "名": "ㄇㄧㄥˊ",
            "位": "ㄨㄟˋ"
        }

        self.mid_numwords = [
            (1000, (("千",), ("ㄑㄧㄢ",))),
            (100, (("百",), ("ㄅㄞˇ",))),
        ]

        self.low_numwords = [
            (("十", "拾"), ("ㄕˊ",)),      # 10
            (("九", "玖"), ("ㄐㄧㄡˇ",)),  # 9
            (("八", "捌"), ("ㄅㄚ",)),     # 8
            (("七", "柒"), ("ㄑㄧ",)),     # 7
            (("六", "陸"), ("ㄌㄧㄡˋ",)),  # 6
            (("五", "伍"), ("ㄨˇ",)),      # 5
            (("四", "肆"), ("ㄙˋ",)),      # 4
            (("三", "參"), ("ㄙㄢ",)),     # 3
            (("二", "貳"), ("ㄦˋ",)),      # 2
            (("一", "壹"), ("ㄧ",)),       # 1
            (("零", "〇"), ("ㄌㄧㄥˊ",)),     # 0
        ]
