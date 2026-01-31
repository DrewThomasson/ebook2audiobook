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


class Num2Word_ZH_HK(Num2Word_ZH):
    CURRENCY_FLOATS_CHILD = ["毫", "仙"]

    CURRENCY_FORMS_CHILD = {
        "EUR": "歐羅",
        "JPY": "日圓",
        "CAD": "加元",
        "AUD": "澳元",
        "KRW": "韓圜",
    }

    CAP_map_CHILD = [
        ("毫", "角"),
        ("仙", "分"),
    ]

    def __init__(self):
        super().__init__()
        self.CURRENCY_FLOATS = self.CURRENCY_FLOATS_CHILD.copy()
        self.CURRENCY_FORMS = self.CURRENCY_FORMS.copy()
        self.CAP_map = self.CAP_map.copy()

        for k, v in self.CURRENCY_FORMS_CHILD.items():
            self.CURRENCY_FORMS[k] = v
        for item in self.CAP_map_CHILD:
            self.CAP_map.append(item)
