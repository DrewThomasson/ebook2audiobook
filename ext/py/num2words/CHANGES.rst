Changelog
=========

Version 0.5.14 -- 2024/12/16
----------------------------

* Fixed a typo in PL (#466)
* Run tests against Python 3.12 (#544)
* ADD num2words: es_CR language (#565)
* New languages: Welsh (Celtic) and Chechen (Nakho-Dagestanian) (#543)
* Add catalan language support (#581)
* Adding Tetum Language (#576)
* FIX ISO code for Belarusian language is be, not by. (#574)
* Add test to improve coverage (#595)
* Added Bangla language support to num2word for Bangladesh. (#589)
* Czech language ISO 639-1 code fix (#587)
* Added support for Tunisian Dinar  (#593)
* Change danish language code to DA (#596)


Version 0.5.13 -- 2023/10/18
---------------------------

* Fix a problem in Brazilian Portuguese code referred to thousands when the hundreds are exact. (#421)
* Fix issue with the hundreds of millions, billions, ... when the hundreds of those are exact. (#436)
* Fix negative number problem (#477)
* Fix lang_DK issues (#366)
* Norwegian uplift (#484)
* BYN to EU and RU (#439)
* Change python3.6 to python3.11 because deprecation in ubuntu 22.04 (#494)
* Add support for Azerbaijani language (#495)
* Add Icelandic (#380)
* Hebrew long-form spelling, gender, ordinals, fractions, maxval=1e66, construct forms (#490)
* Fix 15, 16, 17, 18, 19 issue (#505)
* Added support for the Nigerian Naira (#507)
* Fix several issues with num2words in Arabic (#512)
* Guatemalan currency support (#510)
* Fix #508: Handle string inputs in Italian to_ordinal (#518)
* Add Slovak language support (#533)
* Add gender and morphological cases support for Ukrainian (#530)
* Adding genders for Russian language (#503)
* Lang By Added (#506)
* Add Saudi Riyal to english (#531)

Version 0.5.12 -- 2022/08/19
----------------------------

* Support Japanese Reiwa (令和/れいわ) era. (#412)
* Add basic farsi support (#354)
* Added Tajik language support (#406)
* Fix Amharic language support (#465)
* Fix Hebrew pluralize and implement to_currency (#330)
* Add support to translate some currencies in italian language (#434)
* Fix Polish twenties (#345)
* Add uzs for ru and en (#422)
* Added support for Esperanto numbers. (#387)
* [ADD] to ordinal number for Turkish (#468)
* Fix zeroth in Dutch to nulde fixing (#326)

Version 0.5.11 -- 2022/08/03
----------------------------

* Add KZT and UAH currencies to lang RU (#264)
* Add es_NI currency (#276)
* Update .gitignore to add .eggs/ directory (#280)
* Fix Hebrew support (#289)
* Update test_tr.py to increase coverage (#298)
* Add ordinal 12,345 to ES test suite to increase coverage (#287)
* Add simple tests for lang_DK.py (#286)
* Add testcase for lang_EN.py (#288)
* Add more tests to base.py (#283)
* Fixed misspelling of 21 (cardinal and ordinal number) in IT language (#270)
* Romanian issues 259 (#260)
* Adding Language Support for Telugu / Bug Fix in Kannada (#263)
* Add support of Kazakh language (KZ) (#306)
* Update README.rst (#307)
* Added support for Hungarian language (#310)
* [UPD] Readme file (#363)
* [ADD] num2words: add traslation to spanish of several currencies (#356)
* added swedish language including test cases (#352)
* Remove dupplicated line in lang_PT_BR (#355)
* Fix ordinal_num output for Dutch (NL) (#369)
* Polishordinals (#367)
* [tr] return Turkish 0 ordinal and cardinal (#347)
* Improve Ukrainian support and minor fixes in CZ, KZ, LT, LV, PL, RU, SR languages (#400)
* feat: ci: replace travis by github workflows (#448)
* [ES] Added missing accents ("dieciséis", "dólar", "dólares", "veintiún"), improved currency gender handling, fixed pound cent names (#443)

Version 0.5.10 -- 2019/05/12
----------------------------

* Add Kannada language localization (#243)
* Revert some copyrights changed by mistake (#254)
* Add indian rupee to the supported currencies (#248)
* Improve currency functions for German and French (#247)
* Improve Slovene localization (#246)
* Improve Spanish localization (#240)
* Fix typo 'seperator' on source code (#238)
* Convert string to decimal values (#223)
* Improve German localization and test coverage (#237)
* Improve Polish localization (#233)
* Fix ordinal number for French ending on 1 (#236)

Version 0.5.9 -- 2019/01/10
---------------------------

* Fix encoding issue on release 0.5.8 (#229)
* Improve Polish localization (#228)


Version 0.5.8 -- 2018/11/17
---------------------------

* Add Portuguese (Portugal) localization (#198)
* Add a command line tool to use num2words
* Use language iso code for Vietnamese
* Improve Korean localization (#219)
* Improve Serbian (Latin) localization (#207)
* Improve testing setup (#220)
* Improve German localization (#214) (#222)
* Improve Romanian localization (#215)
* Improve Spanish localization (#187) (#200)
* Improve Russian localization (#211) (#212)
* Improve French localization (23902ab)
* Improve Arabic localization (#176)
* Improve Lithuanian and Latvian localization (#185)
* Improve Ukrainian localization (#183)


Version 0.5.7 -- 2018/06/27
---------------------------

* Add Finnish localization. (#170)
* Add Japanese localization. (#171)
* Add belgian-french localization. (#151)
* Add Czech localization. (#154)
* Add Thai localization. (#139)
* Improve English localization. (#144)
* Improve Spanish localization. (#167)
* Improve Italian localization. (#143)
* Improve documentation. (#155, #145, #174)

Version 0.5.6 -- 2017/11/22
---------------------------

* Refactor to_currency (#135)
* Allow the use of other convertes to_currency, to_year (#95)
* Fix code to respect PEP8 (#98, #105)
* Add Slovene localization (#97)
* Add Ukrainian localization (#93)
* Add Dutch localization (#91)
* Add Algeria-French localization (#86)
* Add Turkish localization (#85)

Version 0.5.5 -- 2017/07/02
---------------------------

* Add Arabic localization (#72)
* Add Spanish-Colombian and Spanish-Venezuelan localization (#67)
* Add VietNam localization (#61)
* Add Italian localization (#56, #59)
* Improve Russian localization (#62)
* Improve Polish localization (#58)

Version 0.5.4 -- 2016/10/18
---------------------------

* Tons of new languages!
* Add Polish localization. (#23)
* Add Swiss-French localization. (#38)
* Add Russian localization. (#28, #46, #48)
* Add Indonesian localization. (#29)
* Add Norwegian localization. (#33)
* Add Danish localization. (#40)
* Add Brazilian localization. (#37, #47)
* Improve German localization. (#25, #27, #49)
* Improve Lithuanian localization. (#52)
* Improve floating point spelling. (#24)

Version 0.5.3 -- 2015/06/09
---------------------------

* Fix packaging issues. (#21, #22)

Version 0.5.2 -- 2015/01/23
---------------------------

* Added Latvian localization. (#9)
* Improved Spanish localization. (#10, #13, #14)
* Improved Lithuanian localization. (#12)

Version 0.5.1 -- 2014/03/14
---------------------------

* Added Python 3 support with 2to3. (#3)
* Fixed big numbers in spanish. (#2)
* Fixed bugs in tanslation from 30 to 40 in spanish. (#4)
* Fixed word joining in english. (#8)

Version 0.5.0 -- 2013/05/28
---------------------------

* Created ``num2words`` based on the old ``pynum2word`` project.