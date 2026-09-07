# ECSS-10 ДП Абай — PROJECT_STATE

Обновлено: 2026-09-07  
Источник истины для продолжения проекта. Не возвращаться к уже подтверждённым этапам без новых фактических данных.

## 1. Архитектура и production foundation — подтверждено
- ECSS-10 3.18.0.271 на двух Ubuntu 22.04 VM: `ecss1` 192.168.190.70 и `ecss2` 192.168.190.80.
- Distributed licensing, оба licence-manager host Alive, VRRP/кластерная связность и нужная Mnesia подтверждены.
- Тестовый `2000`, абоненты 1001/1002, queue `Abai_112`, group `Abai_112_cc`, agents 1001/1002 и production route `112 -> default_routing/abai_112 -> Abai_112_ivr -> Abai_112 -> Abai_112_cc` подтверждены. Не повторять без нового инцидента/требования.
- `ecss-cc-ui`/API foundation и Call API integration registration подтверждены. Реальные API keys/JWT остаются secret-bearing boundary и не коммитятся.

## 2. Conversation correlation — подтверждённые факты
- Прямой 1001→1002 leg: разные `id`, общий `call_id`, общий `call_ref`.
- Queue call: caller/IVR и operator leg имеют общий logical `call_id`, но разные `call_ref`.
- `has_answer_time` различает observed answered и released-without-answer legs.
- Один `call_ref` нельзя считать universal id всей queue-цепочки.

## 3. Offline CDR tooling — verified baseline
CDR рассматривается только как evidence. `CONN_ID`, `T_ECD`, `T_DBA` обрабатываются fail-closed; numeric parsing сохраняет exact integer semantics через `Decimal` и отклоняет отрицательные, fractional/non-finite/malformed значения.

Verified main содержит:
- required-header/duplicate-column guards и exact-ref caller/operator correlation;
- operator/caller timing evidence без heuristic row selection;
- raw `T_ECD/T_DBA` только для ровно одной complete exact caller-ref row без competing incomplete row;
- exact built-in string/record/whitespace guards;
- fail-closed cardinality diagnostics `caller_has_competing_timing_records`, `caller_has_incomplete_timing_records`, `caller_has_complete_timing_records`, `caller_has_any_timing_records`;
- r40 (`5d03c34c01a4eea8d5a5e27db7a5d8ef107dd1ba`) GREEN run 511 и auto-merged как `817a33109a8b428c87a125dc3b25c05d1fbc1469`;
- r41 (`0a91265d9836332a563f62a01b998b3b6626fff3`) GREEN run 521 и auto-merged в `main` как `492992a36c65cf0d029f6a31b2c41bb3a125287f`; `caller_has_single_timing_record` verified как exact-cardinality diagnostic без semantic guesses.

## 4. CDR semantics — НЕ доказано
До свежего sanitized queue-call CDR не считать доказанными:
- финальное сопоставление logical `call_id` ↔ CDR rows;
- queue membership по одному полю;
- `T_DBA` как queue wait;
- какой `T_ECD` должен стать внешним `Duration`;
- recording URL без фактического evidence.

## 5. Текущий offline increment
`ai/cdr-timing-report-r42` переводит накопленные diagnostics в полезный evidence-only offline report вместо добавления очередного одиночного guard.
- `build_caller_timing_report(...)` принимает records + exact caller ref и повторно использует verified `summarize_caller_timing(...)`.
- Report показывает caller ref, total/complete/incomplete counts, evidence classification и raw `T_ECD/T_DBA` только когда underlying summary разрешает их однозначно; ambiguous/multiple/mixed evidence выводит `n/a`.
- Report всегда содержит явное предупреждение: raw timing fields only; queue membership, queue wait, logical call identity и final duration не inferred.
- Добавлены tests для no-evidence, unique complete, competing complete и mixed evidence.
- Никаких live ECSS/112/agent/routing/licensing изменений нет.

## 6. Live data boundary / next
1. Дать Forgejo проверить `ai/cdr-timing-report-r42`; RED не обходить и `main` не форсировать.
2. При GREEN использовать report как безопасный offline artifact для следующего sanitized CDR анализа.
3. При появлении реального queue-call CDR сопоставить known caller/operator refs с rows и только после evidence формализовать Duration/queue timing mapping.
4. Live production changes — только с актуальными фактами и отдельной необходимостью.
5. Синхронизировать Project State, Roadmap и changelog после каждого инкремента.

## 7. Security / запреты
- Не повторять licence/VRRP/Mnesia/test2000/agents/route112 setup.
- Не использовать heuristic guesses как production mapping.
- Не менять боевой 112 без отдельной необходимости.
- Не считать offline unit tests доказательством production ECSS.
- Не коммитить passwords, API keys, JWT, cookies, Rutoken PIN или subscriber-sensitive raw production CDR; fixtures только sanitized.
- Local gate/CI нельзя обходить force-merge в `main`.
