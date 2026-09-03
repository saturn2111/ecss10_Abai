# ECSS-10 ДП Абай — PROJECT_STATE

**Canonical source of truth для проекта**  
**Последнее обновление:** 2026-09-03 15:45+05  
**ECSS:** 3.18.0.271

> Перед продолжением проекта читать этот файл и продолжать с раздела **«Текущая точка / СЛЕДУЮЩИЕ ДЕЙСТВИЯ»**. Не повторять уже подтверждённые этапы. Новые фактические данные пользователя имеют приоритет. Работать: одна операция → проверка → следующий шаг. Секреты не хранить и не повторять.

---

## 1. Цель и архитектура

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

Не возвращаться к старому DEFAULT/No passport.

---

## 5. Абоненты / CDR / trunk

- SIP1001 VP-30P и SIP1002 VP-17P зарегистрированы исторически.
- CDR CSV: period3600, `/var/lib/ecss/ftp/domain/dp_abai/default/csv`, файлы создаются.
- SIP trunk оператора пока не завершён: нужны реальные параметры оператора.

---

## 6. Call API :8089 — выполнено

Package `/usr/share/ecss/ecss-call-api`, service `ecss-call-api`.

- ecss1 `.70:8089`, ecss2 `.80:8089`; SSW `.70/.80:8086`.
- `integration.register`, JWT, WS, heartbeat, `call.make`, conversation events и failover `.70 → .80 → .70` проверены.
- Integration client `dp_abai_test`, service; API key/JWT не хранить, после приёмки ротировать.
- JWT/auth node-local/in-memory.

### Live listener 2026-09-03

На ecss2 создан временный listener `/tmp/ecss-events.js`. Он успешно зарегистрировался и открыл WS на `.80:8089`, не печатая API key/JWT. Listener временный; в продукт не переносить как есть.

---

## 7. Ограничение текущего доступа

Сейчас нет физического доступа к SIP-телефонам. Доступны Web UI, SSH, CoCon и серверные web-интерфейсы. Не делать handset feature-code обязательным шагом до onsite.

---

## 8. Call-center — тест 2000 уже пройден

```text
2000 -> queue test -> group test_cc -> SIP1001 + SIP1002
```

Distribution `multicall`; звонок на 2000 ранее вызывал оба SIP. Не повторять и пока не удалять test/test_cc.

Старые Test Agent1/2 освобождены через `only_one_session=true` + штатный Web login/logout; оба `stopped`. Поле Phone у stopped не является активной блокировкой.

---

## 9. Боевая 112

Группа `Abai_112_cc`:
- Agent1001 = Operator1 / Phone1001;
- Agent1002 = Operator2 / Phone1002.

Queue `Abai_112`, description `ДП Абай 112`:
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

Оба боевых агента полностью проверены через штатный Web UI: Login → Available → AuxWork → Available → Logout. Не повторять этот lifecycle без новой причины.

Web login через ecss2 реально меняет общий CC runtime; ранее подтверждено `1001 available Phone=1001`.

---

## 10. ecss-cc-ui 18.0.34 — оба узла готовы

### ecss1
- `ecss-cc-ui-api` active;
- `ecss-cc-ui` active;
- `8090` nginx/openresty, `8091` node;
- Web UI `.70:8090` работает.

### ecss2
- package `ecss-cc-ui 18.0.34` установлен;
- `ecss-cc-ui-api` active/enabled;
- `ecss-cc-ui` active/enabled;
- `0.0.0.0:8090` nginx/openresty;
- `0.0.0.0:8091` node;
- config: ECSS `localhost:8086`, SQL `localhost:5439`;
- Web UI `.80:8090` работает, login подтверждён.

---

## 11. Внутренний CC API — подтверждено

Services:
```text
CRM        = call
WEB_CC     = cc/common
CC_AGENT   = cc/arm
CC_PUBSUB  = cc/pubsub
CONFERENCE = teleconference
```

Операции подтверждены из кода: `login_agent`, `logout_agent`, `make_available`, `auxwork`, `agent_list`, `agents_list`, `group_list`, `all_queues`, `operator_call_history`, realtime `agents_info_event`.

`operator/forceLogout` обычному профилю запрещён (`force_logout=false`); не повторять. Попытка `call/makeCall #160` не меняла CC runtime; не использовать как logout.

---

## 12. Контракт внешней интеграции от разработчиков

Минимально нужны два события одного состоявшегося звонка:

```text
answered
finished
```

Оба с одинаковым уникальным `Id`.

```text
Id            string
Status        answered | finished
Direction     inbound | outbound
NumberA       внешний номер
NumberB       внутренний номер реально ответившего/обслужившего оператора
Duration      секунды, обязательно для finished
CallRecordUrl при наличии
```

Пропущенные/неотвеченные звонки в минимальном контракте пока не описаны.

---

## 13. КЛЮЧЕВОЙ РЕЗУЛЬТАТ: реальные `conversations_event`

### Прямой вызов 1001 -> 1002, без ответа

На `alerting` ECSS прислал две leg:

- leg 1001: `direction=out`, `digits=1001`, `remote_digits=1002`;
- leg 1002: `direction=in`, `digits=1002`, `remote_digits=1001`.

Подтверждено:
- `id` разный у двух leg;
- `call_id` одинаковый у обеих leg;
- `call_ref` одинаковый у обеих leg;
- `has_answer_time=false`;
- `workitem_id=null`.

При `released` без ответа те же `id`, `call_id`, `call_ref`; `has_answer_time=false`.

**Вывод:** неотвеченный `released` нельзя превращать в внешний `finished`, потому что разговора не было.

### Прямой вызов 1001 -> 1002, с ответом

На фактическом ответе обе leg перешли в:

```text
status: talking
has_answer_time: true
answer_time: 2026/09/03 15:43:50
```

`call_id` и `call_ref` одинаковы на обеих leg и стабильны.

После отбоя обе leg пришли как:

```text
status: released
has_answer_time: true
answer_time: 2026/09/03 15:43:50
```

При этом в `released` **нет** `duration`, `talk_time` или `release_time`.

### Техническое значение полей — подтверждено для прямого вызова

```text
id       = ID конкретной conversation/leg; различается по сторонам
call_id  = общий ID всего двухстороннего звонка; стабилен alerting -> talking -> released
call_ref = общий reference звонка; стабилен; используется внутренней командой get_call_record
```

Рабочий mapping для прямого вызова:

```text
ECSS talking + has_answer_time=true
    -> внешний Status=answered

ECSS released + has_answer_time=true
    -> внешний Status=finished

ECSS released + has_answer_time=false
    -> НЕ отправлять answered/finished по текущему минимальному контракту
```

`call_id` — **главный кандидат** на внешний `Id`, но окончательно утверждать только после проверки queue/multicall 112, где могут появиться дополнительные legs/workitems.

### Duration

`conversations_event` сам не даёт длительность. Для realtime-версии можно хранить момент первого `talking/answer_time` и момент получения `released`; это нужно затем сверить с CDR. Для финального production mapping предпочтительно использовать/сверять точный talk duration по CDR, если задержка событий окажется заметной.

### CallRecordUrl

В коде есть внутренняя SSW-команда `get_call_record(call_ref)`, но в установленном Call API не найден публичный controller/DTO для неё. На первом этапе `CallRecordUrl=null` допустим по контракту разработчиков. `call_ref` сохранять внутренне как ключ для дальнейшего исследования записи.

---

## 14. Текущая точка / СЛЕДУЮЩИЕ ДЕЙСТВИЯ

**Не возвращаться** к лицензии, VRRP, Mnesia, test 2000, созданию агентов, освобождению Test Agent1/2, forceLogout, `#160`, установке ecss-cc-ui или повторным полным lifecycle Agent1001/1002 — всё подтверждено.

Продолжать отсюда:

1. **Сейчас:** проверить именно call-center путь `112 -> Abai_112` на живом listener и снять `conversations_event`/`workitem_id` для queue-вызова. Цель — понять, сохраняется ли один общий `call_id` через очередь/распределение и как однозначно получить реально ответивший `NumberB`.
2. Перед полноценным multicall желательно иметь вызывающего, который не является одним из операторов 1001/1002. Пока физического доступа нет, допустим контролируемый тест `1001 -> 112` при available Operator2 для изучения queue/workitem, но он не доказывает multicall двух свободных операторов.
3. На queue-тесте проверить `workitem_id`, queue legs, победившего оператора и переход `alerting -> talking -> released`.
4. Сверить вычисленную realtime Duration с CDR после состоявшегося разговора.
5. Отдельно решить/проверить `lock_if_no_answer` и `lock_if_reject` перед боевым multicall.
6. Затем проверить node-local поведение CC Web session при отказе одного `ecss-cc-ui-api`.
7. Когда будет физический/внешний вызывающий — полный E2E 112: inbound → multicall двух available операторов → answer → talking → end → RTP/CDR.
8. Затем реализовать `/opt/ecss-integration-api` на обоих узлах и HA endpoint :443.
9. После приёмки ротировать integration API key и agent PINs.

---

## 15. Полезные команды

```bash
ssh admin@localhost -p 8023
```

```text
/domain/dp_abai/cc/group/cache-info Abai_112_cc
/domain/dp_abai/cc/agent/info 1001
/domain/dp_abai/cc/agent/info 1002
/domain/dp_abai/cc/queue/Abai_112/info
```

```bash
systemctl status ecss-call-api
systemctl status ecss-cc-ui-api
systemctl status ecss-cc-ui
ss -lnt
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

Если секрет попал в чат/скрин — запланировать ротацию.
