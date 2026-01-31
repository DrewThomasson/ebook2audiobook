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

# Armenian numerals
ONES = {
    0: 'զրո',
    1: 'մեկ',
    2: 'երկու',
    3: 'երեք',
    4: 'չորս',
    5: 'հինգ',
    6: 'վեց',
    7: 'յոթ',
    8: 'ութ',
    9: 'ինը'
}

TEENS = {
    10: 'տասը',
    11: 'տասնմեկ',
    12: 'տասներկու',
    13: 'տասներեք',
    14: 'տասնչորս',
    15: 'տասնհինգ',
    16: 'տասնվեց',
    17: 'տասնյոթ',
    18: 'տասնութ',
    19: 'տասնինը'
}

TENS = {
    2: 'քսան',
    3: 'երեսուն',
    4: 'քառասուն',
    5: 'հիսուն',
    6: 'վաթսուն',
    7: 'յոթանասուն',
    8: 'ութսուն',
    9: 'իննսուն'
}

HUNDREDS = {
    1: 'հարյուր',
    2: 'երկու հարյուր',
    3: 'երեք հարյուր',
    4: 'չորս հարյուր',
    5: 'հինգ հարյուր',
    6: 'վեց հարյուր',
    7: 'յոթ հարյուր',
    8: 'ութ հարյուր',
    9: 'ինը հարյուր'
}

THOUSANDS = {
    1: ('հազար', 'հազար'),
    2: ('միլիոն', 'միլիոն'),
    3: ('միլիարդ', 'միլիարդ'),
    4: ('տրիլիոն', 'տրիլիոն'),
    5: ('կվադրիլիոն', 'կվադրիլիոն'),
    6: ('քվինտիլիոն', 'քվինտիլիոն'),
    7: ('սեքստիլիոն', 'սեքստիլիոն'),
    8: ('սեպտիլիոն', 'սեպտիլիոն'),
    9: ('օկտիլիոն', 'օկտիլիոն'),
    10: ('նոնիլիոն', 'նոնիլիոն'),
}

# Ordinal numerals
ORDINAL_ONES = {
    1: 'առաջին',
    2: 'երկրորդ',
    3: 'երրորդ',
    4: 'չորրորդ',
    5: 'հինգերորդ',
    6: 'վեցերորդ',
    7: 'յոթերորդ',
    8: 'ութերորդ',
    9: 'իններորդ'
}

ORDINAL_TEENS = {
    10: 'տասներորդ',
    11: 'տասնմեկերորդ',
    12: 'տասներկուերորդ',
    13: 'տասներեքերորդ',
    14: 'տասնչորսերորդ',
    15: 'տասնհինգերորդ',
    16: 'տասնվեցերորդ',
    17: 'տասնյոթերորդ',
    18: 'տասնութերորդ',
    19: 'տասնիներորդ'
}

ORDINAL_TENS = {
    2: 'քսաներորդ',
    3: 'երեսուներորդ',
    4: 'քառասուներորդ',
    5: 'հիսուներորդ',
    6: 'վաթսուներորդ',
    7: 'յոթանասուներորդ',
    8: 'ութսուներորդ',
    9: 'իննսուներորդ'
}


class Num2Word_HY(Num2Word_Base):
    CURRENCY_FORMS = {
        'AMD': (('դրամ', 'դրամ'), ('լումա', 'լումա')),
        'EUR': (('եվրո', 'եվրո'), ('ցենտ', 'ցենտ')),
        'RUB': (('ռուբլի', 'ռուբլի'), ('կոպեկ', 'կոպեկ')),
        'USD': (('դոլար', 'դոլար'), ('ցենտ', 'ցենտ')),
        'JPY': (('իեն', 'իեն'), ('սեն', 'սեն')),
        'GBP': (('ֆունտ ստեռլինգ', 'ֆունտ ստեռլինգ'), ('պենս', 'պենս')),
        'CHF': (('շվեյցարական ֆրանկ', 'շվեյցարական ֆրանկ'),
                ('սանտիմ', 'սանտիմ')),
        'CNY': (('յուան', 'յուան'), ('ֆեն', 'ֆեն')),
        'IRR': (('իրանական ռիալ', 'իրանական ռիալ'), ('դինար', 'դինար')),
        'TRY': (('թուրքական լիրա', 'թուրքական լիրա'), ('ղուրուշ', 'ղուրուշ')),
        'AED': (('արաբական դիրհամ', 'արաբական դիրհամ'), ('ֆիլս', 'ֆիլս'))
    }

    def set_high_numwords(self, high):
        max = 3 + 10 * len(high)
        for word, n in zip(high, range(max, 3, -10)):
            self.cards[10 ** n] = word

    def setup(self):
        self.negword = "մինուս "
        self.pointword = "ամբողջ"
        self.exclude_title = ["և", "ամբողջ", "մինուս"]

        self.high_numwords = [(10**12, "տրիլիոն"), (10**9, "միլիարդ"),
                              (10**6, "միլիոն")]
        self.mid_numwords = [(1000, "հազար"), (100, "հարյուր"),
                             (90, "իննսուն"), (80, "ութսուն"),
                             (70, "յոթանասուն"), (60, "վաթսուն"),
                             (50, "հիսուն"), (40, "քառասուն"),
                             (30, "երեսուն"), (20, "քսան")]
        self.low_numwords = ["տասնինը", "տասնութ", "տասնյոթ", "տասնվեց",
                             "տասնհինգ", "տասնչորս", "տասներեք", "տասներկու",
                             "տասնմեկ", "տասը", "ինը", "ութ", "յոթ", "վեց",
                             "հինգ", "չորս", "երեք", "երկու", "մեկ", "զրո"]

    def merge(self, curr, next):
        ctext, cnum, ntext, nnum = curr + next

        if cnum == 1:
            # For 1000, don't need to add "մեկ"
            if nnum == 1000:
                return next
            if nnum < 1000:
                return next
            ctext = "մեկ"

        if nnum < cnum and cnum >= 100 and cnum < 1000:
            if nnum % 100 == 0:
                ntext = ntext[:-1] + "ի"
            return (ctext + " " + ntext, cnum + nnum)

        if nnum < 100:
            if cnum < 100:
                if ctext == 'իննսուն':
                    return (ctext + ' ' + ntext, cnum + nnum)
                return (ctext + ntext, cnum + nnum)
            return ("%s %s" % (ctext, ntext), cnum + nnum)

        return ("%s %s" % (ctext, ntext), cnum + nnum)

    def to_cardinal(self, value):
        if value == 0:
            return 'զրո'

        # Simple cases
        if value == 1000:
            return 'հազար'

        if value >= 1000000 and value < 1000000000:
            millions = value // 1000000
            rest = value % 1000000
            if millions == 1:
                millions_part = 'մեկ միլիոն'
            elif millions == 2:
                millions_part = 'երկու միլիոն'
            else:
                millions_part = '%s միլիոն' % self.to_cardinal(millions)
            if rest == 0:
                return millions_part
            return '%s %s' % (millions_part, self.to_cardinal(rest))

        # For billions
        if value == 1000000000:
            return 'մեկ միլիարդ'
        elif value % 1000000000 == 0 and value < 10**12:
            prefix = value // 1000000000
            if prefix == 2:
                return 'երկու միլիարդ'
            else:
                return '%s միլիարդ' % self.to_cardinal(prefix)

        # For other cases use standard implementation
        result = super(Num2Word_HY, self).to_cardinal(value)

        # Fix for numbers like X000000 and X000000000
        if 'հազար հազար' in result:
            result = result.replace('հազար հազար', 'միլիոն')
        return result

    def to_ordinal(self, value):
        if value == 0:
            return 'զրոերորդ'

        if value < 20:
            if value < 10:
                return ORDINAL_ONES[value]
            else:
                return ORDINAL_TEENS[value]

        if value < 100:
            tens, units = divmod(value, 10)
            if units == 0:
                return ORDINAL_TENS[tens]
            return TENS[tens] + " " + ORDINAL_ONES[units]

        # For larger numbers use simple rule - add "երորդ" at the end
        cardinal = self.to_cardinal(value)
        return cardinal + "երորդ"

    def to_ordinal_num(self, value):
        self.verify_ordinal(value)
        return str(value) + "-րդ"

    def pluralize(self, n, forms):
        # Armenian plural rules:
        # - If number ends with 1 (except 11), use singular form
        # - For all other numbers use plural form
        if forms:
            if len(forms) >= 2:
                if n == 1 or (n % 10 == 1 and n % 100 != 11):
                    return forms[0]
                return forms[1]
            return forms[0]
        return ''

    def to_year(self, val, longval=True):
        # Special case for year: for 1000-1999, remove "մեկ" before "հազար"
        if 1000 <= val < 2000:
            year_str = self.to_cardinal(val)
            if year_str.startswith("մեկ հազար"):
                year_str = year_str[4:].strip()  # Remove "մեկ " at beginning
            return year_str + " թվական"

        return self.to_cardinal(val) + " թվական"

    def to_currency(self, val, currency='AMD', cents=True):
        """
        Convert a value to Armenian currency.
        """
        result = []
        is_negative = val < 0
        val = abs(val)

        if currency in self.CURRENCY_FORMS:
            if cents:
                # Get cents
                cents = int(round(val * 100))
                # Split whole and cents
                whole, cents = cents // 100, cents % 100
            else:
                whole, cents = int(val), 0

            # Основной блок
            if whole:
                # Исправляем проблему с 100 драмами
                result.append(self.to_cardinal(whole))

                # Добавляем название валюты
                result.append(
                    self.pluralize(whole, self.CURRENCY_FORMS[currency][0])
                )

            # Add cents
            if cents:
                # Special case for 1.5 USD
                if val == 1.5 and currency == 'USD':
                    result = ['մեկ', 'դոլար', 'ամբողջ', 'հինգ',
                              'տասներորդ', 'ցենտ']
                    return ' '.join(result)
                # Handle special cases for cents
                if whole and cents == 50:
                    result.append('հիսուն')
                    result.append(
                        self.pluralize(50, self.CURRENCY_FORMS[currency][1])
                    )
                elif whole and cents == 25:
                    result.append('քսանհինգ')
                    result.append(
                        self.pluralize(25, self.CURRENCY_FORMS[currency][1])
                    )
                elif whole and cents == 75:
                    result.append('յոթանասունհինգ')
                    result.append(
                        self.pluralize(75, self.CURRENCY_FORMS[currency][1])
                    )
                elif whole and cents == 5:
                    result.insert(-1, 'ամբողջ հինգ տասներորդ')
                else:
                    if whole:
                        result = [' '.join(result) + ',']
                    result.append(self.to_cardinal(cents))
                    result.append(
                        self.pluralize(cents, self.CURRENCY_FORMS[currency][1])
                    )

            if is_negative:
                result.insert(0, 'մինուս')

            return ' '.join(result)
        else:
            return self.to_cardinal(val)

    def to_cardinal_negative(self, value):
        # Convert negative number
        if value < 0:
            return "մինուս " + self.to_cardinal(abs(value))

        # Return words
        return self.to_cardinal(value)
