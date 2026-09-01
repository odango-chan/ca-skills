# 5GC File Transfer Orchestration Model

## 1. 请求已经过归一化

本 Skill 不直接执行 gateway 的原始 `[TASK: ...]` 文本。

进入 Runtime 前，Gateway/Agent Adapter 将其归一化为 `file-transfer-request.schema.yaml`：

```text
raw gateway task
  -> task parsing
  -> intent normalization
  -> canonical request
  -> deterministic Procedure selection
```

其中 `urgency` 只允许 `normal` 或 `urgent`。Procedure 执行期间不再次解释自然语言。

## 2. 两种业务操作

### prepare_transfer

目标是准备文件传输需要的网络资源：

```text
participants registered
  -> participants have active PDU sessions
  -> edge cache ready
  -> virtual group created
  -> member addresses assigned
  -> optional QoS boost for urgent requests
  -> goal verification
```

Virtual Group 的激活不属于本 Skill，由 gateway 在接收方确认完成后决定。

### release_group

目标是让目标 Virtual Group 进入 released/not-present 语义状态。

`already released` 和 `not found` 由 Capability/Provider 归一为成功结果，不由模型匹配返回字符串。

## 3. 动态成员不是模型循环

`receiverImsis` 数量是动态的，但模型不负责维护 `for each receiver` 控制流。

P0 采用集合观察能力：

- `transfer.participants.registration.query`
- `transfer.participants.session.query`

Provider 必须对规范化成员集合进行确定性逐项查询，并形成聚合 Evidence：

```text
all members PASS    -> aggregate PASS
any member FAIL     -> aggregate FAIL
otherwise           -> aggregate UNKNOWN
```

成员查询顺序应稳定：sender first，随后按 canonical `receiverImsis` 顺序执行，便于重放和审计。

后续如果 Procedure DSL 正式支持 bounded collection expansion，可以把这部分从 Provider-level deterministic expansion 提升为编译期 Procedure expansion；在此之前不新增非标准 Runtime node type。

## 4. create 结果的数据流

`virtual_group.create` 的 canonical result 必须产生结构化 `groupId`，并通过 Context Contribution / Fact Normalization 形成：

```text
facts.virtual_group.id
```

`virtual_group.assign_members` 从该 Fact 获取 `groupId`，不从 Tool 的人类可读字符串中反向解析。

Gateway 如需 `vg-YYYYMMDD-NNN` 文本格式，由输出 Adapter 使用结构化 `groupId` 渲染。

## 5. UNKNOWN

所有 mutation 都遵守 Runtime 的统一 UNKNOWN 语义：

```text
mutation OUTCOME_UNKNOWN
  -> reconcile
  -> COMMITTED / NOT_COMMITTED / UNRESOLVED
```

非幂等 mutation 不得从 UNKNOWN 直接回到原动作。

QoS boost 和 VG release 都保留“最多一次业务 mutation dispatch”的旧语义：即使 reconcile 证明 `NOT_COMMITTED`，当前 Procedure 也不再次 dispatch 原 mutation，而是失败或安全停止。

## 6. Generic 5GC intent 不在本 Skill

`[TASK: 5GC-INTENT]` 具有远大于文件传输的能力范围，不应与本 Skill 共用同一 `allowedResources`。

通用 5GC Intent 应单独定义 Skill/Contract，在明确其 Capability Envelope、Authority 和 Qualification Case 后再进入正式资产仓。
