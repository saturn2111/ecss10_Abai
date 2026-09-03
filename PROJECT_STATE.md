# ECSS-10 ДП Абай — PROJECT_STATE

**Canonical source of truth для проекта**  
**Последнее обновление:** 2026-09-03  
**ECSS:** 3.18.0.271

> ## Инструкция для любого нового чата ChatGPT
>
> Перед продолжением проекта сначала читать этот файл и продолжать **с раздела «Текущая точка / СЛЕДУЮЩИЕ ДЕЙСТВИЯ»**.
>
> Не повторять уже подтверждённые этапы. Новые фактические данные пользователя имеют приоритет. После существенного этапа обновлять этот файл.
>
> Пользователь предпочитает пошаговую работу: одна операция → проверка → следующий шаг. Команды давать полностью. Секреты не хранить и не повторять.

---

## 1. Цель проекта

Двухузловая отказоустойчивая ECSS-10 для ДП области Абай с Call-center и внешней API-интеграцией.

Цели:

- до ~1000 абонентов;
- HA ECSS на `ecss1/ecss2`;
- SIP/media HA через VRRP;
- коммерческая лицензия через 2 Rutoken;
- Call API на обоих ECSS-узлах;
- штатный Contact Center;
- боевая очередь 112;
- внешний API: очереди/группы, операторы, статусы, звонки, кто ответил, времена/длительности, история, realtime;
- integration service размещать **на ecss1 и ecss2**, без отдельных Gateway VM.

Целевая схема:

```text
External CRM
    |
 HTTPS :443
    |
 API VIP / stable endpoint
    |
 +----------------------+----------------------+
 |                                             |
ecss1                                         ecss2
192.168.190.70                                192.168.190.80
 |                                             |
our integration service                      our integration service
 |                                             |
 +-- Call API :8089                            +-- Call API :8089
 +-- CC UI/API :8091                           +-- CC UI/API :8091 (после установки)
 +-- SSW :8086                                 +-- SSW :8086
```

Свой код не встраивать в `/usr/share/ecss/ecss-call-api`; размещать отдельно, например `/opt/ecss-integration-api`, отдельный systemd unit.

---

## 2. Базовая инфраструктура — выполнено

Два независимых Proxmox-хоста, **не PVE cluster**.

- `srv-prmx-1` mgmt `192.168.190.2/26`, gw `192.168.190.1`, `vmbr0`, `bond0`, 802.3ad LACP, VLAN-aware.
- `srv-prmx-2` mgmt `192.168.190.3/26`, аналогичная схема.

ECSS VM:

- `ecss1` VMID101, Ubuntu 22.04.5, mgmt `192.168.190.70/26`, voice `192.168.191.2/24`, 8 vCPU / 32GB / 280GB.
- `ecss2` VMID102, Ubuntu 22.04.5, mgmt `192.168.190.80/26`, voice `192.168.191.3/24`, 8 vCPU / 32GB / 280GB.
- Linux user `darth_vader`, timezone `Asia/Almaty`, swap off.

Cluster ID: **`ecss1`**. Не менять.

Парные компоненты: `core1`, `ds1`, `md1`, `mycelium1`, `sip1`.

Ранее были Mnesia/split-brain проблемы; они устранены. Без новой причины не повторять восстановление и не удалять Mnesia каталоги.

PostgreSQL BDR:

- `ecss-postgres-bdr-ssw 18.0.0+ssw`
- port `5439`
- replication проверена.

Gluster:

- volume `ecss_volume`
- `.70:/var/lib/ecss/glusterfs`
- `.80:/var/lib/ecss/glusterfs`
- replica 2, heal проверен.

RestFS `/var/lib/ecss/restfs`, port 9990.

---

## 3. SIP / Media / VRRP — выполнено

Media Server `3.18.0.7`.

- msr.ecss1 `192.168.191.2`, SIP5040 TCP/UDP, MCC5700.
- msr.ecss2 `192.168.191.3`, SIP5040 TCP/UDP, MCC5700.
- registrar `.191.2:5000` и `.191.3:5000`.

Domain `dp_abai`, SIP IP-set `sip_main`.

VRRP:

- VIP1 `192.168.191.4/24`, VRID31, normal MASTER ecss1.
- VIP2 `192.168.191.5/24`, VRID32, normal MASTER ecss2.

Failover `ecss-pa-sip` реально проверен.

---

## 4. Лицензирование — выполнено

Не возвращаться к старому DEFAULT/No passport.

- ECSS TPM License / ID1, commercial.
- SSW ID `ECSS0000400`.
- expiry `31.07.2050`.
- License Managers `.70:4321`, `.80:4321`, оба Alive; failover проверен.
- `ecss-license-provider 1.0.6` активен на обоих.
- по одному Rutoken на физическом сервере.

---

## 5. Абоненты / CDR / trunk

Ранее подтверждено:

- SIP1001 зарегистрирован, VP-30P.
- SIP1002 зарегистрирован, VP-17P.

CDR:

- period 3600s;
- `/var/lib/ecss/ftp/domain/dp_abai/default/csv`;
- файлы создаются.

SIP trunk к оператору пока не завершён: нужны реальные параметры оператора.

---

## 6. Call API :8089 — выполнено

Package `/usr/share/ecss/ecss-call-api`, service `ecss-call-api`.

- ecss1 `.70:8089`, SSW `.70:8086`.
- ecss2 `.80:8089`, SSW `.80:8086`.

Подтверждено:

- `integration.register`;
- JWT;
- WS authorization/open;
- heartbeat ping/pong;
- `call.make`;
- conversation events;
- alerting/released;
- failover `.70 → .80 → .70`.

Integration client `dp_abai_test`, service; allowed numbers ранее 1001–1005.

JWT/auth state node-local. API key/JWT не хранить; API key после финальной интеграции ротировать.

---

## 7. Ограничение доступа пользователя

**Сейчас пользователь не имеет физического доступа к SIP-телефонам.**

Доступны Web UI, SSH, CoCon и серверные web-интерфейсы.

Не делать обязательным шагом набор feature code на физическом аппарате, пока пользователь не скажет, что onsite.

---

## 8. Call-center — тестовая схема уже пройдена

Тест:

```text
2000 -> queue test -> group test_cc -> SIP1001 + SIP1002
```

Distribution `multicall`; звонок на 2000 вызывал оба SIP.

**Не повторять этот этап и пока не удалять test/test_cc.**

Текущий runtime test_cc:

```text
Agent 1  Test 1001  available  Phone=1001  Activity=idle
Agent 2  Test 1002  available  Phone=1002  Activity=idle
```

Это важно: старые Test Agent 1/2 были авторизованы ранее с физических аппаратов через feature code и сейчас держат номера 1001/1002.

---

## 9. Боевая 112 — создана

Группа:

```text
Abai_112_cc
```

- Agent1001 — Operator1, description `sip 1001`.
- Agent1002 — Operator2, description `sip 1002`.

Queue:

```text
Abai_112
```

Параметры:

- agents 1001,1002;
- distribution `multicall`;
- max_wait_time 120;
- max_distribution_attempts 3;
- max_distribution_duration 10;
- queue_length 20;
- callback_cooldown_timeout 300;
- skill_based_distribution false;
- lock_if_no_answer true;
- lock_if_reject true;
- serial_lock_enabled true.

Текущий runtime Abai_112_cc:

```text
1001 Operator 1 stopped Phone=- Activity=idle
1002 Operator 2 stopped Phone=- Activity=idle
```

Боевой Agent1001 пока не может занять Phone1001, потому что номер уже держит старый Test Agent1.

---

## 10. Feature codes Call-center

```text
login          *160*AGENT_ID*PASSWORD#
logout         #160
complete       #161
enter_auxwork  #162
make_available #163
call_agent     *165*AGENT_ID#
```

Agent PIN/password не хранить и не повторять; перед боем ротировать.

---

## 11. Внутренний Contact Center API

Найдены сервисы:

```text
CRM       = call
WEB_CC    = cc/common
CC_AGENT  = cc/arm
CC_PUBSUB = cc/pubsub
```

Операции: `login_agent`, `logout_agent`, `make_available`, `auxwork`, `agent_list`, `agents_list`, `group_list`, `all_queues`, `operator_call_history`, queue operations, realtime `agents_info_event`.

`login_agent` сериализуется с `agent_id` и `number`; `logout_agent`/`make_available` — с `agent_id`; `auxwork` — `agent_id + reason`.

---

## 12. ecss-cc-ui 18.0.34 — установлен на ecss1

Перед установкой dry-run: 1 новый пакет, 0 upgrades, 0 removals.

Установлено:

```text
ecss-cc-ui 18.0.34
```

Подтверждено:

```text
ecss-cc-ui-api.service active running
ecss-cc-ui.service     active
0.0.0.0:8090           openresty/nginx UI
0.0.0.0:8091           node WebSocket API
```

API unit:

```text
WorkingDirectory=/usr/share/ecss/ecss-cc-ui-api
ExecStart=/usr/bin/nodejs /usr/share/ecss/ecss-cc-ui-api/dist/websockets/src/main.js
User=ssw
```

Конфиг:

```text
/etc/ecss/ecss-cc-ui-api/config.yaml
```

Фактические параметры:

```text
ECSS core host localhost
ECSS core port 8086
SQL/address-book host localhost
SQL/address-book port 5439
```

Web UI реально открывается на `https://192.168.190.70:8090`.

`ecss-cc-ui` пока **не установлен на ecss2** — ставить после успешного функционального теста ecss1.

---

## 13. НОВОЕ: программный CC login подтверждён

Исходники `ecss-cc-ui-api 18.0.34` подтвердили штатный action:

```text
action = login
payload = login,password,number,profile,domain
```

Он обращается в:

```text
http://localhost:8086/<domain>/service/cc/arm/login
```

с `websocket_control="true"`, получает ECSS cookie/session, создаёт CC User и возвращает encrypted token.

Практически проверено через Web UI и Node/WebSocket:

```text
login=1
number=1001
profile=default
domain=dp_abai
```

успешно возвращает status 200, `agentId=1`, CC token и профиль возможностей.

То есть программный login через штатный CC API **работает**.

При этом это не освобождает Phone1001 от старой телефонной CC-сессии Agent1: `cache-info test_cc` остаётся `available / 1001`.

Web UI кнопка «Выход» закрывает web/frontend ECSS connection, но исходная сессия Agent1, созданная через физический `*160*...#`, остаётся активной.

---

## 14. НОВОЕ: forceLogout найден, но обычному Agent1 запрещён

Штатный WS action:

```text
operator/forceLogout
```

Точный request:

```json
{"action":"operator/forceLogout","requestId":2,"payload":{"id":"1"}}
```

Внутри он формирует ECSS `force_logout {agent_id:"1"}`.

Практически протестировано после успешного WS login Agent1.

Профиль Agent1 (`default`) вернул:

```text
force_logout=false
agents_manage=false
queues_manage=false
```

Ответ на `operator/forceLogout id=1`:

```text
status=500
code=5
message="You are not allowed for this command"
```

Это ожидаемый RBAC-отказ. Не повторять эту попытку обычным Agent1.

---

## 15. Требования внешнего API

Наружу нужно дать:

- очереди/группы и состав операторов;
- текущий availability;
- ready / away(AuxWork) / logout;
- caller/callee;
- очередь вызова;
- кто ответил;
- start/ringing/answer/end;
- wait/talk time;
- answered/missed;
- history;
- realtime events.

Внешняя модель:

```text
availability_status: ready | away | offline
call_state: idle | ringing | talking
```

`busy/talking` не устанавливать вручную.

---

## 16. Текущая точка / СЛЕДУЮЩИЕ ДЕЙСТВИЯ

**Не возвращаться** к установке ecss-cc-ui на ecss1, test/test_cc, лицензии, VRRP, созданию 1001/1002, поиску формата WS login или повторному `operator/forceLogout` обычным Agent1.

Продолжать отсюда:

1. Освободить Phone1001 от старой телефонной сессии Test Agent1 **без физического телефона**.
2. Ближайший безопасный кандидат: после программного login Agent1 использовать разрешённый action `call/makeCall` для набора feature code `#160` от имени Agent1/Phone1001. Профиль Agent1 имеет `call_basic=true`; `call/makeCall` требует обычную authorization, а не `force_logout` privilege.
3. После попытки сразу проверить:
   ```text
   /domain/dp_abai/cc/group/cache-info test_cc
   ```
   Цель:
   ```text
   Agent1 stopped Phone=-
   Agent2 available Phone=1002
   ```
4. Если `call/makeCall -> #160` не завершит старую сессию, перейти к прямому поддерживаемому `cc/arm`/supervisor механизму logout, не удаляя test_cc.
5. После освобождения 1001 — login боевого Agent1001 с Phone1001 через ecss-cc-ui и проверить `Abai_112_cc`.
6. Проверить программно AuxWork → Available → Logout для боевого Agent1001.
7. Повторить аналогично для 1002.
8. После функциональной проверки установить `ecss-cc-ui 18.0.34` на ecss2 и проверить 8090/8091.
9. Проверить маршрут `112 -> Abai_112` и lock flags.
10. Когда будет физический доступ — end-to-end 112: ring/answer/talking/RTP/CDR.
11. Затем реализовать `/opt/ecss-integration-api` на ecss1/ecss2 и HA endpoint :443.
12. После приёмки ротировать integration API key и agent PINs.

---

## 17. Полезные команды

CoCon:

```bash
ssh admin@localhost -p 8023
```

```text
/domain/dp_abai/cc/group/cache-info test_cc
/domain/dp_abai/cc/group/cache-info Abai_112_cc
/domain/dp_abai/cc/agent/info 1001
/domain/dp_abai/cc/agent/info 1002
/domain/dp_abai/cc/queue/Abai_112/info
/domain/dp_abai/ss/feature-codes/info cc_agent
```

Services:

```bash
systemctl status ecss-call-api
systemctl status ecss-cc-ui-api
systemctl status ecss-cc-ui
ss -lnt | grep -E ':(8089|8090|8091)\b'
```

---

## 18. Security

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

---

## 19. Правила продолжения

- Этот файл — canonical source of truth.
- Не повторять выполненные этапы.
- Учитывать отсутствие физического доступа к телефонам.
- Один Agent1001 → проверка → Agent1002.
- Test 2000/test_cc не удалять до полной приёмки 112.
- Не менять cluster/license topology без необходимости.
- Не править штатные файлы ECSS ради интеграции.
- После каждого существенного этапа обновлять этот файл.
