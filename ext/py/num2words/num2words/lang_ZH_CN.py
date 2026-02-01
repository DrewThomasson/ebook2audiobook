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

from .lang_ZH import Num2Word_ZH


class Num2Word_ZH_CN(Num2Word_ZH):
    CURRENCY_FORMS = {
        "XXX": "元",  # Generic dollar
        "CNY": "人民币",
        "NTD": "新台币",
        "HKD": "港币",
        "MOP": "澳门币",
        "SGD": "新加坡元",
        "MYR": "马来西亚令吉",
        "USD": "美元",
        "EUR": "欧元",
        "GBP": "英镑",
        "JPY": "日元",
        "CHF": "瑞士法郎",
        "CAD": "加元",
        "AUD": "澳币",
        "NZD": "纽西兰元",
        "THB": "泰铢",
        "KRW": "韩元",
    }

    def setup(self):
        super().setup()
        self.negword = "负"
        self.pointword = "点"
        self.exclude_title = [self.negword, self.pointword]
        self.high_numwords = [
            "万",       # 10 ** 4
            "亿",       # 10 ** 8
            "兆",       # 10 ** 12
            "京",       # 10 ** 16
            "垓",       # 10 ** 20
            "秭",       # 10 ** 24
            "穣",       # 10 ** 28
            "沟",       # 10 ** 32
            "涧",       # 10 ** 36
            "正",       # 10 ** 40
            "载",       # 10 ** 44
            "极",       # 10 ** 48
            "恒河沙",   # 10 ** 52
            "阿僧祇",   # 10 ** 56
            "那由他",   # 10 ** 60
            "不可思议",  # 10 ** 64
            "无量",     # 10 ** 68
            "不可说",   # 10 ** 72
        ]
        self.high_numwords.reverse()

    CAP_map = [
        ("千", "仟"),
        ("百", "佰"),
        ("十", "拾"),
        ("九", "玖"),
        ("八", "捌"),
        ("七", "柒"),
        ("六", "陆"),
        ("五", "伍"),
        ("四", "肆"),
        ("三", "叁"),
        ("二", "贰"),
        ("一", "壹"),
        ("元", "圆"),
    ]
