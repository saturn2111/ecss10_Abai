# ECSS-10 ДП Абай — PROJECT_STATE

Обновлено: 2026-09-07  
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

```text
112 -> default_routing/abai_112 -> Abai_112_ivr -> queue Abai_112 -> group Abai_112_cc -> Agent1001/Agent1002
```

Live queue test до Operator2 подтверждал реальный проход через маршрут. Не возвращаться к перенастройке этого маршрута без нового требования/инцидента.

## 10. Offline CDR tooling — verified baseline

Offline tooling рассматривает CDR только как evidence. `CONN_ID`, `T_ECD`, `T_DBA` обрабатываются fail-closed; numeric parsing сохраняет exact integer semantics через `Decimal` и отклоняет отрицательные, fractional/non-finite/malformed значения.

Verified main содержит:
- required-header и duplicate-column guards;
- exact-ref caller/operator correlation evidence;
- operator-duration/timing evidence без heuristic row selection;
- r26 exact-decimal precision guard;
- r27 exact caller-ref timing completeness evidence;
- r28 raw `T_ECD/T_DBA` values только для ровно одной complete caller-ref row без competing incomplete rows;
- r29 exact built-in string guard для `caller_call_ref`;
- r30 (`3cafa0dc87045af8d52b60222bd6c15fd0be8d84`) Forgejo GREEN и auto-merged в `main` как `279c9acdef2345d08be411778c18f6ec8da01383`; caller timing evidence принимает только exact `CdrRecord` values.

## 11. CDR semantics — пока НЕ доказано

Пока нет свежего live queue CDR, не считать доказанными:
- финальное сопоставление logical `call_id` ↔ CDR rows;
- queue membership по одному CDR полю;
- семантику `T_DBA` как queue wait;
- какой CDR `T_ECD` должен стать внешним `Duration` для queue call;
- запись разговора/URL без фактического evidence.

## 12. Текущий offline increment

`ai/cdr-caller-ref-whitespace-guard-r31` усиливает exact-ref boundary без новых semantic assumptions:
- padded nonblank caller refs (`" caller-ref"`, `"caller-ref "` и аналоги) fail-close с `ValueError` вместо тихого trim и последующего exact-match поиска по изменённому значению;
- whitespace-only ref по-прежнему нормализуется в пустой ref и возвращает `not_evaluated` без CDR selection;
- exact nonblank ref behavior не меняется;
- regression tests покрывают padded, whitespace-only и exact cases.

Никаких live ECSS/112/agent/routing/licensing изменений этот инкремент не делает.

## 13. Live data boundary

Для следующего фактического semantic mapping нужен sanitized CDR именно подтверждённого queue call вместе с известными caller/operator refs. До этого продолжается только offline tooling/tests/docs.

## 14. Текущая точка / СЛЕДУЮЩИЕ ДЕЙСТВИЯ

1. Дать Forgejo проверить `ai/cdr-caller-ref-whitespace-guard-r31`; красный CI не обходить.
2. Пока live телефоны/CDR недоступны — продолжать deterministic offline correlation tooling, tests и документацию.
3. При появлении реального sanitized queue CDR сопоставить caller/operator refs с rows и только после этого формализовать Duration/queue timing mapping.
4. Live production changes делать только при наличии конкретных фактических данных и отдельной необходимости.
5. Синхронизировать этот файл, `ROADMAP.md` и autonomous changelog после каждого завершённого инкремента.

## 15. Что не делать

- Не повторять licence/VRRP/Mnesia/test2000/agents/route112 setup.
- Не использовать heuristic guesses как production mapping.
- Не менять боевой маршрут 112 без отдельной необходимости.
- Не считать offline unit tests доказательством поведения production ECSS.

## 16. Evidence policy

Каждое новое утверждение о live ECSS/CDR должно опираться на фактический capture/output. Offline helpers должны fail-close при ambiguous/multiple/incomplete evidence.

## 17. Security

- Не коммитить реальные passwords, API keys, JWT, cookies, Rutoken PIN или другие credentials.
- Не коммитить subscriber-sensitive raw production CDR; использовать sanitized fixtures.
- Не расширять live production access только ради автономного инкремента.
- Local gate/CI нельзя обходить force-merge в `main`.
