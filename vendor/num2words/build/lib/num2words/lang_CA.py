from __future__ import division, print_function, unicode_literals

import math

from .lang_EU import Num2Word_EU

GENERIC_DOLLARS = ('dòlar', 'dòlars')
GENERIC_CENTS = ('centau', 'centaus')
CURRENCIES_UNA = (
    'SLL',
    'SEK',
    'NOK',
    'CZK',
    'DKK',
    'ISK',
    'SKK',
    'GBP',
    'CYP',
    'EGP',
    'FKP',
    'GIP',
    'LBP',
    'SDG',
    'SHP',
    'SSP',
    'SYP',
    'INR',
    'IDR',
    'LKR',
    'MUR',
    'NPR',
    'PKR',
    'SCR',
    'ESP',
    'TRY',
    'ITL',
)
CENTS_UNA = ('EGP', 'JOD', 'LBP', 'SDG', 'SSP', 'SYP')


class Num2Word_CA(Num2Word_EU):
    CURRENCY_FORMS = {
        'EUR': (('euro', 'euros'), ('cèntim', 'cèntims')),
        'ESP': (('pesseta', 'pessetes'), ('cèntim', 'cèntims')),
        'USD': (GENERIC_DOLLARS, ('centau', 'centaus')),
        'PEN': (('sol', 'sols'), ('cèntim', 'cèntims')),
        'CRC': (('colón', 'colons'), GENERIC_CENTS),
        'AUD': (GENERIC_DOLLARS, GENERIC_CENTS),
        'CAD': (GENERIC_DOLLARS, GENERIC_CENTS),
        'GBP': (('lliura', 'lliures'), ('penic', 'penics')),
        'RUB': (('ruble', 'rubles'), ('copec', 'copecs')),
        'SEK': (('corona', 'corones'), ('öre', 'öre')),
        'NOK': (('corona', 'corones'), ('øre', 'øre')),
        'PLN': (('zloty', 'zlotys'), ('grosz', 'groszy')),
        'MXN': (('peso', 'pesos'), GENERIC_CENTS),
        'RON': (('leu', 'lei'), ('ban', 'bani')),
        'INR': (('rupia', 'rupies'), ('paisa', 'paise')),
        'HUF': (('fòrint', 'fòrints'), ('fillér', 'fillérs')),
        'FRF': (('franc', 'francs'), ('cèntim', 'cèntims')),
        'CNY': (('iuan', 'iuans'), ('fen', 'jiao')),
        'CZK': (('corona', 'corones'), ('haléř', 'haléřů')),
        'NIO': (('córdoba', 'córdobas'), GENERIC_CENTS),
        'VES': (('bolívar', 'bolívars'), ('cèntim', 'cèntims')),
        'BRL': (('real', 'reals'), GENERIC_CENTS),
        'CHF': (('franc', 'francs'), ('cèntim', 'cèntims')),
        'JPY': (('ien', 'iens'), ('sen', 'sen')),
        'KRW': (('won', 'wons'), ('jeon', 'jeon')),
        'KPW': (('won', 'wons'), ('chŏn', 'chŏn')),
        'TRY': (('lira', 'lires'), ('kuruş', 'kuruş')),
        'ZAR': (('rand', 'rands'), ('cèntim', 'cèntims')),
        'KZT': (('tenge', 'tenge'), ('tin', 'tin')),
        'UAH': (('hrívnia', 'hrívnies'), ('kopiika', 'kopíok')),
        'THB': (('baht', 'bahts'), ('satang', 'satang')),
        'AED': (('dirham', 'dirhams'), ('fils', 'fulūs')),
        'AFN': (('afgani', 'afganis'), ('puli', 'puls')),
        'ALL': (('lek', 'lekë'), ('qqindarka', 'qindarkë')),
        'AMD': (('dram', 'drams'), ('luma', 'lumas')),
        'ANG': (('florí', 'florins'), ('cèntim', 'cèntims')),
        'AOA': (('kwanza', 'kwanzes'), ('cèntim', 'cèntims')),
        'ARS': (('peso', 'pesos'), GENERIC_CENTS),
        'AWG': (('florí', 'florins'), GENERIC_CENTS),
        'AZN': (('manat', 'manats'), ('qəpik', 'qəpik')),
        'BBD': (GENERIC_DOLLARS, GENERIC_CENTS),
        'BDT': (('taka', 'taka'), ('poisha', 'poisha')),
        'BGN': (('lev', 'leva'), ('stotinka', 'stotinki')),
        'BHD': (('dinar', 'dinars'), ('fils', 'fulūs')),
        'BIF': (('franc', 'francs'), ('cèntim', 'cèntims')),
        'BMD': (GENERIC_DOLLARS, GENERIC_CENTS),
        'BND': (GENERIC_DOLLARS, GENERIC_CENTS),
        'BOB': (('boliviano', 'bolivianos'), GENERIC_CENTS),
        'BSD': (GENERIC_DOLLARS, GENERIC_CENTS),
        'BTN': (('ngultrum', 'ngultrums'), ('chetrum', 'chetrums')),
        'BWP': (('pula', 'pula'), ('thebe', 'thebe')),
        'BYN': (('ruble', 'rubles'), ('copec', 'copecs')),
        'BYR': (('ruble', 'rubles'), ('copec', 'copecs')),
        'BZD': (GENERIC_DOLLARS, ('cèntim', 'cèntims')),
        'CDF': (('franc', 'francs'), ('cèntim', 'cèntims')),
        'CLP': (('peso', 'pesos'), GENERIC_CENTS),
        'COP': (('peso', 'pesos'), GENERIC_CENTS),
        'CUP': (('peso', 'pesos'), GENERIC_CENTS),
        'CVE': (('escut', 'escuts'), GENERIC_CENTS),
        'CYP': (('lliura', 'lliures'), ('cèntim', 'cèntims')),
        'DJF': (('franc', 'francs'), ('cèntim', 'cèntims')),
        'DKK': (('corona', 'corones'), ('øre', 'øre')),
        'DOP': (('peso', 'pesos'), GENERIC_CENTS),
        'DZD': (('dinar', 'dinars'), ('cèntim', 'cèntims')),
        'ECS': (('sucre', 'sucres'), GENERIC_CENTS),
        'EGP': (('lliura', 'lliures'), ('piastre', 'piastres')),
        'ERN': (('nakfa', 'nakfes'), ('cèntim', 'cèntims')),
        'ETB': (('birr', 'birr'), ('cèntim', 'cèntims')),
        'FJD': (GENERIC_DOLLARS, GENERIC_CENTS),
        'FKP': (('lliura', 'lliures'), ('penic', 'penics')),
        'GEL': (('lari', 'laris'), ('tetri', 'tetri')),
        'GHS': (('cedi', 'cedis'), ('pesewa', 'pesewas')),
        'GIP': (('lliura', 'lliures'), ('penic', 'penics')),
        'GMD': (('dalasi', 'dalasis'), ('butut', 'bututs')),
        'GNF': (('franc', 'francs'), ('cèntim', 'cèntims')),
        'GTQ': (('quetzal', 'quetzals'), GENERIC_CENTS),
        'GYD': (GENERIC_DOLLARS, GENERIC_CENTS),
        'HKD': (GENERIC_DOLLARS, GENERIC_CENTS),
        'HNL': (('lempira', 'lempires'), GENERIC_CENTS),
        'HRK': (('kuna', 'kuna'), ('lipa', 'lipa')),
        'HTG': (('gourde', 'gourdes'), ('cèntim', 'cèntims')),
        'IDR': (('rúpia', 'rúpies'), ('cèntim', 'cèntims')),
        'ILS': (('xéquel', 'xéquels'), ('agorà', 'agorot')),
        'IQD': (('dinar', 'dinars'), ('fils', 'fils')),
        'IRR': (('rial', 'rials'), ('dinar', 'dinars')),
        'ISK': (('corona', 'corones'), ('eyrir', 'aurar')),
        'ITL': (('lira', 'lires'), ('cèntim', 'cèntims')),
        'JMD': (GENERIC_DOLLARS, ('cèntim', 'cèntims')),
        'JOD': (('dinar', 'dinars'), ('piastra', 'piastres')),
        'KES': (('xiling', 'xílings'), ('cèntim', 'cèntims')),
        'KGS': (('som', 'som'), ('tyiyn', 'tyiyn')),
        'KHR': (('riel', 'riels'), ('cèntim', 'cèntims')),
        'KMF': (('franc', 'francs'), ('cèntim', 'cèntims')),
        'KWD': (('dinar', 'dinars'), ('fils', 'fils')),
        'KYD': (GENERIC_DOLLARS, ('cèntim', 'cèntims')),
        'LAK': (('kip', 'kips'), ('at', 'at')),
        'LBP': (('lliura', 'lliures'), ('piastra', 'piastres')),
        'LKR': (('rúpia', 'rúpies'), ('cèntim', 'cèntims')),
        'LRD': (GENERIC_DOLLARS, ('cèntim', 'cèntims')),
        'LSL': (('loti', 'maloti'), ('sente', 'lisente')),
        'LTL': (('lita', 'litai'), ('cèntim', 'cèntims')),
        'LYD': (('dinar', 'dinars'), ('dírham', 'dírhams')),
        'MAD': (('dírham', 'dirhams'), ('cèntim', 'cèntims')),
        'MDL': (('leu', 'lei'), ('ban', 'bani')),
        'MGA': (('ariary', 'ariary'), ('iraimbilanja', 'iraimbilanja')),
        'MKD': (('denar', 'denari'), ('deni', 'deni')),
        'MMK': (('kyat', 'kyats'), ('pya', 'pyas')),
        'MNT': (('tögrög', 'tögrög'), ('möngö', 'möngö')),
        'MOP': (('pataca', 'pataques'), ('avo', 'avos')),
        'MRO': (('ouguiya', 'ouguiya'), ('khoums', 'khoums')),
        'MRU': (('ouguiya', 'ouguiya'), ('khoums', 'khoums')),
        'MUR': (('rupia', 'rúpies'), ('cèntim', 'cèntims')),
        'MVR': (('rufiyaa', 'rufiyaa'), ('laari', 'laari')),
        'MWK': (('kwacha', 'kwacha'), ('tambala', 'tambala')),
        'MYR': (('ringgit', 'ringgits'), ('sen', 'sens')),
        'MZN': (('metical', 'meticals'), GENERIC_CENTS),
        'NAD': (GENERIC_DOLLARS, ('cèntim', 'cèntims')),
        'NGN': (('naira', 'naires'), ('kobo', 'kobos')),
        'NPR': (('rupia', 'rupies'), ('paisa', 'paises')),
        'NZD': (GENERIC_DOLLARS, GENERIC_CENTS),
        'OMR': (('rial', 'rials'), ('baisa', 'baisa')),
        'PAB': (GENERIC_DOLLARS, ('centésimo', 'centésimos')),
        'PGK': (('kina', 'kina'), ('toea', 'toea')),
        'PHP': (('peso', 'pesos'), GENERIC_CENTS),
        'PKR': (('rupia', 'rupies'), ('paisa', 'paise')),
        'PLZ': (('zloty', 'zlotys'), ('grosz', 'groszy')),
        'PYG': (('guaraní', 'guaranís'), ('cèntim', 'cèntims')),
        'QAR': (('rial', 'rials'), ('dírham', 'dírhams')),
        'QTQ': (('quetzal', 'quetzals'), GENERIC_CENTS),
        'RSD': (('dinar', 'dinars'), ('para', 'para')),
        'RUR': (('ruble', 'rubles'), ('copec', 'copecs')),
        'RWF': (('franc', 'francs'), ('cèntim', 'cèntims')),
        'SAR': (('riyal', 'riyals'), ('hàl·lala', 'hàl·lalat')),
        'SBD': (GENERIC_DOLLARS, ('cèntim', 'cèntims')),
        'SCR': (('rupia', 'rupies'), ('cèntim', 'cèntims')),
        'SDG': (('lliura', 'lliures'), ('piastre', 'piastres')),
        'SGD': (GENERIC_DOLLARS, ('cèntim', 'cèntims')),
        'SHP': (('lliura', 'lliures'), ('penic', 'penics')),
        'SLL': (('leonE', 'leones'), ('cèntim', 'cèntims')),
        'SRD': (GENERIC_DOLLARS, ('cèntim', 'cèntims')),
        'SSP': (('lliura', 'lliures'), ('piastre', 'piastres')),
        'STD': (('dobra', 'dobrAs'), ('cèntim', 'cèntims')),
        'SVC': (('colón', 'colons'), GENERIC_CENTS),
        'SYP': (('lliura', 'lliures'), ('piastre', 'piastres')),
        'SZL': (('lilangeni', 'emalangeni'), ('cèntim', 'cèntims')),
        'TJS': (('somoni', 'somoni'), ('diram', 'diram')),
        'TMT': (('manat', 'manats'), ('teňňesi', 'teňňesi')),
        'TND': (('dinar', 'dinars'), ('mil·lim', 'mil·limat')),
        'TOP': (('paanga', 'paangas'), ('seniti', 'seniti')),
        'TTD': (GENERIC_DOLLARS, ('cèntim', 'cèntims')),
        'TWD': (('nou dòlar', 'nous dòlars'), ('fen', 'fen')),
        'TZS': (('xíling', 'xílings'), ('cèntim', 'cèntims')),
        'UGX': (('xíling', 'xílings'), ('cèntim', 'cèntims')),
        'UYU': (('peso', 'pesos'), ('centèsim', 'centèsims')),
        'UZS': (('som', 'som'), ('tiyin', 'tiyin')),
        'VND': (('dong', 'dongs'), ('xu', 'xu')),
        'VUV': (('vatu', 'vatus'), ('cèntim', 'cèntims')),
        'WST': (('tala', 'tala'), ('sene', 'sene')),
        'XAF': (('franc CFA', 'francs CFA'), ('cèntim', 'cèntims')),
        'XCD': (GENERIC_DOLLARS, ('cèntim', 'cèntims')),
        'XOF': (('franc CFA', 'francs CFA'), ('cèntim', 'cèntims')),
        'XPF': (('franc CFP', 'francs CFP'), ('cèntim', 'cèntims')),
        'YER': (('rial', 'rials'), ('fils', 'fils')),
        'YUM': (('dinar', 'dinars'), ('para', 'para')),
        'ZMW': (('kwacha', 'kwacha'), ('ngwee', 'ngwee')),
        'ZWL': (GENERIC_DOLLARS, ('cèntim', 'cèntims')),
        'ZWL': (GENERIC_DOLLARS, ('cèntim', 'cèntims')),
    }

    GIGA_SUFFIX = None
    MEGA_SUFFIX = "ilió"

    def setup(self):
        lows = ["quadr", "tr", "b", "m"]
        self.high_numwords = self.gen_high_numwords([], [], lows)
        self.negword = "menys "
        self.pointword = "punt"
        self.errmsg_nonnum = "type(%s) no és [long, int, float]"
        self.errmsg_floatord = "El float %s no pot ser tractat com un" \
            " ordinal."
        self.errmsg_negord = "El número negatiu %s no pot ser tractat" \
            " com un ordinal."
        self.errmsg_toobig = "abs(%s) ha de ser inferior a %s."
        self.gender_stem = "è"
        self.exclude_title = ["i", "menys", "punt"]

        self.mid_numwords = [
            (1000, "mil"),
            (100, "cent"),
            (90, "noranta"),
            (80, "vuitanta"),
            (70, "setanta"),
            (60, "seixanta"),
            (50, "cinquanta"),
            (40, "quaranta"),
            (30, "trenta"),
        ]
        self.low_numwords = [
            "vint-i-nou",
            "vint-i-vuit",
            "vint-i-set",
            "vint-i-sis",
            "vint-i-cinc",
            "vint-i-quatre",
            "vint-i-tres",
            "vint-i-dos",
            "vint-i-un",
            "vint",
            "dinou",
            "divuit",
            "disset",
            "setze",
            "quinze",
            "catorze",
            "tretze",
            "dotze",
            "onze",
            "deu",
            "nou",
            "vuit",
            "set",
            "sis",
            "cinc",
            "quatre",
            "tres",
            "dos",
            "un",
            "zero",
        ]
        self.mid_num = {
            1000: "mil",
            100: "cent",
            90: "noranta",
            80: "vuitanta",
            70: "setanta",
            60: "seixanta",
            50: "cinquanta",
            40: "quaranta",
            30: "trenta",
            20: "vint",
            10: "deu",
        }
        self.low_num = {
            0: "zero",
            1: "un",
            2: "dos",
            3: "tres",
            4: "quatre",
            5: "cinc",
            6: "sis",
            7: "set",
            8: "vuit",
            9: "nou",
            10: "deu",
            11: "onze",
            12: "dotze",
            13: "tretze",
            14: "catorze",
            15: "quinze",
            16: "setze",
            17: "disset",
            18: "divuit",
            19: "dinou",
            20: "vint",
            21: "vint-i-un",
            22: "vint-i-dos",
            23: "vint-i-tres",
            24: "vint-i-quatre",
            25: "vint-i-cinc",
            26: "vint-i-sis",
            27: "vint-i-set",
            28: "vint-i-vuit",
            29: "vint-i-nou",
        }
        self.ords = {
            1: "primer",
            2: "segon",
            3: "tercer",
            4: "quart",
            5: "cinqu",
            6: "sis",
            7: "set",
            8: "vuit",
            9: "nov",
            10: "des",
            11: "onz",
            12: "dotz",
            13: "tretz",
            14: "catorz",
            15: "quinz",
            16: "setz",
            17: "disset",
            18: "divuit",
            19: "dinov",
            20: "vint",
            30: "trent",
            40: "quarant",
            50: "cinquant",
            60: "seixant",
            70: "setant",
            80: "vuitant",
            90: "norant",
            100: "cent",
            200: "dos-cent",
            300: "tres-cent",
            400: "quatre-cent",
            500: "cinc-cent",
            600: "sis-cent",
            700: "set-cent",
            800: "vuit-cent",
            900: "nou-cent",
            1e3: "mil",
            1e6: "milion",
            1e9: "mil milion",
            1e12: "bilion",
            1e15: "mil bilion",
        }

        self.ords_2 = {1: "1r", 2: "2n", 3: "3r", 4: "4t"}
        self.ords_3 = {
            1: "unè",
            2: "dosè",
            3: "tresè",
            4: "quatrè",
            5: "cinquè",
            6: "sisè",
            7: "setè",
            8: "vuitè",
            9: "novè",
        }

    def merge(self, curr, next):
        ctext, cnum, ntext, nnum = curr + next
        if cnum == 1:
            if nnum < 1000000:
                return next
            ctext = "un"

        if nnum < cnum:
            if cnum < 100:
                return "%s-%s" % (ctext, ntext), cnum + nnum
            elif nnum == 1:
                return "%s %s" % (ctext, ntext), cnum + nnum
            elif cnum == 100:
                return "%s %s" % (ctext, ntext), cnum + nnum
            else:
                return "%s %s" % (ctext, ntext), cnum + nnum
        elif (not nnum % 1000000) and cnum > 1:
            ntext = ntext[:-3] + "lions"
        if nnum == 100:
            ntext += "s"
            ctext += "-"
        else:
            ntext = " " + ntext
        return (ctext + ntext, cnum * nnum)

    def to_ordinal(self, value):
        self.verify_ordinal(value)
        if value == 0:
            text = ""
        elif value < 5:
            text = self.ords[value]
        elif value <= 20:
            text = "%s%s" % (self.ords[value], self.gender_stem)
        elif value <= 30:
            frac = value % 10
            text = "%s%s%s" % (self.ords[20], "-i-", self.ords_3[frac])
        elif value < 100:
            dec = (value // 10) * 10
            text = "%s%s%s%s" % (self.ords[dec], "a",
                                 "-", self.ords_3[value - dec])
        elif value == 1e2:
            text = "%s%s" % (self.ords[value], self.gender_stem)
        elif value < 2e2:
            cen = (value // 100) * 100
            text = "%s %s" % (self.ords[cen], self.to_ordinal(value - cen))
        elif value < 1e3:
            cen = (value // 100) * 100
            text = "%s%s %s" % (self.ords[cen], "s",
                                self.to_ordinal(value - cen))
        elif value == 1e3:
            text = "%s%s" % (self.ords[value], self.gender_stem)
        elif value < 1e6:
            dec = 1000 ** int(math.log(int(value), 1000))
            high_part, low_part = divmod(value, dec)
            cardinal = self.to_cardinal(high_part) if high_part != 1 else ""
            text = "%s %s %s" % (cardinal, self.ords[dec],
                                 self.to_ordinal(low_part))
        elif value < 1e18:
            dec = 1000 ** int(math.log(int(value), 1000))
            high_part, low_part = divmod(value, dec)
            cardinal = self.to_cardinal(high_part) if high_part != 1 else ""
            text = "%s%s%s %s" % (cardinal, self.ords[dec],
                                  self.gender_stem, self.to_ordinal(low_part))
        else:
            part1 = self.to_cardinal(value)
            text = "%s%s" % (part1[:-1], "onè")
        return text.strip()

    def to_ordinal_num(self, value):
        self.verify_ordinal(value)
        if value not in self.ords_2:
            return "%s%s" % (value, "è" if self.gender_stem == "è" else "a")
        else:
            return self.ords_2[value]

    def to_currency(self, val, currency="EUR", cents=True,
                    separator=" amb", adjective=False):
        result = super(Num2Word_CA, self).to_currency(
            val, currency=currency, cents=cents,
            separator=separator, adjective=adjective
        )
        list_result = result.split(separator + " ")

        if currency in CURRENCIES_UNA:
            list_result[0] = list_result[0].replace("un", "una")
            list_result[0] = list_result[0].replace("dos", "dues")
            list_result[0] = list_result[0].replace("cents", "centes")

        list_result[0] = list_result[0].replace("vint-i-un", "vint-i-un")
        list_result[0] = list_result[0].replace(" i un", "-un")
        list_result[0] = list_result[0].replace("un", "un")

        if currency in CENTS_UNA:
            list_result[1] = list_result[1].replace("un", "una")
            list_result[1] = list_result[1].replace("dos", "dues")

        list_result[1] = list_result[1].replace("vint-i-un", "vint-i-una")

        list_result[1] = list_result[1].replace("un", "un")

        result = (separator + " ").join(list_result)

        return result
