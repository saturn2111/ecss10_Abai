# ECSS-10 ДП Абай — PROJECT_STATE

**Canonical source of truth для проекта**  
**Последнее обновление:** 2026-09-03 16:52+05  
**ECSS:** 3.18.0.271

> Перед продолжением проекта читать этот файл и продолжать с раздела **«Текущая точка / СЛЕДУЮЩИЕ ДЕЙСТВИЯ»**. Не повторять подтверждённые этапы. Новые фактические данные пользователя имеют приоритет. Работать: одна операция → проверка → следующий шаг. Секреты не хранить и не повторять.

---

## 1. Архитектура

Двухузловая отказоустойчивая ECSS-10 для ДП области Абай, Call-center 112 и внешняя API-интеграция, до ~1000 абонентов.

```text
External CRM
    |
 HTTPS :443
    |
 stable endpoint / HA
    |
 +------------------------+------------------------+
 |                                                 |
ecss1                                             ecss2
192.168.190.70                                    192.168.190.80
 |                                                 |
our integration service                          our integration service
 |                                                 |
 +-- Call API :8089                                +-- Call API :8089
 +-- CC UI/API :8090/:8091                         +-- CC UI/API :8090/:8091
 +-- SSW :8086                                     +-- SSW :8086
```

Свой код размещать отдельно, например `/opt/ecss-integration-api`, отдельный systemd unit. Не править штатные файлы ELTEX ради интеграции.

---

## 2. Базовая инфраструктура — выполнено

- Два независимых Proxmox-хоста, не PVE cluster.
- `srv-prmx-1` mgmt `192.168.190.2/26`; `srv-prmx-2` mgmt `192.168.190.3/26`.
- LACP 802.3ad / VLAN-aware.
- `ecss1` VMID101: Ubuntu 22.04.5, mgmt `.190.70/26`, voice `.191.2/24`, 8 vCPU / 32GB / 280GB.
- `ecss2` VMID102: Ubuntu 22.04.5, mgmt `.190.80/26`, voice `.191.3/24`, 8 vCPU / 32GB / 280GB.
- Cluster ID **`ecss1`** — не менять.
- Парные компоненты `core1`, `ds1`, `md1`, `mycelium1`, `sip1`.
- Mnesia/split-brain восстановлены; без новой причины не повторять.
- PostgreSQL BDR `18.0.0+ssw`, port5439, replication проверена.
- Gluster `ecss_volume`, replica2, heal проверен.
- RestFS `/var/lib/ecss/restfs`, port9990.

---

## 3. SIP / Media / VRRP — выполнено

- MSR `3.18.0.7`: ecss1 `.191.2`, ecss2 `.191.3`.
- registrar `.191.2:5000`, `.191.3:5000`.
- Domain `dp_abai`, IP-set `sip_main`.
- VIP1 `.191.4/24` VRID31, normal MASTER ecss1.
- VIP2 `.191.5/24` VRID32, normal MASTER ecss2.
- Failover `ecss-pa-sip` реально проверен.

---

## 4. Лицензирование — выполнено

- ECSS TPM License / ID1, commercial, expiry `31.07.2050`.
- SSW ID `ECSS0000400`.
- License Managers `.70:4321`, `.80:4321`, оба Alive; failover проверен.
- `ecss-license-provider 1.0.6` активен на обоих.
- По одному Rutoken на физическом сервере.

---

## 5. Абоненты / CDR / trunk

- SIP1001 VP-30P и SIP1002 VP-17P зарегистрированы исторически.
- CDR CSV: period3600, `/var/lib/ecss/ftp/domain/dp_abai/default/csv`, файлы создаются.
- Файл `cdr_dp_abai_default_YYYYMMDD_HH_00_00_p.csv` закрывает **предыдущий час**: например файл `20260903_16_00_00` содержит звонки 15:xx. Следовательно live 112 вызов 16:21–16:22 ожидается в файле `20260903_17_00_00`.
- SIP trunk оператора пока не завершён: нужны реальные параметры оператора.

---

## 6. Call API :8089 — выполнено

- ecss1 `.70:8089`, ecss2 `.80:8089`; SSW `.70/.80:8086`.
- `integration.register`, JWT, WS, heartbeat, `call.make`, conversation events и failover `.70 → .80 → .70` проверены.
- Integration client `dp_abai_test`, service; API key/JWT не хранить, после приёмки ротировать.
- JWT/auth node-local/in-memory.
- На ecss2 временный listener `/tmp/ecss-events.js` успешно слушает реальные `conversations_event`; в продукт его не переносить как есть.
- В live listener `workitem_id` оказался `null` даже на реальном queue-вызове 112; поэтому на него нельзя рассчитывать как на обязательный идентификатор Call API conversation events.

---

## 7. Текущий доступ

Сейчас нет физического доступа к SIP-телефонам. Доступны Web UI, SSH, CoCon и серверные web-интерфейсы. Web UI умеет инициировать и отвечать на вызов, поэтому текущие интеграционные тесты можно продолжать удалённо.

---

## 8. Call-center test 2000 — уже пройден

```text
2000 -> IVR test_cc_ivr -> queue test -> group test_cc -> SIP1001 + SIP1002
```

Distribution `multicall`; звонок ранее вызывал оба SIP. Не повторять и пока не удалять test/test_cc.

Рабочий IVR теста:
- name `test_cc_ivr`;
- id `06fbb268b12127f9`;
- begin → queue;
- `queue_id=test`;
- `transfer_scenario=release`;
- `mode=permanent`.

---

## 9. Боевая 112 — очередь/агенты/IVR/маршрут

Группа `Abai_112_cc`:
- Agent1001 = Operator1 / Phone1001;
- Agent1002 = Operator2 / Phone1002.

Queue `Abai_112`:
- distribution `multicall`;
- max_wait_time120;
- max_distribution_attempts3;
- max_distribution_duration10;
- queue_length20;
- callback_cooldown_timeout300;
- skill_based_distribution false;
- `lock_if_no_answer=true`;
- `lock_if_reject=true`;
- `serial_lock_enabled=true`.

Оба боевых агента полностью проверены через Web UI: Login → Available → AuxWork → Available → Logout. Не повторять полный lifecycle без новой причины.

2026-09-03 16:21 перед live 112 тестом подтверждено одновременно:

```text
1001 Operator1 available Phone=1001 idle
1002 Operator2 available Phone=1002 idle
```

### Боевой IVR

```text
name/id: Abai_112_ivr
begin -> queue
queue_id: Abai_112
transfer_scenario: release
position_notification_mode: absolute
time_prediction_mode: fair
callback_on_failure: false
callback_on_overload: false
mode: permanent
version: 3.18.0.33
```

`/domain/dp_abai/ivr/script/show --id Abai_112_ivr` подтвердил `queue_id=Abai_112`.

### Маршрут 112 — создан и подтверждён

Перед изменением сделан штатный backup `default_routing`.

Активный context после импорта:

```text
rule test:
  CDPN 2000 -> IVR 06fbb268b12127f9

rule abai_112:
  CDPN 112 -> IVR Abai_112_ivr

rule local_calls:
  final=true
  CDPN % -> local
```

Итоговая цепочка:

```text
112 -> default_routing/abai_112 -> Abai_112_ivr -> queue Abai_112 -> group Abai_112_cc -> Agent1001/Agent1002
```

Тестовый `2000` и общий `% -> local` сохранены.

---

## 10. ecss-cc-ui 18.0.34 — оба узла готовы

### ecss1
- `ecss-cc-ui-api` active;
- `ecss-cc-ui` active;
- `8090` nginx/openresty, `8091` node;
- Web UI `.70:8090` работает.

### ecss2
- `ecss-cc-ui 18.0.34` установлен;
- `ecss-cc-ui-api` active/enabled;
- `ecss-cc-ui` active/enabled;
- `0.0.0.0:8090` nginx/openresty;
- `0.0.0.0:8091` node;
- config: ECSS `localhost:8086`, SQL `localhost:5439`;
- Web UI `.80:8090` работает, login подтверждён.

---

## 11. Внутренний CC API — подтверждено

```text
CRM        = call
WEB_CC     = cc/common
CC_AGENT   = cc/arm
CC_PUBSUB  = cc/pubsub
CONFERENCE = teleconference
```

Подтверждены операции `login_agent`, `logout_agent`, `make_available`, `auxwork`, `agent_list`, `agents_list`, `group_list`, `all_queues`, `operator_call_history`, realtime `agents_info_event`.

`operator/forceLogout` обычному профилю запрещён; не повторять. `call/makeCall #160` не использовать как logout.

---

## 12. Контракт внешней интеграции

Минимально нужны два события одного состоявшегося звонка:

```text
answered
finished
```

Оба с одинаковым `Id`.

```text
Id            string
Status        answered | finished
Direction     inbound | outbound
NumberA       внешний номер
NumberB       внутренний номер реально ответившего оператора
Duration      секунды, обязательно для finished
CallRecordUrl при наличии
```

Пропущенные/неотвеченные звонки в минимальном контракте пока не описаны.

---

## 13. Реальные `conversations_event` и CDR — подтверждённый mapping

### 13.1 Прямой 1001 -> 1002

На `alerting` две leg:
- 1001: `direction=out`, `digits=1001`, `remote_digits=1002`;
- 1002: `direction=in`, `digits=1002`, `remote_digits=1001`.

Подтверждено:
- `id` разный у leg;
- `call_id` общий и стабилен;
- `call_ref` общий и стабилен на прямом двухстороннем звонке;
- `workitem_id=null`.

При реальном ответе обе leg переходят `talking`, `has_answer_time=true`. После отбоя — `released`, `has_answer_time=true`. Без ответа — `released`, `has_answer_time=false`.

### 13.2 Live queue test 1001 -> 112 -> Abai_112 -> Operator2, 2026-09-03 16:21–16:22

Это первый подтверждённый реальный проход через боевой маршрут 112.

Caller/IVR leg:

```text
alerting:
  direction=out
  digits=1001
  remote_digits=112
  call_id=<shared logical call id>
  call_ref=<caller/IVR ref A>
  workitem_id=null

talking at 16:21:59:
  has_answer_time=true
  answer_time=16:21:59
```

Operator leg после распределения на Operator2:

```text
alerting:
  direction=in
  digits=1002
  remote_digits=1001
  call_id=<THE SAME shared logical call id>
  call_ref=<operator leg ref B, DIFFERENT from A>
  workitem_id=null

talking at 16:22:04:
  display_name=Operator 2
  has_answer_time=true
  answer_time=16:22:04
```

Обе leg затем пришли `released` с тем же общим `call_id` и со своими соответствующими `call_ref`/`answer_time`.

### 13.3 CDR field semantics — подтверждено по прямым звонкам

CSV columns включают `T_ECD`, `T_DBA`, `CONN_ID`.

Сопоставление с live listener дало:

- `CONN_ID = call_ref` для прямого вызова. Это подтверждено несколькими звонками: значения CDR `CONN_ID` точно совпадают с `call_ref` из `conversations_event`.
- `T_DBA` соответствует задержке до ответа (пример: start 15:43:40.922, live answer 15:43:50, CDR `T_DBA=9`; другой вызов start 15:55:39.382, answer 15:55:45, `T_DBA=5`).
- `T_ECD` соответствует длительности разговора после ответа: пример с лимитом 60 секунд дал `T_ECD=60`, короткий отвеченный вызов дал `T_ECD=2`.
- Неотвеченный вызов имеет `T_ECD=0`, `T_DBA=0`.
- Старый вызов `1001 -> 112` до создания маршрута зафиксирован как `unassignedNumber`, что дополнительно подтверждает, что новый live 112 тест произошёл уже после активации правила.

Для queue-вызова 16:21–16:22 CDR ещё не выгружен: он должен появиться в `cdr_dp_abai_default_20260903_17_00_00_p.csv`. Именно этот файл нужен, чтобы понять, сколько CDR-records создаётся на queue-call и какой из двух `call_ref`/`CONN_ID` несёт операторский `T_ECD`.

### КЛЮЧЕВЫЕ ВЫВОДЫ из queue test

1. **`call_id` подтверждён как лучший общий логический Id звонка через IVR/queue.** Он одинаков у caller->112 leg и у реально ответившей операторской leg.
2. **`call_ref` НЕ является общим Id queue-звонка.** Через очередь caller/IVR leg и operator leg имеют разные `call_ref`. Для записи разговора нужно сохранять все call_ref данного call_id и отдельно определить, какой ref соответствует нужной записи.
3. **`workitem_id` в Call API conversation events равен `null` даже при реальном queue-вызове.** Не строить production correlation на обязательном наличии `workitem_id`.
4. **Нельзя преобразовывать любой `talking` в CRM `answered`.** Caller leg `1001 -> 112` перешла в `talking` в 16:21:59, когда вызов принял IVR/queue, а Operator2 реально ответил только в 16:22:04. Наивное правило дало бы ложный `answered` на 5 секунд раньше.
5. Для входящего queue-вызова CRM `answered` должен формироваться по **реально ответившей операторской leg**, то есть leg внутреннего агента/номера, которая перешла в `talking` после распределения. В текущем тесте это `digits=1002`, `direction=in`, `display_name=Operator 2`.
6. Для текущего внутреннего теста логический mapping:
   - `Id = call_id`;
   - `NumberA = 1001` (тестовый вызывающий; при реальном внешнем 112 здесь должен быть внешний CLI);
   - `NumberB = 1002` (реально ответивший оператор);
   - `answered` = операторская leg `talking` в 16:22:04;
   - `finished` = завершение после уже зафиксированного operator answered для этого `call_id`;
   - `CallRecordUrl = null` на первом этапе.
7. `conversations_event` не содержит `duration`/`release_time`; для точного `Duration` CDR `T_ECD` является главным кандидатом и уже подтверждён на прямых звонках. Для queue-call осталось выбрать правильный CDR record через `CONN_ID/call_ref`.

### Production mapping — текущая рабочая версия

Для входящего 112:

```text
logical Id = call_id

ignore caller/IVR talking as CRM answered

operator leg talking + has_answer_time=true
    -> CRM Status=answered
    -> NumberB = digits фактически ответившего внутреннего оператора

после того как answered уже зафиксирован для call_id:
operator/call logical release
    -> CRM Status=finished
    -> Duration брать из CDR T_ECD правильной operator record

released без ранее подтверждённого operator answered
    -> не отправлять answered/finished по минимальному контракту
```

Для outbound логику нужно проверить отдельно на реальном вызове через требуемый бизнес-сценарий.

---

## 14. Текущая точка / СЛЕДУЮЩИЕ ДЕЙСТВИЯ

**Не возвращаться** к лицензии, VRRP, Mnesia, test 2000, созданию агентов, освобождению Test Agent1/2, forceLogout, `#160`, установке ecss-cc-ui, созданию `Abai_112_ivr`, созданию маршрута `112` или повторению direct 1001->1002 — всё подтверждено.

Продолжать отсюда:

1. **Сейчас:** дождаться/получить `cdr_dp_abai_default_20260903_17_00_00_p.csv`, который должен содержать live queue-вызов `1001 -> 112 -> Operator2` 16:21–16:22.
2. В этом CDR сопоставить `CONN_ID` с обоими `call_ref` live listener и определить, какая record содержит операторский разговор и `T_ECD`.
3. После этого окончательно зафиксировать алгоритм `Duration` и `finished` для queue-call.
4. Отдельно проверить поведение `lock_if_no_answer` и `lock_if_reject` до боевого multicall.
5. Полноценный multicall двух свободных операторов провести с внешним/третьим вызывающим; текущий `1001 -> 112` доказал queue routing и operator selection, но не одновременный ring двух свободных операторов, потому что 1001 был вызывающим.
6. На внешнем/третьем вызове подтвердить, что `NumberA` сохраняет реальный внешний CLI и `NumberB` становится фактически ответившим агентом.
7. Проверить node-local поведение CC Web session при отказе одного `ecss-cc-ui-api`.
8. Затем реализовать `/opt/ecss-integration-api` на обоих узлах и HA endpoint :443.
9. После приёмки ротировать integration API key и agent PINs.

---

## 15. Полезные команды

```bash
ssh admin@localhost -p 8023
```

```text
/domain/dp_abai/routing/show default_routing
/domain/dp_abai/ivr/script/show --id Abai_112_ivr
/domain/dp_abai/cc/group/cache-info Abai_112_cc
/domain/dp_abai/cc/queue/Abai_112/info
```

CDR path:

```text
/var/lib/ecss/ftp/domain/dp_abai/default/csv
```

---

## 16. Стандарт оформления Google Sheets — ЗАКРЕПЛЁН

Основная рабочая Google-таблица проекта:

```text
ECSS10 ДП Абай — полный проект 2026-08-28
Google Sheet ID: 1FsqGYKz7ZZPqtSTsG0jqfN28pCqRp92gvZW8Ma7dTc4
```

2026-09-03 единый профессиональный стандарт оформления применён ко всем 14 вкладкам и является обязательным для всех будущих изменений таблицы.

**Стандарт, от которого не отходить без прямого запроса пользователя:**

- Скрывать стандартную сетку Google Sheets; использовать аккуратные тонкие светло-сине-серые границы только в рабочей области.
- Закреплять верхние строки с названием/заголовками, чтобы структура не терялась при прокрутке.
- Главный заголовок вкладки: тёмно-синий `#1F4E78`, белый Arial 14 bold.
- Заголовки разделов: средний синий `#2F75B5`, белый Arial 11 bold.
- Заголовки таблиц: светло-голубой `#D9EAF7`, тёмно-синий текст, bold, выравнивание по центру.
- Основной текст: Arial 10, белый фон, перенос строк, вертикальное выравнивание по центру.
- Статусы: центрировать и выделять bold; использовать спокойную семантическую заливку/условное форматирование. Не делать пёструю таблицу.
- Команды и shell/CoCon строки: моноширинный шрифт (`Roboto Mono`), лёгкая серо-голубая подложка.
- Ширины колонок подбирать по смыслу: длинные описания получают широкие колонки, короткие ID/статусы — компактные. Высоту строк подгонять автоматически.
- Не оставлять сломанные, пустые или декоративные диаграммы. Диаграмма допускается только если она корректна, информативна и улучшает чтение.
- Все новые вкладки и все будущие обновления существующих вкладок оформлять в этом же стиле.
- Визуальная таблица не заменяет источник истины: при расхождении фактов приоритет всегда у `PROJECT_STATE.md`.

В рамках фиксации стандарта:
- приведены к единому стилю все вкладки (`Сводка`, `Статус проекта`, `Архитектура`, `Сеть и серверы`, `ECSS cluster`, `Лицензирование`, `SIP и абоненты`, `Call API & HA`, `Gateway HA`, `Порты`, `Риски и решения`, `Команды`, `История`, `Источники`);
- на `Сводка` удалена сломанная диаграмма, вызывавшая ошибку числовых данных;
- исправлена строка `CRM answered/finished`;
- для `Команды` закреплено моноширинное оформление команд.

---

## 17. Security

Никогда не сохранять/не повторять:
- ECSS integration API key;
- JWT/CC token;
- Linux/CoCon/WebConf passwords;
- Rutoken PIN;
- agent passwords/PIN;
- PostgreSQL password;
- private keys/Erlang cookie;
- `/etc/ecss/ssl/*.key`.

Если секрет попал в чат/скрин — запланировать ротацию.
