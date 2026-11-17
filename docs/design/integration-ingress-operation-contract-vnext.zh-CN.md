# CA Integration Ingress Operation Contract — 设计提案

**状态：** 设计提案；尚未冻结、尚未发布。  
**适用范围：** CA-SL v1alpha4 之后的语言修订，以及与之配套的可信 Integration 依赖导出。  
**语义依据：** [Node-level Event Wait 冻结语义 PR #60](https://github.com/odango-chan/ca-skills/pull/60)；accepted-event tombstone/replay 澄清见 [PR #64](https://github.com/odango-chan/ca-skills/pull/64)。  
**相关文档：** [CA-SL Wait 规范化草案 PR #61](https://github.com/odango-chan/ca-skills/pull/61)、[Generic Host/Runtime Inbound Event 契约 PR #210](https://github.com/odango-chan/ca-agent-demo/pull/210)。  
**版本边界：** 本文提出独立的 Integration 导出契约版本，不分配 CA-SL 语言版本，也不改变 v1alpha4。

本文中的 MUST、MUST NOT、REQUIRED、SHOULD、SHOULD NOT 和 MAY 均为规范性用语。本文是待评审设计，不构成现有 Compiler、Host、Runtime 或 Integration 产品已经符合的声明。

## 1. 目标与非目标

### 1.1 目标

定义一个可由 Compiler 静态链接、由 Generic Host 可靠转交、由 Runtime 精确消费、由 Domain Integration 实际执行的可信入站协议契约。

该契约必须回答：

1. 入站消息究竟是哪一个协议/API 操作；
2. 由哪个受信 Integration Owner 实现和负责；
3. 使用哪一份精确的协议规范、OpenAPI artifact、请求 Schema 和响应 Schema；
4. 如何将 wire request 确定性地归一化为 Skill 可消费的 typed request；
5. 如何在触发外部动作之前，建立唯一、可验证的 correlation binding；
6. 如何区分并发 Run、连续 Wait occurrence、重复消息和迟到消息；
7. 如何定义配对协议响应、响应结果数据来源、响应期限和恢复责任；
8. 如何在不把协议细节泄漏给 Generic Host / Runtime 的前提下完成上述流程。

### 1.2 非目标

本文不定义：

- 新的 CA-SL Node、Stage、Outcome 或 Wait 语义；
- Skill 作者自定义 payloadSchema、correlationKey、callbackToken 或 HTTP 路由；
- 全局 EventCatalog、运行时全局事件发现或按名称猜测 API；
- Generic Host 对 3GPP、HTTP/2、SBI 路径或协议 Payload 的解析；
- Runtime 对原始 HTTP request 的解析或协议身份推导；
- 新 Invocation、Root selection、Skill selection 或 Run；
- 出站 SBI Tool 的调用契约。出站 Tool 仍使用 ToolCatalog Operation；
- TLS/OAuth 密钥、证书、令牌、服务发现地址等部署秘密；
- Integration 的具体 HTTP Server、队列、数据库、持久化产品或 DTO 线格式。

## 2. 核心模型与术语

### 2.1 Ingress Operation

**Ingress Operation** 是 Integration Owner 发布的、描述一个精确入站协议操作的可信契约导出。

它描述“外部协议请求如何进入 CA”，不是一个由 Agent 主动调用的 Tool Operation。

因此：

- Ingress Operation 不属于 ToolCatalog 的 operation 或 observation callable；
- Ingress Operation 不属于 Skill 的 Capability Grant；
- Ingress Operation 不增加 Tool Action Budget；
- 它不能由 Skill 的 operation.tool 调用；
- 它不能产生 Tool Operation Result 或 Evidence；
- 它只为 CA-SL Node-entry Event Wait 提供事件身份、请求 Schema、归一化、Correlation 和可选响应契约。

触发入站事件的出站动作仍然是一个普通、精确链接的 ToolCatalog Operation。Ingress Operation 通过可信引用声明允许哪些出站 Operation 触发它。

### 2.2 IngressCatalog

一个 Integration dependency snapshot MAY 发布一个或多个 IngressCatalog 资源。IngressCatalog 是包内的、受信的、版本化导出；不是全局 EventCatalog。

建议的独立资源版本为：

~~~yaml
apiVersion: connectionagent.io/ingresscatalog/v1alpha1
kind: IngressCatalog
metadata:
  owner: example.integration-owner
spec:
  operations: []
~~~

上述 API 标识是本文提出的契约版本，不代表已存在可下载的正式发布物。资源的物理文件路径由 Integration Package 决定，不成为 Skill 作者可见的身份。每个 operations[] 元素是一个 exportKind=ingressOperation 的独立导出；Catalog 文件本身不取代 trusted dependency binding。

建议的结构校验 Schema 位于 [ingresscatalog.v1alpha1.schema.json](schemas/ingresscatalog.v1alpha1.schema.json)。它只校验 IngressCatalog 的结构、字段类型和局部条件；Package ID / Owner binding、跨快照唯一性、Schema 引用闭包、Trigger Operation 链接、Procedure path analysis、部署 profile binding 和真实协议行为仍由 Compiler、Admission 与 Integration conformance tests 分别验证。该 JSON Schema 与本文一样保持 NOT FROZEN。

### 2.3 四种不同身份

| 身份 | 权威 Owner | 用途 | 是否暴露给 Skill |
|---|---|---|---|
| Ingress Operation export identity | Integration Package / trusted dependency binding | 精确链接协议入站契约 | 仅通过 wait.event 选择，不暴露内部句柄 |
| expectedIngressRef | Runtime | 一个 Run 内一个 Wait occurrence 的不透明注册句柄 | 否 |
| deliveryRef | Integration | 一次归一化交付的幂等身份 | 否 |
| responseObligationRef | Integration | 一个配对协议响应的私有责任记录 | 否 |

它们不能互换。尤其是，协议 Resource ID、SUPI、smContextRef、deliveryRef 和 expectedIngressRef 不是同一种身份。

### 2.4 事件选择器

CA-SL wait.event 使用三个精确字段：

~~~yaml
event:
  source: AMF
  service: Nsmf_PDUSession
  operation: UpdateSMContext
~~~

字段语义：

- source：由 Integration 从已认证对端身份得出的规范 NF 类型，不是请求 Body 中的自报字段，也不是 NF 实例地址；
- service：3GPP Service 名称；
- operation：该 Service 下的规范 Service-Operation 名称。

三个字段按区分大小写的精确字符串匹配。它们不等同于 OpenAPI 的 operationId。例如，3GPP Service-Operation UpdateSMContext 与 OpenAPI artifact 中的 UpdateSmContext 是两个不同层次的字段，均须由契约分别记录。

## 3. 发布、依赖和可信身份

### 3.1 依赖方式

Skill 通过普通、版本固定的 contract.yaml dependencies 声明 Integration Package。Studio / trusted caller 负责取得不可变快照并将确切字节交给 Compiler；Compiler 不联网下载、不自动升级，也不选择 latest。

IngressCatalog、OpenAPI artifact、源请求 Schema、归一化 Schema、映射清单和响应 Schema 均必须包含在该快照闭包内，或由该快照明确声明的其他受信依赖提供。不得引用任意 URL、工作区路径或未锁定的远端资源。

### 3.2 新增的可信导出类别

下一语言修订的依赖装配契约必须新增精确的 exportKind: ingressOperation。

每个 Ingress Operation 的受信 Owner 绑定至少包含：

- dependency alias；
- 精确 Package ID；
- 精确 Owner ID；
- exportKind = ingressOperation；
- 精确 export ID；
- 所属 snapshot digest。

Owner 身份必须来自 trusted dependency binding，不能只相信 IngressCatalog 的 metadata.owner 自述。Catalog 中的 owner 必须与受信绑定一致。

export ID 在一个 dependency snapshot 的 ingressOperation 命名空间内唯一。整个 Skill dependency closure 中，重复的 (exportKind, exportId) 或重复的事件选择器均不得被静默覆盖。

### 3.3 与 v1alpha4 的隔离

v1alpha4 的依赖互操作集合保持不变。v1alpha4 不接受 IngressCatalog、ingressOperation export kind 或本文的 Event Wait 语法。

下一语言修订必须显式增加该 export kind 和对应版本规则。不能通过修改 v1alpha4 ToolCatalog 的 apiVersion、将 Ingress Operation 伪装成 ToolCatalog callable，或在旧版本中增加 fallback 来实现。

### 3.4 精确解析

Compiler 在 Skill 声明的精确 dependency snapshots 中解析 wait.event：

- 零个匹配：WAIT_INGRESS_EXPORT_NOT_FOUND；
- 多个匹配：WAIT_INGRESS_EXPORT_AMBIGUOUS；
- 恰好一个匹配：继续校验该 export 的完整身份、Owner、Schema 和触发绑定。

Compiler MUST NOT：

- 从相似名称、OpenAPI operationId 或自然语言描述猜测；
- 根据入站 Body 选择 Schema 或 API 版本；
- 选择最新发布物或自动版本协商；
- 使用未声明依赖中的全局 IngressCatalog；
- 仅凭 source/service/operation 三个字符串就声称已经完成 Owner 身份验证。

依赖存在只允许 Compiler 链接该契约，不授予任意外部 NF 访问权限，也不代表部署已启用对应 Integration。实际准入仍由受信部署策略授权。

## 4. Ingress Operation 的逻辑字段

每个 Ingress Operation export 必须提供以下逻辑字段。具体 YAML 序列化由本契约版本固定；不得由每个 Integration Owner 自行发明不兼容的字段含义。

### 4.1 稳定导出身份

- id：非空、稳定、包内唯一的精确 export ID；
- event：精确的 source/service/operation 三元组；
- adapter：非空的 Integration 内部适配器身份，由受信部署绑定到实际运行实现；
- owner：继承所属 IngressCatalog.metadata.owner，不在 operations[] 中重复声明。

Catalog 的 apiVersion 固定 operations[] 中所有 Ingress Operation export 的结构版本。每个操作的有效 Owner 为 Catalog Owner；Compiler 对每个 (exportKind=ingressOperation, exportId) 使用独立的 trusted dependency Owner binding 核验。export identity 由受信 Package ID、Owner、exportKind、export ID 和 snapshot digest 共同确定，不再引入第二套可漂移的 contractVersion。adapter 只是实现身份，不是 Owner 身份或网络地址。

同一 id 的任何协议版本、Schema、归一化、Correlation、响应或安全语义变化都必须产生新的不可变快照；不得原地改变已被 Skill pin 的内容。

### 4.2 协议来源与 API 身份

protocol 至少声明：

| 字段 | 要求 |
|---|---|
| specification | 精确标准身份，例如 3GPP TS 29.502 |
| release | 精确发布版本；不得使用 latest、范围或浮动标签 |
| apiUriVersion | API URI 版本 |
| openapi.artifactRef | dependency snapshot 内精确 OpenAPI artifact 身份 |
| openapi.artifactDigest | 对应 artifact 的 SHA-256 摘要 |
| openapi.operationId | 精确 OpenAPI operationId |
| openapi.method | 精确 HTTP method |
| openapi.path | 精确 path template，不允许 wildcard route |

OpenAPI artifact digest 必须覆盖被链接的 paths、operation、requestBody、responses 和 Schema 引用。外部 $ref 必须被解析到同一受信快照闭包中的精确内容；禁止运行时远程解析。

一个 Ingress Operation export 只代表一个精确的协议操作。相同的 Service-Operation 名称在不同 API release、API version、HTTP method 或路径下，不得被当作同一个 wire contract。

### 4.3 请求媒体类型与源 Schema

request 必须声明：

- acceptedMediaTypes[]：精确允许的 wire media types；
- maxBytes：单个 wire request body 的总字节上限，包含 multipart framing 和所有 parts；
- sourceSchemas[]：每种请求媒体类型对应的源 Schema 身份及摘要；
- normalizedSchemaRef 和 normalizedSchemaDigest：唯一的 Skill-facing normalized request Schema；
- normalization：按每种 accepted media type 声明的确定性、内联、可静态检查的 source-to-normalized mapping。

acceptedMediaTypes/sourceSchemas/normalization.representations 中的 mediaType 固定记录规范化后的 type/subtype essence（小写，不包含参数）。Integration 必须独立解析并校验 Content-Type parameters；例如 multipart/related 的 boundary 参数必须存在且符合受限长度/词法要求，参数不得被误认为另一种 media type。除 pinned OpenAPI/部署 profile 明确允许的参数外，未知参数必须拒绝。

sourceSchemas 必须与 acceptedMediaTypes 一一对应：每个允许的 media type 恰有一个源 Schema，不得存在缺失或多余的源 Schema。源 Schema 必须与 pinned OpenAPI artifact 中的 Request Body / multipart part 声明一致。Integration Adapter 按该精确 OpenAPI artifact 的方言验证 wire request；Compiler 验证源 Schema 引用及其 artifact/digest 归属，但不要求完整 OpenAPI Schema 方言落入 CA-SL 的 JSON Schema 子集，也不在 Compiler 中执行协议 wire validation。normalizedSchemaRef 才是 Compiler 用于 wait.output 路径、类型赋值和 CA-SL 静态分析的 Schema，必须符合 CA-SL 支持的 JSON Schema Draft 2020-12 子集。

### 4.4 归一化规则

Integration Adapter 按以下顺序处理入站请求：

1. 识别精确 API route、method 和 API version；
2. 验证已认证对端身份及授权；
3. 验证请求媒体类型；
4. 按 pinned source Schema 验证 wire request；
5. 按 pinned normalization mapping 转换为 normalized request；
6. 按 normalized Schema 验证转换结果；
7. 从已验证的 normalized request 和可信对端身份派生 correlation；
8. 将该请求关联到唯一的 armed expectedIngressRef；
9. 创建或恢复 delivery / response obligation 记录，再向 Host 提交。

Schema 选择不能依赖未验证的 Body 字段。未经认证的 source、UE 标识、Session 标识或回调字段不得用于选择 Run。

归一化必须确定、可复现、可审计。每个必需的源字段必须有明确目标字段；可选或忽略字段必须在 mapping 中明确标注。未知的语义字段、缺失的必需字段、类型不符和不支持的 media type 必须拒绝或隔离，不能静默丢弃、猜测或截断。

request.normalization.representations[] 必须对每个 accepted media type 恰好声明一个映射配置。每个配置至少包含精确 mediaType、multipart parts（适用时）和 mappings[]。multipart 配置还必须声明 `minBinaryParts` 与 `maxBinaryParts`，分别约束实际 wire message 中 binary parts 的数量下限和上限；它们不是 Catalog 中可声明的 part 定义数量。每条 mapping 必须包含 source selector、normalized target JSON Pointer 和 transform。Normalization mapping 是 IngressCatalog operations[] 中的内联声明式数据，随整个 dependency snapshot digest 一起固定；本版不再引入独立 mappingRef/mappingDigest。

source selector 的 kind 仅允许 path、query、header、json-body、multipart-json 和 multipart-binary。path/query/header 必须带精确参数名；json-body 必须带 JSON Pointer；multipart-json 必须带精确 part 名及 JSON Pointer；multipart-binary 必须带精确 part 名。对于源协议使用 `RefToBinaryData` 关联 multipart `Content-ID` 的情况，multipart-binary source 还必须声明 `contentIdReference: { part, pointer }`，指向根 JSON part 中对应的引用属性。`ignoredSources[]` 用于从被整体映射的 JSON object 中屏蔽明确列出的传输字段；屏蔽在映射前执行，祖先对象的 identity mapping 不得重新暴露这些字段。3GPP 的 `n1SmMsg`、`n2SmInfo`、`n2SmInfoExt1` 都是 RefToBinaryData，必须从 JSON 业务映射中屏蔽，再分别以验证后的不可变 binary reference 暴露；不得把原始 `contentId` 留在 Skill-facing normalized request 中。`n2SmInfoType` 与 `n2SmInfoTypeExt1` 是业务协议字段，不得一并屏蔽。header 只有在源协议明确将其定义为业务输入且 normalized Schema 显式声明对应属性时才允许映射，认证和传输控制 Header 不得映射。

transform 的初始封闭集合仅为 identity、parse-integer、parse-number、parse-boolean 和 binary-content-ref。identity 要求来源 Schema 类型可直接赋值给目标属性；parse-integer 只接受规范十进制整数词法且不得溢出；parse-number 只接受规范十进制有限数值且不得舍入或产生非有限值；parse-boolean 只接受精确小写 true/false；binary-content-ref 只适用于 multipart-binary 并生成 normalized Schema 声明的受限不可变内容引用。不得执行任意 CEL、Python、表达式、反射、网络查询、隐式字符串化、locale 转换、截断或有损转换。

对于 3GPP TS 29.502 V19.5.0 §6.1.2.4 的 multipart/related，Integration MUST 校验每个 binary part 的 `Content-ID` 与根 JSON part 中对应 `RefToBinaryData.contentId` 属性逐一匹配。`RefToBinaryData` 的结构由 TS 29.571 V19.5.0 §5.4.4.14 定义；`contentIdReference.part` 必须指向该 representation 的 JSON 根 part，`pointer` 必须指向精确 RefToBinaryData 对象中的 `contentId` 字符串属性；引用缺失、悬空、重复、指向错误 part、Content-ID 重复或存在未被引用的 binary part，均必须拒绝/隔离。part 名称不是 Content-ID，不能代替该关联校验。归一化后的业务字段只暴露受限 binary content reference，不把原始 Content-ID 当成业务身份。对 `application/json` representation，由于不存在 binary part，任何非空 RefToBinaryData 引用都必须拒绝，不得保留成看似可用的内容引用。

对每一种 media type，normalized Schema 的每个 required 属性必须恰好由一条 mapping 提供；不得有重复 target、悬空 source、未知 target 或类型不可赋值。未映射源字段/part 默认拒绝；只有 pinned source Schema 明确声明其可忽略，且 export 显式列出该忽略项时才可丢弃。可选 normalized 属性可以在对应 wire representation 中缺失，但不得合成默认值。真实 Adapter 必须通过 conformance fixtures 证明执行结果与内联 mapping 完全一致。禁止以 Skill Script、CEL 或 LLM 在运行时临时完成协议归一化。

### 4.5 Multipart 与二进制内容

对 multipart 或二进制 part，Integration export 必须明确：

- part 名称及媒体类型；
- 对应源 Schema / OpenAPI part 定义；
- normalized request 中的目标字段；
- 每个 part 的最大长度与允许的内容类型；
- 整个 wire request body（包含 multipart framing 和所有 parts）的总 maxBytes；
- normalized Schema 中对应的 binary reference Schema 身份；
- 二进制内容的不可变引用表示及其生命周期。

二进制内容不得因方便而转为未校验的任意字符串，也不得被静默丢弃。若 normalized request 暴露二进制引用，该引用是受限的业务数据引用，不是 normalizedPayloadRef、expectedIngressRef 或 responseObligationRef。

二进制业务引用必须绑定内容摘要、媒体类型、长度、不可变性、授权范围和保留期限；不得是任意 URL 或本地文件路径。每个 multipart part 的 maxBytes 是该 part 的独立上限，request.maxBytes 是整个 wire request body（含 framing）的总上限，binaryContent.maxBytes 是单个不可变 binary object 的上限。Integration 必须在读取/缓冲完整 Body 前执行可用的流式总长度限制。

binaryContent.retention 从 delivery 持久接受时起算，必须使用固定正时长，并覆盖所有可能引用该内容的 Skill Consumer 的最后一次访问，包括 Run 暂停、Host/Runtime 恢复和 Tool 重试窗口。Admission 必须将 retention 与部署允许的最大 Invocation 生命周期及恢复宽限期比较；若无法证明内容在最后一个声明 Consumer 完成前不会过期，则不得链接该二进制 Schema。不得仅以 HTTP response deadline 或某个 Node 的预期耗时替代完整 Consumer 生命周期。

Skill 只能通过声明的 Tool/Owner 能力消费该引用，不能直接访问 Host 的内部 Payload Store。若 Integration 无法安全表达某个 part，必须拒绝该请求。

### 4.6 规范化数据与私有传输元数据隔离

normalized request Schema 只包含明确声明的业务输入。默认不得包含：

- Authorization、Cookie、TLS 证书或访问令牌；
- Host 内部 correlation index；
- runId、waitOccurrenceRef；
- expectedIngressRef、deliveryRef；
- responseObligationRef、HTTP/2 stream 或 socket handle；
- Host/Runtime 内部持久化路径或数据库主键。

若某个协议字段确实属于业务输入，Integration 必须在 normalized Schema 中显式定义，并说明其业务语义；不能因为它出现在 HTTP Header 或 transport envelope 中就自动暴露。

## 5. 对端身份与协议安全

### 5.1 认证身份

Integration 必须使用受信传输认证结果确定 peer identity，并验证其 NF type 与 event.source 一致。

认证方式由部署安全配置决定，可使用受信 TLS/mTLS、OAuth 2.0 或部署认可的组合。IngressCatalog 只引用非秘密的 profile identity；证书、私钥、client secret、token、JWKS 内容和运行时凭证不得写入 Skill、IngressCatalog 或公开 mapping。

### 5.2 授权

认证成功不等于授权成功。Integration 必须验证：

- peer NF type 是否允许调用该 Service-Operation；
- peer identity 是否属于部署配置允许的实例/信任域；
- API version、route、method、media type 是否在该 export 的允许范围；
- 当前 deployment 是否启用了该 Ingress Operation；
- 请求是否满足协议要求的目标资源与授权范围。

Host 不重复执行协议级认证或解析；Host 只接受受信 Integration Adapter 的交付。Runtime 不从原始 HTTP 请求推导授权。

### 5.3 失败处理

认证失败、授权失败、API version 不匹配、路径/method 不匹配、媒体类型不支持、源 Schema 无效或 normalized Schema 校验失败的请求：

- 不得满足任何 Wait；
- 不得重置 Wait timeout；
- 不得创建新的 Invocation；
- 不得通过猜测关联到其他 Run；
- 必须由 Integration 按部署和协议策略拒绝或隔离，并留下可审计的拒绝记录。

## 6. Correlation 与预派发注册

### 6.1 Correlation key

correlation.keyFields[] 必须声明一组足以唯一匹配该协议事件的 normalized request 字段。correlation.armInputSchemaRef 必须声明 Runtime 在预派发注册时提交给 Integration 的 typed correlationBinding Schema；它必须与 keyFields 一一对应，且只包含建立匹配所需的值。每项至少包含：

- normalized request 内的精确 JSON Pointer；
- 该字段的身份维度，例如 session、resource 或 correlation；
- 精确比较/规范化规则；
- 字段的静态类型约束。

Correlation key 的每个字段必须是可稳定比较的标量。归一化完成后只允许精确值比较。若协议要求大小写、编码或标识格式规范化，该处理必须在 pinned normalization mapping 中完成并受其 digest 约束；Correlation 阶段不得再执行隐式转换。不得按字段名相似、前缀、模糊字符串、时间接近或“最新 Run”推断匹配。

Peer identity、API export identity 和 correlation key 共同限定匹配范围。仅凭 SUPI、DNN、S-NSSAI 或一个不具备唯一性的资源标识，不能推断某个 Wait occurrence。

### 6.2 预派发绑定的两种来源

Integration export 必须声明它支持的 Wait arming 模式。

**A. 由入口 Invocation Context 启动**

适用于 Wait-bearing Node 本身就是 Procedure start 的场景。Export 声明允许 start arming，并为每个 correlation key 字段指定一个 Invocation Context JSON Pointer，以及 correlation.armInputSchemaRef 中对应的 bindingPath。arming.start.bindings[] 的每项包含 requestKey、bindingPath 和 source；source.kind 固定为 invocation-context，source.path 为 Context JSON Pointer。

Compiler 必须验证该路径由 Skill 已声明的 Host Context Schema 或 Request Schema 提供，类型与 correlation key 兼容，并可赋值给 armInputSchemaRef 对应字段。Runtime 在 Node 激活之前从已准入 Context 物化绑定并注册。

**B. 由前序 Tool Operation 触发**

适用于前序出站 Operation 可能导致外部 NF 后续发送该入站请求的场景。Export 必须声明允许的触发 Operation 集合。每个触发项至少包含：

- 精确 ToolCatalog Package ID；
- 精确受信 Owner；
- kind = operation；
- 精确 Operation ID；
- 该 Operation 的 Input Schema 身份（由 Compiler 从精确 ToolCatalog export 解析，不在 IngressCatalog 中复制）；
- 将 correlation key 映射到 Operation arguments JSON Pointer 和 correlation.armInputSchemaRef bindingPath 的绑定规则。arming.triggers[].bindings[] 的每项包含 requestKey、bindingPath 和 source；source.kind 固定为 operation-argument，source.path 为该 Operation 已物化 arguments 的 JSON Pointer。

触发 Operation 必须来自 Skill 已声明的可信依赖快照。Observation、Predicate、Script、Capability ID、Tool display name 或网络地址不能充当 triggering Operation identity。

Compiler 必须从 Procedure 图中解析触发 Operation 的实际调用点，并验证每个 correlation 值都能从该 Operation 的已物化 arguments 中取得。该 Operation 身份必须在整个 dependency closure 中解析到恰好一个 ToolCatalog Operation export；若同一 Package ID 的多个快照或多个 Owner/export 候选导致歧义，必须拒绝。Runtime 必须在 Operation 派发前使用同一份已物化 arguments 建立 correlation binding；不得等 Operation 返回后再推导。

### 6.3 每条入边的唯一触发关系

对每个 Wait-bearing Node 的每条可达入边，Compiler 必须证明以下二者之一：

- 若该 Node 是 Procedure start，存在完整且可用的 start Context binding；
- 否则，该路径在进入 Wait Node 之前恰好经过一个与该 Ingress export 匹配的 triggering Operation 调用点，并且该调用点能在派发前物化所有 correlation key。

不同入边可以对应 export 中声明的不同 triggering Operation，但每条实际路径必须唯一。某条路径缺少触发器、出现多个无法消歧的触发器、参数缺失、参数不可用或参数类型不匹配时，Compiler 必须拒绝该 Wait 绑定。

所有入边仍必须解析到同一个精确 Ingress Operation export、normalized request Schema、Correlation contract 和 response contract。若事件身份或契约不同，作者必须使用不同 Wait-bearing Node，再通过普通 Procedure 图汇合。

### 6.4 注册顺序

Runtime 在派发 triggering Operation 之前必须：

1. 创建新的 opaque expectedIngressRef；
2. 将其私有绑定到精确 Run、目标 Node、Wait occurrence/generation 和已解析 Ingress export；
3. 通过 Generic Host 持久化注册请求；
4. 要求 Integration Adapter 验证 correlation binding 并建立唯一匹配槽；
5. 只有收到持久化的 ARMED acknowledgement 后，才允许派发 triggering Operation。

若 arm 失败或 acknowledgement 状态不确定，Runtime 必须使用相同幂等请求恢复/确认注册；在确认前不得派发。不得“先发送再关联”。

注册不等于 Node 激活，不启动 Wait timeout，也不使 wait.output 可用。事件若在注册后、目标 Node 激活前到达，Integration/Host 必须按同一个 opaque expectedIngressRef 持久缓冲；只有 Runtime 实际选中该 Node 时才可消费。若其他路由被选中，未激活的注册必须失效，缓冲事件不得重新分配给其他 Wait。

## 7. 并发、重复与迟到消息

### 7.1 并发唯一性

Integration 必须证明一个经过认证、验证和归一化的请求最多匹配一个仍有效的 armed expectedIngressRef。

若匹配结果为零或多个，必须拒绝/隔离。不得选择创建时间最新、最近活跃、SUPI 相同或其他启发式候选。

同一 UE 可以有多个并发 Run；同一资源也可能出现连续 Wait occurrence。Correlation 必须区分这些情形。

### 7.2 Wire discriminator

若协议提供 request ID、transaction ID、generation 或其他可验证 discriminator，Ingress export 的 staleDelivery 必须声明 strategy=wire-discriminator，并声明 discriminator 的来源。v1alpha1 支持两种来源：

- `normalized-request-path`：从已验证的 normalized request 中读取精确 JSON Pointer；该字段必须在源 Schema、归一化映射和受信协议定义中闭合，并且必须是协议定义的逐请求身份字段，在同一逻辑请求的所有重传中保持不变；资源 ID、UE/SUPI、PDU Session ID、Content-ID 和时间戳都不满足这一条件；
- `authenticated-header-parameter`：当前仅支持 3GPP SBI 的 `3gpp-Sbi-Request-Info` header 中的 `idempotency-key` 参数。Peer profile 必须要求该参数在每个请求中提供；Integration 必须按 TS 29.500 解析参数，而不是把整个 Header 字符串当作 ID。

对 TS 29.502 V19.5.0 `UpdateSmContext`，`smContextRef` 只是资源 URI 路径参数，不能作为 successive Wait 的 wire discriminator；该 API 未定义可替代它的必需逐请求 ID。TS 29.502 §6.1.2.5 规定 AMF 可在新 TCP 连接上重试同一 HTTP 请求，并在重试时更新 `3gpp-Sbi-Origination-Timestamp` 与 `3gpp-Sbi-Sender-Timestamp`（若存在），因此这些时间戳不能用作 discriminator。TS 29.500 §5.2.3.3.3 的 `3gpp-Sbi-Max-Rsp-Time` 只表示 HTTP Client 等待响应的时长；它与适用的发送时间戳共同用于计算 responseDeadline，不是请求身份，也不是 maximumLateArrival 或 tombstoneRetention 的依据。重试时该时长也可能重新设置。

Wire discriminator 是外部请求身份，不是用于预派发匹配 Run/Wait 的 correlation key；它不要求在 arming 时预先知道，也不要求加入 normalized business Schema。Integration 在接收请求时提取 discriminator，并在匹配/提交 delivery 前检查它是否已被消费。消费记录必须按源协议定义的唯一性作用域持久化，不能擅自用 authenticated peer 或 Ingress export identity 缩小该作用域；`basisRef` 必须支持该作用域及其有限保留期。缺失、重复复用或格式不合法时必须拒绝/隔离，不得退回到猜测或选择 newest。

wire-discriminator 策略还必须声明 maximumLateArrival、clockSkewAllowance、discriminatorRetention 和 basisRef。Integration 持久化已消费 discriminator 时，索引键必须遵循源协议定义的唯一性作用域，不能机械地统一加上 authenticated peer、Ingress export identity 或 expectedIngressRef。对于 3GPP SBI `idempotency-key`，索引必须使用 TS 29.500 定义的目标 NF 重复检测作用域；同一目标 NF 的不同 Ingress Operation export，以及同一 NF Set 中可替代处理该请求的实例，必须共享同一判重视图。不得把 AMF peer、单个 Ingress export 或 expectedIngressRef 加入该协议身份键而缩小作用域。记录值应保留首次接受请求的 Ingress export、expectedIngressRef、deliveryRef 及其响应责任，以便同一请求重试时只重放到原 occurrence，而不分配给新 Wait。其他 wire discriminator 使用其 pinned protocol artifact 定义的作用域，并由 basisRef 支持。discriminatorRetention MUST strictly exceed maximumLateArrival + clockSkewAllowance；相等不接受，以避免边界时刻的过期/匹配竞态。迟到副本在该保留期内到达时必须识别为已消费请求，不得分配给新 Wait。若无法证明有限迟到窗口或提供可审计依据，则不得使用 wire-discriminator 策略。

3GPP 的 `3gpp-Sbi-Request-Info: idempotency-key=...` 在客户端/服务端启用 TS 29.500 V19.5.0 §5.2.8 的重复请求检测时可提供这一保证；该机制是可选能力，因此不能假定所有 AMF 都会发送。SCP 若参与转发，必须按 TS 29.500 将该 key 原样转发。该 key 的唯一性作用域是目标 NF，而不是单个 AMF peer 或单个 Ingress export；同一目标 NF 的多个 Operation export 以及同一 NF Set 内的替代实例必须共享已消费 key 的判重视图。若不要求并验证该 Header，则必须使用 single-flight/tombstone 策略。只在 Host/Runtime 内生成的 generation counter 不能区分外部迟到请求，除非该 generation 也能由入站协议请求可靠证明。

### 7.3 无 Wire discriminator 时的 Single-flight

如果协议没有可区分连续 Wait occurrence 的 on-wire discriminator，Integration 必须证明等价的 single-flight + stale-delivery/tombstone 策略：

- 对相同 correlation resource key，同一时刻最多允许一个有效 Wait occurrence；
- 当有效请求首次与已 armed Wait 匹配并被持久接受时，Integration MUST 原子消费该 correlation resource key，并在向 Host/Runtime 投递前立即建立 tombstone；
- 后续 `EVENT_ACCEPTED` 只关闭该 Wait occurrence，不释放 tombstone。无论该 occurrence 最终以 `EVENT_ACCEPTED`、`TIMEOUT`、`CANCELLED` 还是 `INVALIDATED` 结束，tombstone 都必须持续到 retention 到期；
- export 必须声明 maximumLateArrival、clockSkewAllowance 和 tombstoneRetention 三个固定时长；
- tombstoneRetention MUST strictly exceed maximumLateArrival + clockSkewAllowance；相等不接受，以避免边界时刻的过期/匹配竞态；
- 在 tombstoneRetention 到期前，不得为相同 key 建立下一 Wait；
- maximumLateArrival 与 clockSkewAllowance 的依据必须由可审计的协议或部署保证支持，不得由 Skill 作者随意声明；
- maximumLateArrival 使用 CA-SL 固定正时长的同一词法子集；若无法证明有限的迟到窗口，则不得复用该 key；Compiler/Admission 必须 fail-closed。

当一个有效请求首次匹配到 armed expectedIngressRef 并被 Integration 持久接受时，Integration 必须原子地消费该 correlation resource key 并立即启动 tombstone；不得等 Runtime 消费事件、业务 Node 完成或 paired response 交付后才启动。这样同一请求的重试/副本不能落入下一 Wait。该 tombstone 仅阻止将旧请求分配给新 occurrence，不得删除首次接受的 delivery 记录：Integration 必须保留稳定的 deliveryRef、原始 expectedIngressRef，以及（paired 模式下）原始 responseObligationRef。相同请求重试时必须重放原 delivery/disposition 并继续关联原 occurrence；不得因为 tombstone 已存在而将其重新匹配给下一 Wait，也不得为同一请求创建第二个 Runtime delivery。若 Wait 在没有匹配请求的情况下因 TIMEOUT、CANCELLED 或 INVALIDATED 关闭，则在该关闭状态提交时启动 tombstone。tombstone 到期前到达的请求必须作为旧请求副本/迟到请求处理，不得匹配新 Wait。

如果协议允许同一 resource key 在 tombstone 窗口内出现合法的下一条独立请求，而又没有可验证的 wire discriminator，则 single-flight-tombstone 策略不适用于该接口；Compiler/Admission 必须拒绝该绑定，要求更强的 wire discriminator 或其他协议级可验证区分依据。

不得只用 Runtime 内部 generation counter、expectedIngressRef 随机性或数据库行版本声称解决外部消息的迟到歧义。

### 7.4 重复交付

Integration 为一次已接受的 normalized delivery 生成稳定 deliveryRef，并在重试时保持不变。Host 按 deliveryRef 幂等持久化。

Integration 必须声明其协议请求去重身份来源及其身份作用域。允许的来源为 protocol-request-id、trusted-gateway-request-id、3gpp-sbi-idempotency-key，或在同一 expectedIngressRef 范围内的 canonical-request-digest。作用域必须与该身份来源的权威定义一致：canonical-request-digest 使用 expected-ingress；3gpp-sbi-idempotency-key 使用 target-nf；protocol-request-id 与 trusted-gateway-request-id 使用各自协议/网关定义的作用域。不得把所有来源强制缩小为 authenticated peer + Ingress export identity + expectedIngressRef。该协议身份去重与 Host 对稳定 deliveryRef 的幂等持久化是两个不同层次；重试同一已接受请求时必须复用同一个 deliveryRef，并继续关联首次接受的 expectedIngressRef / response obligation。

对 3GPP SBI，`3gpp-Sbi-Request-Info` 中的 `idempotency-key` 仅在客户端启用 TS 29.500 §5.2.8 的重复请求检测时才存在；同一重传必须复用同一 key，独立请求不得复用。该 key 可同时作为 staleDelivery 的 authenticated-header-parameter discriminator。不要使用 `3gpp-Sbi-Correlation-Info` 代替：它承载 UE/subscriber correlation information，不是每个请求唯一的事务身份。

duplicate.identitySource 用于识别一次协议请求的重试，不自动构成 successive Wait generation 的 wire discriminator。只有当 request ID 可从已验证的入站请求或受信 Header 中稳定取得、在协议规定范围内对每个原始请求唯一并在重传时保持不变时，它才可以同时用于 staleDelivery.strategy=wire-discriminator；wire discriminator 不需要加入 correlation.keyFields，因为 correlation.keyFields 负责把请求匹配到资源/Wait，而 discriminator 负责排除旧请求副本。若 identitySource 同时用于 staleDelivery，duplicate.scope 与 discriminator 的持久化作用域必须完全一致；Host 的 deliveryRef 去重仍按原 delivery 记录幂等执行，不能改变协议身份的唯一性作用域。

若使用 canonical request digest，初始 profile 定义为对 normalized business value 执行 RFC 8785 JSON Canonicalization，再将每个 binary content reference 替换为其 media type、长度和 SHA-256 内容摘要描述，最后对该确定性字节序列计算 SHA-256。不得把 payload-store URL、临时引用句柄或其他传输元数据纳入摘要。摘要只在同一个 expectedIngressRef 范围内用于识别重复；同一 Wait occurrence 内两个内容完全相同的独立请求将被视为重复。若业务协议允许同一 Wait 下出现两个内容相同但语义独立的请求，而 Integration 无法区分二者，必须拒绝/隔离歧义情形，不得声称 exactly-once 网络投递。

## 8. 配对协议响应

### 8.1 响应模式

每个 Ingress Operation 必须明确声明以下之一：

- response.mode: none：该协议操作不要求由本次 Ingress delivery 配对返回协议响应；
- response.mode: paired：每次接受的入站请求都产生一个由 Integration 管理的 response obligation。

不得仅根据 HTTP method 或 API operationId 猜测响应模式。

paired 模式下，Integration 在接受协议请求时创建私有 responseObligationRef，并将其与 expectedIngressRef 关联。该引用由 Integration/Host 保存，Runtime 和 Skill 不得接收。

### 8.2 响应边界与 Producer 来源

CA-SL 的 wait.response.after 只选择一个 Node completion boundary；省略时默认为 Wait-bearing Node。它不声明协议 Schema，也不携带响应句柄。

为避免 Integration Package 依赖 Skill 专属 Node ID，**Producer 来源由 Ingress export 声明阶段类型，而不是声明 Skill SourcePath**：

- response.result.producer: operation：响应结果来自 <response.after>.operation.output；
- response.result.producer: observation：响应结果来自 <response.after>.observation.output；
- 仅当唯一的 response disposition 是固定的 body: none 时，才不声明 result Producer；多个 bodyless dispositions 仍须通过 typed result 和 dispositionSelector 明确选择。

Compiler 根据 Skill 的 wait.response.after 和 Ingress export 的 producer 类型，确定唯一 SourcePath。该 Producer 必须存在、其输出必须在每条正常到达 response boundary 的路径上可用，并且其 Output Schema 必须可赋值给 Integration export 声明的 responseResultSchema。

若响应需要早前 Node 的数据，Skill 必须通过 boundary Node 的 Operation/Observation arguments 显式传递这些值，并由该 Producer 输出完整、类型化的 response result。Integration export 不得引用某个 Skill 的 Node ID；Runtime/Integration 不得读取任意历史 Run 输出或猜测 latest output。

### 8.3 响应 Schema 与映射

paired response 必须声明非空的 `response.dispositions[]`。Disposition 表示 HTTP 状态语义，而不是媒体类型；每个 disposition 至少声明唯一 `id`、精确 HTTP `status` 和 `body` 模式。同一 status 只能有一个 disposition，但一个 body-bearing disposition 可以包含多个可协商的 representation。因此 UpdateSmContext 的 200 JSON 与 200 multipart 是同一个 `status: 200` disposition 下的两个 representation，不能伪造为两个不同 disposition。

- `body: required` 时，必须声明非空 `representations[]`；每个 representation 有其作用域内唯一的 `id`、精确 `mediaType`、`responseSchemaRef`、`responseSchemaDigest` 和 `maxBytes`。`maxBytes` 是该 representation 整个 wire body 的总字节上限，不含 HTTP headers。
- `application/json` representation 不得声明 multipart parts；`responseSchemaRef` 指向完整 JSON response body Schema。
- `multipart/related` representation 必须声明 `rootPart`、`parts[]`、`minBinaryParts` 和 `maxBinaryParts`。`rootPart` 必须是 parts 中第一个且唯一的 JSON part（UpdateSmContext 固定为 `jsonData`），其 Schema 必须与 representation 的 `responseSchemaRef`/digest 一致；至少声明一个 binary part。每个 part 都必须声明精确名称、媒体类型、kind、required、maxBytes；JSON part 另须绑定其 Schema/digest。实际 wire message 中 binary part 的数量必须落在 min/max 范围内；part maxBytes 不得超过 representation.maxBytes。
- `body: none` 时，不得声明 representations、Body Schema 或 Body mapping。204 是这种 disposition，不得附带空 JSON 或 multipart framing。

`response.result` 是 typed result 绑定。只要任一 disposition 为 `body: required`，就必须声明 `responseResultSchemaRef`、`response.result.producer`（operation 或 observation）和非空 `response.result.mappings[]`。若有多个 dispositions，或任一 disposition 有多个 representations，还必须声明 `dispositionSelector`。Selector 每个 case 选择一个 disposition；对于 body-bearing disposition，还必须同时选择该 disposition 下精确的 `representationId`；bodyless disposition 不得选择 representation。所有允许的 disposition/representation 组合必须被精确覆盖，不能依赖 Accept header 或运行时猜测替代业务结果选择。

每条 response mapping 必须声明 `dispositionId`、`representationId`、`from`（responseResultSchema 内的 JSON Pointer）、`target` 和 `transform`。target 是以下封闭集合之一：

- `json-body`：写入 `application/json` representation 的 JSON Pointer，transform 仅允许 `identity`；
- `multipart-json`：写入 multipart representation 中指定 JSON part 的 JSON Pointer，transform 仅允许 `identity`；
- `multipart-binary`：从 typed immutable binary content reference 读取内容，写入指定 binary part，并声明 `contentIdField`（JSON root part + 指向 `RefToBinaryData.contentId` 字符串属性的 JSON Pointer），transform 固定为 `binary-content-ref`。

对于 multipart response，Integration MUST 生成 `Content-Type: multipart/related`，包含唯一 boundary 和 `type=application/json` 参数；`rootPart` 必须是第一个 part，若发送 `start` 参数则必须精确指向该 root part。Integration MUST 为每个实际输出的 binary part 生成该消息内唯一、符合 Content-ID 语法的值，将其写入 `contentIdField` 指定的 JSON root 属性，并在对应 binary part 的 `Content-ID` header 中写入同一个值。Skill/Producer 不得自行提供或复用 wire Content-ID。每个已声明 binary part 必须恰有一条映射；每个 `contentIdField` 必须唯一且位于 `rootPart`；不得存在未映射的 binary part、悬空引用、重复 Content-ID 或无对应 binary part 的 RefToBinaryData。multipart response 至少实际输出一个 binary part；可选 part 只有在对应 typed reference 存在时才输出。

Representation 选择必须与 typed result 的内容一致：存在任一 binary reference 时只能选择 multipart/related；不存在 binary reference 时只能选择 application/json；bodyless disposition 不得丢弃仍存在的 JSON 或 binary response data。Integration MUST 在序列化时再次检查这一条件，不能因为 selector 选错而静默丢弃二进制内容。每个 representation 的 maxBytes 是完整 wire Body 上限，必须容纳所有实际 parts、boundary、part headers 和 framing；每个 part 的 maxBytes 不得超过 representation.maxBytes。

对 TS 29.502 `SmContextUpdatedData`，若响应包含 `n2SmInfo`，JSON root MUST 同时包含 `n2SmInfoType`，其值必须符合 pinned OpenAPI 中的 `N2SmInfoType` 定义。该字段不是二进制 part，也不能由 Content-ID 推导；responseResultSchema 必须显式声明并绑定它。此示例的 typed DTO 采用 N2 字段 all-or-nothing：`n2SmInformation` 与 `n2SmInfoType` 同时存在或同时省略；multipart JSON mapping 必须显式输出 `n2SmInfoType`。

本 5GC Step 15–17 示例的 `responseResultSchemaRef` 解析到 `schemas/update-sm-context-response-result.v1.schema.json`；`response.binaryContent.referenceSchemaRef` 解析到 `schemas/response-binary-content-reference.v1.schema.json`。前者将 Step 16 分支结果作为内部 typed Producer 数据：成功时要求 `n4Action=session-modified`，并要求 UDM 注册为 `completed` 或 `not-required`；成功结果不得同时携带 N1 SM Reject；若携带 N2 响应 binary part，其 `n2SmInfoType` 必须为 `PDU_RES_SETUP_RSP`。N2 user-plane resource setup failure 时要求 `n4Action=session-released`、`udmRegistration=skipped`、`responseRepresentation=multipart` 且 `n1SmMessage` 存在；User Plane Enforcement Policy Notification 表示无 user-plane resources established 且 policy=`required` 时要求 `n4Action=not-performed`、`udmRegistration=skipped`、`responseRepresentation=multipart` 且 `n1SmMessage` 存在。两种失败分支都禁止带 N2 响应 binary part。`step16Outcome` 和 `procedureOutcome` 仅用于内部类型/分支校验，不序列化进 `SmContextUpdatedData`。Step 18 的 SM Context Status Notify Release 及资源清理发生在 Step 17 response boundary 之后，不属于 Step 16 outcome，也不得延迟 paired response。后者定义不可变的 opaque payload reference、media type、长度和 SHA-256；payloadRef 不是 URL 或文件路径。

若任一 response representation 是 multipart/related，必须声明 `response.binaryContent`：其 `referenceSchemaRef` 必须与 responseResultSchema 中的 typed binary reference 类型一致，且必须绑定 SHA-256、immutable、`access: integration-response-only`、有限 retention 和 maxBytes。Integration 只能通过授权的不可变 Payload resolver 读取该引用，不得将任意 URL、文件路径或原始字节字符串作为引用。Retention 必须覆盖 response boundary、响应序列化、协议重试/重放及最大恢复窗口。每个 binary part 的 maxBytes 不得超过 response.binaryContent.maxBytes。

Compiler 根据 `wait.response.after`（或默认 Wait-bearing Node）和 producer 类型推导唯一 SourcePath，并验证 boundary Producer Output 对 responseResultSchema 的可赋值性。responseResultSchema 必须符合 CA-SL 支持的 JSON Schema 子集；协议 responseSchemaRef 和每个 multipart JSON root part Schema 则按 pinned OpenAPI artifact 验证，由 Integration Adapter 负责实际 wire response validation。Compiler MUST 验证每条 mapping 的 `from` JSON Pointer 在 responseResultSchema 中存在、类型可赋值给目标字段，JSON target pointer 在对应 OpenAPI response Schema 中存在；对于 multipart-binary，`contentIdField` 必须指向 root Schema 中精确的 `RefToBinaryData.contentId` 字符串属性。Compiler 还必须验证每个 body-bearing representation 的 mapping 覆盖全部 required JSON fields，每个 binary part 恰有一条 mapping、每个 mapping target 不重复且无未声明 part；dispositionSelector 的源属性必须是闭合 enum，且其值集合与所有允许的 disposition/representation 组合完整且一一对应。初始 profile 不得执行脚本、CEL、任意表达式或读取历史 Run 输出。

若仅声明一个 body: none 的 response disposition，则 response.result 可以省略；该 status 是固定的，不需要 Producer 来选择。若有多个 bodyless dispositions，也必须使用 typed result 和 mapping 明确选择，不能依赖运行时猜测。

映射由 Integration 拥有，不由 Skill 重复声明。若协议要求响应体，则不得以空 Body 或 Runtime Trace 代替。Integration 必须在持久接受请求前检查 HTTP Accept 与所有可能的 body-bearing disposition representation 是否兼容；若后续可能选择的响应表示不被请求方接受，必须在提交 Ingress delivery 前按协议/HTTP 规则拒绝（通常为 406），不得先触发业务执行再发现无法序列化响应。

v1alpha1 支持 `application/json` 与 `multipart/related` 两种显式 response representation，但不支持任意媒体类型或不透明 URL/文件路径作为二进制引用。multipart response 必须通过 `response.binaryContent`、immutable typed reference、root JSON part、逐 part Schema/大小限制和显式 Content-ID mapping 完整声明；缺少任一绑定时 Compiler/Admission 必须拒绝，不得省略、字符串化或伪造 binary parts。

### 8.4 成功、早期失败和响应超时

Integration export 必须定义：

- response.dispositions[] 中每个允许的 HTTP status/body 模式及其 representations、Schema、multipart parts，以及 typed response result 到 disposition/representation/Body 的映射；disposition id 和 HTTP status 在该 Ingress export 内必须唯一，同一 status 的不同媒体类型应建模为同一 disposition 下的 representations；该映射表达协议响应，不代表 Skill Goal 已 PASS；
- 在响应 Producer 尚未产生可用结果前，Run 提前以 FAILED、UNRESOLVED 或 SAFE_STOPPED 结束时的显式 failure response mapping；
- response deadline 的来源、起算点、时钟语义与到期处置；
- response obligation 的持久化、重放、重复响应和失去原传输通道后的恢复策略。

早期失败响应可以是协议允许的 bodyless response，或由 Integration Package 内不可变的 responseRef 定义、并经过协议 Schema 校验的固定错误响应。responseRef 必须绑定精确 status、media type、response Schema 和固定错误 Body；不得从任意 Run summary、Host 私有字段或未类型化历史输出拼接失败 Body。

paired 模式的 deadlinePolicyRef 必须解析到受信部署策略，明确有限响应期限、起算事件、时钟基准和允许的最大时钟偏差。没有客户端 deadline header 时，默认起算事件是 Integration 首次收到完整且最终被接受的有效 wire request 的时刻；若协议规定更早的起算点，则必须采用协议规定的起算点。Integration 在持久接受 delivery 时计算绝对 responseDeadline，并随 delivery 提交给 Host。

对于 3GPP SBI，deadlinePolicyRef 必须按 pinned TS 29.500 V19.5.0 §5.2.3.3.2/§5.2.3.3.3/§6.11.2 与 TS 29.502 V19.5.0 §5.2.3.3.2.1/§6.1.2.5 解释客户端响应期限 Header：当 `3gpp-Sbi-Max-Rsp-Time` 与请求起算时间 Header 同时存在时，起算时间优先使用 `3gpp-Sbi-Sender-Timestamp`；该 Header 不存在时，按 TS 29.502 该 API release 的规定使用 `3gpp-Sbi-Origination-Timestamp`。客户端 deadline 为该起算时间加 Max-Rsp-Time 毫秒；若只提供 Max-Rsp-Time 而没有适用起算时间，必须按 profile 拒绝不完整 Header，不能猜测。有效 responseDeadline 取客户端 deadline 与部署有限处理上限中较早者。客户端 Header 缺失时使用部署上限。若计算出的 deadline 已经超过允许时钟偏差范围，则必须在持久接受 delivery 前拒绝/隔离。

对同一逻辑请求的重传，3GPP SBI 可按协议更新 Sender-Timestamp / Origination-Timestamp / Max-Rsp-Time，但必须复用相同 idempotency-key。重传是新的 HTTP transport attempt，不是新的 Wait occurrence 或新的业务 response obligation。Integration 可以使用本次 attempt 的 Header 校验该 attempt 的客户端期限，并可立即重放已完成的响应或返回协议允许的超时/失败响应；但不得因重传而延长首次持久接受时提交的逻辑 responseDeadline。若本次 attempt 的客户端 deadline 更早，Integration 可以缩短当前响应期限，不能延长既有业务处理时限。responseDeadline 在线格式为带 Z 后缀的 RFC 3339 UTC instant；Host 必须原样持久化和转交，不得重新计算或延长。Runtime/Host 的本地 deadline 比较必须遵守部署策略声明的时钟偏差；若无法满足时钟保证，Integration 仍是响应逾期的最终权威，其他组件不得自行延长 deadline。Runtime 后续的 EVENT_ACCEPTED 不得重置或延长该期限；事件在 Node 激活前被缓冲时，期限仍持续流逝。

responseDeadline 与 Wait 的 pre-event timeout 是两个独立期限。Host 必须持久保存并原样转交 responseDeadline；Runtime 可以将其作为通用处理上界，但不得将其转换为 CA-SL TIMEOUT Outcome 或作者可路由的 Stage Outcome。Integration 是协议响应是否逾期及如何失败/恢复的最终权威。响应 deadline 到期时，Integration 执行协议规定的失败响应策略；Runtime 保留已接受事件的 checkpoint 和未解决的业务/资源责任。任何 Run cancellation 均使用既有全局 cancellation 语义。

### 8.5 响应交付和恢复

Integration 负责协议状态码、Headers、Body/media serialization、HTTP/2 stream 和 wire response。Host 负责持久保存私有 response obligation association，并可靠转交 Runtime 的 typed response-ready result。Runtime 只在声明的 response boundary commit 时报告结果，不等待整个 Run 终止。

Integration 必须声明响应交付是可重放还是连接绑定：

- 可重放：必须定义协议 request identity、响应缓存/重放和重复请求处理；
- 连接绑定：必须定义连接丢失、进程重启或 deadline 到期时的明确失败响应/恢复策略。

不得假设 HTTP/2 stream handle 能跨进程重启存活，也不得声称跨网络 exactly-once。

## 9. 与 Generic Host / Runtime 的边界

| 责任方 | 必须负责 | 不得负责 |
|---|---|---|
| Domain Integration | 协议认证/授权、API 版本与路由校验、wire Schema、归一化、Correlation、重复/迟到消息处理、协议响应编码与恢复 | 通过启发式选择 Run/Node；接收 Runtime 的 runId / waitOccurrenceRef |
| Generic Host | 持久保存并转交 arm/delivery/response obligation；durable inbox/outbox；deliveryRef 幂等；保护 Payload 引用 | 解析 3GPP API、解析原始 HTTP Body、推导协议 correlation、选择 Run/Node |
| Runtime | 创建/解析 expectedIngressRef；拥有 Wait occurrence 状态、deadline race、checkpoint 和同一 Run continuation；按 linked normalized Schema 消费输入 | 解析原始 HTTP/SBI；推导 peer NF 或协议资源身份 |
| Tool Owner / Agent | 执行声明的业务 Operation/Observation；提供其 Owner Output 和 Evidence | 接管协议 response obligation、监听外部 SBI 请求、拥有 Run correlation |

### 9.1 逻辑端口

以下是逻辑操作，不冻结物理方法名或 DTO：

~~~text
Runtime -> Host -> Integration:
  ArmExpectedIngress(
    expectedIngressRef,
    ingressContractRef,
    typedCorrelationBinding
  ) -> ARMED | REJECTED

Integration -> Host:
  SubmitInboundDelivery(
    deliveryRef,
    expectedIngressRef,
    ingressContractRef,
    normalizedPayloadRef,
    responseObligationRef?,
    responseDeadline?
  ) -> ACCEPTED | DUPLICATE | REJECTED

Host -> Runtime:
  InboundDeliveryAvailable(
    deliveryRef,
    expectedIngressRef,
    ingressContractRef,
    normalizedPayloadRef,
    responseDeadline?
  )

Runtime -> Host:
  ResponseBoundaryCommitted(
    expectedIngressRef,
    ingressContractRef,
    responseResultRef?
  )
~~~

Host 对 expectedIngressRef、ingressContractRef 和 Integration 私有 response obligation 做不透明转交和持久关联；Host 不解释协议 correlation。Integration 不接收 runId 或 waitOccurrenceRef。

responseObligationRef 当且仅当 Ingress export 声明 paired response 时提供；paired 模式下 responseDeadline 必须提供，并且在 Host → Runtime 的 delivery envelope 中原样转交。responseResultRef 当且仅当需要 typed Producer result 时提供：至少一个 disposition 为 body: required，或存在多个必须选择的 disposition；仅单一固定 body: none disposition 可以省略。responseResultRef 指向精确 boundary Producer output 的不可变、受保护 typed value；Host 不解释内容，Integration 只能通过授权的结果读取接口访问。

### 9.2 可靠性语义

Delivery 采用 durable at-least-once + idempotent acceptance。网络层不承诺 exactly-once。对一个 Wait occurrence 的 exactly-once Node entry 由 Runtime 的 authoritative atomic state transition 和 durable checkpoint 保证。

若 Host 与 Runtime 使用不同持久化存储，必须使用 durable inbox/outbox、幂等命令和可恢复状态；不得声称存在实际上不具备的跨存储原子事务。

## 10. Compiler 链接与静态检查

Compiler 必须对一个被引用的 Ingress Operation 执行以下链接：

1. 验证 dependency alias、Package ID、snapshot digest、Owner binding、exportKind 和 IngressCatalog apiVersion；
2. 验证 export ID 唯一，并对 wait.event 得到恰好一个匹配；
3. 验证 3GPP/OpenAPI provenance、artifact digest、method、path、operationId 和 API release；
4. 验证 accepted media types、source Schema、normalized Schema 和 mapping artifact 均在可信依赖闭包中；
5. 验证 normalized Schema 属于 CA-SL 支持的 JSON Schema 子集；
6. 验证 peer type 与 wait.event.source 一致，并验证部署 profile 引用是非秘密标识；实际 profile 是否已绑定到部署配置由 Admission/Deployment 校验，不能由 Compiler 仅凭字符串声称通过；
7. 验证 correlation key 路径、标量类型和比较规则；
8. 验证每个 Wait 入边上的 start Context 或 triggering Operation 绑定；
9. 验证 triggering Operation 是精确 ToolCatalog Operation export，且全部 correlation 参数在 dispatch 前可用；
10. 验证 single-flight/tombstone 或 wire discriminator 能防止连续 occurrence 的迟到消息串用；
11. 验证 response mode、response.after boundary、result Producer 类型和 Output Schema 赋值；
12. 验证正常响应 mapping 和所有允许的提前失败响应 mapping 完整。

Compiler 不执行协议认证，不调用真实 Integration adapter，不通过网络请求证明 API 可用，也不替代 Integration conformance tests。

## 11. 5GC 参考映射：TS 23.502 Step 15 / Step 17

以下按 3GPP TS 23.502 V19.5.0 §4.3.2.2.1、TS 29.502 V19.5.0 §6.1.2.2/§6.1.2.4/§6.1.2.5 及 Annex A.2 OpenAPI、TS 29.571 V19.5.0 §5.4.4.14 对照说明责任和身份映射。TS 29.502 的正式来源为 ETSI 发布的 V19.5.0 PDF；Annex A.1 说明 Annex A 的 YAML OpenAPI 定义是正式 API 编码依据，并在编码不一致时优先。Annex A.2 标识 `Nsmf_PDUSession`、OpenAPI 3.0.0、API version `1.4.0`。已从 ETSI 官方 companion `p0.zip` 提取 `TS29502_Nsmf_PDUSession.yaml` 并固定其 SHA-256；官方 PDF、companion ZIP 与提取 YAML 的摘要均已通过 GitHub Actions 实际下载核验。GitLab `5G_APIs` 的 `REL-19` 分支文件摘要与 ETSI companion 文件不同，因此只记录为 informative copy，不作为规范 artifact。TS 29.571 V19.5.0 Annex A.2 的 `Common Data Types`（OpenAPI 1.6.0）也已从 ETSI 官方 PDF 和 companion ZIP 提取并固定 SHA-256。完整来源、字节长度、摘要及依赖范围见 [TS 29.502 V19.5.0 OpenAPI source lock](artifacts/ts-29.502-v19.5.0-nsmf-pdusession-openapi-source-lock.yaml)。CI 对本 IngressCatalog 实际映射的请求/响应字段执行引用解析：N1/N2/N2 扩展的 `RefToBinaryData` 均解析到已固定的 `TS29571_CommonData.yaml`，并验证 `contentId` 必需且为字符串；N2 类型字段解析到 TS 29.502 本地 Schema。这里的依赖闭包有意限定为本映射读取和生成的字段，不声称递归导入 TS 29.571 中所有未使用的可选数据类型及其其他 3GPP API 依赖。示例 `artifactDigest` 绑定官方 TS 29.502 YAML 字节摘要；示例中的 `responseSchemaDigest` 和 `schemaDigest` 全零值是明确的未准入占位符，不是有效 Schema digest，必须在 Compiler 的 canonical source-Schema digest 规则确定并写入受信 dependency snapshot 后替换。真实 Integration Adapter wire conformance 和 Owner deployment qualification 尚未完成，因此 Admission 仍保持 blocked。

- Step 11 Namf_Communication_N1N2MessageTransfer 是触发后续事件的出站 Operation。
- Step 3 Nsmf_PDUSession_CreateSMContext 建立 SM Context；Step 5 成功响应的 Location resource URI 提供精确 smContextRef。
- Runtime 在 Step 11 派发前注册 Step 15 的预期入站事件。Integration export 声明触发 Operation 的精确 ToolCatalog callable，并把其已物化 arguments 中的 smContextRef 绑定到入站请求 path 中的 smContextRef。
- Step 15 是 AMF 发起的 Nsmf_PDUSession.UpdateSMContext Request。Ingress selector 为 source=AMF、service=Nsmf_PDUSession、operation=UpdateSMContext；OpenAPI artifact 的 operationId UpdateSmContext 独立记录。
- Integration 认证 AMF、校验精确 TS 29.502 API artifact、解析 path/body/media parts、验证源 Schema、归一化请求并以精确 smContextRef 关联已 armed Wait。
- Host 持久提交 normalized delivery；Runtime 接受事件并继续同一个 Run，wait.output 提供 typed UpdateSMContext request。
- Agent 执行声明的 SMF 业务 Operation。补充的只读 SMF Context Observation（若需要）仍在同一个 Node 的 Operation 之后执行，不转移协议响应责任。
- Step 16a/16b 是 SMF 与 UPF 之间的 N4 Session Modification Request/Response；成功分支随后可能执行条件性的 Step 16c UDM 注册动作。
- 若 Step 15 的 N2 SM information 表示 user-plane resource setup failure，Step 16a/16b/16c 被跳过，SMF 改为在 Step 17 前释放 N4 Session；若 User Plane Enforcement Policy Notification 表示没有 user-plane resources could be established 且 policy=`required`，Step 16 同样跳过，但此条件不要求把 N4 Release 放在 Step 17 之前。
- 两种失败均在 Step 17 返回 N1 SM PDU Session Establishment Reject。Step 18 随后在会话建立失败时执行 SM Context Status Notify (Release) 和建立期间资源清理；Step 18 位于 Step 17 response boundary 之后。
- 因此 `wait.response.after` 必须绑定到 Step 17 response Producer：成功分支在 N4 Modification 和适用的 UDM 注册后到达；N2 resource-setup failure 分支在 N4 Release 后到达；required-UPE failure 分支在 Step 16 跳过后直接到达。Step 18 cleanup 是后续 Node，不得延迟响应。
- 若响应需要更早 Node 的值，Skill 必须将其显式传入最终 response-boundary Node 的 Operation/Observation arguments，并由该 Producer 输出完整 response result。

此模型是传统 3GPP SMF 对外协议边界。不得把 OpenAMSM 内部模块名写成 3GPP 协议身份，不得把 AMF/(R)AN/UE 行为描述为 SMF 自身的 Operation。不得在 Step 3 尚未创建 SM Context 时查询一个不存在的 smContextRef 来注册 Step 15。

## 12. 建议的最小 IngressCatalog 结构

以下为字段归属示意，不是可直接部署的 3GPP 发布物。对应结构约束见 [IngressCatalog v1alpha1 structural schema](schemas/ingresscatalog.v1alpha1.schema.json)。所有 urn:example、摘要、Package ID、profile 和 Schema ID 都是占位符。

~~~yaml
apiVersion: connectionagent.io/ingresscatalog/v1alpha1
kind: IngressCatalog
metadata:
  owner: example.smf-integration
spec:
  operations:
    - id: nsmf-pdusession.update-sm-context
      adapter: integration-adapter::nsmf-pdusession
      event:
        source: AMF
        service: Nsmf_PDUSession
        operation: UpdateSMContext

      protocol:
        specification: 3GPP TS 29.502
        release: "19.5.0"
        apiUriVersion: v1
        openapi:
          artifactRef: urn:connectionagent:standard-artifact:3gpp-ts-29.502-v19.5.0-nsmf-pdusession
          artifactDigest: sha256:ca5d94e296a334c85635715fc325167459d865f2c83a16c47926c979dab7545b
          operationId: UpdateSmContext
          method: POST
          path: /sm-contexts/{smContextRef}/modify

      security:
        authenticatedPeerType: AMF
        authenticationProfileRef: deployment-auth::amf-peer
        authorizationPolicyRef: deployment-auth::nsmf-update-sm-context

      request:
        acceptedMediaTypes:
          - application/json
          - multipart/related
        maxBytes: 4194304
        sourceSchemas:
          - mediaType: application/json
            schemaRef: urn:example:openapi:update-sm-context-request
            schemaDigest: sha256:0000000000000000000000000000000000000000000000000000000000000000
          - mediaType: multipart/related
            schemaRef: urn:example:openapi:update-sm-context-multipart-request
            schemaDigest: sha256:0000000000000000000000000000000000000000000000000000000000000000
        normalizedSchemaRef: urn:example:normalized:update-sm-context:v1
        normalizedSchemaDigest: sha256:0000000000000000000000000000000000000000000000000000000000000000
        normalization:
          representations:
            - mediaType: application/json
              mappings:
                - source:
                    kind: path
                    name: smContextRef
                  target: /smContextRef
                  transform: identity
                - source:
                    kind: json-body
                    pointer: ""
                  target: /updateData
                  transform: identity
            - mediaType: multipart/related
              minBinaryParts: 1
              maxBinaryParts: 2
              parts:
                - name: jsonData
                  mediaType: application/json
                  kind: json
                  required: true
                  schemaRef: urn:example:openapi:update-sm-context-json-part
                  schemaDigest: sha256:0000000000000000000000000000000000000000000000000000000000000000
                  maxBytes: 262144
                - name: binaryDataN1SmMessage
                  mediaType: application/vnd.3gpp.5gnas
                  kind: binary
                  required: false
                  maxBytes: 1048576
                - name: binaryDataN2SmInformation
                  mediaType: application/vnd.3gpp.ngap
                  kind: binary
                  required: false
                  maxBytes: 1048576
                - name: binaryDataN2SmInformationExt1
                  mediaType: application/vnd.3gpp.ngap
                  kind: binary
                  required: false
                  maxBytes: 1048576
              mappings:
                - source:
                    kind: path
                    name: smContextRef
                  target: /smContextRef
                  transform: identity
                - source:
                    kind: multipart-json
                    part: jsonData
                    pointer: ""
                  target: /updateData
                  transform: identity
                - source:
                    kind: multipart-binary
                    part: binaryDataN1SmMessage
                    contentIdReference:
                      part: jsonData
                      pointer: /n1SmMsg/contentId
                  target: /n1SmMessage
                  transform: binary-content-ref
                - source:
                    kind: multipart-binary
                    part: binaryDataN2SmInformation
                    contentIdReference:
                      part: jsonData
                      pointer: /n2SmInfo/contentId
                  target: /n2SmInformation
                  transform: binary-content-ref
                - source:
                    kind: multipart-binary
                    part: binaryDataN2SmInformationExt1
                    contentIdReference:
                      part: jsonData
                      pointer: /n2SmInfoExt1/contentId
                  target: /n2SmInformationExt1
                  transform: binary-content-ref
              ignoredSources:
                - source:
                    kind: multipart-json
                    part: jsonData
                    pointer: /n1SmMsg
                  reason: RefToBinaryData is transport-only; its verified binary part is exposed as n1SmMessage.
                - source:
                    kind: multipart-json
                    part: jsonData
                    pointer: /n2SmInfo
                  reason: RefToBinaryData is transport-only; its verified binary part is exposed as n2SmInformation.
                - source:
                    kind: multipart-json
                    part: jsonData
                    pointer: /n2SmInfoExt1
                  reason: RefToBinaryData is transport-only; its verified binary part is exposed as n2SmInformationExt1.
        binaryContent:
          referenceSchemaRef: urn:example:normalized:binary-content-reference:v1
          digestAlgorithm: sha-256
          immutable: true
          access: authorized-tool-only
          retention: "<max-invocation-lifetime-plus-recovery-window>"
          maxBytes: 1048576

      correlation:
        armInputSchemaRef: urn:example:schema:update-sm-context-arm-input
        keyFields:
          - requestPath: /smContextRef
            dimension: session
            comparison: exact
        duplicate:
          identitySource: canonical-request-digest
          scope: expected-ingress
        staleDelivery:
          strategy: single-flight-tombstone
          resourceKey: /smContextRef
          maximumLateArrival: "<exact-positive-duration>"
          clockSkewAllowance: "<exact-positive-duration>"
          tombstoneRetention: "<strictly-greater-than-maximumLateArrival-plus-clockSkewAllowance>"
          basisRef: urn:example:protocol-or-deployment-guarantee

      arming:
        start:
          allowed: false
          # If allowed=true, bindings map Context values into correlation.armInputSchemaRef.
        triggers:
          - operation:
              packageId: urn:example:package:amf-client-tools
              owner: example.amf-tool-owner
              kind: operation
              id: ca::amf.communication.n1n2_message_transfer
            bindings:
              - requestKey: /smContextRef
                bindingPath: /smContextRef
                source:
                  kind: operation-argument
                  path: /smContextRef

      response:
        mode: paired
        deadlinePolicyRef: deployment-deadline::nsmf-update-sm-context
        result:
          producer: observation
          responseResultSchemaRef: urn:example:response-result:update-sm-context:v1
          dispositionSelector:
            sourcePath: /responseRepresentation
            cases:
              - value: json
                dispositionId: update-completed
                representationId: json
              - value: multipart
                dispositionId: update-completed
                representationId: multipart
              - value: no-content
                dispositionId: update-completed-no-content
          mappings:
            - dispositionId: update-completed
              representationId: json
              from: /cause
              target:
                kind: json-body
                pointer: /cause
              transform: identity
            - dispositionId: update-completed
              representationId: multipart
              from: /cause
              target:
                kind: multipart-json
                part: jsonData
                pointer: /cause
              transform: identity
            - dispositionId: update-completed
              representationId: multipart
              from: /n2SmInfoType
              target:
                kind: multipart-json
                part: jsonData
                pointer: /n2SmInfoType
              transform: identity
            - dispositionId: update-completed
              representationId: multipart
              from: /n1SmMessage
              target:
                kind: multipart-binary
                part: binaryDataN1SmMessage
                contentIdField:
                  part: jsonData
                  pointer: /n1SmMsg/contentId
              transform: binary-content-ref
            - dispositionId: update-completed
              representationId: multipart
              from: /n2SmInformation
              target:
                kind: multipart-binary
                part: binaryDataN2SmInformation
                contentIdField:
                  part: jsonData
                  pointer: /n2SmInfo/contentId
              transform: binary-content-ref
        dispositions:
          - id: update-completed
            status: 200
            body: required
            representations:
              - id: json
                mediaType: application/json
                responseSchemaRef: urn:example:openapi:update-sm-context-response
                responseSchemaDigest: sha256:0000000000000000000000000000000000000000000000000000000000000000
                maxBytes: 65536
              - id: multipart
                mediaType: multipart/related
                minBinaryParts: 1
                maxBinaryParts: 2
                responseSchemaRef: urn:example:openapi:update-sm-context-response
                responseSchemaDigest: sha256:0000000000000000000000000000000000000000000000000000000000000000
                maxBytes: 2228224
                rootPart: jsonData
                parts:
                  - name: jsonData
                    mediaType: application/json
                    kind: json
                    required: true
                    schemaRef: urn:example:openapi:update-sm-context-response
                    schemaDigest: sha256:0000000000000000000000000000000000000000000000000000000000000000
                    maxBytes: 65536
                  - name: binaryDataN1SmMessage
                    mediaType: application/vnd.3gpp.5gnas
                    kind: binary
                    required: false
                    maxBytes: 1048576
                  - name: binaryDataN2SmInformation
                    mediaType: application/vnd.3gpp.ngap
                    kind: binary
                    required: false
                    maxBytes: 1048576
          - id: update-completed-no-content
            status: 204
            body: none
        binaryContent:
          referenceSchemaRef: urn:example:response:binary-content-reference:v1
          digestAlgorithm: sha-256
          immutable: true
          access: integration-response-only
          retention: "<response-deadline-plus-replay-and-recovery-window>"
          maxBytes: 1048576
        earlyFailureResponses:
          FAILED:
            responseRef: urn:example:protocol-error:failed
          UNRESOLVED:
            responseRef: urn:example:protocol-error:unresolved
          SAFE_STOPPED:
            responseRef: urn:example:protocol-error:safe-stopped
        deliveryRecovery:
          mode: protocol-replay
          requestIdentity: canonical-request-digest
          lostChannelDisposition: protocol-defined-retry
~~~

注意：

- sourceSchemas 和 normalizedSchemaRef 是不同契约，不得互相替代；
- artifactDigest 绑定精确 OpenAPI 文件；内联 normalization/response mappings 由整个 IngressCatalog dependency snapshot digest 固定；
- operationId 不能替代 Service-Operation 名称；UpdateSMContext 的 multipart part 名称使用 pinned OpenAPI 中的 binaryDataN1SmMessage / binaryDataN2SmInformation，不能缩写成 n1SmMsg / n2SmInfo；
- TS 29.502 V19.5.0 的 UpdateSmContext 请求 OpenAPI 声明三个可选 binary part：`binaryDataN1SmMessage`、`binaryDataN2SmInformation` 和 `binaryDataN2SmInformationExt1`；三者分别通过 `jsonData` 中的 `n1SmMsg.contentId`、`n2SmInfo.contentId` 和 `n2SmInfoExt1.contentId` 关联 Content-ID。但 TS 29.502 §6.1.2.4 限制每个实际 multipart message 只能包含一个或两个 binary parts；Catalog 声明三个可选 part 并不允许实际请求同时携带三个。示例用 `minBinaryParts: 1`、`maxBinaryParts: 2` 表达该约束，并用 `ignoredSources` 防止原始 Content-ID 进入 normalized request；`n2SmInfoTypeExt1` 保留在 `updateData` 中，与 ext1 binary part 一一对应；`n2SmInfo` 必须与 `n2SmInfoType` 配对，`n2SmInfoExt1` 必须与 `n2SmInfoTypeExt1` 配对；Adapter 必须按 TS 29.502 §6.1.6.2.4 在 wire admission 时验证这些条件，不能仅依赖 JSON Schema。
- UpdateSmContext 的 200 响应在协议上可使用 `application/json` 或 `multipart/related`，204 则没有响应体。V19.5.0 的 200 multipart response parts 为 `jsonData`、`binaryDataN1SmMessage` 和 `binaryDataN2SmInformation`；每个实际 multipart response 必须包含一至两个 binary parts。示例在同一个 200 disposition 下分别声明 JSON 与 multipart representations，并将 binary parts 通过 `SmContextUpdatedData.n1SmMsg.contentId` / `n2SmInfo.contentId` 绑定到 Content-ID。v1alpha1 的 multipart response mapping 通过 typed immutable binary reference、root JSON part、显式 Content-ID field、binary part cardinality 和有限 retention 表达，不允许省略或字符串化二进制内容；
- 示例 200 JSON representation maxBytes=65536，仅映射 SmContextUpdatedData 的条件属性 cause；smContextRef 是 request path 参数，不是 SmContextUpdatedData response body 字段；若响应需要 N1/N2 binary part 或 JSON root 含 RefToBinaryData 引用，必须选择 multipart representation，不能把 Content-ID 当成业务身份；Adapter conformance fixtures MUST 覆盖实际 binary part 数量为 0/1/2/3 的 multipart 请求（仅 1/2 可接受）、Content-ID 不匹配/悬空/重复、n2SmInfoType 与 n2SmInfoExt1Type 缺失，以及 normalized request 中不存在原始 `contentId` 的断言；响应 fixtures MUST 覆盖 N1 Reject 的 200 multipart 与缺少 N1 part 的拒绝。
- TS 23.502 V19.5.0 §4.3.2.2.1 Step 15 定义两种不同的 PDU Session Establishment Reject 条件。其一，N2 SM information indicates failure of user-plane resource setup：SMF 跳过 Step 16a/16b/16c，改为在 Step 17 前释放 N4 Session，并在 Step 17 返回包含 PDU Session Establishment Reject 的 N1 SM binary container。其二，User Plane Enforcement Policy Notification 表示没有 user-plane resources could be established，且该 policy 为 `required`：SMF 跳过 Step 16，并在 Step 17 返回同样的 N1 SM Reject；该条件本身没有规定 Step 17 前执行前述 N4 Release。两种业务失败均使用 TS 29.502 `UpdateSmContext` 的 200 disposition 和 `multipart/related` representation，不是 HTTP 4xx/5xx，也不是 204。`update-sm-context-response-result.v1.schema.json` 分别以 `procedureOutcome` 区分两种失败，并要求 `n4Action=session-released` 或 `n4Action=not-performed`；两者均要求 `udmRegistration=skipped`、`responseRepresentation=multipart` 和 `n1SmMessage`，并禁止 N2 response part。Step 18 随后执行 SM Context Status Notify Release，并释放建立过程中创建的 N4 Session、PDU Session address 和 PCF association（若存在）；这些清理动作发生在 Step 17 response boundary 之后，不得延迟响应。若缺少可信、不可变的 N1 SM binary reference 或其 Content-ID mapping，必须保持 NOT LINKABLE；不得伪装成 204 或通用 JSON 错误。示例中的 `earlyFailureResponses` 仅处理 Producer 尚未产生结果时的其他早期终止情形，绝不能替代该协议定义的业务失败响应；
- arming.triggers[].operation 是出站 ToolCatalog Operation，不是 Ingress Operation；Compiler 从该精确 ToolCatalog export 解析 Operation Input Schema，armInputSchemaRef 则定义单独的 correlationBinding Schema；
- requestKey 指向 normalized request 的字段，bindingPath 指向 correlation.armInputSchemaRef 的字段，operation-argument.path 指向出站 Operation 已物化输入；
- response.result.producer 只允许 operation 或 observation；本示例使用 boundary Node 中 Operation 之后的 Observation 输出完整 typed Step 17 response result，不能把 N4 Tool 的原始输出未经类型验证直接当作 SBI response；只有单一 bodyless disposition 时才可省略 typed result Producer；
- 示例的 maximumLateArrival、clockSkewAllowance 和 tombstoneRetention 必须由受信协议/部署保证给出，且 tombstoneRetention 必须严格大于前两者之和；
- 示例没有提供任何凭证、证书、网络地址或运行时私有句柄；示例采用 canonical-request-digest 作为重复识别占位策略，不宣称 TS 29.502 提供 protocol request ID；实际 Adapter 必须确认同一 Wait occurrence 内相同规范化请求应按重复处理；
- 示例 request.maxBytes=4194304、各 part maxBytes=1048576 和 binaryContent.maxBytes=1048576 仅为结构示例，必须按 pinned API 与部署限额设置；binaryContent.retention 是待部署策略绑定的占位符，必须覆盖最大 Invocation 生命周期及恢复宽限期；
- 3GPP SBI 的 `3gpp-Sbi-Request-Info: idempotency-key=...` 是可选重复请求检测能力；示例不假定 AMF 一定提供它，因此使用 canonical-request-digest + single-flight/tombstone。若部署要求并验证该 Header 在每个请求中存在，可改用 authenticated-header-parameter wire discriminator。

## 13. 建议的诊断与拒绝分类

以下是待加入下一语言修订诊断索引的候选静态诊断。最终 Code/Phase/Message 仍须在规范发布前统一冻结。

| Code | 触发条件 |
|---|---|
| INGRESS_CATALOG_INVALID | IngressCatalog 结构或版本不受支持 |
| INGRESS_EXPORT_ID_DUPLICATE | 同一受信快照中 export ID 重复 |
| INGRESS_OWNER_UNVERIFIED | Catalog Owner 与 trusted dependency Owner binding 不一致或缺失 |
| INGRESS_PROTOCOL_ARTIFACT_INVALID | OpenAPI artifact、digest、release、method、path 或 operationId 不匹配 |
| INGRESS_REQUEST_SCHEMA_INVALID | 源 Schema、normalized Schema 或 Schema 闭包无效 |
| INGRESS_NORMALIZATION_INVALID | mapping 缺失、digest 不匹配、字段映射不完整或目标路径无效 |
| INGRESS_PEER_PROFILE_REFERENCE_INVALID | Peer authentication/authorization profile 引用格式无效或引用了未声明的资源；实际部署未绑定属于 Admission 拒绝 |
| INGRESS_CORRELATION_INVALID | key 字段不是可比较标量、无法唯一匹配或比较规则不确定 |
| INGRESS_TRIGGER_OPERATION_NOT_FOUND | 指定的触发 Operation 不在可信依赖闭包中 |
| INGRESS_TRIGGER_OPERATION_AMBIGUOUS | 触发 Operation 身份不唯一 |
| INGRESS_TRIGGER_BINDING_INVALID | 参数缺失、类型不兼容或不能在派发前取得 |
| INGRESS_STALE_DELIVERY_UNSAFE | 无 wire discriminator 且无法证明 single-flight/tombstone 安全性 |
| INGRESS_RESPONSE_CONTRACT_INVALID | response mode、deadline、failure response 或恢复契约不完整 |
| INGRESS_RESPONSE_MAPPING_INVALID | boundary Producer 缺失、输出不可用或无法映射到协议响应 Schema |

运行时认证失败、无匹配注册、重复交付、迟到交付和响应传输失败属于 Integration/Host/Runtime 独立版本化的运行时诊断，不得伪装成 Skill Stage Outcome，也不得由 Skill 作者路由。

## 14. 最小跨组件符合性矩阵

以下为 Integration export、Compiler、Host、Runtime 的联合验收要求。它们是设计用例 ID，不代表当前产品已执行。

| Case | 条件 | 必须结果 |
|---|---|---|
| IN-001 | 未声明 Integration dependency | Compiler 不得从全局目录猜测 Ingress export |
| IN-002 | selector 无匹配 export | WAIT_INGRESS_EXPORT_NOT_FOUND |
| IN-003 | selector 匹配多个 export | WAIT_INGRESS_EXPORT_AMBIGUOUS |
| IN-004 | Owner binding 缺失或不匹配 | 构建拒绝 |
| IN-005 | export ID 重复 | 构建拒绝 |
| IN-006 | OpenAPI digest 与实际 artifact 不匹配 | 构建拒绝 |
| IN-007 | Service-Operation 与 operationId 混用 | 构建拒绝 |
| IN-008 | method/path/API release 不匹配 | Integration 拒绝请求 |
| IN-009 | 未认证 peer 或 peer NF type 不等于 event.source | Integration 拒绝，不满足 Wait |
| IN-010 | 未授权 peer 调用已认证 API | Integration 拒绝，不满足 Wait |
| IN-011 | media type 不在 acceptedMediaTypes | Integration 拒绝 |
| IN-012 | 源 request Schema 校验失败 | Integration 拒绝，不重置 Wait timeout |
| IN-013 | normalized Schema 缺失或超出支持子集 | Compiler 拒绝 |
| IN-014 | normalization mapping digest 不匹配 | 构建/部署拒绝 |
| IN-015 | required wire field 未映射到 normalized Schema | 构建拒绝 |
| IN-016 | multipart/binary part 没有受限不可变引用表示 | Integration 拒绝或隔离 |
| IN-017 | Host correlation metadata 泄漏进 wait.output | Integration conformance 失败 |
| IN-018 | trigger callable 不是精确 ToolCatalog Operation | Compiler 拒绝 |
| IN-019 | trigger argument 依赖 trigger 自身 output | Compiler 拒绝 |
| IN-020 | start Wait 缺少可验证 Context binding | Compiler 拒绝 |
| IN-021 | 多条入边中有一条没有唯一触发关系 | Compiler 拒绝 |
| IN-022 | 同一请求匹配两个 active expectedIngressRef | Integration 拒绝/隔离，不得选择 newest |
| IN-023 | 无 wire discriminator 且无可证明的 single-flight/tombstone | Compiler/Admission fail-closed |
| IN-024 | Wait 已 timeout 后收到旧消息 | 不得满足旧或新 Wait |
| IN-025 | 重试提交同一 deliveryRef | Host 返回幂等 disposition，不重复 Node entry |
| IN-026 | 同一 Wait 下两个不可区分的独立请求 | Integration 拒绝/隔离歧义 |
| IN-027 | paired response 被声明但无 response obligation | Integration/Host 拒绝不完整交付 |
| IN-028 | 单一固定 bodyless paired response disposition | 不要求 response-result Producer；多个 disposition 仍须 typed result 选择 |
| IN-029 | body-bearing response 缺少 result Producer | Compiler 拒绝 |
| IN-030 | response.after Node 缺少 export 指定的 Producer stage | Compiler 拒绝 |
| IN-031 | boundary Producer Output 不可赋值给 responseResultSchema | Compiler 拒绝 |
| IN-032 | response mapping 未覆盖协议响应必需字段 | Compiler 拒绝 |
| IN-033 | Run 在 response boundary 前以允许的失败终态结束 | Integration 使用显式 early-failure response mapping |
| IN-034 | response deadline 到期 | 不得路由为 CA-SL Wait TIMEOUT |
| IN-035 | 原 HTTP/2 stream 在进程重启后不可恢复 | Integration 按声明的 recovery/failure policy 处理，不假设句柄仍有效 |
| IN-036 | Host/Runtime 试图解析原始 3GPP HTTP request | 架构符合性失败 |
| IN-037 | Integration 试图通过启发式选择 Run/Node | 架构符合性失败 |
| IN-038 | 同一资源的旧 Wait 关闭后立即重新 armed，tombstone 尚未到期 | Integration 必须拒绝重新注册 |
| IN-039 | acceptedMediaTypes 与 sourceSchemas 不一一对应 | Compiler/Integration 拒绝不完整协议契约 |
| IN-040 | 同一 Ingress export 的 response disposition id 或 HTTP status 重复 | Compiler 拒绝歧义响应映射 |
| IN-041 | EVENT_ACCEPTED 后同一 resource key 的旧请求副本在 tombstone 到期前到达，或尝试提前 arm 下一 Wait | Integration 必须返回既有重复处置或拒绝/隔离；不得将旧请求分配给下一 Wait |
| IN-042 | binaryContent retention 早于最后一个声明 Consumer 的最晚访问/恢复时间 | Compiler/Admission 拒绝不安全的内容生命周期 |
| IN-043 | multipart body 或单个 part 超过其声明 maxBytes | Integration 在无界缓冲前拒绝请求，不提交 normalized delivery |
| IN-044 | pinned OpenAPI response 需要 multipart/related binary parts，但 v1alpha1 export 仅声明 JSON response mapping | Compiler/Admission 拒绝不完整响应表示；不得丢弃或字符串化 binary parts |
| IN-045 | Step 15 任一规范定义的 user-plane setup rejection 要求 Step 17 携带 N1 SM Reject binary container，而 export 仅声明 JSON response 或 204 | Integration/Admission 不得以 204 或通用 JSON error 替代；两种失败分支均须使用 200 multipart，缺少 N1 binary mapping 时保持 NOT LINKABLE |
| IN-046 | staleDelivery 使用 3gpp-Sbi-Request-Info.idempotency-key，但请求缺少该参数或独立请求复用该 key | Integration 拒绝/隔离；不得退回 canonical digest 或重新分配到其他 Wait |
| IN-047 | wire-discriminator 的 discriminatorRetention 小于或等于 maximumLateArrival + clockSkewAllowance | Compiler/Admission 拒绝不足以覆盖迟到重传窗口及边界竞态的身份保留策略 |
| IN-048 | body-bearing response serialization 超过 disposition.maxBytes | Integration 不得发送超限 Body；按明确的协议失败策略处理，不得截断或静默省略字段 |
| IN-049 | 3GPP multipart binary part 的 Content-ID 与根 JSON 中 RefToBinaryData 不匹配、缺失、重复或悬空 | Integration 拒绝/隔离，不生成 normalized delivery |
| IN-050 | application/json representation 包含无法由 multipart binary part 解析的 RefToBinaryData | Integration 拒绝/隔离，不生成伪造 binary content reference |
| IN-051 | 同一 3GPP SBI idempotency-key 在同一目标 NF 的不同 Ingress export 或替代实例间被复用/重复出现 | Integration 按目标 NF 作用域识别为已消费 key；不得因 peer/export 不同而将其当作新请求 |
| IN-052 | 将 `3gpp-Sbi-Max-Rsp-Time` 或发送时间戳用作 request discriminator / maximumLateArrival | Integration 拒绝该配置；这些字段只参与响应期限计算，不证明请求身份或迟到窗口 |

## 15. 冻结与发布门槛

本文完成独立评审前，Ingress Operation Contract 保持 NOT FROZEN。正式冻结前必须完成：

1. 对 IngressCatalog 资源结构、字段类型、版本标识和 export identity 的独立 Schema 评审；
2. 对 trusted dependency binding 新增 exportKind: ingressOperation 的 BuildRequest/Compiler 评审；
3. 对 correlation key、trigger argument binding、start Context binding 和 stale-delivery 证明规则的安全评审；
4. 对 normalization、multipart/binary、content reference 和保留期限的 Owner 评审；
5. 对 response result producer、bodyless/body-bearing response、early-failure response 和恢复责任的协议评审；
6. 与 CA-SL Wait 规范化草案 PR #61 完成字段和诊断一致性核对；
7. 与 Generic Host/Runtime 契约 PR #210 完成端口、私有身份和持久化责任核对；
8. 为 IN-001–IN-052 建立机器可执行的正反例与实际 Integration adapter conformance tests；
9. 完成独立审阅并明确该导出契约的发布版本和生效范围。

本文不要求当前 v1alpha4 产品支持 IngressCatalog。当前实现仍是 NOT_QUALIFIED；缺少真实、受信、版本固定的 Ingress export 时必须 fail-closed。

## 16. 已冻结语义与允许的后续工作

以下语义由 PR #60 冻结，不在本文重新设计：

- Wait 是 Node-entry control，不是第五种 Stage；
- Event Wait 是 push-driven ingress，不是 Observation polling；
- accepted event 继续同一个 Run；
- timeout 使用 wait.routes.TIMEOUT；
- wait.output 是 Integration normalized request 的 typed Producer source；
- 事件到达本身不是 Predicate PASS、Evidence 或 Goal proof；
- correlation 必须区分并发 Run 和连续 Wait generation；
- paired response 在声明的 Node boundary 提交，不等待整个 Run terminal；
- Generic Host、Runtime、Integration 和 Tool Owner 的职责分离。

本文允许继续细化的内容仅包括：精确 Schema 序列化、诊断消息、BuildRequest 物理传输、deployment profile binding、DTO、持久化、恢复实现和机器 Fixture。任何改变上述冻结语义的提议必须单独进行影响分析和重新裁决。
