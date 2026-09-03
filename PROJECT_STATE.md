# ECSS-10 ДП Абай — PROJECT_STATE

**Canonical source of truth для проекта**  
**Последнее обновление:** 2026-09-03 16:05+05  
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
- SIP trunk оператора пока не завершён: нужны реальные параметры оператора.

---

## 6. Call API :8089 — выполнено

- ecss1 `.70:8089`, ecss2 `.80:8089`; SSW `.70/.80:8086`.
- `integration.register`, JWT, WS, heartbeat, `call.make`, conversation events и failover `.70 → .80 → .70` проверены.
- Integration client `dp_abai_test`, service; API key/JWT не хранить, после приёмки ротировать.
- JWT/auth node-local/in-memory.
- На ecss2 временный listener `/tmp/ecss-events.js` успешно слушает реальные `conversations_event`; в продукт его не переносить как есть.

---

## 7. Текущий доступ

Сейчас нет физического доступа к SIP-телефонам. Доступны Web UI, SSH, CoCon и серверные web-интерфейсы. Не делать handset feature-code обязательным шагом до onsite.

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

## 9. Боевая 112 — очередь/агенты/IVR

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

2026-09-03 15:49 одновременно подтверждено:

```text
1001 Operator1 available Phone=1001 idle
1002 Operator2 available Phone=1002 idle
```

### Routing до 16:05

Единственный context: `default_routing`.

Текущее содержимое:

```text
rule test:
  CDPN 2000 -> IVR script 06fbb268b12127f9

rule local_calls:
  final=true
  CDPN % -> local
```

Отдельного правила для `112` пока **нет**.

### Боевой IVR — создан и проверен 2026-09-03 16:05

Создан отдельный IVR:

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

Импорт успешен:

```text
Script successfully imported with id <<"Abai_112_ivr">>.
```

`/domain/dp_abai/ivr/script/show --id Abai_112_ivr` подтвердил правильную привязку к `queue_id=Abai_112`.

**Важно:** IVR готов, но маршрут `CDPN=112 -> Abai_112_ivr` ещё не добавлен.

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

## 13. Реальные `conversations_event` — ключевой результат

### Прямой 1001 -> 1002

На `alerting` две leg:
- 1001: `direction=out`, `digits=1001`, `remote_digits=1002`;
- 1002: `direction=in`, `digits=1002`, `remote_digits=1001`.

Подтверждено:
- `id` разный у leg;
- `call_id` общий и стабилен;
- `call_ref` общий и стабилен;
- `workitem_id=null` для прямого вызова.

При ответе:

```text
status: talking
has_answer_time: true
answer_time: ...
```

После отбоя:

```text
status: released
has_answer_time: true
answer_time: тот же
```

Без ответа `released` имеет `has_answer_time=false`.

Рабочий mapping для прямого звонка:

```text
talking + has_answer_time=true -> answered
released + has_answer_time=true -> finished
released + has_answer_time=false -> не отправлять answered/finished
```

`call_id` — главный кандидат на внешний `Id`, но окончательно утверждать после queue/multicall 112.

`conversations_event` не даёт `duration`; realtime можно считать от `answer_time` до `released`, затем сверить с CDR.

Внутренняя SSW-команда `get_call_record(call_ref)` есть, но публичный controller/DTO Call API не найден. На первом этапе `CallRecordUrl=null`; `call_ref` сохранять внутренне.

---

## 14. Текущая точка / СЛЕДУЮЩИЕ ДЕЙСТВИЯ

**Не возвращаться** к лицензии, VRRP, Mnesia, test 2000, созданию агентов, освобождению Test Agent1/2, forceLogout, `#160`, установке ecss-cc-ui или повторным полным lifecycle Agent1001/1002.

Продолжать отсюда:

1. **Сейчас:** перед изменением `default_routing` сделать экспорт/резервную копию существующего контекста.
2. После подтверждения backup — добавить отдельное правило `CDPN=112 -> IVR Abai_112_ivr` **перед** финальным `local_calls` (`% -> local`). Тестовый `2000` не менять.
3. Проверить `/domain/dp_abai/routing/show default_routing` после изменения.
4. Только затем тестировать `112 -> Abai_112` на live listener и снять `workitem_id`, queue legs, общий `call_id` и фактический `NumberB`.
5. Полноценный multicall двух свободных операторов лучше проверять внешним/третьим вызывающим. Пока физического доступа нет, допустим ограниченный тест `1001 -> 112` для изучения queue/workitem, но он не доказывает multicall двух свободных операторов.
6. Сверить realtime Duration с CDR.
7. Решить/проверить `lock_if_no_answer` и `lock_if_reject` перед боем.
8. Проверить node-local поведение CC Web session при отказе одного `ecss-cc-ui-api`.
9. Когда будет внешний/физический вызов — полный E2E 112: inbound → multicall → answer → talking → end → RTP/CDR.
10. Затем реализовать `/opt/ecss-integration-api` на обоих узлах и HA endpoint :443.
11. После приёмки ротировать integration API key и agent PINs.

---

## 15. Полезные команды

```bash
ssh admin@localhost -p 8023
```

```text
/domain/dp_abai/routing/list
/domain/dp_abai/routing/show default_routing
/domain/dp_abai/routing/export ecss1 default_routing
/domain/dp_abai/ivr/script/list
/domain/dp_abai/ivr/script/show --id 06fbb268b12127f9
/domain/dp_abai/ivr/script/show --id Abai_112_ivr
/domain/dp_abai/cc/group/cache-info Abai_112_cc
/domain/dp_abai/cc/queue/Abai_112/info
```

---

## 16. Security

Никогда не сохранять/не повторять:
- ECSS integration API key;
- JWT/CC token;
- Linux/CoCon/WebConf passwords;
- Rutoken PIN;
- agent passwords/PIN;
- PostgreSQL password;
- private keys/Erlang cookie;
- `/etc/ecss/ssl/*.key`.
