# -*- coding: utf-8 -*-
# Author: Mehedi Hasan Khondoker
# Email: mehedihasankhondoker [at] gmail.com
# Copyright (c) 2024, Mehedi Hasan Khondoker.  All Rights Reserved.

# This library is build for Bangladesh format Number to Word conversion.
# You are welcome as contributor to the library.

# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.


from decimal import Decimal

RANKING = ['', 'প্রথম', 'দ্বিতীয়', 'তৃতীয়', 'চতুর্থ', 'পঞ্চম', 'ষষ্ঠ',
           'সপ্তম', 'অষ্টম', 'নবম', 'দশম']  # pragma: no cover

AKOK = ['', 'এক', 'দুই', 'তিন', 'চার', 'পাঁচ', 'ছয়',
        'সাত', 'আট', 'নয়']  # pragma: no cover

DOSOK = [
    'দশ', 'এগারো', 'বারো', 'তেরো', 'চৌদ্দ', 'পনের',
    'ষোল', 'সতের', 'আঠারো', 'উনিশ',
    'বিশ', 'একুশ', 'বাইশ', 'তেইশ', 'চব্বিশ', 'পঁচিশ',
    'ছাব্বিশ', 'সাতাশ', 'আটাশ', 'উনত্রিশ',
    'ত্রিশ', 'একত্রিশ', 'বত্রিশ', 'তেত্রিশ', 'চৌত্রিশ', 'পঁইত্রিশ',
    'ছত্রিশ', 'সাতত্রিশ', 'আটত্রিশ', 'উনচল্লিশ', 'চল্লিশ',
    'একচল্লিশ', 'বিয়াল্লিশ', 'তেতাল্লিশ', 'চৌচল্লিশ',
    'পঁয়তাল্লিশ', 'ছেচল্লিশ', 'সাতচল্লিশ', 'আটচল্লিশ', 'উনপঞ্চাশ',
    'পঞ্চাশ', 'একান্ন', 'বাহান্ন', 'তিপ্পান্ন', 'চুয়ান্ন', 'পঞ্চান্ন',
    'ছাপ্পান্ন', 'সাতান্ন', 'আটান্ন', 'উনষাট', 'ষাট',
    'একষট্টি', 'বাষট্টি', 'তেষট্টি', 'চৌষট্টি', 'পঁয়ষট্টি',
    'ছিষট্টি', 'সাতষট্টি', 'আটষট্টি', 'উনসত্তর', 'সত্তর',
    'একাত্তর ', 'বাহাত্তর', 'তিয়াত্তর', 'চুয়াত্তর', 'পঁচাত্তর',
    'ছিয়াত্তর', 'সাতাত্তর', 'আটাত্তর', 'উনআশি', 'আশি',
    'একাশি', 'বিরাশি', 'তিরাশি', 'চুরাশি', 'পঁচাশি',
    'ছিয়াশি', 'সাতাশি', 'আটাশি', 'উননব্বই', 'নব্বই',
    'একানব্বই', 'বিরানব্বই', 'তিরানব্বই', 'চুরানব্বই', 'পঁচানব্বই',
    'ছিয়ানব্বই', 'সাতানব্বই', 'আটানব্বই', 'নিরানব্বই'
]  # pragma: no cover
HAZAR = ' হাজার '  # pragma: no cover
LAKH = ' লাখ '  # pragma: no cover
KOTI = ' কোটি '  # pragma: no cover
MAX_NUMBER = 9999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999  # noqa: E501 # pragma: no cover


class NumberTooLargeError(Exception):
    """Custom exception for numbers that are too large."""
    pass


class Num2Word_BN:

    @staticmethod
    def str_to_number(number):
        return abs(Decimal(str(number)))  # pragma: no cover

    @staticmethod
    def parse_number(number: Decimal):
        dosomik = str(number - int(number)).split('.')[1:]
        dosomik_str = ''.join(dosomik) if dosomik else 0
        return int(number), int(dosomik_str)

    @staticmethod
    def parse_paisa(number: Decimal):
        # 1-99 for paisa count so two digits are valid.
        paisa = str(number - int(number)).split('.')[1:]
        paisa_str = ''.join(paisa) if paisa else 0

        # this is need, when we parse to decimal it removes trailing 0 .
        if paisa_str:
            paisa_str = str(int(paisa_str) * 100)[:2]
        return int(number), int(paisa_str)

    def _is_smaller_than_max_number(self, number):
        if MAX_NUMBER >= number:
            return True
        raise NumberTooLargeError(f'Too Large number maximum '
                                  f'value={MAX_NUMBER}')

    def _dosomik_to_bengali_word(self, number):
        word = ''
        for i in str(number):
            word += ' ' + AKOK[int(i)]
        return word

    def _number_to_bengali_word(self, number):
        if number == 0:
            return 'শূন্য'

        words = ''

        if number >= 10 ** 7:
            words += self._number_to_bengali_word(number // 10 ** 7) + KOTI
            number %= 10 ** 7

        if number >= 10 ** 5:
            words += self._number_to_bengali_word(number // 10 ** 5) + LAKH
            number %= 10 ** 5

        if number >= 1000:
            words += self._number_to_bengali_word(number // 1000) + HAZAR
            number %= 1000

        if number >= 100:
            words += AKOK[number // 100] + 'শত '
            number %= 100

        if 10 <= number <= 99:
            words += DOSOK[number - 10] + ' '
            number = 0

        if 0 < number < 10:
            words += AKOK[number] + ' '

        return words.strip()

    def to_currency(self, val):
        """
        This function represent a number to word in bangla taka and paisa.
        example:
        1 = এক টাকা,
        101 = একশত এক টাকা,
        9999.15 = নয় হাজার নয়শত নিরানব্বই টাকা পনের পয়সা
        and so on.
        """

        dosomik_word = None
        number = self.str_to_number(val)
        number, decimal_part = self.parse_paisa(number)
        self._is_smaller_than_max_number(number)

        if decimal_part > 0:
            dosomik_word = f' {self._number_to_bengali_word(decimal_part)} পয়সা'  # noqa: E501

        words = f'{self._number_to_bengali_word(number)} টাকা'

        if dosomik_word:
            return (words + dosomik_word).strip()
        return words.strip()

    def to_cardinal(self, number):
        """
        This function represent a number to word in bangla.
        example:
        1 = এক,
        101 = একশত এক,
        9999 = নয় হাজার নয়শত নিরানব্বই
        and so on.
        """

        dosomik_word = None
        number = self.str_to_number(number)
        number, decimal_part = self.parse_number(number)
        self._is_smaller_than_max_number(number)

        if decimal_part > 0:
            dosomik_word = f' দশমিক{self._dosomik_to_bengali_word(decimal_part)}'  # noqa: E501

        words = self._number_to_bengali_word(number)

        if dosomik_word:
            return (words + dosomik_word).strip()
        return words.strip()

    def to_ordinal(self, number):
        return self.to_cardinal(number)

    def to_ordinal_num(self, number):
        """
        This function represent a number to ranking in bangla.
        example:
        1 = প্রথম,
        2 = দ্বিতীয়,
        1001 = এক হাজার একতম
        and so on.
        """
        self._is_smaller_than_max_number(number)

        if number in range(1, 11):
            return RANKING[number]
        else:
            rank = self.to_cardinal(int(abs(number)))
            if rank.endswith('ত'):
                return rank + 'ম'
            return rank + 'তম'

    def to_year(self, number):
        """
        This function represent a number to year in bangla.
        example:
        2002 = দুই হাজার দুই সাল,
        2024 = দুই হাজার চব্বিশ সাল
        and so on.
        """
        self._is_smaller_than_max_number(number)
        return self.to_cardinal(int(abs(number))) + ' সাল'
