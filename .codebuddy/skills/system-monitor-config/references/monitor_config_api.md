# 监控配置接口

## 1. 监控配置核心接口

| 接口 | 说明 | 入参 |
|---|---|---|
| `/queryMonitorConfigList` | 分页查询监控配置列表 | `IgRequestObject` |
| `/getMonitorConfigById` | 查询详情（含所有子表） | `?id=xxx` |
| `/insertMonitorConfig` | 新增（含子表） | `TicketMonitorConfigSaveVO` |
| `/updateMonitorConfig` | 更新（子表先删后插） | `TicketMonitorConfigSaveVO` |
| `/deleteMonitorConfig` | 删除（级联删子表） | `?id=xxx` |
| `/downloadMonitorConfig` | 导出监控配置列表 Excel | `IgRequestObject` |
| `/queryMonitorConfigListNoPage` | 全量查询（不分页） | `IgRequestObject` |
| `/queryMonitorConfigWithDetails` | 按 ticket_type 查含子表详情 | `TicketMonitorConfigReq` |
| `/cityDropDownList` | 城市下拉列表 | 无 |
| `/getNotifyPersonCandidates` | 获取可选通知人列表（含角色） | 无 |

## 2. 申报数据异常城市配置接口

| 接口 | 说明 | 入参 |
|---|---|---|
| `/queryDeclareDataErrorConfigList` | 分页查询申报数据异常城市配置 | `IgRequestObject`（必传 monitorId） |
| `/downloadDeclareDataErrorTemplate` | 下载城市配置导入模板 | 无 |
| `/exportDeclareDataErrorConfig` | 导出城市配置数据（支持查询条件过滤） | `IgRequestObject`（必传 monitorId） |
| `/importDeclareDataErrorConfig` | 导入城市配置（支持部分成功） | `?monitorId=xxx&fileId=xxx` |
| `/addDeclareDataErrorConfig` | 新增单条城市配置 | `TicketMonitorCityConfig` |
| `/addDeclareDataErrorConfigList` | 批量新增城市配置 | `TicketMonitorCityConfigDto` |
| `/updateDeclareDataErrorConfig` | 更新城市配置 | `TicketMonitorCityConfig` |
| `/deleteDeclareDataErrorConfig` | 删除城市配置 | `?id=xxx` |

## 3. 网址监控忽略清单接口

| 接口 | 说明 | 入参 |
|---|---|---|
| `/queryIgnoreList` | 分页查询忽略清单 | `IgRequestObject` |
| `/queryIgnoreListNoPage` | 不分页查询忽略清单 | `IgRequestObject` |
| `/batchInsert` | 批量新增忽略清单 | `List<TicketMonitorWebsiteIgnoreList>` |
| `/batchDelete` | 批量删除忽略清单 | `List<Integer>` |
| `/downloadTemplate` | 下载忽略清单导入模板 | 无 |
| `/exportIgnoreList` | 导出忽略清单数据（支持查询条件过滤） | `IgRequestObject` |
| `/importIgnoreList` | 导入忽略清单（部分成功，含网址格式校验） | `?monitorId=xxx&fileId=xxx` |

## 4. 监控配置综合查询接口

| 接口 | 说明 | 入参 |
|---|---|---|
| `/getFullConfig` | 按 ticketType + customerId 查系统配置和客户配置完整视图 | `?ticketType=xxx&customerId=xxx` |

> `customerId` 可不传，不传时只返回系统监控配置，`customerConfig` 为 null。

## 5. 关键 VO 说明

### `TicketMonitorConfigSaveVO`

```
继承 TicketMonitorConfig 所有字段，扩展：
notifyPersonList    → List<TicketMonitorNotifyPerson>（含 roles 字段）
websiteConfig       → List<TicketMonitorWebsiteConfigVO>（40010001）
ignoreList          → List<TicketMonitorWebsiteIgnoreList>（网址监控忽略清单，40010001 时使用）
cityConfigList      → List<TicketMonitorCityConfig>（40010002）
payFeeConfigList    → List<TicketMonitorPayFeeConfig>（40010005）
flowConfigList      → List<TicketMonitorFlowConfig>（40010004）
ukeyCustomerList    → List<TicketMonitorUkeyCustomer>（40010006）
updateName          → 修改人姓名（通过 rpaAuthService.getUserList 填充）
```

### `TicketMonitorFullConfigVO`

```
monitorConfig  → TicketMonitorConfigSaveVO（系统监控配置主表 + 所有子表，无启用配置则为 null）
customerConfig → TicketMonitorCustomerConfigSaveVO（客户自定义配置主表 + 所有子表，无配置则为 null）
```