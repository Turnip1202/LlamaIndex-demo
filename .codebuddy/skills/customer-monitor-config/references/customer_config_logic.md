# 客户配置核心逻辑

## 1. 分页列表查询 (`selectCustomerConfigList`)

```
1. 调用 `selectCustomerConfigRespList` 查询客户配置列表
2. 通过 `rpaAuthService.getUserList()` 填充 `updateName`
3. 返回 `IgGridDefaultPage<TicketMonitorCustomerConfigSaveVO>`
```

## 2. 详情查询 (`getCustomerConfigById`)

```
1. 查主表
2. 按 ticketType 填充对应子表（使用 TicketTypeEnum 枚举判断，禁止硬编码字符串）
3. 返回 `TicketMonitorCustomerConfigSaveVO`
```

## 3. 新增/更新配置 (`insertCustomerConfig` / `updateCustomerConfig`)

```
新增：
1. 按 `customerId + ticketType` 查库，已存在则抛 BusinessException
2. 插主表 → saveCustomerSubTableData

更新：
1. updateByPrimaryKeySelective → deleteCustomerSubTableData → saveCustomerSubTableData（先删后插）
```

## 4. 删除配置 (`deleteCustomerConfig`)

```
1. 查主表获取 ticketType
2. 根据 ticketType 删除对应子表数据
3. 删除主表数据
```

## 5. 子表更新规则

```
有独立 CRUD 接口的子表（申报数据异常城市明细、Ukey城市监控配置）：
  → updateCustomerConfig 不操作这两类子表，deleteCustomerConfig 时单独级联删除

无独立接口的子表（流程重复执行、缴费异常）：
  → 统一先删后插（deleteCustomerSubTableData + saveCustomerSubTableData）
```

## 6. 客户配置与系统配置关联

### 触发工单时的规则

```
1. 先按 `customer_id + ticket_type` 查客户配置
2. 有则用客户自定义规则
3. 无则降级使用全局监控配置规则
```

### 综合查询 (`getFullConfig`)

```
1. 按 ticketType + status=1 查系统监控配置主表，取第一条
2. fillSubTableData 填充系统配置对应子表 → 赋值 monitorConfig
3. 按 customerId + ticketType 查客户配置主表，取第一条
4. fillCustomerSubTableData 填充客户配置对应子表 → 赋值 customerConfig
5. 返回 TicketMonitorFullConfigVO（customerId 不传或无客户配置时 customerConfig=null）
```

## 7. 注意事项

1. **客户配置新增唯一性校验**：`insertCustomerConfig` 在 insert 前按 `customerId + ticketType` 查库，已存在则抛 `BusinessException`；更新接口不校验（ticketType 创建后不可改）。

2. **客户配置与监控配置逻辑独立**：`ticket_monitor_customer_config` 无 monitor_id 外键，通过 `customer_id + ticket_type` 在业务层查询。

3. **申报数据异常和Ukey城市监控子表不走先删后插**：这两类子表有独立的增删改查接口，`updateCustomerConfig` 不操作它们；删除主配置时再单独级联清理。

4. **子表更新统一先删后插（其余类型）**：`deleteCustomerSubTableData` + `saveCustomerSubTableData`，不要单独 update 子表某行。

5. **缴费异常子表固定4行**：`(customer_monitor_id, status_type)` 唯一约束。

6. **流程重复执行子表固定16行**：`service_item` 存 DICT_CODE（40015xxx），`(customer_monitor_id, service_item)` 唯一约束。

7. **批量新增申报城市明细 DTO**：`TicketMonitorCustomerConfigDetailDto` 含 `addrCode`、`addrName`、`customerMonitorId`、`detailList`，与 `TicketMonitorCityConfigDto` 结构对齐，方便前端统一处理。

8. **`businessType` 查询条件用 `FIND_IN_SET`**：前端传 "1"、"2" 或 "1,2" 三种格式，XML 中统一用 `FIND_IN_SET(t.business_type, #{businessType})`，禁止用 LIKE。

9. **三个导出接口入参已改为 `IgRequestObject`**：`/exportCustomerDeclareDetail`、`/exportUkeyCityConfig` 均支持动态查询条件过滤（addrCode、addrName、businessType、status 等），必传各自的 customerMonitorId，Service 层直接将 map 透传给 XML 动态 SQL。