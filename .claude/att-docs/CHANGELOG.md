# Changelog

## [0.31.36](https://github.com/merph518/Overmind/compare/v0.31.35...v0.31.36) (2026-11-13)


### Bug Fixes

* **convert-docs:** drop Word hidden text, write letter and roman list labels, keep a leading o ([#681](https://github.com/merph518/Overmind/issues/681)) ([#684](https://github.com/merph518/Overmind/issues/684)) ([339674b](https://github.com/merph518/Overmind/commit/339674bc53ac1c9b167747b5929310c8557cf09f))
* **convert-docs:** keep the list number check from wrapping onto an earlier item ([#677](https://github.com/merph518/Overmind/issues/677)) ([2fb0abb](https://github.com/merph518/Overmind/commit/2fb0abb338b662c16af5227bd18ab690f3597f9d))

## [0.31.35](https://github.com/merph518/Overmind/compare/v0.31.34...v0.31.35) (2026-11-13)


### Bug Fixes

* **convert-docs:** draw Word list numbers and nesting through Pandoc ([#675](https://github.com/merph518/Overmind/issues/675)) ([0dad792](https://github.com/merph518/Overmind/commit/0dad792b5792684652b2dec9a1f394c4c1b83e0a))
* gate every local model run in build-test-pack on the user's yes ([#665](https://github.com/merph518/Overmind/issues/665)) ([#666](https://github.com/merph518/Overmind/issues/666)) ([5dd5621](https://github.com/merph518/Overmind/commit/5dd56214409409b4ca27e294e8b13bf42513412c))
* give each revalidation finding a repair call of its own, sized by cards ([#656](https://github.com/merph518/Overmind/issues/656)) ([#657](https://github.com/merph518/Overmind/issues/657)) ([0fb4b06](https://github.com/merph518/Overmind/commit/0fb4b06299cc916399e6b141b0eb31a5f22bf393))
* hold the overall confidence to the builder's confidence ceiling ([#650](https://github.com/merph518/Overmind/issues/650)) ([#652](https://github.com/merph518/Overmind/issues/652)) ([dd97b0c](https://github.com/merph518/Overmind/commit/dd97b0ceeab1c23f206229dcfff5d69ea14134f0))
* name both hosts in the report's advice for a repeatedly cut step ([#653](https://github.com/merph518/Overmind/issues/653)) ([#663](https://github.com/merph518/Overmind/issues/663)) ([7e7970e](https://github.com/merph518/Overmind/commit/7e7970e281a0f88f826fe6fb54c61660fc1c6501))
* recommend a server thinking budget and warn in the setup check when it is missing ([#651](https://github.com/merph518/Overmind/issues/651)) ([#654](https://github.com/merph518/Overmind/issues/654)) ([9ac186b](https://github.com/merph518/Overmind/commit/9ac186b111429ce63dd374d24263b0514ef18232))
* state the design rules to the checklist reads ([#661](https://github.com/merph518/Overmind/issues/661)) ([#664](https://github.com/merph518/Overmind/issues/664)) ([f97b76b](https://github.com/merph518/Overmind/commit/f97b76b0b6edc13e407f6a271d10a4d0391397c5))
* state the design rules to the revalidation walk and put repaired cards back through the sets ([#659](https://github.com/merph518/Overmind/issues/659)) ([#660](https://github.com/merph518/Overmind/issues/660)) ([abeb642](https://github.com/merph518/Overmind/commit/abeb6427b11b10e18c85f4611af5690e3ac93100))

## [0.31.34](https://github.com/merph518/Overmind/compare/v0.31.33...v0.31.34) (2026-11-09)


### Bug Fixes

* keep the partial clone mark when a signal lands during the restore ([#645](https://github.com/merph518/Overmind/issues/645)) ([#648](https://github.com/merph518/Overmind/issues/648)) ([e3829f3](https://github.com/merph518/Overmind/commit/e3829f3040027658f596ce05b6187ff9ec3cc808))

## [0.31.33](https://github.com/merph518/Overmind/compare/v0.31.32...v0.31.33) (2026-11-09)


### Bug Fixes

* ask build-test-pack reply fields in the order they are worked out ([#545](https://github.com/merph518/Overmind/issues/545)) ([#640](https://github.com/merph518/Overmind/issues/640)) ([0a85974](https://github.com/merph518/Overmind/commit/0a85974fb5d466cfca40ba40335adef30ef52458))
* carry each card's scenario kind on pack.testCards ([#563](https://github.com/merph518/Overmind/issues/563)) ([#644](https://github.com/merph518/Overmind/issues/644)) ([10bcf62](https://github.com/merph518/Overmind/commit/10bcf6241c4574fbdb0f72b26a073d3960ed8dfa))
* end the build-test-pack break-only pass when its reply is cut off ([#557](https://github.com/merph518/Overmind/issues/557)) ([#641](https://github.com/merph518/Overmind/issues/641)) ([7608e33](https://github.com/merph518/Overmind/commit/7608e33c6f086bffb23374ff615ce7241bdbad71))
* stop build-test-pack model calls reusing a closed connection, bound the inventory reply, and order step rows ([#639](https://github.com/merph518/Overmind/issues/639), [#642](https://github.com/merph518/Overmind/issues/642), [#643](https://github.com/merph518/Overmind/issues/643)) ([#647](https://github.com/merph518/Overmind/issues/647)) ([0484125](https://github.com/merph518/Overmind/commit/04841253235ddd64af38b5142cbbb3841f55d63a))
* stop queue add promising a restore that sudoers will refuse ([#539](https://github.com/merph518/Overmind/issues/539)) ([#637](https://github.com/merph518/Overmind/issues/637)) ([dff268c](https://github.com/merph518/Overmind/commit/dff268ca94442b85119778742783fb850e34071f))

## [0.31.32](https://github.com/merph518/Overmind/compare/v0.31.31...v0.31.32) (2026-11-09)


### Features

* log check verdicts, repairs, progress and call usage to status.log ([#635](https://github.com/merph518/Overmind/issues/635)) ([39ed3e3](https://github.com/merph518/Overmind/commit/39ed3e3e23ca2e3fe21b9c2ad1c1d7221fee3457))

## [0.31.31](https://github.com/merph518/Overmind/compare/v0.31.30...v0.31.31) (2026-11-09)


### Features

* split the revalidation walk and the senior review into one call per group or part ([#488](https://github.com/merph518/Overmind/issues/488)) ([#632](https://github.com/merph518/Overmind/issues/632)) ([3631a30](https://github.com/merph518/Overmind/commit/3631a30ecf27129f6becf0fe555a0472b514a49e))


### Bug Fixes

* fail acronym verify when a cited source file is missing ([#631](https://github.com/merph518/Overmind/issues/631)) ([de8bb3b](https://github.com/merph518/Overmind/commit/de8bb3b468be0e2e7287ed39b4383622735161b3))

## [0.31.30](https://github.com/merph518/Overmind/compare/v0.31.29...v0.31.30) (2026-11-09)


### Features

* Warn when the Baton tool snapshot is behind Code Conductor ([#529](https://github.com/merph518/Overmind/issues/529)) ([#628](https://github.com/merph518/Overmind/issues/628)) ([1b8706d](https://github.com/merph518/Overmind/commit/1b8706da0a4f171341c3b98273edb6bfc59a097f))

## [0.31.29](https://github.com/merph518/Overmind/compare/v0.31.28...v0.31.29) (2026-11-08)


### Features

* **general:** add the azdo-sync skill ([#590](https://github.com/merph518/Overmind/issues/590)) ([#625](https://github.com/merph518/Overmind/issues/625)) ([e378bc0](https://github.com/merph518/Overmind/commit/e378bc08d48855471ea8f0f32b7528333a01ab0d))

## [0.31.28](https://github.com/merph518/Overmind/compare/v0.31.27...v0.31.28) (2026-11-08)


### Features

* **general:** add the azdo-stories skill ([#589](https://github.com/merph518/Overmind/issues/589)) ([#624](https://github.com/merph518/Overmind/issues/624)) ([045591d](https://github.com/merph518/Overmind/commit/045591dee65968d33124fd9c9eb95fe2188981bc))

## [0.31.27](https://github.com/merph518/Overmind/compare/v0.31.26...v0.31.27) (2026-11-08)


### Features

* **general:** add the azdo-build-issue skill ([#586](https://github.com/merph518/Overmind/issues/586)) ([#617](https://github.com/merph518/Overmind/issues/617)) ([6c11dd2](https://github.com/merph518/Overmind/commit/6c11dd2ec1775fefccbf57c2cb1233577914fd9f))
* **general:** add the azdo-digest skill ([#587](https://github.com/merph518/Overmind/issues/587)) ([#621](https://github.com/merph518/Overmind/issues/621)) ([c205fe4](https://github.com/merph518/Overmind/commit/c205fe4dac72cc4c5e2a697de7d2b045a5f32a36))
* **general:** add the azdo-review skill ([#588](https://github.com/merph518/Overmind/issues/588)) ([#623](https://github.com/merph518/Overmind/issues/623)) ([528de8c](https://github.com/merph518/Overmind/commit/528de8c23fea7fd72f19833dc29c8b64f7432dc2))
* **general:** add the wyatt-review-phase-1 skill ([#593](https://github.com/merph518/Overmind/issues/593)) ([#619](https://github.com/merph518/Overmind/issues/619)) ([2599c0a](https://github.com/merph518/Overmind/commit/2599c0a0bb62b6fa436f64134de3d8a073ed0424))
* **general:** add the wyatt-review-phase-2 skill ([#618](https://github.com/merph518/Overmind/issues/618)) ([#622](https://github.com/merph518/Overmind/issues/622)) ([5c1d1dc](https://github.com/merph518/Overmind/commit/5c1d1dc8bd560420fb75cac296617e6fa3af93d5))

## [0.31.26](https://github.com/merph518/Overmind/compare/v0.31.25...v0.31.26) (2026-11-08)


### Features

* **general:** add runs and resume to the oversee ledger ([#611](https://github.com/merph518/Overmind/issues/611)) ([#614](https://github.com/merph518/Overmind/issues/614)) ([9181c12](https://github.com/merph518/Overmind/commit/9181c12bf296d5431d3d8e17da377bf0536a7a77))
* **general:** add the sql-discovery-learning-log skill ([#612](https://github.com/merph518/Overmind/issues/612)) ([e94a6bb](https://github.com/merph518/Overmind/commit/e94a6bba23ce551007771532c245fc76934228c6))
* **general:** add the wyatt-regression-issue skill ([#592](https://github.com/merph518/Overmind/issues/592)) ([#615](https://github.com/merph518/Overmind/issues/615)) ([366e71c](https://github.com/merph518/Overmind/commit/366e71cbe548e9d7181278f34d2075fcb6a53757))

## [0.31.25](https://github.com/merph518/Overmind/compare/v0.31.24...v0.31.25) (2026-11-08)


### Features

* **general:** add the new-branch skill ([#591](https://github.com/merph518/Overmind/issues/591)) ([#610](https://github.com/merph518/Overmind/issues/610)) ([f89c484](https://github.com/merph518/Overmind/commit/f89c4842c8a992f6b725678c98543be4e570dcfa))
* **general:** add the sql-lookup skill ([#584](https://github.com/merph518/Overmind/issues/584)) ([#608](https://github.com/merph518/Overmind/issues/608)) ([b3b0427](https://github.com/merph518/Overmind/commit/b3b0427743e9dc366ef1c6d44c85e22d697debe9))

## [0.31.24](https://github.com/merph518/Overmind/compare/v0.31.23...v0.31.24) (2026-11-08)


### Features

* **general:** add the sweep-suite skill ([#583](https://github.com/merph518/Overmind/issues/583)) ([#606](https://github.com/merph518/Overmind/issues/606)) ([cd942eb](https://github.com/merph518/Overmind/commit/cd942eb99852de531a5a056cd0ac34b0e404a80e))

## [0.31.23](https://github.com/merph518/Overmind/compare/v0.31.22...v0.31.23) (2026-11-08)


### Bug Fixes

* show needs you only for a question to the user, add waiting on a partner ([#601](https://github.com/merph518/Overmind/issues/601)) ([#604](https://github.com/merph518/Overmind/issues/604)) ([6381647](https://github.com/merph518/Overmind/commit/638164728612e74c38733868debfbdc57986aa08))

## [0.31.22](https://github.com/merph518/Overmind/compare/v0.31.21...v0.31.22) (2026-11-08)


### Features

* **att-docs:** add the skip-ledger skill ([#600](https://github.com/merph518/Overmind/issues/600)) ([e9643b1](https://github.com/merph518/Overmind/commit/e9643b12d5d8416789ae2d8c943aeb8ec0c6a583))
* **general:** add the manual-spec skill ([#581](https://github.com/merph518/Overmind/issues/581)) ([#599](https://github.com/merph518/Overmind/issues/599)) ([932eec4](https://github.com/merph518/Overmind/commit/932eec4526a9b5814dac3286ce88b212adcbdc17))

## [0.31.21](https://github.com/merph518/Overmind/compare/v0.31.20...v0.31.21) (2026-11-08)


### Features

* **general:** add the debug-spec skill ([#580](https://github.com/merph518/Overmind/issues/580)) ([#597](https://github.com/merph518/Overmind/issues/597)) ([db02183](https://github.com/merph518/Overmind/commit/db021837d94bc98051c48c885c2953ff8dba28bd))

## [0.31.20](https://github.com/merph518/Overmind/compare/v0.31.19...v0.31.20) (2026-11-08)


### Features

* **att-docs:** add the manual-validation-walkthrough skill ([#596](https://github.com/merph518/Overmind/issues/596)) ([f0c941e](https://github.com/merph518/Overmind/commit/f0c941eaf24f90be86f4e9705bfdb87268087ca9))


### Bug Fixes

* cut a long list of document numbers so a gate stop still writes its fail line ([#413](https://github.com/merph518/Overmind/issues/413)) ([#577](https://github.com/merph518/Overmind/issues/577)) ([77a8d79](https://github.com/merph518/Overmind/commit/77a8d795b2198c3abdbbd3421f3a8310eee84dce))
* let the revalidation repair build the new cards a finding names ([#487](https://github.com/merph518/Overmind/issues/487)) ([#574](https://github.com/merph518/Overmind/issues/574)) ([3b09445](https://github.com/merph518/Overmind/commit/3b094450c4d158095f6a2db5bd00c7b0d2b36c92))

## [0.31.19](https://github.com/merph518/Overmind/compare/v0.31.18...v0.31.19) (2026-11-06)


### Features

* **att-docs:** add the sir-housekeeping skill ([#569](https://github.com/merph518/Overmind/issues/569)) ([6775ead](https://github.com/merph518/Overmind/commit/6775ead1a0c8d3cd1a21f2914533fb9d09d7ad73))

## [0.31.18](https://github.com/merph518/Overmind/compare/v0.31.17...v0.31.18) (2026-11-05)


### Bug Fixes

* offer flagged break cards to the core objective pass when the pack has no BREAK IT set ([#567](https://github.com/merph518/Overmind/issues/567)) ([b5badc4](https://github.com/merph518/Overmind/commit/b5badc42b8c46dc55ba0276a9edf0c5871cdb7df)), closes [#565](https://github.com/merph518/Overmind/issues/565)

## [0.31.17](https://github.com/merph518/Overmind/compare/v0.31.16...v0.31.17) (2026-11-05)


### Bug Fixes

* keep BREAK IT and plain cards apart in the design tidy ([#560](https://github.com/merph518/Overmind/issues/560)) ([#564](https://github.com/merph518/Overmind/issues/564)) ([7dfce07](https://github.com/merph518/Overmind/commit/7dfce0706d7c25e845b97825758248ef4c91b78d))

## [0.31.16](https://github.com/merph518/Overmind/compare/v0.31.15...v0.31.16) (2026-11-05)


### Features

* Let the build supervisor answer a job's questions while it waits ([#542](https://github.com/merph518/Overmind/issues/542)) ([#549](https://github.com/merph518/Overmind/issues/549)) ([82bcb06](https://github.com/merph518/Overmind/commit/82bcb06fba1b97538229d44e22c5f25b5efcb334))
* Send build calls at temperature 0 with a fixed seed and record the seed ([#541](https://github.com/merph518/Overmind/issues/541)) ([#547](https://github.com/merph518/Overmind/issues/547)) ([249b2a5](https://github.com/merph518/Overmind/commit/249b2a505901c89a43d1b1c48de94f5d28220f94))


### Bug Fixes

* Run phase 1 understanding with thinking off and flag repeated budget cuts ([#540](https://github.com/merph518/Overmind/issues/540)) ([#543](https://github.com/merph518/Overmind/issues/543)) ([52c9e86](https://github.com/merph518/Overmind/commit/52c9e868d4cf8276a9c85524782cf851598d9719))
* Settle phase 3 review questions from the change description before stopping ([#538](https://github.com/merph518/Overmind/issues/538)) ([#546](https://github.com/merph518/Overmind/issues/546)) ([6edeb18](https://github.com/merph518/Overmind/commit/6edeb18dd96a56a9f1fe1ac35856e65d2ee54d76))
* State that scenario kind stays inside Phase 6 ([#559](https://github.com/merph518/Overmind/issues/559)) ([fc6dba6](https://github.com/merph518/Overmind/commit/fc6dba6be7891bed6f919298d5a728f42e80f586))
* Stream model calls so a cancel stops generation and the unload passes ([#552](https://github.com/merph518/Overmind/issues/552)) ([#556](https://github.com/merph518/Overmind/issues/556)) ([42e67dd](https://github.com/merph518/Overmind/commit/42e67ddbbb5756f6d0502423ecfbdc861391cfca))
* Write one Phase 6 assumption per document for empty scenario kinds ([#551](https://github.com/merph518/Overmind/issues/551)) ([#558](https://github.com/merph518/Overmind/issues/558)) ([db1ed9b](https://github.com/merph518/Overmind/commit/db1ed9b02a0b309469a1fbdb2123c656b250d07e))
* Write the Draft workbook at Phase 8 and drop the Phase 9 summary fallback ([#553](https://github.com/merph518/Overmind/issues/553)) ([#555](https://github.com/merph518/Overmind/issues/555)) ([e412768](https://github.com/merph518/Overmind/commit/e412768712b99bc3c917ed92566ad89bc0aee1a8))

## [0.31.15](https://github.com/merph518/Overmind/compare/v0.31.14...v0.31.15) (2026-11-04)


### Features

* claim shared files so concurrent sessions in one repo do not collide ([#257](https://github.com/merph518/Overmind/issues/257)) ([#528](https://github.com/merph518/Overmind/issues/528)) ([44b8456](https://github.com/merph518/Overmind/commit/44b84562ee31e604c2b37be86035e26c65662f79))
* replay recorded model calls with --model replay: ([#492](https://github.com/merph518/Overmind/issues/492)) ([#536](https://github.com/merph518/Overmind/issues/536)) ([3439d38](https://github.com/merph518/Overmind/commit/3439d38d35be0ae579dbce8069c389f05b16da3f))

## [0.31.14](https://github.com/merph518/Overmind/compare/v0.31.13...v0.31.14) (2026-11-04)


### Features

* Check that skills name only Baton tools and arguments that exist ([#134](https://github.com/merph518/Overmind/issues/134)) ([#531](https://github.com/merph518/Overmind/issues/531)) ([c9edb20](https://github.com/merph518/Overmind/commit/c9edb2035953391bf53f0645c63109a54d08af99))

## [0.31.13](https://github.com/merph518/Overmind/compare/v0.31.12...v0.31.13) (2026-11-04)


### Bug Fixes

* cover a partial-clone Overmind checkout in the pin tests ([#508](https://github.com/merph518/Overmind/issues/508)) ([#526](https://github.com/merph518/Overmind/issues/526)) ([6c91a8b](https://github.com/merph518/Overmind/commit/6c91a8babf046b18fe7162247e4ca81cb2bfb1af))

## [0.31.12](https://github.com/merph518/Overmind/compare/v0.31.11...v0.31.12) (2026-11-04)


### Features

* run one Phase 9 step or one builder pass on its own ([#491](https://github.com/merph518/Overmind/issues/491)) ([#525](https://github.com/merph518/Overmind/issues/525)) ([44e9754](https://github.com/merph518/Overmind/commit/44e975462796d1f0c9fae53d125bf41d5bc705d0))


### Bug Fixes

* remove the scratch folders test files leave in the temp folder ([#523](https://github.com/merph518/Overmind/issues/523)) ([c84c49b](https://github.com/merph518/Overmind/commit/c84c49b74cd257fccaff470a36c3cc2aa15a9ced))

## [0.31.11](https://github.com/merph518/Overmind/compare/v0.31.10...v0.31.11) (2026-11-04)


### Bug Fixes

* fetch the objects a partial clone left in the pin workflow checkout ([#521](https://github.com/merph518/Overmind/issues/521)) ([297011f](https://github.com/merph518/Overmind/commit/297011f182c75ff70ba75a4915513cafb4fd19bb))

## [0.31.10](https://github.com/merph518/Overmind/compare/v0.31.9...v0.31.10) (2026-11-04)


### Bug Fixes

* guard the main checkout in sessions that load .omp extensions ([#517](https://github.com/merph518/Overmind/issues/517)) ([#518](https://github.com/merph518/Overmind/issues/518)) ([5e7ce09](https://github.com/merph518/Overmind/commit/5e7ce093b4c13de0343f1dc334901149854a355e))
* keep the guard extension's shipped comments harness neutral ([#520](https://github.com/merph518/Overmind/issues/520)) ([2f6556e](https://github.com/merph518/Overmind/commit/2f6556e0e7d8bf090c9d675fa9601183da62f646))

## [0.31.9](https://github.com/merph518/Overmind/compare/v0.31.8...v0.31.9) (2026-11-04)


### Features

* persist implement backlog loops ([#256](https://github.com/merph518/Overmind/issues/256)) ([#515](https://github.com/merph518/Overmind/issues/515)) ([9113602](https://github.com/merph518/Overmind/commit/9113602b15fd8048c089198e3f4637a8b161aa8a))

## [0.31.8](https://github.com/merph518/Overmind/compare/v0.31.7...v0.31.8) (2026-11-04)


### Features

* doc-watch waits 30 seconds for a manual sign-in on an attended run ([#182](https://github.com/merph518/Overmind/issues/182)) ([#512](https://github.com/merph518/Overmind/issues/512)) ([93ac88b](https://github.com/merph518/Overmind/commit/93ac88bdc4d39f0c57757df56f462743970cff78))

## [0.31.7](https://github.com/merph518/Overmind/compare/v0.31.6...v0.31.7) (2026-11-04)


### Bug Fixes

* Remove the build-pack test scratch folders after each run ([#506](https://github.com/merph518/Overmind/issues/506)) ([deced9a](https://github.com/merph518/Overmind/commit/deced9ac12e7212d8c1073fbe04d971f1a2bcf70))

## [0.31.6](https://github.com/merph518/Overmind/compare/v0.31.5...v0.31.6) (2026-11-04)


### Features

* open consumer pin pull requests after releases ([#194](https://github.com/merph518/Overmind/issues/194)) ([#503](https://github.com/merph518/Overmind/issues/503)) ([ca3b7d5](https://github.com/merph518/Overmind/commit/ca3b7d550bc0c04bd737c06ae559b54e6756cc12))
* read long replies in short and a ready reply as one line ([#189](https://github.com/merph518/Overmind/issues/189)) ([#504](https://github.com/merph518/Overmind/issues/504)) ([90ffda7](https://github.com/merph518/Overmind/commit/90ffda78d1c76aca6a12193e00e811f969361961))

## [0.31.5](https://github.com/merph518/Overmind/compare/v0.31.4...v0.31.5) (2026-11-04)


### Features

* record each model call's prompt and reply in work/calls ([#492](https://github.com/merph518/Overmind/issues/492)) ([#496](https://github.com/merph518/Overmind/issues/496)) ([0ac9451](https://github.com/merph518/Overmind/commit/0ac9451e7f5d5f8a88337565f95c89a8cc45e69c))


### Bug Fixes

* document git worktree fallback ([#500](https://github.com/merph518/Overmind/issues/500)) ([603d9fc](https://github.com/merph518/Overmind/commit/603d9fcb04ac0861a6ae0a980cbea51389c2b7f0))

## [0.31.4](https://github.com/merph518/Overmind/compare/v0.31.3...v0.31.4) (2026-11-04)


### Features

* build-test-pack keeps a snapshot per phase and reruns a slice of a job in a sandbox ([#490](https://github.com/merph518/Overmind/issues/490)) ([#497](https://github.com/merph518/Overmind/issues/497)) ([c5758c1](https://github.com/merph518/Overmind/commit/c5758c17cead4ccb8a24ad4a641b39ce7aea0703))
* oversee-development serves the best next issue in a milestone ([#230](https://github.com/merph518/Overmind/issues/230)) ([#494](https://github.com/merph518/Overmind/issues/494)) ([8a8e13f](https://github.com/merph518/Overmind/commit/8a8e13f13f4df11f75d0985dd0ecd6199c5ced59))
* refuse stray files and bulk adds before every commit ([#157](https://github.com/merph518/Overmind/issues/157)) ([#495](https://github.com/merph518/Overmind/issues/495)) ([d9d6ada](https://github.com/merph518/Overmind/commit/d9d6ada042fd52245335f78de5e8a34fd0dfcab4))

## [0.31.3](https://github.com/merph518/Overmind/compare/v0.31.2...v0.31.3) (2026-11-04)


### Features

* apply a volume change to the clip already playing ([#111](https://github.com/merph518/Overmind/issues/111)) ([#481](https://github.com/merph518/Overmind/issues/481)) ([9c641be](https://github.com/merph518/Overmind/commit/9c641bedc6afd78a045a2922cf9fa46ede4b440c))
* list worktrees with their pull request state and remove merged ones ([#144](https://github.com/merph518/Overmind/issues/144)) ([#484](https://github.com/merph518/Overmind/issues/484)) ([7ecd79e](https://github.com/merph518/Overmind/commit/7ecd79ec198eee68a07269ba5eba6ec8dc057f7e))
* report installed plugins that are behind the repository ([#137](https://github.com/merph518/Overmind/issues/137)) ([#482](https://github.com/merph518/Overmind/issues/482)) ([76416b9](https://github.com/merph518/Overmind/commit/76416b9207a60b357ba66955676329f023f75cd3))
* ship the consumer sync and check scripts in every snapshot ([#234](https://github.com/merph518/Overmind/issues/234)) ([#480](https://github.com/merph518/Overmind/issues/480)) ([a5de379](https://github.com/merph518/Overmind/commit/a5de3793a2f6667a32c1031eb37edcaf97df0eed))

## [0.31.2](https://github.com/merph518/Overmind/compare/v0.31.1...v0.31.2) (2026-11-04)


### Features

* **general:** oversee-development serves only ready-for-agent issues and skips open blockers ([#472](https://github.com/merph518/Overmind/issues/472)) ([#473](https://github.com/merph518/Overmind/issues/473)) ([51fb388](https://github.com/merph518/Overmind/commit/51fb38854026798b77d68cb04113dec75b29a708))

## [0.31.1](https://github.com/merph518/Overmind/compare/v0.31.0...v0.31.1) (2026-11-03)


### Features

* **general:** let oversee-development hand issues to subagents ([#464](https://github.com/merph518/Overmind/issues/464)) ([def2371](https://github.com/merph518/Overmind/commit/def23715f4353b630e8977a7cda1c9a0656b3b17))


### Bug Fixes

* **general:** oversee-development skips issues waiting on triage or a human ([#467](https://github.com/merph518/Overmind/issues/467)) ([68c6f82](https://github.com/merph518/Overmind/commit/68c6f827a192a3271d79b4e24e334f52b73b4e0d))
