# ECSS-10 ДП Абай — PROJECT_STATE

**Canonical source of truth для проекта**  
**Последнее обновление:** 2026-09-03  
**ECSS:** 3.18.0.271  

> ## Инструкция для любого нового чата ChatGPT
>
> Перед продолжением проекта сначала прочитать этот файл и продолжать **с раздела «Текущая точка / СЛЕДУЮЩИЕ ДЕЙСТВИЯ»**.
>
> Не заставлять пользователя повторять уже подтверждённые этапы. Новые фактические данные пользователя имеют приоритет. После существенного этапа обновлять этот файл.
>
> Пользователь работает пошагово: одна операция → проверка результата → следующий шаг. Команды давать полностью. Секреты не хранить и не повторять.

---

## 1. Цель проекта

Двухузловая отказоустойчивая ECSS-10 для ДП области Абай с Call-center и внешней API-интеграцией.

Основные цели:

- до ~1000 абонентов;
- HA ECSS на `ecss1/ecss2`;
- SIP/media HA через VRRP;
- коммерческая лицензия через 2 Rutoken;
- Call API на обоих ECSS-узлах;
- штатный Contact Center;
- боевая очередь 112;
- внешний API для разработчиков: очереди/группы, операторы, статусы, звонки, кто ответил, времена/длительности, история, realtime;
- integration service размещать **не на отдельных Gateway VM, а прямо на ecss1 и ecss2**.

---

## 2. Архитектура API — принятое решение

Отдельные `ecss-gateway01/ecss-gateway02` больше не целевая архитектура.

```text
External CRM
    |
 HTTPS :443
    |
 API VIP / stable endpoint
    |
 +--+-------------------+
 |                      |
ecss1                  ecss2
192.168.190.70          192.168.190.80
 |                      |
our integration       our integration
service               service
 |                      |
 +-- Call API :8089     +-- Call API :8089
 +-- CC UI/API :8091    +-- CC UI/API :8091 (после установки на ecss2)
 +-- SSW :8086          +-- SSW :8086
```

Свой код не встраивать в `/usr/share/ecss/ecss-call-api`; размещать отдельно, например `/opt/ecss-integration-api`, отдельный systemd unit.

---

## 3. Proxmox / ECSS VM

Два независимых Proxmox-хоста, **не PVE cluster**.

### srv-prmx-1

- management `192.168.190.2/26`
- gateway `192.168.190.1`
- `vmbr0`, VLAN-aware
- `bond0`, 802.3ad LACP, nic0+nic1
- PVE 9.2.2, kernel 7.0.2-6-pve

### srv-prmx-2

- management `192.168.190.3/26`
- gateway `192.168.190.1`
- аналогичная LACP/VLAN схема

### ecss1

- VMID 101
- Ubuntu Server 22.04.5
- management `192.168.190.70/26`, IF `enp6s18`
- gateway `192.168.190.65`
- voice `192.168.191.2/24`, IF `enp6s19`
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
- `/etc/hosts` настроен для `ecss1/ecss2`

---

## 4. ECSS cluster — выполнено

Cluster ID: **`ecss1`**. Не менять.

Инициализация:

```text
/system/clusters/set [ecss1, ecss2]
```

Парные компоненты: `core1`, `ds1`, `md1`, `mycelium1`, `sip1`.

Ранее устранялись Mnesia/split-brain проблемы; кластер доведён до синхронизированного состояния. Без новой причины не повторять восстановление и не удалять Mnesia каталоги вручную.

CoCon:

```bash
ssh admin@localhost -p 8023
```

PostgreSQL BDR:

- `ecss-postgres-bdr-ssw 18.0.0+ssw`
- port `5439`
- replication проверена

Gluster:

- volume `ecss_volume`
- `192.168.190.70:/var/lib/ecss/glusterfs`
- `192.168.190.80:/var/lib/ecss/glusterfs`
- replica 2, heal проверен

RestFS:

- `/var/lib/ecss/restfs`
- port 9990

PostgreSQL backup:

- `ssw_dump_postgres.timer`
- daily около 00:00
- manual dump тестировался

---

## 5. SIP / Media / VRRP — выполнено

Media Server `3.18.0.7`.

- msr.ecss1 `192.168.191.2`, SIP 5040 TCP/UDP, MCC 5700 TCP
- msr.ecss2 `192.168.191.3`, SIP 5040 TCP/UDP, MCC 5700 TCP
- registrar ecss1 `.191.2:5000`
- registrar ecss2 `.191.3:5000`

Domain `dp_abai`, SIP IP-set `sip_main`.

VRRP:

- VIP1 `192.168.191.4/24`, VRID31, normal MASTER ecss1
- VIP2 `192.168.191.5/24`, VRID32, normal MASTER ecss2

Failover `ecss-pa-sip` реально проверялся: VIP переходил на второй узел и возвращался после восстановления.

---

## 6. Лицензирование — выполнено

Не возвращаться к старому DEFAULT/No passport.

Текущее состояние:

- ECSS TPM License / ID 1
- commercial
- SSW ID `ECSS0000400`
- организация Департамент полиции области Абай
- expiry `31.07.2050`

License Manager:

- `192.168.190.70:4321`
- `192.168.190.80:4321`

Оба были Alive; failover лицензии проверялся.

`ecss-license-provider 1.0.6` активен на обоих. По одному Rutoken на каждом физическом сервере.

---

## 7. Абоненты / CDR / trunk

Ранее подтверждено:

- SIP 1001 зарегистрирован (VP-30P; старый contact `.191.246`)
- SIP 1002 зарегистрирован (VP-17P; старый contact `.191.245`)

CDR:

- period 3600s
- `/var/lib/ecss/ftp/domain/dp_abai/default/csv`
- файлы создаются

SIP trunk к оператору пока не завершён: нужны реальные параметры оператора (IP/port/auth/DID/codecs/From/PAI/формат номера).

---

## 8. Call API :8089 — выполнено

Package `/usr/share/ecss/ecss-call-api`, service `ecss-call-api`.

- ecss1: `192.168.190.70:8089`, SSW `.70:8086`
- ecss2: `192.168.190.80:8089`, SSW `.80:8086`

Подтверждено:

- `integration.register`
- JWT
- WS authorization/open
- heartbeat ping/pong
- `call.make`
- conversation events
- alerting/released

Integration client `dp_abai_test`, service, allowed numbers ранее 1001–1005.

Call API failover проверен: `.70` → stop service → `.80` register/WS/pong → восстановление `.70`.

JWT/auth state node-local; после failover новый активный узел должен получать новый JWT и WS.

ECSS integration API key ранее попадал в чат/логи → после финальной интеграции обязательно ротировать. Никогда не хранить key/JWT в этом файле.

---

## 9. Ограничение текущего доступа пользователя

**Сейчас пользователь не имеет физического доступа к SIP-телефонам.**

Доступны Web UI, SSH, CoCon и серверные веб-интерфейсы.

Не предлагать обязательные действия на физическом телефоне до явного сообщения, что пользователь onsite.

---

## 10. Call-center — тест уже пройден

Тестовая схема была создана и проверена ранее:

```text
2000 -> queue test -> group test_cc -> SIP 1001 + SIP 1002
```

Distribution `multicall`; звонок на 2000 вызывал оба SIP.

**Не повторять этот этап.** Тестовую схему пока не удалять до полной приёмки 112.

---

## 11. Боевая 112 — создана

Группа агентов:

```text
Abai_112_cc
```

- Agent 1001 — Operator 1, description `sip 1001`
- Agent 1002 — Operator 2, description `sip 1002`

Agent ID совпадает с SIP-номером.

Подтверждено:

```text
/domain/dp_abai/cc/agent/where 1001 -> Abai_112
/domain/dp_abai/cc/agent/where 1002 -> Abai_112
/domain/dp_abai/cc/group/info -> Abai_112_cc: 1001,1002
```

Queue:

```text
Abai_112
```

Description `ДП Абай 112`.

Подтверждённые параметры:

- agents `1001,1002`
- distribution `multicall`
- max_wait_time 120
- max_distribution_attempts 3
- max_distribution_duration 10
- queue_length 20
- callback_cooldown_timeout 300
- skill_based_distribution false
- lock_if_no_answer true
- lock_if_reject true
- serial_lock_enabled true

Перед реальным multicall отдельно решить/проверить `lock_if_no_answer` и `lock_if_reject`.

До установки CC UI/API runtime был:

```text
1001 Status=stopped Phone number=- Activity=idle
1002 Status=stopped Phone number=- Activity=idle
```

---

## 12. Feature codes CC — найдены

```text
/domain/dp_abai/ss/feature-codes/info cc_agent
```

- login `*160*AGENT_ID*PASSWORD#`
- logout `#160`
- complete `#161`
- enter_auxwork `#162`
- make_available `#163`
- call_agent `*165*AGENT_ID#`

Пароли/PIN агентов не хранить. Они попадали на скриншоты → перед боем ротировать.

---

## 13. Внутренний Contact Center API — найден

В установленном Call API найдены сервисы:

```text
CRM       = call
WEB_CC    = cc/common
CC_AGENT  = cc/arm
CC_PUBSUB = cc/pubsub
```

Найдены операции `login_agent`, `logout_agent`, `make_available`, `auxwork`, `agent_list`, `agents_list`, `group_list`, `all_queues`, `operator_call_history`, queue operations и realtime `agents_info_event`.

`login_agent` сериализуется как XML с:

```text
agent_id
number
```

`logout_agent`/`make_available` используют `agent_id`; `auxwork` использует `agent_id` + `reason`.

Транспорт SSW: HTTP POST XML + cookie/token + WebSocket.

---

## 14. ecss-cc-ui — НОВЫЙ ПОДТВЕРЖДЁННЫЙ ЭТАП 2026-09-03

На `ecss1` из официального ELTEX repo jammy/3.18 установлен:

```text
ecss-cc-ui 18.0.34
```

Dry-run перед установкой показал: 1 новый пакет, 0 upgrades, 0 removals.

После установки подтверждено:

```text
ecss-cc-ui-api.service  active running
ecss-cc-ui.service      active
```

Listeners:

```text
0.0.0.0:8090  openresty/nginx — Call-center UI
0.0.0.0:8091  node MainThread — Call-center API/WebSocket proxy
```

Systemd API unit:

```text
WorkingDirectory=/usr/share/ecss/ecss-cc-ui-api
ExecStart=/usr/bin/nodejs /usr/share/ecss/ecss-cc-ui-api/dist/websockets/src/main.js
User=ssw
```

UI unit управляет openresty конфигом `/etc/openresty/sites-available/ecss-cc-ui.conf`.

Конфиг API найден:

```text
/etc/ecss/ecss-cc-ui-api/config.yaml
/etc/ecss/ecss-cc-ui-api/example.yaml
```

Web UI **фактически открывается в браузере на ecss1:8090**; пользователь прислал экран авторизации Call-center.

При установке параметры БД адресной книги оставлены по значениям установщика для ECSS 3.18: PostgreSQL, localhost, port 5439, user postgres. Секрет БД не хранить.

`ecss-cc-ui` пока установлен только на **ecss1**. На ecss2 ставить после успешного функционального теста ecss1.

---

## 15. Требования внешних разработчиков

Нужно дать:

- очереди/группы и состав операторов;
- текущий availability/status;
- управление ready / away(AuxWork) / logout;
- caller/callee;
- очередь вызова;
- кто из операторов ответил;
- timestamps start/ringing/answer/end;
- wait/talk time;
- answered/missed;
- историю;
- realtime events.

Модель наружу:

```text
availability_status: ready | away | offline
call_state: idle | ringing | talking
```

`busy/talking` нельзя устанавливать вручную — это фактический call state.

---

## 16. Текущая точка / СЛЕДУЮЩИЕ ДЕЙСТВИЯ

**Не возвращаться** к test/test_cc, callcenter_enabled, лицензии, VRRP, созданию 1001/1002 или Abai_112, установке ecss-cc-ui на ecss1 — это уже выполнено.

Продолжать отсюда:

1. На открывшемся `ecss-cc-ui` ecss1 выполнить **только login Agent 1001** программно через web UI/API:
   - Agent ID `1001`
   - Phone number `1001`
   - Domain `dp_abai`
   - role/profile `operator` если поле требуется
   - пароль агента вводить только локально, в чат не передавать.
2. Сразу после login проверить:
   ```text
   /domain/dp_abai/cc/group/cache-info Abai_112_cc
   ```
   Ожидаем для 1001 Phone number=1001 и status != stopped.
3. Если login не проходит — смотреть `/etc/ecss/ecss-cc-ui-api/config.yaml` без вывода секретов и `journalctl -u ecss-cc-ui-api` после попытки.
4. После успешного login 1001 проверить AuxWork → Available → Logout и realtime изменение.
5. Повторить для 1002.
6. После функциональной проверки установить `ecss-cc-ui 18.0.34` на ecss2 с теми же параметрами и проверить 8090/8091.
7. Проверить runtime `agent/realtime` и `queue/realtime`.
8. Проверить маршрут `112 -> Abai_112` (не считать завершённым без факта).
9. Когда будет физический доступ — end-to-end звонок 112, answer/talking/RTP/CDR.
10. Затем писать `/opt/ecss-integration-api` на ecss1/ecss2 и HA endpoint 443.
11. После приёмки ротировать ECSS integration API key и agent PINs.

---

## 17. Полезные команды

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

Services/ports:

```bash
systemctl status ecss-call-api
systemctl status ecss-cc-ui-api
systemctl status ecss-cc-ui
ss -lnt | grep -E ':(8089|8090|8091)\b'
```

---

## 18. Security

Никогда не сохранять:

- ECSS integration API key
- JWT
- Linux/CoCon/WebConf passwords
- Rutoken PIN
- agent passwords/PIN
- PostgreSQL password
- private keys
- Erlang cookie
- `/etc/ecss/ssl/*.key`

Если секрет попал на скрин/в чат — не повторять; запланировать ротацию.

---

## 19. Правила продолжения

- `PROJECT_STATE.md` — canonical source of truth.
- Не повторять выполненные этапы.
- Учитывать отсутствие физического доступа к телефонам.
- Сначала один Agent 1001 → проверка → затем Agent 1002.
- Тестовый 2000 не удалять до приёмки 112.
- Не менять cluster/license topology без необходимости.
- Не править штатные файлы ECSS ради интеграции.
- После каждого существенного этапа обновлять этот файл.
