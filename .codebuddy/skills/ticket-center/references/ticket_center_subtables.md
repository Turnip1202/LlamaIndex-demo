# 工单中心子表结构

## 1. 网站异常明细 (`ticket_center_website_detail`)

| 字段 | 类型 | 说明 |
|---|---|---|
| id | int(11) | 主键 id |
| ticket_id | int(11) | 关联工单 ID，对应 ticket_center.id |
| process_name | varchar(255) | 流程名称 |
| error_desc | varchar(500) | 异常描述 |

> `ticket_id` 建立索引，方便查询。

## 2. 设备离线明细 (`ticket_center_device_detail`)

| 字段 | 类型 | 说明 |
|---|---|---|
| id | int(11) | 主键 id |
| ticket_id | int(11) | 关联工单 ID，对应 ticket_center.id |
| device_name | varchar(255) | 设备名称 |
| device_type | varchar(50) | 设备类型 |
| device_status | varchar(50) | 设备状态 |

> `ticket_id` 建立索引，方便查询。

## 3. 流程重复执行明细 (`ticket_center_flow_detail`)

| 字段 | 类型 | 说明 |
|---|---|---|
| id | int(11) | 主键 id |
| ticket_id | int(11) | 关联工单 ID，对应 ticket_center.id |
| flow_name | varchar(255) | 流程名称 |
| error_count | int(11) | 错误次数 |

> `ticket_id` 建立索引，方便查询。

## 4. 缴费异常明细 (`ticket_center_pay_fee_detail`)

| 字段 | 类型 | 说明 |
|---|---|---|
| id | int(11) | 主键 id |
| ticket_id | int(11) | 关联工单 ID，对应 ticket_center.id |
| pay_fee_type | varchar(50) | 缴费类型 |
| pay_fee_status | varchar(50) | 缴费状态 |
| pay_fee_amount | decimal(10,2) | 缴费金额 |
| pay_fee_period | varchar(50) | 缴费周期 |

> `ticket_id` 建立索引，方便查询。

## 5. Ukey未插入明细 (`ticket_center_ukey_detail`)

| 字段 | 类型 | 说明 |
|---|---|---|
| id | int(11) | 主键 id |
| ticket_id | int(11) | 关联工单 ID，对应 ticket_center.id |
| ukey_serial | varchar(255) | Ukey 序列号 |
| ukey_status | varchar(50) | Ukey 状态 |
| business_type | varchar(50) | 业务类型 |

> `ticket_id` 建立索引，方便查询。

## 6. 申报数据异常明细 (`ticket_center_declare_detail`)

| 字段 | 类型 | 说明 |
|---|---|---|
| id | int(11) | 主键 id |
| ticket_id | int(11) | 关联工单 ID，对应 ticket_center.id |
| declare_account | varchar(255) | 申报账户 |
| declare_type | varchar(50) | 申报类型 |
| pending_count | int(11) | 待申报计数 |
| processing_count | int(11) | 申报中计数 |

> `ticket_id` 建立索引，方便查询。