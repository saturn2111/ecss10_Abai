# ECSS-10 ДП Абай — PROJECT_STATE

Обновлено: 2026-09-18  
Источник истины для продолжения проекта. Не возвращаться к уже подтверждённым этапам без новых фактических данных.

## 1. Архитектура
- ECSS-10 3.18.0.271 на двух Ubuntu 22.04 VM: `ecss1` 192.168.190.70 и `ecss2` 192.168.190.80.
- Два независимых Proxmox-хоста; USB Rutoken/eToken лицензирование учтено.
- Distributed licensing подтверждён; оба licence-manager host Alive.
- VRRP/кластерная связность и Mnesia для нужных ECSS компонентов подтверждены.
- Тестовый `2000` подтверждён и сохранён.

## 2. Базовый кластер — подтверждено
Лицензия, VRRP, Mnesia и базовая межузловая связность уже проверены. Эти этапы не повторять без нового инцидента или новых фактических данных.

## 3. Абоненты и тестовый маршрут — подтверждено
Абоненты 1001/1002 и тестовый 2000 используются как уже подтверждённая база. Повторная базовая настройка не нужна.

## 4. Call-center foundation — подтверждено
Queue `Abai_112`, group `Abai_112_cc`, agents 1001/1002 и agent-state foundation подтверждены. Live production изменения без конкретной необходимости не выполнять.

## 5. ecss-cc-ui / внутренний CC API — подтверждено
`ecss-cc-ui` 18.0.34 и связанные API/UI сервисы на обоих узлах подтверждены. Наблюдавшиеся agent/list/history/realtime операции зафиксированы; запрещённые/неподходящие операции не повторять.

## 6. Call API :8089 — выполнено
ECSS Call API integration registration ранее подтверждён. Использование integration token/API key остаётся secret-bearing boundary: реальные ключи/JWT в репозиторий и обычные логи не коммитить.

## 7. Контракт внешней интеграции
Минимальная цель — два события одного состоявшегося звонка: `answered` и `finished` с общим Id, Direction, NumberA, NumberB, Duration для finished и CallRecordUrl при фактическом наличии.

## 8. Conversation correlation — подтверждённые факты
Live `conversations_event` показал:
- у прямого 1001→1002 leg разные `id`, общий `call_id`, общий `call_ref`;
- у queue-вызова caller/IVR и operator leg имеют общий logical `call_id`, но разные `call_ref`;
- `has_answer_time` различает observed answered и released-without-answer legs;
- один `call_ref` нельзя считать универсальным id всей queue-цепочки.

## 9. Боевая 112 — очередь/агенты/IVR/маршрут
Подтверждённая цепочка:
`112 -> default_routing/abai_112 -> Abai_112_ivr -> queue Abai_112 -> group Abai_112_cc -> Agent1001/Agent1002`.
Live queue test до Operator2 подтверждал реальный проход через маршрут. Не возвращаться к перенастройке этого маршрута без нового требования/инцидента.

## 10. Offline CDR tooling — verified baseline
Offline tooling рассматривает CDR только как evidence. `CONN_ID`, `T_ECD`, `T_DBA` обрабатываются fail-closed; numeric parsing сохраняет exact integer semantics через `Decimal` и отклоняет отрицательные, fractional/non-finite/malformed значения.

Verified main содержит required-header/duplicate-column guards, exact-ref correlation, evidence-only text/JSON/CLI, multi-artifact bundle, TSV report, summary/diff, standalone HTML report, r51 интерактивный локальный поиск/filter/reset, r52 export текущего visible subset в spreadsheet-safe CSV плюс print-to-PDF, r53 live summary, r54 session-only operator bookmarks, r55 local `Export visible JSON` и r56 local `Export visible Markdown`.

r55 exact SHA `7e179cf42a5830a0fa3e9a9c05547e9eecadc7b7` прошёл Forgejo run 677 и auto-merged. r56 exact SHA `b00aadfa8059a69a1374c4bfd07cefa72d689ef6` прошёл Forgejo run 700 и auto-merged в canonical main `ce04bd3d676c872642091cb4dbd695eeed09a72e`.

Документационный r56 state-sync также уже прошёл gate и auto-merged в canonical main `29aa9affd04471fe934cfcfb9a4d7b83d6b11116`; его больше не считать pending-действием.

## 11. CDR semantics — пока НЕ доказано
Пока нет свежего live queue CDR, не считать доказанными:
- финальное сопоставление logical `call_id` ↔ CDR rows;
- queue membership по одному CDR полю;
- семантику `T_DBA` как queue wait;
- какой CDR `T_ECD` должен стать внешним `Duration` для queue call;
- запись разговора/URL без фактического evidence.

## 12. Verified operator handoff baseline
- Offline operator workflow теперь имеет portable handoff в HTML/TSV/CSV/JSON/Markdown/print-to-PDF.
- `Export visible Markdown` выгружает только строки, фактически видимые после Search/classification/Bookmarked-only фильтров, вместе с filter context и bookmark state.
- Markdown и остальные offline views сохраняют raw evidence labels; `T_ECD/T_DBA` не переименовываются в queue wait/final Duration.
- Browser exports остаются local-only через Blob/object URL; нет `fetch`, `localStorage`, ECSS/server write или production access.
- После r56 GREEN не добавлять мелкие guard/presentation слои только ради активности: следующий offline шаг должен давать заметную correlation/operator пользу либо ждать новых фактических данных.

## 13. Live data boundary
Для следующего фактического semantic mapping нужен sanitized CDR именно подтверждённого queue call вместе с известными caller/operator refs. До его появления semantic mapping считается внешне заблокированным, а production ECSS не трогается.

## 14. Текущая точка / СЛЕДУЮЩИЕ ДЕЙСТВИЯ
1. По основному ECSS/CDR треку не плодить следующий микрогард: r56 и его state-sync уже verified/merged.
2. Активный отдельный инцидент — AuP/Auto Provision licensing на `aup1`.
3. `ecss-license-master` пока не доводить до лицензии: сначала устранить бинарную несовместимость `GLIBC_2.34 not found`, выяснив фактическую ОС/glibc и origin установленного пакета `1.0.31`.
4. После совместимого запуска мастера отдельно решить отсутствие реального `.lic` и заменить literal `LICENSE_PATH=<license_path>/test.lic` на фактический абсолютный путь.
5. Не обновлять/подменять системную glibc вручную ради одного пакета.
6. Live production changes SSW/маршрута 112 делать только при отдельной необходимости.

## 15. Что не делать
- Не повторять licence/VRRP/Mnesia/test2000/agents/route112 setup для SSW без нового SSW-инцидента.
- Не использовать heuristic guesses как production mapping.
- Не менять боевой маршрут 112 без отдельной необходимости.
- Не считать offline unit tests доказательством поведения production ECSS.
- Не считать Docker/repository credentials или сам USB/Rutoken заменой файла лицензии AuP без фактического подтверждения установленной схемы лицензирования.
- Не пытаться лечить `GLIBC_2.34 not found` ручной заменой `libc.so.6` или принудительным обновлением glibc из чужого дистрибутива.

## 16. Evidence policy
Каждое новое утверждение о live ECSS/CDR должно опираться на фактический capture/output. Offline helpers, reports, CLI и bundles должны fail-close при ambiguous/multiple/incomplete evidence.

## 17. Security
- Не коммитить реальные passwords, API keys, JWT, cookies, Rutoken PIN или другие credentials.
- Не коммитить subscriber-sensitive raw production CDR; использовать sanitized fixtures.
- Не расширять live production access только ради автономного инкремента.
- Local gate/CI нельзя обходить force-merge в `main`.

## 18. AuP licensing incident — 2026-09-18
- Речь идёт об AuP/Auto Provision и `ecss-license-master`, а не о `ecss-license-provider` SSW.
- Фактический пакет: `ecss-license-master 1.0.31`.
- `ecss-license-master.service` установлен и enabled, но находится в restart loop; в журнале повторяется: `erlexec: /lib/x86_64-linux-gnu/libc.so.6: version 'GLIBC_2.34' not found`.
- Следствие: мастер падает до обработки лицензии; текущая первичная блокировка — несовместимость бинарника пакета с glibc хоста.
- USB passthrough подтверждён: `lsusb` видит `0a89:0030 Aktiv Rutoken ECP`.
- PC/SC socket активен; `pcscd.service` socket-activated и завершался success, поэтому отсутствие постоянно active daemon само по себе не считать проблемой.
- В drop-in `/etc/systemd/system/ecss-license-master.service.d/override.conf` пока буквально задано `Environment=LICENSE_PATH=<license_path>/test.lic`.
- `find / -type f -iname '*.lic'` не нашёл ни одного файла лицензии на `aup1`.
- Это вторая независимая блокировка, которая проявится после починки запуска мастера: нужен фактический `.lic` и реальный абсолютный `LICENSE_PATH`.
- Следующий сбор evidence: `cat /etc/os-release`, `ldd --version`/`getconf GNU_LIBC_VERSION`, Eltex AuP apt source, `apt-cache policy/madison ecss-license-master`; по результату выбрать корректный пакет/репозиторий под ОС, а не менять glibc вручную.

## 19. ECSS SIP trunk show Unicode-format error — 2026-10-30
- User supplied output from `[/commands/sip_trunk_show]`: `<error cmd="sip_trunk_show" reason="invalid_xml" ... entity="dp_abai"/>`.
- Inner error: `{badarg,{ion_common,format,["~s",[[1062,1077,1085,1090,1088,32,1054,1087,1077,1088,1072,1090,1080,1074,1085,1086,1075,1086,32,1059,1087,1088,1072,1074,1083,1077,1085,1080,1103]]]}}`; code points decode to `Центр Оперативного Управления`.
- Strong indication of a Unicode/character-list formatting failure in the `sip_trunk_show` path, likely triggered by a Cyrillic name/label; this is an inference from the exception, not yet confirmed root cause.
- Do not change SIP authentication, server addresses, dialplan, or live routing to troubleshoot a display/formatting error.
- Next safe step: identify where the exact Cyrillic string is configured and whether it is a SIP trunk display/name field. If operationally safe and approved, test renaming only that label to ASCII (e.g. `COU`) and rerun `sip_trunk_show`; otherwise preserve current config and collect the exact command/input XML plus relevant trunk metadata for Eltex support.
- Web search for this exact exception/command did not return a relevant official reference; avoid asserting a documented vendor bug until reproduced or confirmed by Eltex.

## 20. Follow-up evidence for SIP trunk Unicode error — 2026-10-30
- New screenshot shows the text truncated as `Центр Оперативного У...` repeated in the far-right column of the ECSS-10 subscriber list for many subscribers.
- The column header is not visible in the screenshot, so the field is not yet identified. A prior subscriber card showed `группа доступа = all`; therefore do not assume the list's far-right column is the access group.
- This screenshot does not prove the Cyrillic text is the SIP trunk name. Earlier hypothesis to rename a trunk label is premature.
- Do not rename trunks, alter subscriber groups, or change SIP routing/authentication until the exact field is identified.
- Next safe step: expose/read the far-right column header or open a subscriber's edit card and identify the corresponding field; then compare with the exact XML/request and `sip_trunk_show` failure. Treat Unicode formatting failure as a hypothesis, not a confirmed vendor bug.

## 21. User confirmed text is not present inside subscriber card — 2026-10-30
- User reports the value `Центр Оперативного Управления` is not shown as a field inside the subscriber card.
- Therefore do not instruct the user to edit this value from the card's `Основные` tab.
- The visible list column and its header/meaning remain unidentified; do not assume it is `группа доступа` (the card showed `all`) or the SIP trunk name.
- Next safe UI inspection: select one subscriber and open the top-level `Параметры` dropdown in the subscriber list, inspect available operations; alternatively reveal the table column header. Do not commit any changes until the field/operation is identified.

## 22. Access-group bulk edit via UI not available — 2026-10-30
- User confirms the subscriber list's `Параметры` dropdown does not expose the needed bulk group-access edit action, and the displayed `Центр Оперативного Управления` text is not a field in the subscriber card.
- Official ECSS-10 documentation describes alias access group as property `access_group`, available in CoCon CLI via `domain/<DOMAIN>/alias/set`; it also documents `domain/<DOMAIN>/alias/info <address>` for inspection and `domain/<DOMAIN>/access-group/ls-groups` to list groups.
- For this installation, domain visible in UI is `dp_abai`, but do not assume the truncated Cyrillic table column is the `access_group` value.
- Next safe step is read-only inspection in CoCon console: `domain/dp_abai/access-group/ls-groups` and `domain/dp_abai/alias/info 1001`. Review output and verify the intended target group before issuing any `alias/set` write.
- Do not use broad wildcard writes or change trunk/route settings. If the exact per-alias CLI argument scope is uncertain, inspect one alias first and apply only to a confirmed address range.

## 23. CoCon search for Cyrillic affecting sip_trunk_show — 2026-10-30
- User asks for CoCon commands to locate and remove Cyrillic causing HTTP-terminal `sip_trunk_show` error.
- Official Eltex CLI docs (ECSS-10 3.14.x reference; current deployment is 3.18, so verify syntax in local help) confirm read-only commands:
  - `domain/dp_abai/trunk/list` lists trunk names, owner, group, type.
  - `domain/dp_abai/trunk/sip/info * *` shows all SIP trunk interface parameters across groups.
  - `domain/dp_abai/iface/list * *` can inspect interface inventory; `domain/dp_abai/iface/info * <GROUP> <NAME>` may be used for a specific interface if needed.
  - `domain/dp_abai/alias/extended-info 1001 1001@dp_abai` can inspect subscriber alias/interface metadata; `domain/dp_abai/alias/info <range>` can inspect properties.
- CoCon docs do not document a single global command that searches all configuration values for Cyrillic. Inspect read-only outputs first; from a local shell, output can be piped to Unicode-aware grep if needed.
- Do not issue any `set`, `clean`, `remove`, `alias/set`, or mass edits until the exact property (trunk group, interface name, or parameter value) is identified. The Cyrillic string in subscriber list screenshot has no visible column header and cannot yet be mapped to a property.
- Likely safe process: list trunks; dump SIP trunk info; identify exact Cyrillic field; then set only that field to an ASCII label/value using documented `domain/<DOMAIN>/trunk/sip/set <GROUP> <TRUNK_INTERFACE> <PARAMETER> <VALUE>` if it is a settable property, with before/after verification. If the value is an interface/group identifier used in routing, do not rename blindly.

## 24. Exact Cyrillic source identified in live CoCon output — 2026-10-30
- User ran read-only commands in CoCon on ECSS-10 3.18.0.271:
  - `domain/dp_abai/trunk/list`
  - `domain/dp_abai/trunk/sip/info * *`
- Confirmed exactly one trunk in `dp_abai`: trunk/interface `kt`, owner `sip1`, group `Центр Оперативного Управления`, active=true, type=sip, destination `10.97.100.1:5060`, listen `"sip_main"/"192.168.191.4":5060`, need-registration=false, blocked=false, accessible=true.
- The Cyrillic is in the SIP trunk interface-group field, not a subscriber-card field. It is the leading candidate for the earlier `sip_trunk_show invalid_xml` error; causal link is plausible but not yet verified by rerunning command after correction.
- Official Eltex ECSS-10 docs describe SIP parameter `group` as the group to which the SIP interface belongs and support `trunk/sip/set <GROUP> <TRUNK_INTERFACE> <PARAMETER> <VALUE>`. However, moving the trunk to an ASCII-named group can affect group references/operations; do not execute write yet until read-only `domain/dp_abai/trunk/sip/info "Центр Оперативного Управления" kt` identifies routing.context and that context is inspected with `domain/dp_abai/routing/show <CONTEXT>`.
- Potential planned target group: `COU` (ASCII). Proposed write only after dependency review: `domain/dp_abai/trunk/sip/set "Центр Оперативного Управления" kt group COU`; verify syntax in local CoCon help/version and do not use `remove`/redeclare as a first step.
- Do not alter destination IP/port, listen interface, auth, or route behavior. After an approved group change, verify `trunk/list`, `trunk/sip/info * *`, `sip_trunk_show`, and test inbound/outbound call behavior.
