# PROJECT STATE — ECSS10 ДП Абай

Обновлено: 2026-09-06  
Источник истины для продолжения проекта. Не возвращаться к уже подтверждённым этапам без новых фактических данных.

## 1. Подтверждённая инфраструктура — НЕ ПОВТОРЯТЬ

- ECSS-10 3.18.0.271 на двух Ubuntu 22.04 VM: `ecss1` 192.168.190.70 и `ecss2` 192.168.190.80.
- Два независимых Proxmox-хоста; USB Rutoken/eToken лицензирование учтено.
- Distributed licensing подтверждён; оба licence-manager host Alive.
- VRRP/кластерная связность и Mnesia для нужных ECSS компонентов подтверждены.
- Тестовый абонент/маршрут `2000` подтверждён и сохранён.
- Call-center: queue `Abai_112`, group `Abai_112_cc`, agents 1001/1002, route 112 через `default_routing/abai_112 -> Abai_112_ivr -> Abai_112 -> Abai_112_cc` подтверждён live-тестом.
- `ecss-cc-ui` 18.0.34 и API/UI сервисы на обоих узлах подтверждены.
- Внутренний CC API operations для agent/login/status/list/history подтверждены; запрещённые/неподходящие операции не повторять.
- ECSS Call API integration registration ранее подтверждён; секреты/JWT/API keys в репозиторий не коммитить.

## 2. Подтверждённый call/correlation contract

Для внешней интеграции минимальная цель — `answered` и `finished` для одного звонка с общим Id, Direction, NumberA, NumberB, Duration для finished и CallRecordUrl при наличии.

Live `conversations_event` подтверждает:
- у прямого 1001→1002 leg разные `id`, общий `call_id`, общий `call_ref`;
- у queue-вызова 1001→112→Operator2 caller/IVR и operator leg имеют общий logical `call_id`, но разные `call_ref`;
- `has_answer_time` различает answered/released-without-answer на наблюдавшихся leg;
- нельзя считать один `call_ref` универсальным идентификатором всей queue-цепочки.

## 3. CDR — что подтверждено и что ещё нельзя утверждать

Offline tooling читает CDR только как evidence. `CONN_ID`, `T_ECD`, `T_DBA` обрабатываются fail-closed; numeric parsing сохраняет exact integer semantics через `Decimal` и отклоняет отрицательные, fractional/non-finite или malformed значения.

Verified main содержит:
- header/duplicate-required-column guards;
- exact-ref correlation helpers и evidence classifications;
- operator-duration evidence без выбора сомнительной записи;
- r26 exact-decimal precision guard;
- r27 (`a1ee141193b647cb784109d9447115b4bb08b0b9`) Forgejo GREEN и auto-merged в `main` как `d7fb0a7b7fac682e6c2678cc1b51c32be9b87e20`; `summarize_caller_timing(...)` считает complete/incomplete timing rows только для exact `CONN_ID == caller_call_ref`.

Пока нет свежего live queue CDR, НЕ считать доказанными:
- финальное сопоставление logical `call_id` ↔ CDR rows;
- queue membership по одному CDR полю;
- семантику `T_DBA` как queue wait;
- какой именно CDR `T_ECD` должен стать внешним `Duration` для queue call;
- запись разговора/URL без фактического evidence.

## 4. Текущий автономный инкремент

`ai/cdr-caller-timing-values-r28` расширяет только offline exact-ref evidence:
- при ровно одной complete caller-ref строке и отсутствии конкурирующих incomplete rows безопасно выдаёт сырые `caller_t_ecd_seconds` и `caller_t_dba_seconds`;
- при duplicate/mixed/no evidence оба selected-value поля остаются `None`;
- значения не переименовываются в queue wait/duration и не используются для live production changes;
- добавлены unit tests на unique, duplicate, mixed и blank-ref случаи.

Никаких live ECSS/112/agent/routing/licensing изменений этот инкремент не делает.

## 5. Следующие действия

1. Дать Forgejo проверить `ai/cdr-caller-timing-values-r28`; красный CI не обходить.
2. Пока live телефоны/CDR недоступны — продолжать только deterministic offline correlation tooling, tests и документацию.
3. Когда появится реальный sanitized CDR именно подтверждённого queue call, сопоставить caller/operator refs с rows и только после этого формализовать Duration/queue timing mapping.
4. Live production changes делать только при наличии конкретных фактических данных и отдельной необходимости.
5. Синхронизировать этот файл, `ROADMAP.md` и autonomous changelog после каждого завершённого инкремента.
