# 工单中心接口

## 1. 工单中心核心接口

| 接口 | 说明 | 入参 |
|---|---|---|
| `/queryTicketCenterList` | 分页查询工单列表 | `IgRequestObject` |
| `/getTicketById` | 查询工单详情（含子表数据） | `?id=xxx` |
| `/batchProcessTicket` | 批量处理工单 | `List<Integer>` |
| `/batchDeleteTicket` | 批量删除工单 | `List<Integer>` |
| `/exportTicketCenter` | 导出工单列表 | `IgRequestObject` |

## 2. `getTicketById` 接口详细说明

### 功能
- 根据工单 ID 查询工单详情
- 同时查询对应子表数据
- 支持所有类型工单的明细查询

### 实现逻辑
1. 查询工单主表数据
2. 根据工单类型（`ticket_type`）查询对应子表数据：
   - 网站异常（40010001）：查询 `ticket_center_website_detail`
   - 设备离线（40010003）：查询 `ticket_center_device_detail`
   - 流程重复执行（40010004）：查询 `ticket_center_flow_detail`
   - 缴费异常（40010005）：查询 `ticket_center_pay_fee_detail`
   - Ukey未插入（40010006）：查询 `ticket_center_ukey_detail`
   - 申报数据异常（40010002）：查询 `ticket_center_declare_detail`
3. 将子表数据封装到 `TicketCenterVO` 中返回

### 入参
- `id`：工单 ID

### 返回值
- `TicketCenterVO`：包含主表数据和对应子表数据

## 3. 工单列表查询接口

### 功能
- 分页查询工单列表
- 支持按工单类型、状态、时间等条件过滤

### 入参
- `IgRequestObject`：包含分页参数和查询条件

### 返回值
- `IgGridDefaultPage<TicketCenterVO>`：分页数据

## 4. 批量操作接口

### 批量处理
- 入参：`List<Integer>`（工单 ID 列表）
- 功能：将指定工单标记为已处理

### 批量删除
- 入参：`List<Integer>`（工单 ID 列表）
- 功能：删除指定工单

## 5. 导出接口

### 功能
- 导出工单列表到 Excel
- 支持按查询条件过滤

### 入参
- `IgRequestObject`：包含查询条件

### 返回值
- Excel 文件流