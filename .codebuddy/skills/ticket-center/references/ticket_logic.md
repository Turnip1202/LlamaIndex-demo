# 工单生成与处理逻辑

## 1. 工单生成逻辑

### 1.1 申报数据异常 (`batchInsertTicket`)

**去重逻辑**：
- 去重 key：`ticket_type + declare_account + customer_id + business_type + addr_code + declare_type`
- 处理规则：
  - `ticket_status=0`（未处理）：只更新 `reportTime` 及明细计数（`processingCount`/`pendingCount` 有变化才更新）
  - `ticket_status=1`（已处理）：重新插入
  - 不存在：全新插入

**处理人分配**：
- 从 `dev_user_addr` 表按 `businessType + addrName` 查询
- 找不到则跳过

### 1.2 其他类型 (`batchInsertTicketOther`)

**支持的工单类型**：
- 网站异常（40010001）
- 设备离线（40010003）
- 流程重复执行（40010004）
- 缴费异常（40010005）
- Ukey未插入（40010006）

**去重逻辑**：
- 去重 key：`ticket_type + customer_id + business_type + addr_code`
- 处理规则：
  - `ticket_status=0`（未处理）：只更新 `reportTime`
  - `ticket_status=1`（已处理）：重新插入
  - 不存在：全新插入

**处理人/通知人来源**：
- **网站异常、流程重复执行、缴费异常**：从 `dev_user_addr` 按 `businessType + addrName` 查询
- **设备离线、Ukey未插入**：从 `ticket_monitor_notify_person` 表查询（多人），`handler` 取第一人，通知时每人各发一条

## 2. 工单编号生成

- 格式：`yyyyMMdd + 8位当日自增序号`
- 实现方式：使用 Redis `INCR` 命令保证唯一
- 过期策略：key 次日 0 点过期

## 3. 优先级升级

- **执行频率**：定时任务每 30 分钟执行（staging/production 环境）
- **升级规则**：每超 2 小时升一级（3→2→1）
- **通知**：升级后通知处理人

## 4. 工单处理

### 4.1 处理状态更新
- 将 `ticket_status` 从 0 更新为 1
- 记录 `process_time` 为当前时间

### 4.2 批量操作
- 支持批量处理、批量删除等操作
- 批量操作时需注意事务管理

## 5. 核心代码位置

| 内容 | 路径 |
|---|---|
| 工单中心 Service 实现 | `rpa-saas/.../service/ticket/impl/TicketCenterServiceImpl.java` |
| 工单中心 DAO/XML | `TicketCenterDao.java` + `TicketCenterMapper.xml` |
| 工单中心 Controller | `rpa-saas/.../controller/ticket/TicketCenterController.java` |
| 工单类型枚举 | `rpa-common/.../entity/ticket/enums/TicketTypeEnum.java` |