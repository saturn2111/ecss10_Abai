# ECSS-10 ДП Абай — PROJECT_STATE

Обновлено: 2026-09-08  
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

Verified main содержит required-header/duplicate-column guards, exact-ref correlation, evidence-only text/JSON/CLI, multi-artifact bundle, TSV report, summary/diff, standalone HTML report, r51 интерактивный локальный поиск/filter/reset, r52 export текущего visible subset в spreadsheet-safe CSV плюс print-to-PDF, r53 live summary текущего visible subset и базовый r54 session-only bookmark review. Базовый r54 был auto-merged локальным gate в current main `d9ff2dd1f1b206080f00064eafdd0ab0bfac5148`.

## 11. CDR semantics — пока НЕ доказано
Пока нет свежего live queue CDR, не считать доказанными:
- финальное сопоставление logical `call_id` ↔ CDR rows;
- queue membership по одному CDR полю;
- семантику `T_DBA` как queue wait;
- какой CDR `T_ECD` должен стать внешним `Duration` для queue call;
- запись разговора/URL без фактического evidence.

## 12. Текущий offline increment
После auto-merge базового r54 старая ветка `ai/cdr-html-bookmarks-r54` стала divergent, поэтому её не продвигаем и не force-merge.

Чистая ветка `ai/cdr-html-bookmark-visible-r54` создана от current `main` и содержит только ещё не merged операторское улучшение:
- `Bookmark visible` отмечает одним действием ровно текущий subset, заданный existing Search + classification filter.
- Если visible subset пуст, действие disabled.
- После bulk-bookmark существующие `Bookmarked only`, CSV export, Print/PDF и visible summary продолжают работать по фактически видимому subset.
- Закладки остаются session-only: нет `localStorage`, fetch/server calls или ECSS write.
- Regression coverage фиксирует exact subset behavior и не позволяет переименовать raw `T_ECD/T_DBA` в неподтверждённые queue wait/final Duration.

## 13. Live data boundary
Для следующего фактического semantic mapping нужен sanitized CDR именно подтверждённого queue call вместе с известными caller/operator refs. До этого продолжается только offline tooling/tests/docs.

## 14. Текущая точка / СЛЕДУЮЩИЕ ДЕЙСТВИЯ
1. Дать Forgejo проверить exact final SHA `ai/cdr-html-bookmark-visible-r54`; красный CI не обходить и `main` не форсировать.
2. После GREEN переходить к следующему крупному полезному offline review/report increment, а не плодить микрогарды.
3. При появлении реального sanitized queue CDR сопоставить caller/operator refs с rows и только после этого формализовать Duration/queue timing mapping.
4. Live production changes делать только при наличии конкретных фактических данных и отдельной необходимости.
5. Синхронизировать этот файл, `ROADMAP.md` и autonomous changelog после каждого завершённого инкремента.

## 15. Что не делать
- Не повторять licence/VRRP/Mnesia/test2000/agents/route112 setup.
- Не использовать heuristic guesses как production mapping.
- Не менять боевой маршрут 112 без отдельной необходимости.
- Не считать offline unit tests доказательством поведения production ECSS.
- Не возвращать divergent `ai/cdr-html-bookmarks-r54` поверх уже продвинутого main.

## 16. Evidence policy
Каждое новое утверждение о live ECSS/CDR должно опираться на фактический capture/output. Offline helpers, reports, CLI и bundles должны fail-close при ambiguous/multiple/incomplete evidence.

## 17. Security
- Не коммитить реальные passwords, API keys, JWT, cookies, Rutoken PIN или другие credentials.
- Не коммитить subscriber-sensitive raw production CDR; использовать sanitized fixtures.
- Не расширять live production access только ради автономного инкремента.
- Local gate/CI нельзя обходить force-merge в `main`.
