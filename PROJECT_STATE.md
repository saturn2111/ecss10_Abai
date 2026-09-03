# ECSS-10 ДП Абай — PROJECT STATE / шпаргалка

**Canonical source of truth для проекта**  
**Последнее обновление:** 2026-09-03  
**ECSS:** 3.18.0.271  

> ## Инструкция для любого нового чата ChatGPT
>
> Перед продолжением проекта сначала прочитать этот файл и продолжать **с раздела «Текущая точка / Следующие действия»**.
>
> Не заставлять пользователя повторно проходить уже подтверждённые этапы. Новые фактические данные пользователя имеют приоритет над этой памяткой; после существенного изменения файл нужно обновить.
>
> Пользователь предпочитает пошаговую работу: одна понятная операция → проверка результата → следующий шаг. Команды давать полностью, без `...`. Не раскрывать/не хранить секреты.

---

## 1. Цель проекта

Двухузловая отказоустойчивая ECSS-10 для ДП области Абай с последующей интеграцией внешней системы через API.

Цели:

- до ~1000 абонентов;
- HA ECSS на `ecss1`/`ecss2`;
- SIP/media с VRRP;
- коммерческая лицензия через 2 Rutoken;
- Call API на обоих ECSS-узлах;
- штатный Call-center ECSS;
- боевая очередь/группа 112;
- внешний API для разработчиков: группы/очереди, операторы, статусы, кто звонил/кто ответил, времена, длительности, история, управление состоянием операторов;
- integration service/API разворачивать **не на отдельных Gateway VM, а прямо на ecss1 и ecss2**.

---

## 2. Архитектурное решение по API

Отдельные `ecss-gateway01/ecss-gateway02` больше **не являются целевой архитектурой**.

Интеграционный сервис размещать непосредственно на:

- `ecss1` — `192.168.190.70`
- `ecss2` — `192.168.190.80`

Целевая схема:

```text
External CRM / система разработчиков
              |
          HTTPS :443
              |
      единый API endpoint / VIP
              |
       +------+------+
       |             |
     ecss1         ecss2
       |             |
 integration     integration
   service         service
       |             |
  +----+----+   +----+----+
  |         |   |         |
Call API  SSW  Call API  SSW
 :8089   :8086  :8089   :8086
```

Свой сервис не встраивать в штатный пакет `/usr/share/ecss/ecss-call-api`; размещать отдельно, например `/opt/ecss-integration-api`, отдельный systemd unit.

---

## 3. Proxmox / сеть

Два независимых Proxmox-хоста, **не PVE cluster**.

### srv-prmx-1

- management `192.168.190.2/26`
- gateway `192.168.190.1`
- `vmbr0`
- `bond0`, 802.3ad LACP, nic0+nic1
- VLAN-aware
- PVE 9.2.2
- kernel 7.0.2-6-pve

Последняя фиксация storage:

- `local` ~98.5 GB, used ~17.3 GB
- `local-lvm` thin pool ~335.55 GB, Data% ~12.14%
- NVMe ~447.1 GB
- VM101 ecss1 disk 280 GB
- VM103 aup1 фактический thin disk 60 GB

### srv-prmx-2

- management `192.168.190.3/26`
- gateway `192.168.190.1`
- аналогичная LACP/VLAN схема

Свежая подробная статистика storage `srv-prmx-2` ещё не зафиксирована.

---

## 4. ECSS VM

### ecss1

- VMID 101
- Ubuntu Server 22.04.5
- management `192.168.190.70/26`
- management IF `enp6s18`
- VM gateway `192.168.190.65`
- voice `192.168.191.2/24`
- voice IF `enp6s19`
- 8 vCPU / 32 GB RAM / 280 GB

### ecss2

- VMID 102
- Ubuntu Server 22.04.5
- management `192.168.190.80/26`
- voice `192.168.191.3/24`
- 8 vCPU / 32 GB RAM / 280 GB

Общее:

- Linux user `darth_vader`
- timezone `Asia/Almaty`
- swap disabled
- `/etc/hosts` настроен для `ecss1`/`ecss2`

---

## 5. ECSS cluster — уже выполнено

Cluster ID: **`ecss1`**. Не менять.

Инициализация/объединение:

```text
/system/clusters/set [ecss1, ecss2]
```

Парные компоненты:

- core1
- ds1
- md1
- mycelium1
- sip1

Ранее были Mnesia/split-brain проблемы; их устраняли и кластер был доведён до синхронизированного состояния. Без необходимости не повторять эти этапы и не удалять Mnesia каталоги вручную.

CoCon:

```bash
ssh admin@localhost -p 8023
```

PostgreSQL BDR:

- package `ecss-postgres-bdr-ssw 18.0.0+ssw`
- port 5439
- replication проверялась и работала

Gluster:

- volume `ecss_volume`
- ecss1 brick `192.168.190.70:/var/lib/ecss/glusterfs`
- ecss2 brick `192.168.190.80:/var/lib/ecss/glusterfs`
- replica 2
- heal проверялся

RestFS:

- `/var/lib/ecss/restfs`
- port 9990
- fuse.glusterfs

PostgreSQL backup:

- `ssw_dump_postgres.timer`
- daily около 00:00
- manual dump тестировался

---

## 6. Media Server / SIP

Media Server `3.18.0.7`.

### msr.ecss1

- `192.168.191.2`
- SIP 5040 TCP/UDP
- MCC 5700 TCP

### msr.ecss2

- `192.168.191.3`
- SIP 5040 TCP/UDP
- MCC 5700 TCP

Registrar:

- core1@ecss1 → `.191.2:5000`
- core1@ecss2 → `.191.3:5000`

Core↔MSR connectivity подтверждена.

---

## 7. SIP VRRP — уже выполнено и протестировано

Domain `dp_abai`, IP-set `sip_main`.

### VIP1

- `192.168.191.4/24`
- VRID 31
- normal MASTER ecss1 priority 100
- BACKUP ecss2 priority 50

### VIP2

- `192.168.191.5/24`
- VRID 32
- normal MASTER ecss2 priority 100
- BACKUP ecss1 priority 50

keepalived на `enp6s19`, unicast peers `.191.2`/`.191.3`.

Failover реально проверялся остановкой `ecss-pa-sip`: VIP переходил на второй узел и возвращался после восстановления.

SIP health check:

- `127.0.0.1:65535`
- `/usr/bin/ecss_pa_sip_port`
- тест от nobody → EXIT=0

`sip_main`: `.191.4:5060` и `.191.5:5060`, TCP+UDP.

---

## 8. Лицензирование — коммерческая лицензия активна

Не возвращаться к старому этапу DEFAULT/No passport.

Текущее зафиксированное состояние:

- ECSS TPM License / ID 1
- commercial
- SSW ID `ECSS0000400`
- организация Департамент полиции области Абай
- expiry `31.07.2050`

License Manager:

- `192.168.190.70:4321`
- `192.168.190.80:4321`

Оба были Alive; failover лицензии проверялся.

`ecss-license-provider 1.0.6` активен на обоих.

Rutoken:

- по одному токену на каждом физическом сервере
- USB `0a89:0030`
- PKCS#11 `librtpkcs11ecp.so`

Известный nuisance: passive DS мог писать `Licence management service not available`, хотя активный DS и License Providers работали; диагностика отправлялась ELTEX. Топологию лицензирования без причины не менять.

---

## 9. Домен / абоненты / CDR

Domain `dp_abai`.

Ранее подтверждалось:

- 1001 зарегистрирован, VP-30P, contact ранее `192.168.191.246`
- 1002 зарегистрирован, VP-17P, contact ранее `192.168.191.245`
- 111 в старом снимке был inactive

90 supplementary services устанавливались; CLIP/CNIP проверялись.

CDR:

- period 3600s
- `/var/lib/ecss/ftp/domain/dp_abai/default/csv`
- файлы реально создавались

SIP trunk к оператору пока не считается завершённым: нужны IP/port/auth/DID/codecs/From/PAI/формат номера.

---

## 10. Call API — уже работает на двух узлах

Package:

```text
/usr/share/ecss/ecss-call-api
```

Service:

```text
ecss-call-api
```

- ecss1 HTTPS/WSS `192.168.190.70:8089`, SSW `192.168.190.70:8086`
- ecss2 HTTPS/WSS `192.168.190.80:8089`, SSW `192.168.190.80:8086`

Подтверждено:

- `integration.register`
- JWT выдаётся
- WS authorization
- connection_state open
- heartbeat ping/pong
- `call.make`
- conversation/call leg events
- alerting
- released

Integration client:

- `dp_abai_test`
- type service
- allowed numbers ранее 1001–1005

Важно:

- API key/JWT не хранить здесь;
- API key ранее попадал в чат/логи → после финальной интеграции ротировать;
- JWT/state node-local: токен `.70` не считать токеном `.80`;
- после failover новый активный сервис должен делать новый `integration.register` и WS.

Call API failover проверен:

- baseline `.70`
- stop `ecss-call-api` на ecss1 → register/WS/pong через `.80`
- после восстановления `.70` снова доступен

Рекомендуется sticky active endpoint, без немедленного failback-флапа.

Физический answer/talking/RTP через Call API пока не закрыт, потому что пользователь часто без физического доступа к телефонам.

---

## 11. Текущее ограничение доступа пользователя

**На текущем этапе пользователь НЕ имеет физического доступа к SIP-телефонам.**

Доступны:

- ECSS Web UI
- SSH
- CoCon
- серверные веб-морды

Поэтому не предлагать обязательный следующий шаг «подойти к телефону и набрать feature code», пока пользователь явно не скажет, что onsite.

Следующий этап должен использовать программный способ login/logout/AuxWork/Available через ECSS API/CoCon/SSW.

---

## 12. Call-center — тестовый этап уже пройден

Ранее с пользователем был создан и проверен тест:

- групповой номер `2000`
- очередь `test`
- группа `test_cc`
- Agent 1 → Test 1001 → SIP 1001
- Agent 2 → Test 1002 → SIP 1002
- distribution `multicall`
- звонок на 2000 вызывал SIP 1001 и 1002

**Не повторять этот этап.**

Тестовую схему пока оставить как rollback/reference до полной приёмки 112.

---

## 13. Боевая 112 — ТЕКУЩЕЕ СОСТОЯНИЕ

Создан боевой каркас.

### Группа агентов

```text
Abai_112_cc
```

Содержит:

- Agent ID `1001` — `Operator 1`, description `sip 1001`
- Agent ID `1002` — `Operator 2`, description `sip 1002`

Agent ID совпадает с SIP номером для удобного сопоставления в API.

Подтверждено через CoCon:

```text
/domain/dp_abai/cc/agent/list
```

`/domain/dp_abai/cc/group/info`:

```text
Abai_112_cc -> 1001, 1002
```

`agent/where`:

```text
/domain/dp_abai/cc/agent/where 1001 -> Abai_112
/domain/dp_abai/cc/agent/where 1002 -> Abai_112
```

### Очередь

Queue ID:

```text
Abai_112
```

Description: `ДП Абай 112`

Подтверждённые параметры `/domain/dp_abai/cc/queue/Abai_112/info`:

- agents `agent:1001`, `agent:1002`
- distribution_mode `multicall`
- max_wait_time `120`
- max_distribution_attempts `3`
- max_distribution_duration `10`
- queue_length `20`
- callback_cooldown_timeout `300`
- skill_based_distribution `false`
- remember_choice `none`
- ringback_mode `once`
- decline_if_no_operators `false`
- lock_if_no_answer `true`
- lock_if_reject `true`
- serial_lock_enabled `true`

Перед первым реальным multicall-тестом отдельно решить/проверить `lock_if_no_answer` и `lock_if_reject`; ранее рекомендовано временно выключить их, но это ещё не подтверждено как выполненное.

### Runtime агентов сейчас

`/domain/dp_abai/cc/group/cache-info Abai_112_cc`:

```text
1001  Status=stopped  Phone number=-  Activity=idle
1002  Status=stopped  Phone number=-  Activity=idle
```

То есть агенты созданы, состоят в группе и очереди, но **ещё не авторизованы в runtime Call-center**.

Это текущая точка продолжения.

---

## 14. Feature codes Call-center

Команда:

```text
/domain/dp_abai/ss/feature-codes/info cc_agent
```

Показала реальные коды:

- login `*160*AGENT_ID*PASSWORD#`
- logout `#160`
- complete `#161`
- enter_auxwork `#162`
- make_available `#163`
- supervise `*164...`
- call_agent `*165*AGENT_ID#`
- supervise2 `*166...`
- set_default_supervise_mode `*167...`

Agent PIN/password не хранить и не повторять. Пароли попадали на скриншоты → перед боевым использованием заменить/ротировать.

Из-за отсутствия физического доступа к телефонам следующий этап — программный login/status, а не набор feature code.

---

## 15. Что уже найдено по внутреннему Contact Center API

В установленном `/usr/share/ecss/ecss-call-api` найдены сервисы:

```text
CRM       = call
WEB_CC    = cc/common
CC_AGENT  = cc/arm
CC_PUBSUB = cc/pubsub
```

Найдены операции:

- `login_agent`
- `logout_agent`
- `make_available`
- `auxwork`
- `agent_list`
- `agents_list`
- `group_list`
- `all_queues`
- `operator_call_history`
- `block_operator`
- `unblock_operator`
- `force_logout`
- `add_to_queue`
- `remove_from_queue`
- `move_conversation_to_queue`
- `remove_conversation_from_queue`
- `make_agent_call`
- realtime `agents_info_event`

Найдены статусы/смыслы `busy`, `dinner`, `handle_call`, `callback`, `rest`, `locality_transfer`.

Транспорт SSW по исходникам:

- HTTP POST + XML
- cookie/token auth
- WebSocket для событий
- service paths `cc/arm`, `cc/common`, `cc/pubsub`

Штатный WebConf использует команды:

- agent_list/info/declare/set/remove
- queue_list/info/declare/set/remove
- auxwork profiles/reasons

CoCon дерево подтверждено:

```text
/domain/dp_abai/cc/
  agent/
  conference/
  group/
  properties/
  queue/
  restrictions/
```

Agent tree включает:

```text
auxwork/
clean
declare
info
list
profile/
realtime/
remove
set
where
```

Queue tree включает:

```text
Abai_112/
acw/
declare
info
is-member
list
realtime/
remove
test/
```

Queue realtime содержит как минимум:

- callback/
- cc-load
- clear-preffered-operator
- handling-time-series-info
- info
- preffered-operator

Agent realtime содержит `conversations`.

---

## 16. Требования внешних разработчиков к API

Нужно дать:

- список операторских групп/очередей;
- состав операторов;
- текущий статус оператора;
- управление `ready`, `away/auxwork`, logout/offline;
- кто звонит;
- в какую очередь пришёл вызов;
- какой оператор принял;
- start/ringing/answer/end timestamps;
- wait time;
- talk time;
- answered/missed;
- историю;
- realtime события.

Правильная внешняя модель:

```text
availability_status:
  ready
  away/auxwork
  offline/logged_out

call_state:
  idle
  ringing
  talking
```

`busy/talking` внешняя система не должна устанавливать вручную — это фактическое состояние вызова.

---

## 17. План внешнего API

Целевые endpoint'ы:

```text
GET /api/v1/queues
GET /api/v1/queues/{id}
GET /api/v1/queues/{id}/operators

GET /api/v1/operators
GET /api/v1/operators/{id}
PUT /api/v1/operators/{id}/status

GET /api/v1/calls/active
GET /api/v1/calls/history
GET /api/v1/calls/{id}

GET /api/v1/health
WS  /api/v1/events
```

Источники:

```text
Call-center / cc/arm / CoCon
  -> agents, queues, AuxWork, Available, login/logout

Call API :8089
  -> realtime call/conversation events, caller, legs, alerting, answer/release

CDR
  -> финальная история/сверка
```

Внешним разработчикам НЕ отдавать:

- ECSS integration API key
- Call API JWT
- прямой доступ `:8089`
- прямой доступ `:8086`
- CoCon credentials

Наружу только наш HTTPS API на 443 с auth, firewall/IP allowlist, rate limit, audit.

---

## 18. Текущая точка / СЛЕДУЮЩИЕ ДЕЙСТВИЯ

**Не возвращаться** к созданию `test/test_cc`, поиску `callcenter_enabled`, повторной проверке лицензии, SIP VRRP, повторному созданию 1001/1002 или `Abai_112`.

Продолжать отсюда:

1. Найти программный способ runtime login Agent 1001/1002 через штатный ECSS `cc/arm`, CoCon или поддерживаемый внутренний интерфейс. Не просить пользователя использовать физический телефон.
2. Сначала авторизовать только Agent 1001 и проверить:
   ```text
   /domain/dp_abai/cc/group/cache-info Abai_112_cc
   ```
   Ожидаем `Phone number=1001` и статус не `stopped`.
3. Проверить программно:
   - AuxWork 1001
   - Make Available 1001
   - Logout 1001
   - realtime изменение статуса
4. Повторить для 1002.
5. Проверить runtime query `agent/realtime` и `queue/realtime`:
   - current conversations
   - queue load
   - waiting/active calls
   - status/activity агентов
6. Проверить, настроен ли маршрут **номер 112 → queue Abai_112**. Не считать выполненным без фактической проверки.
7. До первого реального multicall решить `lock_if_no_answer=true` и `lock_if_reject=true`.
8. Когда будет физический доступ к телефонам — выполнить end-to-end 112:
   - нужные SIP звонят
   - кто ответил
   - второй агент не блокируется
   - Call API answer/talking/release
   - RTP
   - CDR
9. Затем писать `ecss-integration-api` на ecss1/ecss2.
10. Сделать HA API endpoint/VIP на 443 без отдельных Gateway VM.
11. Проверить failover нашего integration service между ecss1/ecss2.
12. После финальной приёмки ротировать integration API key и agent PINs.

---

## 19. Полезные команды — уже найдены

```bash
ssh admin@localhost -p 8023
```

```text
/domain/dp_abai/cc/agent/list
/domain/dp_abai/cc/agent/info 1001
/domain/dp_abai/cc/agent/info 1002
/domain/dp_abai/cc/agent/where 1001
/domain/dp_abai/cc/agent/where 1002
/domain/dp_abai/cc/group/info
/domain/dp_abai/cc/group/cache-info Abai_112_cc
/domain/dp_abai/cc/queue/list
/domain/dp_abai/cc/queue/Abai_112/info
/domain/dp_abai/ss/feature-codes/info cc_agent
```

Call API:

```bash
systemctl status ecss-call-api
ss -lntp | grep 8089
```

---

## 20. Security

Никогда не сохранять в GitHub/Google Sheet/памятку:

- ECSS integration API key
- JWT
- Linux/CoCon/WebConf passwords
- Rutoken PIN
- private keys
- Erlang cookie
- agent PIN/password
- `/etc/ecss/ssl/*.key`

Если секрет случайно попал на скрин/в чат — не повторять его текстом; отметить необходимость ротации.

---

## 21. Google Sheet проекта

Создана нативная Google Sheet с полной структурой проекта.

Google file ID:

```text
1FsqGYKz7ZZPqtSTsG0jqfN28pCqRp92gvZW8Ma7dTc4
```

14 вкладок:

1. Сводка
2. Статус проекта
3. Архитектура
4. Сеть и серверы
5. ECSS cluster
6. Лицензирование
7. SIP и абоненты
8. Call API & HA
9. Gateway HA — историческая секция, отдельные Gateway VM больше не целевая архитектура
10. Порты
11. Риски и решения
12. Команды
13. История
14. Источники

---

## 22. Правила продолжения

- Этот файл — canonical source of truth.
- Не повторять выполненные этапы «на всякий случай».
- Учитывать отсутствие физического доступа к телефонам.
- Сначала read-only/малый безопасный тест, потом изменение.
- Для 112: один агент → второй агент → runtime → маршрут → реальный звонок.
- Тестовый 2000 не удалять до полной приёмки 112.
- Не менять cluster/license topology без необходимости.
- Не править штатные файлы ECSS ради нашей интеграции.
- После каждого существенного этапа обновлять этот файл.
