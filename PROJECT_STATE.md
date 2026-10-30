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
2. Активный отдельный ECSS-10 incident — AuP/Auto Provision licensing на `aup1`: выяснить фактическую ОС/glibc и origin пакета `ecss-license-master 1.0.31`, устранить `GLIBC_2.34 not found` совместимым пакетом/репозиторием; системную glibc вручную не менять. После запуска отдельно найти реальный `.lic` и задать абсолютный `LICENSE_PATH`.
3. Активный отдельный live-инцидент ECSS-10 3.18.0.271 / домен `dp_abai`: HTTP-terminal `sip_trunk_show` возвращает `invalid_xml` с `ion_common:format(["~s", [Unicode codepoints]])` на строке `Центр Оперативного Управления`. У SIP-транка `kt` эта строка находится в группе и сгенерированном trunk name; destination `10.97.100.1:5060`, listen `sip_main:5060`, access_group `all`, trunk active/unblocked.
4. Маршрутизация полностью инвентаризирована на уровне routing contexts: `domain/dp_abai/routing/list` вернул только `default_routing`; его правила `test` (2000 -> IVR), `abai_112` (112 -> IVR), `local_calls` (local) просмотрены и явных ссылок на Cyrillic trunk group не содержат. Не менять эти правила.
5. Попытка `domain/dp_abai/trunk/sip/set "Центр Оперативного Управления" kt group COU` 30.10.2026 вернула `Error: Wrong identifier`; live re-check подтвердил, что группа не изменилась. Активных вызовов было 0 на момент проверки 11:36. Не повторять эту команду. Официальная документация подтверждает wildcard `*` в аргументе GROUP для SIP trunk set/info и возможность смены группы через set, но не раскрывает допустимый формат identifier или конкретный пример изменения группы.
6. Локальная справка получена через `man domain/dp_abai/trunk/sip/set` и подтверждена также ключом `-h`: `set GROUP TRUNK_INTERFACE PARAMETER [VALUE]`; `group` переносит транк в существующую или новую группу; GROUP в начале команды — существующая группа или `--profile`. Вызов без параметров возвращает `Wrong identifier`, но `man` работает. Официальная документация ECSS-10 3.18 отдельно подтверждает `*` как допустимый GROUP для `trunk/sip/set`; так как в `dp_abai` только один транк `kt`, wildcard по группе вместе с явным `kt` адресует именно этот транк. Предыдущий `COU` write отклонён, точный аргумент-причина не установлена; вероятные причины — Cyrillic/пробелы в source GROUP и/или uppercase target. Локальная справка говорит, что target group может быть новой; `cou.gr` соответствует стилю примеров Eltex (`sbc.gr`, `loc.gr`, `test.group`), но конкретный target identifier пока не проверен на этой системе. Следующий шаг до записи: read-only проверить текущие вызовы `domain/dp_abai/trunk/sip/call-list * kt` и свойства текущей группы `domain/dp_abai/iface/group-info -g \"Центр Оперативного Управления\" -o sip1`; затем оценить, можно ли переносить группу без потери групповых свойств. Не считать `--check` dry-run: локальная справка показывает его только в примере изменения remote-end-point, а семантика предварительной проверки group move не подтверждена. Не выполнять write до новой проверки активных вызовов и подтверждения окна работ. Сохранять неизменными endpoints, auth, access_group, routing.context и маршруты. После согласованного изменения проверить `trunk/list`, `trunk/sip/info * kt`, HTTP-terminal `sip_trunk_show`, затем входящие/исходящие звонки.
7. Live production changes SSW/маршрута 112 делать только при отдельной необходимости.

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

## 25. Full CoCon output confirms Cyrillic in generated trunk identifier — 2026-10-30
- User ran `domain/dp_abai/trunk/sip/info * kt` on ECSS-10 3.18.0.271.
- Exact result:
  - `routing.context = default_routing` (not `ctx_from_local`; the earlier ctx_from_local command was only an illustrative placeholder and correctly returned Bad context).
  - `Group` is rendered as Erlang integer list `[1062,1077,1085,1090,1088,32,1054,1077,1088,1072,1090,1080,1074,1085,1086,1075,1086,32,1059,1087,1088,1072,1074,1083,1077,1085,1080,1103]` = `Центр Оперативного Управления`.
  - read-only parameter `trunk (trunk name)` contains `dp_abai.Центр Оперативного Управления.trunk.autoname`, likewise rendered as a codepoint list.
  - Other critical parameters: remote-end-point 10.97.100.1:5060; local-end-point sip_main:5060; mode sip-proxy; access_group all; interface active=true and not blocked; disconnections number 0.
- This strongly implicates Cyrillic in the group and generated trunk name as the trigger for `sip_trunk_show`'s `ion_common:format(["~s", [codepoints]])` badarg. Root cause is highly likely but should be verified after any approved fix.
- The user's `routing/show ctx_from_local` failed because the actual context is `default_routing`; next read-only inspection is `domain/dp_abai/routing/show default_routing`.
- Official ECSS-10 v3.18 documentation confirms SIP trunk group can be changed via the trunk SIP set command; however, inspect current `default_routing` rules first and plan a rollback before any write. Do not change destination/listen endpoints or access group.
- Candidate ASCII group name: `COU`. Do not execute the write until routing dependencies and rollback are understood. Proposed syntax to validate against local CoCon help/docs: `domain/dp_abai/trunk/sip/set "Центр Оперативного Управления" kt group COU`.


## 26. Routing context review for SIP trunk Unicode incident — 2026-10-30
- User ran read-only `domain/dp_abai/routing/show default_routing`; actual context exists and was imported 03.09.2026 16:18:08.
- XML rules: `test` matches CDPN 2000 -> IVR script `06fbb268b12127f9`; `abai_112` matches CDPN 112 -> IVR `Abai_112_ivr`; `local_calls` matches final + CDPN % -> `local`.
- No explicit reference to trunk group `Центр Оперативного Управления` appears in this context. This reduces concern about dependencies in `default_routing`, but does not rule out references in other routing contexts or configuration.
- The earlier `ctx_from_local` error was caused by using a hypothetical example context; actual context for SIP trunk `kt` is `default_routing`. Do not alter any route rules to address the Unicode formatting error.
- Official Eltex ECSS docs describe `domain/<DOMAIN>/routing/list` and support changing a SIP trunk's group through `domain/<DOMAIN>/trunk/sip/set`; a 3.14 release note explicitly lists support for changing trunk group with this command. Syntax is `set <GROUP> <TRUNK_INTERFACE> <PARAMETER> <VALUE>`. This is documentation evidence for capability, not proof that changing the group is safe for this exact production configuration.
- Next safe step: run read-only `domain/dp_abai/routing/list`, then inspect every listed context for dependencies before changing group. Candidate ASCII target remains `COU`; do not write until all contexts are reviewed and a rollback command is prepared.


## 27. All routing contexts enumerated for SIP trunk Unicode incident — 2026-10-30
- User ran read-only `domain/dp_abai/routing/list`; output: only `default_routing`, `Total: 1`.
- The only context was already read in full (section 26): `test` (2000 -> IVR), `abai_112` (112 -> IVR), `local_calls` (local). No explicit reference to Cyrillic SIP trunk group appears in these rules.
- This completes the routing-context inventory. It does not prove there are no references outside routing contexts, but there are no other routing contexts to inspect.
- Official Eltex ECSS-10 3.18 docs describe `domain/<DOMAIN>/trunk/sip/set <GROUP> <TRUNK_INTERFACE> <PARAMETER> <VALUE>`; release notes for 3.14 list support for changing an interface's group (`group`) through this command. This supports the planned parameter name and syntax; it is not a guarantee of impact-free operation.
- Planned minimal change, pending operator execution: `domain/dp_abai/trunk/sip/set "Центр Оперативного Управления" kt group COU`. Keep the static trunk and preserve destination, listen endpoint, mode, auth, access_group, and routing.context. No remove/redeclare.
- Current output from `trunk/sip/info * kt` should be retained as rollback evidence. If the change succeeds, immediately re-read `trunk/list` and `trunk/sip/info * kt`, retry HTTP-terminal `sip_trunk_show`, and place/test inbound and outbound calls. If command returns an error or unexpected state, stop and re-read before attempting any further write.


## 28. SIP trunk group change rejected by CoCon identifier validation — 2026-10-30
- User attempted `domain/dp_abai/trunk/sip/set "Центр Оперативного Управления" kt group COU`; CoCon returned `Error: Wrong identifier`. No successful execution or changed group is evidenced; re-read live state.
- The error does not identify which argument failed. Possible causes include the Cyrillic/space-containing source GROUP and/or target name `COU`; neither is proven. Do not repeat the same command.
- ECSS-10 3.18 docs state that `trunk/sip/set` and `trunk/sip/call-list` accept `*` for all groups. Release notes confirm trunk group changes through `trunk/sip/set`. Sources: https://docs.eltex-co.ru/e318/domain-domain-trunk-sip-komandy-upravleniya-trankami-sip-701043669.html and https://docs.eltex-co.ru/ecss3148/kratkij-perechen-funktsij-realizovannyh-v-ramkah-dannoj-versii-ecss-10-181606964.html
- Next, run only read-only commands: `domain/dp_abai/trunk/list`, `domain/dp_abai/trunk/sip/info * kt`, `domain/dp_abai/trunk/sip/call-list * kt`. Confirm the group is unchanged and no calls are active before considering another write.
- If approved after those checks, use `*` as source GROUP to avoid the Cyrillic identifier. A lowercase ASCII target such as `cou` is only a candidate pending confirmation of CLI identifier rules. Do not remove/redeclare or alter endpoints, auth, access_group, routing.context, or routes.


## 29. SIP trunk unchanged after rejected group update; no active calls — 2026-10-30
- User supplied fresh CoCon outputs after the failed `set ... group COU` attempt:
  - `domain/dp_abai/trunk/list`: exactly one trunk `kt`, owner `sip1`, group still `Центр Оперативного Управления`, active=true, type=sip, total bandwidth 256(0).
  - `domain/dp_abai/trunk/sip/info * kt`: group still returned as Erlang Unicode codepoint list for `Центр Оперативного Управления`; URI kt; active=true, blocked=false, static, non-dynamic; remote-end-point 10.97.100.1:5060; local-end-point sip_main:5060; mode sip-proxy; access_group=all; routing.context=default_routing; generated trunk name still contains Cyrillic; disconnections number=0.
  - `domain/dp_abai/trunk/sip/call-list * kt`: 0 sessions. Earlier source-group-specific call-list also returned 0.
  - `domain/dp_abai/routing/list`: only default_routing, total 1 (already fully inspected in sections 26-27).
- The failed command made no visible configuration change. This is now confirmed by before/after live trunk listing and info.
- Current service state appears active and unblocked; do not infer call success from that alone. No active calls were present at the time of capture.
- Official v3.18 docs confirm `*` can be used for GROUP in `trunk/sip/info` and `trunk/sip/set`, and the 3.14.3 release notes mention trunk group change through `trunk/sip/set`. However, docs do not expose identifier character restrictions or a concrete `set ... group ...` example. The previous `COU` write returned `Wrong identifier`; do not assume whether source group, target group, or parameter token caused it.
- Next safe step: inspect local CoCon help/command metadata for `domain/dp_abai/trunk/sip/set` and accepted parameter/value syntax, or request Eltex support confirmation of the exact `group` value format and whether target group must pre-exist. Until that is clarified, do not attempt `cou`, `COU`, wildcard writes, group creation by redeclare, or any other production write. Preserve endpoints/auth/access_group/routing.context and all routes.
- After vendor/CLI syntax confirmation, make a single controlled group-only change during a maintenance window, then verify trunk list/info, HTTP-terminal `sip_trunk_show`, and real inbound/outbound calls. The root cause of `sip_trunk_show invalid_xml` remains highly suspected but not confirmed until retested.


## 30. Identifier-format research after SIP trunk set rejection — 2026-10-30
- Further official-doc review confirms:
  - ECSS-10 v3.18 SIP trunk CLI documents `set <GROUP> <TRUNK_INTERFACE> <PARAMETER> <VALUE>`, with `*` allowed for GROUP; 3.14.3 release notes explicitly mention the ability to change a trunk's group via `domain/<DOMAIN>/trunk/sip/set`.
  - Public ECSS docs show common group-name examples such as `ssw.gr`, `sbc.gr`, `loc.gr`; a separate SIP-subscriber `change-group` command documents that a missing target group may be created, with example `800.gr`. These are subscriber/group examples and do NOT establish a mandatory suffix or exact identifier grammar for SIP trunk groups.
- Therefore `COU` may have failed due target identifier format (uppercase and/or missing conventional suffix), but this remains an unverified hypothesis. Do not infer that `cou.gr` is guaranteed valid for a SIP trunk.
- Next diagnostic should be non-mutating: obtain local CoCon command usage/help for `domain/dp_abai/trunk/sip/set` (e.g. invoke the command path without parameters only if local CLI safely returns usage; otherwise use the documented built-in help mechanism) and confirm the exact accepted parameter/value syntax with Eltex if help is insufficient.
- Do not issue another group-change write until exact trunk-group identifier requirements are confirmed. Last live state capture remains: kt active/unblocked, original Cyrillic group unchanged, endpoints/mode/access_group/routing.context unchanged, and 0 active sessions at capture time 30.10.2026 11:36.


## 31. CoCon bare set invocation rejected; documented help syntax identified — 2026-10-30
- User executed read-only diagnostic `domain/dp_abai/trunk/sip/set` with no arguments at 11:38:25. CoCon returned `Error: Wrong identifier` in 10 ms; no configuration change is evidenced, and no usage/help was printed.
- This confirms that bare invocation is not a safe way to obtain usage on this ECSS-10 3.18.0.271 node. It does not reveal which argument failed in the earlier write attempt and does not establish valid trunk-group identifier syntax.
- Official Eltex CLI documentation says command help can be requested either by placing `man` before the command (example `man shell-trace`) or appending `-h` after the command. Source: https://docs.eltex-co.ru/e16/interfejs-komandnoj-stroki-cli-649287025.html
- Next safe diagnostic: run `man domain/dp_abai/trunk/sip/set`; if needed, try `domain/dp_abai/trunk/sip/set -h`. These are help-only requests. Do not attempt any `set` with arguments until the help output or Eltex confirms the exact syntax and identifier requirements. Preserve the current trunk configuration.


## 32. Local SIP trunk set help captured — 2026-10-30
- User ran `man domain/dp_abai/trunk/sip/set`; the local 3.18.0.271 help confirms `set GROUP TRUNK_INTERFACE PARAMETER [VALUE]` and lists `group` as “move trunk to other group (that is existing or new)”. It defines the leading GROUP as an existing interface group name or `--profile`; `TRUNK_INTERFACE` may be the configured interface name or `*`.
- The user also ran `domain/dp_abai/trunk/sip/set -h`; it returned the same help. Bare command invocation without args still returns `Wrong identifier` and is not a help mechanism.
- The help output's examples show `--check` with a `remote-end-point` change, not as a generic dry-run. Do not use `--check` to assume a group change is non-mutating.
- Official ECSS-10 v3.18 SIP trunk documentation explicitly says `*` may be used for GROUP in `trunk/sip/set`; in this domain only trunk `kt` exists, so `* kt` is the documented way to avoid passing the Cyrillic/space-containing source group as an identifier while still naming the target interface. Source: https://docs.eltex-co.ru/e318/domain-domain-trunk-sip-komandy-upravleniya-trankami-sip-701043669.html
- The failed previous command used source group `"Центр Оперативного Управления"` and target `COU`; `Wrong identifier` does not identify which argument was rejected. Source group syntax and uppercase target are both possible causes, not confirmed individually.
- The local help explicitly permits a new target group. `cou.gr` follows common documented Eltex naming examples (`sbc.gr`, `loc.gr`, `test.group`) but has not been validated as a legal target identifier on this node. Do not execute it yet.
- Before a controlled group move, recheck `domain/dp_abai/trunk/sip/call-list * kt` immediately before the write and inspect current group-specific resources with read-only `domain/dp_abai/iface/group-info -g "Центр Оперативного Управления" -o sip1`. Only proceed in an approved maintenance window after considering any group-level properties. Preserve remote/local endpoints, mode, authentication, access_group, routing.context, and routes.


## 33. Повторная read-only проверка вызовов и диагностика iface/group-info — 2026-10-30
- User повторно выполнил `domain/dp_abai/trunk/sip/call-list * kt` в 11:43:08; результат — 0 sessions. Это подтверждает отсутствие активных вызовов только на момент данного capture; перед любой будущей production-записью проверку нужно повторить непосредственно перед изменением.
- User выполнил `domain/dp_abai/iface/group-info -g "Центр Оперативного Управления" -o sip1`. Команда была распределённо исполнена на `ds1@ecss1` и вернула ошибку форматирования вывода с внутренним результатом `{ok,[]}`.
- В аргументе GROUP отображены codepoints `34` в начале и конце — это символы двойных кавычек. Значит, в этом вызове кавычки попали в значение фильтра как буквальные символы; пустой результат не доказывает отсутствие свойств у реальной группы `Центр Оперативного Управления`.
- Не повторять фильтр с двойными кавычками и не делать выводов о свойствах группы по `{ok,[]}`. Следующий безопасный запрос — получить все группы владельца `sip1` без фильтра GROUP: `domain/dp_abai/iface/group-info -o sip1`. Это read-only. Никаких `set`/переносов группы пока не выполнять.

## 34. Нефильтрованный iface/group-info по sip1 — 2026-10-30
- User выполнил read-only `domain/dp_abai/iface/group-info -o sip1` в 11:45:55; команда отработала на `ds1@ecss1` и вернула заголовок `Domain dp_abai owner sip1 group * iface resources properties`, но таблица `W / Property / Value` осталась пустой.
- Это означает, что данный запрос не показал дополнительных iface resource properties для всех групп владельца `sip1`. Не трактовать пустую таблицу как доказательство отсутствия любых зависимостей/ссылок на группу в конфигурации ECSS: команда показывает именно iface resource properties.
- Предыдущий запрос с `-g "Центр Оперативного Управления"` включил кавычки в сам аргумент (codepoint 34) и вернул ошибку с `{ok,[]}`; его результат не использовать как данные о группе.
- Состояние транка не менялось. Последняя проверка `domain/dp_abai/trunk/sip/call-list * kt` в 11:43:08 показала 0 sessions; перед любой записью проверить заново непосредственно перед изменением.
- Следующий read-only шаг: получить интерфейсный инвентарь `domain/dp_abai/iface/list * *`, чтобы увидеть фактические группы/интерфейсы и проверить, нет ли дополнительных интерфейсов, привязанных к текущей группе. До анализа вывода не выполнять `trunk/sip/set` и не создавать/переименовывать группы.

## 35. Полная инвентаризация интерфейсов dp_abai — 2026-10-30
- User выполнил read-only `domain/dp_abai/iface/list * *` в 11:47:13; команда вернула 28 интерфейсов.
- Среди SIP-интерфейсов:
  - 1001–1024 (24 интерфейса), owner `sip1`, все находятся в группе `Центр Оперативного Управления`;
  - SIP-транк `kt`, owner `sip1`, находится в той же группе;
  - SIP-интерфейс 9999, owner `sip1`, находится отдельно в группе `DP_Abai`.
- Также перечислены `system:ivr` и `system:teleconference`, оба с owner/group `.system`.
- Следствие: Cyrillic group используется не только транком, но и 24 SIP-абонентскими интерфейсами. Нельзя переименовывать/удалять/массово менять текущую группу: это затронет абонентские интерфейсы. Если впоследствии будет согласован перенос, рассматривать только отдельный перенос транка `kt`, не менять группы 1001–1024.
- Ранее `domain/dp_abai/iface/group-info -o sip1` показал пустую таблицу дополнительных iface resource properties. Это не исключает иных ссылок/зависимостей вне области данной команды.
- На момент этого capture конфигурация не менялась. Синтаксис target identifier для нового ASCII trunk group по-прежнему не подтверждён; прежний `COU` был отклонён с `Wrong identifier`, а причина не локализована.
- Следующий шаг: не выполнять write. Получить от Eltex подтверждение допустимого формата имени группы для SIP trunk и точного значения аргумента `group`; либо найти локальную CLI-команду/справку, которая показывает существующие interface groups и правила identifier. Не переносить транк в `DP_Abai` только потому, что эта группа присутствует в списке: её эксплуатационная совместимость с транком не подтверждена. Перед любой будущей записью повторить call-list непосредственно перед окном работ и сохранить rollback evidence. Проверять после согласованного изменения `trunk/list`, `trunk/sip/info * kt`, HTTP-terminal `sip_trunk_show` и реальные входящие/исходящие вызовы.
