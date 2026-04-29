# 监控配置核心逻辑

## 1. 分页列表查询 (`selectMonitorConfigList`)

```
1. 调用 `selectMonitorConfigRespList`（XML resultMap + <collection> 子查询填充 notifyPersonList）
2. 通过 `rpaAuthService.getUserList()` 填充 `updateName`
3. 调用 `fillNotifyPersonNames` 为 40010002 覆写 notifyPersonList
   （从 dev_user_addr 按城市+业务类型查处理人）
4. 返回 `IgGridDefaultPage<TicketMonitorConfigSaveVO>`
```

## 2. 详情查询 (`getMonitorConfigById`)

```
1. 查主表
2. 非申报异常：从 notify_person 表填充 notifyPersonList
3. 按 ticketType 填充对应子表（使用 TicketTypeEnum 枚举判断，禁止硬编码字符串）
4. 网站异常（40010001）：
   - 填充 websiteConfig 列表
   - 单独填充 ignoreList 字段（网址监控忽略清单）
```

## 3. 新增/更新配置 (`insertMonitorConfig` / `updateMonitorConfig`)

```
新增：插主表 → saveSubTableData
更新：updateByPrimaryKeySelective → deleteSubTableData → saveSubTableData（先删后插）
```

## 4. 删除配置 (`deleteMonitorConfig`)

```
先查主表获取 ticketType → deleteSubTableData → 删主表
申报数据异常：deleteSubTableData 不删城市子表，deleteMonitorConfig 单独级联删除
```

## 5. 子表更新规则

```
有独立 CRUD 接口的子表（申报数据异常城市配置、Ukey城市监控配置）：
  → updateXxx 不操作这两类子表，deleteXxx 时单独级联删除

无独立接口的子表（通知人、网站配置、流程重复、缴费异常）：
  → 统一先删后插（deleteSubTableData + saveSubTableData）
```

## 6. 综合查询 (`getFullConfig`)

```
1. 按 ticketType + status=1 查系统监控配置主表，取第一条
2. fillSubTableData 填充系统配置对应子表 → 赋值 monitorConfig
3. 按 customerId + ticketType 查客户配置主表，取第一条
4. fillCustomerSubTableData 填充客户配置对应子表 → 赋值 customerConfig
5. 返回 TicketMonitorFullConfigVO（customerId 不传或无客户配置时 customerConfig=null）
```

## 7. 通知人候选获取 (`getNotifyPersonCandidates`)

```
1. rpaAuthService.getUserListWithRole(1)（运营用户）
2. 转换为 List<TicketMonitorNotifyPerson>
3. roles = 角色名顿号拼接
```

## 8. 注意事项

1. **所有 ticketType 判断必须用枚举** `TicketTypeEnum.XXX.getCode()`，禁止直接比较字符串。

2. **申报数据异常的通知人来源特殊**：不使用 `ticket_monitor_notify_person` 表，从 `dev_user_addr`（城市+业务类型）查处理人，由 `fillNotifyPersonNames` 方法在 Java 层填充并覆写。

3. **trigger_rule 只有设备离线和Ukey类型使用**，其他类型此字段留空。

4. **申报数据异常和Ukey城市监控子表不走先删后插**：这两类子表有独立的增删改查接口，`updateMonitorConfig` / `updateCustomerConfig` 不操作它们；删除主配置时再单独级联清理。

5. **子表更新统一先删后插（其余类型）**：`deleteSubTableData` + `saveSubTableData`，不要单独 update 子表某行。

6. **缴费异常子表固定4行**：`(monitor_id, status_type)` 唯一约束。

7. **流程重复执行子表固定16行**：`service_item` 存 DICT_CODE（40015xxx），`(monitor_id, service_item)` 唯一约束。

8. **客户配置与监控配置逻辑独立**：`ticket_monitor_customer_config` 无 monitor_id 外键，通过 `customer_id + ticket_type` 在业务层查询，触发时先查客户配置，无则降级用全局配置。

9. **deleteMonitorConfig 必须先查主表获取 ticketType** 再决定删哪张子表。

10. **导入接口不接收文件直传**：前端先上传获取 `fileId`，Service 层用 `ISysFileService.downloadFile(fileId)` 获取字节流。

11. **`businessType` 查询条件用 `FIND_IN_SET`**：前端传 "1"、"2" 或 "1,2" 三种格式，XML 中统一用 `FIND_IN_SET(t.business_type, #{businessType})`，禁止用 LIKE。