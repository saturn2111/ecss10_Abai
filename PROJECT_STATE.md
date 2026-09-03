# ECSS-10 ДП Абай — PROJECT_STATE

**Canonical source of truth для проекта**  
**Последнее обновление:** 2026-09-03 15:01+05  
**ECSS:** 3.18.0.271

> ## Инструкция для любого нового чата ChatGPT
>
> Перед продолжением проекта сначала читать этот файл и продолжать **с раздела «Текущая точка / СЛЕДУЮЩИЕ ДЕЙСТВИЯ»**.
>
> Не повторять уже подтверждённые этапы. Новые фактические данные пользователя имеют приоритет. После существенного этапа обновлять этот файл.
>
> Работать пошагово: одна операция → проверка → следующий шаг. Команды давать полностью. Секреты не хранить и не повторять.

---

## 1. Цель и архитектура

Двухузловая отказоустойчивая ECSS-10 для ДП области Абай с Call-center и внешней API-интеграцией, до ~1000 абонентов.

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
 +-- CC UI/API :8091                           +-- CC UI/API :8091
 +-- SSW :8086                                 +-- SSW :8086
```

Свой код не встраивать в `/usr/share/ecss/ecss-call-api`; размещать отдельно, например `/opt/ecss-integration-api`, отдельный systemd unit.

---

## 2. Базовая инфраструктура — выполнено

- Два независимых Proxmox-хоста, не PVE cluster.
- `srv-prmx-1` mgmt `192.168.190.2/26`, `vmbr0`, `bond0`, 802.3ad LACP, VLAN-aware.
- `srv-prmx-2` mgmt `192.168.190.3/26`, аналогичная схема.
- `ecss1` VMID101, Ubuntu 22.04.5, mgmt `192.168.190.70/26`, voice `192.168.191.2/24`, 8 vCPU / 32GB / 280GB.
- `ecss2` VMID102, Ubuntu 22.04.5, mgmt `192.168.190.80/26`, voice `192.168.191.3/24`, 8 vCPU / 32GB / 280GB.
- Linux user `darth_vader`, timezone `Asia/Almaty`, swap off.
- Cluster ID **`ecss1`**. Не менять.
- Парные компоненты: `core1`, `ds1`, `md1`, `mycelium1`, `sip1`.
- Mnesia/split-brain ранее устранены; не повторять восстановление без новой причины.
- PostgreSQL BDR `ecss-postgres-bdr-ssw 18.0.0+ssw`, port 5439, replication проверена.
- Gluster `ecss_volume`, replica2, heal проверен.
- RestFS `/var/lib/ecss/restfs`, port9990.

---

## 3. SIP / Media / VRRP — выполнено

- Media Server `3.18.0.7`.
- msr.ecss1 `192.168.191.2`, SIP5040 TCP/UDP, MCC5700.
- msr.ecss2 `192.168.191.3`, SIP5040 TCP/UDP, MCC5700.
- registrar `.191.2:5000` и `.191.3:5000`.
- Domain `dp_abai`, SIP IP-set `sip_main`.
- VIP1 `192.168.191.4/24`, VRID31, normal MASTER ecss1.
- VIP2 `192.168.191.5/24`, VRID32, normal MASTER ecss2.
- Failover `ecss-pa-sip` реально проверен.

---

## 4. Лицензирование — выполнено

- ECSS TPM License / ID1, commercial.
- SSW ID `ECSS0000400`.
- expiry `31.07.2050`.
- License Managers `.70:4321`, `.80:4321`, оба Alive; failover проверен.
- `ecss-license-provider 1.0.6` активен на обоих.
- По одному Rutoken на физическом сервере.

Не возвращаться к старому DEFAULT/No passport.

---

## 5. Абоненты / CDR / trunk

- SIP1001 зарегистрирован, VP-30P.
- SIP1002 зарегистрирован, VP-17P.
- CDR period 3600s, `/var/lib/ecss/ftp/domain/dp_abai/default/csv`, файлы создаются.
- SIP trunk к оператору пока не завершён: нужны реальные параметры оператора.

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
- conversation events alerting/released;
- failover `.70 → .80 → .70`.

Integration client `dp_abai_test`, service; allowed numbers ранее 1001–1005. JWT/auth state node-local. API key/JWT не хранить; API key после финальной интеграции ротировать.

---

## 7. Ограничение текущего доступа

**Сейчас пользователь не имеет физического доступа к SIP-телефонам.**

Доступны Web UI, SSH, CoCon и серверные web-интерфейсы. Не делать обязательным шагом набор feature code на физическом аппарате, пока пользователь не скажет, что onsite.

---

## 8. Call-center — тестовая схема уже пройдена

Тест:

```text
2000 -> queue test -> group test_cc -> SIP1001 + SIP1002
```

Distribution `multicall`; звонок на 2000 вызывал оба SIP. **Не повторять этот этап и пока не удалять test/test_cc.**

Старые Test Agent1/2 были авторизованы с физических аппаратов через feature code.

Для вытеснения старых телефонных сессий применено:

```text
/domain/dp_abai/cc/agent/set 1 only_one_session true
/domain/dp_abai/cc/agent/set 2 only_one_session true
```

Для каждого тестового агента выполнен Web login на его Phone и обычный Web logout.

Подтверждённый runtime `test_cc`:

```text
Agent 1  Test 1001  stopped  Phone=1001  Activity=idle
Agent 2  Test 1002  stopped  Phone=1002  Activity=idle
```

Обе старые телефонные CC-сессии остановлены. Поле Phone у `stopped` является последним/сохранённым значением и не означает активную блокировку номера; это подтверждено успешным входом боевых Agent1001 и Agent1002.

---

## 9. Боевая 112 — создана и оба агента функционально проверены

Группа `Abai_112_cc`:

- Agent1001 — Operator1, description `sip 1001`.
- Agent1002 — Operator2, description `sip 1002`.

Queue `Abai_112`, description `ДП Абай 112`.

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

### Agent1001 — полный цикл подтверждён

```text
Web Login      -> available Phone=1001
Available      -> AuxWork   Phone=1001
AuxWork        -> Available Phone=1001
Web Logout     -> stopped   Phone=1001
```

### Agent1002 — полный цикл подтверждён

```text
Web Login      -> available Phone=1002
Available      -> AuxWork   Phone=1002
AuxWork        -> Available Phone=1002
Web Logout     -> stopped   Phone=1002
```

После Web login через `ecss2` подтверждён runtime 2026-09-03 15:01:

```text
1001 Operator 1 available Phone=1001 Activity=idle
1002 Operator 2 stopped   Phone=1002 Activity=idle
```

Итог: оба боевых агента 1001/1002 функционально проверены через штатный `ecss-cc-ui`: login, AuxWork, Available, logout. Web login через второй UI-узел ecss2 также реально изменяет общий CC runtime.

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

Попытка `call/makeCall` на `#160` через CC Web API вернула `status=200` и internalCallId, но runtime Test Agent1 не изменила. **Этот способ logout не повторять.**

---

## 11. Внутренний Contact Center API — подтверждено из установленного кода

Сервисы:

```text
CRM        = call
WEB_CC     = cc/common
CC_AGENT   = cc/arm
CC_PUBSUB  = cc/pubsub
CONFERENCE = teleconference
```

`createHttpUrl` строит URL:

```text
<schema>://<host>:<port>/<domain>/service/<serviceUrl>/<method>
```

Для CC Agent endpoint подтверждён `cc/arm`.

Операции: `login_agent`, `logout_agent`, `make_available`, `auxwork`, `agent_list`, `agents_list`, `group_list`, `all_queues`, `operator_call_history`, realtime `agents_info_event`.

`logout_agent`/`make_available` сериализуются с `agent_id`. SSW HTTP-команды отправляются POST с ECSS session cookie; WebSocket используется для событий/сессии. Не слать XML вручную без корректной session cookie.

---

## 12. ecss-cc-ui 18.0.34 — установлен на обоих узлах

### ecss1 — установлен и проверен

```text
ecss-cc-ui-api.service active running
ecss-cc-ui.service     active
0.0.0.0:8090           openresty/nginx UI
0.0.0.0:8091           node WebSocket API
```

Конфиг `/etc/ecss/ecss-cc-ui-api/config.yaml`:

```text
ECSS core host localhost
ECSS core port 8086
SQL/address-book host localhost
SQL/address-book port 5439
```

Web UI реально открывается на `https://192.168.190.70:8090`.

### ecss2 — установлен и проверен

Установлен пакет:

```text
ecss-cc-ui 18.0.34 amd64
```

Подтверждено:

```text
ecss-cc-ui-api.service active / enabled
ecss-cc-ui.service     active / enabled
0.0.0.0:8090           LISTEN nginx/openresty
0.0.0.0:8091           LISTEN node/MainThread
```

Конфиг `/etc/ecss/ecss-cc-ui-api/config.yaml` подтверждён:

```text
ECSS core host localhost
ECSS core port 8086
SQL/address-book host localhost
SQL/address-book port 5439
```

Web login через `ecss2` (`https://192.168.190.80:8090`) и его влияние на общий runtime подтверждены: Agent1001 стал `available Phone=1001`.

---

## 13. Программный CC login — подтверждён

Штатный WS action:

```text
action = login
payload = login,password,number,profile,domain
```

Он обращается к:

```text
http://localhost:8086/<domain>/service/cc/arm/login
```

с `websocket_control="true"`, получает ECSS cookie/session и CC token.

Практически успешно проверен для Test Agent1/Phone1001, Test Agent2/Phone1002, боевого Agent1001/Phone1001 и боевого Agent1002/Phone1002. Web login через второй UI-узел ecss2 также подтверждён.

---

## 14. forceLogout — найден, но обычному агенту запрещён

WS action `operator/forceLogout` найден. Профиль обычного агента `default` имеет `force_logout=false`; практический ответ был `code=5 / You are not allowed for this command`. Не повторять `operator/forceLogout` обычным агентом.

---

## 15. Требования внешней интеграции — получен контракт от разработчиков

Получен документ «Интеграция с телефонией: состав данных» (5 страниц).

Минимально разработчикам нужны два события одного звонка:

```text
answered  — оператор ответил
finished  — разговор завершён
```

Оба события должны иметь один и тот же уникальный `Id`.

Требуемый объект:

```text
Id            string  обязательно, стабилен в течение звонка
Status        string  answered | finished
Direction     string  inbound | outbound
NumberA       string  внешний абонент
NumberB       string  внутренний номер реально обслужившего/ответившего оператора
Duration      integer предпочтительно секунды; обязателен для finished
CallRecordUrl string  при наличии
```

Предварительное соответствие ECSS:

- `Id` — брать стабильный call/conversation identifier из Call API и использовать его для всех событий одного звонка;
- `Status=answered` — формировать только после фактического ответа оператора, не на стадии alerting;
- `Status=finished` — формировать после released/end для уже отвеченного звонка;
- `Direction` — определять из направления вызова;
- `NumberA` — внешний caller/callee в зависимости от направления;
- `NumberB` — фактический внутренний номер оператора, ответившего на вызов; для multicall нельзя подставлять номер очереди;
- `Duration` — фактическое talk time от answer до end, в секундах;
- `CallRecordUrl` — пока не подтверждено, требует отдельной проверки механизма записи/публикации записи ECSS.

Критические точки для проверки до реализации:

1. Какой именно идентификатор Call API остаётся стабильным при queue/multicall и между событиями answer/end.
2. Как однозначно определить победившего оператора/`NumberB` при `multicall`.
3. Какие реальные события Call API/CC API соответствуют answer и finished на входящем 112.
4. Где и когда появляется запись разговора и можно ли сформировать HTTP(S) URL.
5. Пропущенные/неотвеченные звонки в документе пока не описаны — минимальный контракт требует только answered/finished.

Внешняя модель операторов дополнительно остаётся:

```text
availability_status: ready | away | offline
call_state: idle | ringing | talking
```

`busy/talking` не устанавливать вручную.

---

## 16. Текущая точка / СЛЕДУЮЩИЕ ДЕЙСТВИЯ

**Не возвращаться** к test 2000, лицензии, VRRP, созданию 1001/1002, поиску WS login, `forceLogout`, `call/makeCall #160`, освобождению Test Agent1/2, повторной проверке циклов Agent1001/1002 или установке ecss-cc-ui на ecss1/ecss2 — всё это уже подтверждено.

Продолжать отсюда:

1. **Сейчас:** зафиксировать технический mapping контракта разработчиков `answered/finished` на реальные события ECSS Call API/CC API. Нужны стабильный `Id`, фактический `NumberB` при multicall и talk duration.
2. Проверить runtime/realtime агентов и очереди (`agents_info_event`, queue state) и найти события, позволяющие однозначно определить ответившего оператора.
3. Проверить node-local поведение CC Web session при отказе `ecss-cc-ui-api` одного узла, без остановки core/SSW.
4. Проверить маршрут `112 -> Abai_112` и отдельно решить/проверить `lock_if_no_answer` и `lock_if_reject` перед боевым multicall.
5. Когда будет физический доступ — end-to-end 112: inbound call → multicall → answer → talking → end → RTP/CDR; на этом же тесте снять реальные payloads для `answered/finished`.
6. Отдельно исследовать запись разговора и `CallRecordUrl`.
7. Затем реализовать `/opt/ecss-integration-api` на ecss1/ecss2 и HA endpoint :443, выдающий разработчикам согласованный JSON-контракт.
8. После приёмки ротировать integration API key и agent PINs.

---

## 17. Полезные команды

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
- Оба боевых агента 1001/1002 полностью функционально проверены.
- `ecss-cc-ui 18.0.34` установлен и базово проверен на обоих узлах.
- Web login через ecss2 и влияние на общий CC runtime подтверждены.
- Получен минимальный JSON-контракт интеграции answered/finished; следующий этап — точное сопоставление с событиями ECSS.
- Test 2000/test_cc не удалять до полной приёмки 112.
- Не менять cluster/license topology без необходимости.
- Не править штатные файлы ECSS ради интеграции.
- После каждого существенного этапа обновлять этот файл.