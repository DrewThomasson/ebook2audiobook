from lib.conf_models import TTS_ENGINES, default_engine_settings

models = {
    "internal": {
        "lang": "multi",
        "repo": "rhasspy/piper-voices",
        "sub": {
            "ar_JO": ["ar_JO-kareem-medium", "ar_JO-kareem-medium"],
            "ca_ES": ["ca_ES-upc_ona-medium", "ca_ES-upc_ona-medium"],
            "cs_CZ": ["cs_CZ-jirka-medium", "cs_CZ-jirka-medium"],
            "cy_GB": ["cy_GB-gwryw_gogleddol-medium", "cy_GB-bu_tts-medium"],
            "da_DK": ["da_DK-talesyntese-medium", "da_DK-talesyntese-medium"],
            "de_DE": ["de_DE-thorsten_emotional-medium", "de_DE-mls-medium"],
            "el_GR": ["el_GR-rapunzelina-low", "el_GR-rapunzelina-low"],
            "en_GB": ["en_GB-alan-medium", "en_GB-cori-high"],
            "es_ES": ["es_ES-davefx-medium", "es_ES-sharvard-medium"],
            "fa_IR": ["fa_IR-amir-medium", "fa_IR-amir-medium"],
            "fi_FI": ["fi_FI-harri-medium", "fi_FI-harri-low"],
            "fr_FR": ["fr_FR-tom-medium", "fr_FR-siwis-medium"],
            "hu_HU": ["hu_HU-anna-medium", "hu_HU-anna-medium"],
            "is_IS": ["is_IS-bui-medium", "is_IS-salka-medium"],
            "it_IT": ["it_IT-riccardo-x_low", "it_IT-paola-medium"],
            "ka_GE": ["ka_GE-natia-medium", "ka_GE-natia-medium"],
            "kk_KZ": ["kk_KZ-issai-high", "kk_KZ-iseke-x_low"],
            "lb_LU": ["lb_LU-marylux-medium", "lb_LU-marylux-medium"],
            "lv_LV": ["lv_LV-aivars-medium", "lv_LV-aivars-medium"],
            "ne_NP": ["ne_NP-google-medium", "ne_NP-google-medium"],
            "nl_NL": ["nl_NL-mls-medium", "nl_NL-mls_5809-low"],
            "no_NO": ["no_NO-talesyntese-medium", "no_NO-talesyntese-medium"],
            "pl_PL": ["pl_PL-darkman-medium", "pl_PL-gosia-medium"],
            "pt_PT": ["pt_PT-tug%C3%A3o-medium", "pt_PT-tugão-medium"],
            "ro_RO": ["ro_RO-mihai-medium", "ro_RO-mihai-medium"],
            "ru_RU": ["ru_RU-denis-medium", "ru_RU-irina-medium"],
            "sk_SK": ["sk_SK-lili-medium", "sk_SK-lili-medium"],
            "sl_SI": ["sl_SI-artur-medium", "sl_SI-artur-medium"],
            "sr_RS": ["sr_RS-serbski_institut-medium", "sr_RS-serbski_institut-medium"],
            "sv_SE": ["sv_SE-nst-medium", "sv_SE-nst-medium"],
            "sw_CD": ["sw_CD-lanfrica-medium", "sw_CD-lanfrica-medium"],
            "tr_TR": ["tr_TR-dfki-medium", "tr_TR-dfki-medium"],
            "uk_UA": ["uk_UA-ukrainian_tts-medium", "uk_UA-lada-x_low"],
            "ur_PK": ["ur_PK-fasih-medium", "ur_PK-fasih-medium"],
            "vi_VN": ["vi_VN-vais1000-medium", "vi_VN-25hours_single-low"],
            "zh_CN": ["zh_CN-huayan-medium", "zh_CN-huayan-medium"]
        },
        "voice": default_engine_settings[TTS_ENGINES['PIPER']]['voice'],
        "files": default_engine_settings[TTS_ENGINES['PIPER']]['files'],
        "samplerate": default_engine_settings[TTS_ENGINES['PIPER']]['samplerate']
    }
}
