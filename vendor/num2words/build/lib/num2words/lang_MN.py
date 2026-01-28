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

from __future__ import unicode_literals

from .base import Num2Word_Base
from .currency import parse_currency_parts
from .utils import get_digits, splitbyx

ZERO = 'тэг'

ONES = {
    1: ('нэг', 'нэг'),
    2: ('хоёр', 'хоёр'),
    3: ('гурав', 'гурван'),
    4: ('дөрөв', 'дөрвөн'),
    5: ('тав', 'таван'),
    6: ('зургаа', 'зургаан'),
    7: ('долоо', 'долоон'),
    8: ('найм', 'найман'),
    9: ('ес', 'есөн'),
}

TEN = ('арав', 'арван')

TWENTIES = {
    2: ('хорь', 'хорин'),
    3: ('гуч', 'гучин'),
    4: ('дөч', 'дөчин'),
    5: ('тавь', 'тавин'),
    6: ('жар', 'жаран'),
    7: ('дал', 'далан'),
    8: ('ная', 'наян'),
    9: ('ер', 'ерэн'),
}

HUNDRED = ('зуу', 'зуун')

THOUSANDS = {
    1: "мянга",  # 10^3
    2: "сая",  # 10^6
    3: "тэрбум",  # 10^9
    4: "их наяд",  # 10^12
    5: "тунамал",  # 10^15
    6: "их ингүүмэл",  # 10^18
    7: "ялгаруулагч",  # 10^21
    8: "их өөр дээр",  # 10^24
    9: "хязгаар үзэгдэл",  # 10^27
    10: "их шалтгааны зүйл",  # 10^30
    11: "эрхт",  # 10^33
    12: "их сайтар хүргэсэн",  # 10^36
    13: "живэх тоосон билэг",  # 10^39
    14: "их билэг тэмдэг",  # 10^42
    15: "тохио мэдэхүй",  # 10^45
    16: "их тийн болсон",  # 10^48
    17: "асрахуй",  # 10^51
    18: "их нигүүлсэнгүй",  # 10^54
    19: "тоолшгүй",  # 10^57
    20: "өгүүлшгүй",  # 10^60
    21: "үлэшгүй",  # 10^63
    22: "сэтгэшгүй",  # 10^66
}

POINT_WORDS = {
    1: 'аравны',
    2: 'зууны',
    3: 'мянганы',
    4: 'арван мянганы',
    5: 'зуун мянганы',
    6: 'саяны',
}


class Num2Word_MN(Num2Word_Base):

    CURRENCY_FORMS = {
        "AED": (("дирхам",), ("филс",)),
        "AUD": (("доллар",), ("цент",)),
        "BGN": (("лев",), ("стотинка",)),
        "CAD": (("доллар",), ("цент",)),
        "CHF": (("франк",), ("раппен",)),
        "CNY": (("юань",), ("фэнь",)),
        "CZK": (("крон",), ("галерж",)),
        "DKK": (("крон",), ("өре",)),
        "EGP": (("фунт",), ("пиастр",)),
        "EUR": (("евро",), ("цент",)),
        "GBP": (("фунт стерлинг",), ("пенс",)),
        "HKD": (("доллар",), ("цент",)),
        "HUF": (("форинт",), ("филлер",)),
        "IDR": (("рупи",), ("сен",)),
        "INR": (("рупи",), ("пайса",)),
        "JPY": (("иен",), ("сен",)),
        "KPW": (("вон",), ("чон",)),
        "KRW": (("вон",), ("чон",)),
        "KWD": (("динaр",), ("филс",)),
        "KZT": (("тенге",), ("тийн",)),
        "MNT": (("төгрөг",), ("мөнгө",)),
        "MYR": (("ринггит",), ("сен",)),
        "NOK": (("крон",), ("өре",)),
        "NPR": (("рупи",), ("пайса",)),
        "NZD": (("доллар",), ("цент",)),
        "PLN": (("злот",), ("грош",)),
        "RUB": (("рубль",), ("копейк",)),
        "SEK": (("крон",), ("өре",)),
        "SGD": (("доллар",), ("цент",)),
        "THB": (("бат",), ("сатанг",)),
        "TRY": (("лира",), ("куруш",)),
        "TWD": (("доллар",), ("сентао",)),
        "UAH": (("гривн",), ("копейк",)),
        "USD": (("доллар",), ("цент",)),
        "VND": (("донг",), ("су",)),
        "ZAR": (("ранд",), ("сента",))
    }

    CURRENCY_ADJECTIVES = {
        "AUD": "Австралийн",
        "CAD": "Канадын",
        "CZK": "Чехийн ",
        "DKK": "Данийн",
        "HKD": "Хонконг",
        "IDR": "Индонезийн",
        "INR": "Энэтхэгийн",
        "KPW": "БНАСАУ-ын",
        "KRW": "БНСУ-ын",
        "NOK": "Норвегийн",
        "NPR": "Непалын",
        "NZD": "Шинэ Зеландын",
        "SEK": "Шведийн",
        "SGD": "Сингапур",
        "TWD": "Тайванийн",
        "USD": "Америк"
    }

    def setup(self):
        self.negword = "хасах"

    def to_cardinal(self, value, all_suffixed=False):
        n = str(value).replace(',', '.')
        if '.' in n:
            left, right = n.split('.')

            # Бутархай хэсэг нь тэг бол бүхэл тоо шиг хувирна
            if int(right) == 0:
                return self._int2word(int(left), all_suffixed=all_suffixed)

            fractional_length = len(right)
            if fractional_length > 6:
                raise NotImplementedError()

            return '%s, %s %s' % (
                self._int2word(int(left), all_suffixed=all_suffixed),
                POINT_WORDS[fractional_length],
                self._int2word(int(right), all_suffixed=all_suffixed)
            )
        else:
            return self._int2word(int(n), all_suffixed=all_suffixed)

    def pluralize(self, n, form):
        return form[0]

    def _int2word(self, n, all_suffixed=False):
        if n < 0:
            return ' '.join([self.negword, self._int2word(abs(n))])

        if n == 0:
            return ZERO

        words = []
        chunks = list(splitbyx(str(n), 3))

        i = len(chunks)

        for x in chunks:

            i -= 1

            if x == 0:
                continue

            n1, n2, n3 = get_digits(x)

            use_suffix1 = use_suffix2 = use_suffix3 = True
            if (not all_suffixed) and i == 0:
                if n1 == 0 and n2 == 0:
                    use_suffix3 = False
                elif n1 == 0:
                    use_suffix2 = False
                else:
                    use_suffix1 = False

            if n3 > 0:
                if n3 > 1:
                    words.append(ONES[n3][1])
                words.append(HUNDRED[1 if use_suffix3 else 0])

            if n2 == 1:
                words.append(TEN[1 if use_suffix2 else 0])
            elif n2 > 1:
                words.append(TWENTIES[n2][1 if use_suffix2 else 0])

            if n1 > 0:
                words.append(ONES[n1][1 if use_suffix1 else 0])

            if i > 0:
                words.append(THOUSANDS[i])

        if all_suffixed and words and words[-1] == 'мянга':
            words[-1] = 'мянган'

        return ' '.join(words)

    def to_ordinal(self, value):
        number = int(value)
        return "%s %s" % (
            self.to_cardinal(number),
            self._get_ordinal_suffix(number),
        )

    def to_ordinal_num(self, value):
        number = int(value)
        return '%s %s' % (number, self._get_ordinal_suffix(number))

    def _get_ordinal_suffix(self, number):
        number_str = str(number)
        suffix = 'дугаар'
        if number_str[-1] != '0':
            if number_str[-1] in ('1', '4', '9'):
                suffix = 'дүгээр'
        elif number_str[-2] != '0':
            if number_str[-2] in ('4', '9'):
                suffix = 'дүгээр'
        return suffix

    def to_year(self, value):
        prefix = ''
        if value < 0:
            value = abs(value)
            prefix = 'МЭӨ '
        return '%s%s он' % (prefix, self.to_cardinal(value, all_suffixed=True))

    def _money_verbose(self, number, currency):
        return self.to_cardinal(number, all_suffixed=True)

    def _cents_verbose(self, number, currency):
        return self.to_cardinal(number, all_suffixed=True)

    def to_currency(self, val, currency='MNT', cents=True, separator=',',
                    adjective=True):
        left, right, is_negative = parse_currency_parts(val)
        if isinstance(val, float) and int(right) == 0:  # Бутархай орон нь 0
            val = int(left) * 100
        return super(
            Num2Word_MN, self
        ).to_currency(
            val,
            currency=currency,
            cents=cents,
            separator=separator,
            adjective=adjective,
        )
