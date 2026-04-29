# 工单中心主表结构

## `ticket_center` 表

| 字段 | 类型 | 说明 |
|---|---|---|
| id | int(11) | 主键 ID |
| ticket_no | varchar(50) | 工单编号，格式：yyyyMMdd + 8位当日自增序号 |
| ticket_type | varchar(50) | 工单类型，存 DICT_CODE（40010xxx） |
| customer_id | int(11) | 客户 ID |
| customer_name | varchar(255) | 客户名称 |
| business_type | varchar(50) | 业务类型：1=社保，2=公积金 |
| addr_code | varchar(50) | 城市编码 |
| addr_name | varchar(255) | 城市名称 |
| handler | varchar(255) | 处理人 |
| ticket_status | int(1) | 工单状态：0=未处理，1=已处理 |
| priority | int(1) | 优先级：1=高，2=中，3=低 |
| report_time | datetime | 上报时间 |
| process_time | datetime | 处理时间 |
| error_count | int(11) | 错误次数 |
| processing_count | int(11) | 处理中计数 |
| pending_count | int(11) | 待处理计数 |
| error_desc | varchar(500) | 异常描述 |
| create_id | int(11) | 创建人 ID |
| create_time | datetime | 创建时间 |
| update_id | int(11) | 更新人 ID |
| update_time | datetime | 更新时间 |

## 核心字段说明

- **ticket_type**：工单类型，必须使用 DICT_CODE（40010xxx），对应字典表 `sys_data_dict` 的 DATA_KEY=40010
- **business_type**：业务类型，1=社保，2=公积金
- **ticket_status**：工单状态，0=未处理，1=已处理
- **priority**：优先级，1=高，2=中，3=低
- **report_time**：上报时间，用于工单去重逻辑
- **error_count/processing_count/pending_count**：用于申报数据异常工单的计数统计