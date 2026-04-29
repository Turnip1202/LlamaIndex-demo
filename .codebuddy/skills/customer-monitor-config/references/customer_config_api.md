# 客户配置接口

## 1. 客户配置核心接口

| 接口 | 说明 | 入参 |
|---|---|---|
| `/queryCustomerConfigList` | 分页查询客户配置列表 | `IgRequestObject` |
| `/getCustomerConfigById` | 查询详情（含子表数据） | `?id=xxx` |
| `/insertCustomerConfig` | 新增客户配置（含子表，同客户+同类型唯一校验） | `TicketMonitorCustomerConfigSaveVO` |
| `/updateCustomerConfig` | 更新客户配置（子表先删后插） | `TicketMonitorCustomerConfigSaveVO` |
| `/deleteCustomerConfig` | 删除客户配置（级联删子表） | `?id=xxx` |

## 2. 申报数据异常客户城市明细接口

| 接口 | 说明 | 入参 |
|---|---|---|
| `/queryCustomerDeclareDetailList` | 分页查询[申报数据异常]客户城市明细 | `IgRequestObject`（必传 customerMonitorId） |
| `/addCustomerDeclareDetail` | 新增[申报数据异常]城市明细 | `TicketMonitorCustomerConfigDetail` |
| `/addCustomerDeclareDetailList` | 批量新增[申报数据异常]城市明细 | `TicketMonitorCustomerConfigDetailDto`（含 addrCode/addrName/customerMonitorId/detailList） |
| `/updateCustomerDeclareDetail` | 更新[申报数据异常]城市明细 | `TicketMonitorCustomerConfigDetail` |
| `/deleteCustomerDeclareDetail` | 删除[申报数据异常]城市明细 | `?id=xxx` |
| `/downloadCustomerDeclareDetailTemplate` | 下载[申报数据异常]城市明细导入模板 | 无 |
| `/exportCustomerDeclareDetail` | 导出[申报数据异常]城市明细数据（支持查询条件过滤） | `IgRequestObject`（必传 customerMonitorId） |
| `/importCustomerDeclareDetail` | 导入[申报数据异常]城市明细（部分成功） | `?customerMonitorId=xxx&fileId=xxx` |

## 3. Ukey异常客户城市监控配置接口

| 接口 | 说明 | 入参 |
|---|---|---|
| `/queryUkeyCityConfigList` | 分页查询[Ukey异常]客户城市监控配置 | `IgRequestObject`（必传 customerMonitorId） |
| `/queryUkeyCityConfigListNoPage` | 不分页查询[Ukey异常]客户城市监控配置 | `IgRequestObject`（必传 customerMonitorId） |
| `/addUkeyCityConfig` | 新增[Ukey异常]城市监控配置 | `TicketMonitorUkeyCustomerCityConfig` |
| `/updateUkeyCityConfig` | 更新[Ukey异常]城市监控配置 | `TicketMonitorUkeyCustomerCityConfig` |
| `/deleteUkeyCityConfig` | 删除[Ukey异常]城市监控配置 | `?id=xxx` |
| `/downloadUkeyCityConfigTemplate` | 下载[Ukey异常]城市监控配置导入模板 | 无 |
| `/exportUkeyCityConfig` | 导出[Ukey异常]城市监控配置数据（支持查询条件过滤） | `IgRequestObject`（必传 customerMonitorId） |
| `/importUkeyCityConfig` | 导入[Ukey异常]城市监控配置（部分成功） | `?customerMonitorId=xxx&fileId=xxx` |

## 4. 关键 VO 说明

### `TicketMonitorCustomerConfigSaveVO`

```
继承 TicketMonitorCustomerConfig 所有字段，扩展：
updateName       → 修改人姓名
 detailList       → List<TicketMonitorCustomerConfigDetail>（40010002 申报数据异常）
flowConfigList   → List<TicketMonitorFlowCustomerConfig>（40010004 流程重复执行）
payFeeConfigList → List<TicketMonitorPayFeeCustomerConfig>（40010005 缴费异常）
ukeyConfigList   → List<TicketMonitorUkeyCustomerCityConfig>（40010006 Ukey未插入）
```

### `TicketMonitorCustomerConfigDetailDto`

```
addrCode           → 城市 code
addrName           → 城市名称
customerMonitorId  → 关联 ticket_monitor_customer_config.id
detailList         → List<TicketMonitorCustomerConfigDetail>
```

> 与 `TicketMonitorCityConfigDto` 结构保持一致，方便前端统一处理。

### `TicketMonitorUkeyCityConfigExcelVO`

```
addrName     → 城市名称（导入时必填，通过 findByAddrName 查 addrCode）
businessType → 业务类型（"社保" 或 "公积金"）
```

> 导出时每个城市按 socialMonitor/fundMonitor 各自拆一行；导入时同城市多行聚合为一条记录写库。