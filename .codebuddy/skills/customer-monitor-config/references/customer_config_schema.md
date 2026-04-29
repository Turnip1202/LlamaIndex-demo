# 客户配置表结构

## 1. 主表 (`ticket_monitor_customer_config`)

| 字段 | 说明 |
|---|---|
| id | 主键 |
| customer_id | 客户ID |
| customer_name | 客户名称 |
| ticket_type | 工单类型 DICT_CODE，标识该客户配置属于哪种监控类型 |
| create_id | 创建人ID |
| create_time | 创建时间 |
| update_id | 更新人ID |
| update_time | 更新时间 |

> 与 `ticket_monitor_config` 逻辑独立，通过 `ticket_type` 在业务层耦合，无外键关联。

## 2. 申报数据异常客户城市覆盖 (`ticket_monitor_customer_config_detail`)

| 字段 | 说明 |
|---|---|
| customer_monitor_id | 关联 ticket_monitor_customer_config.id |
| addr_code | 城市 code |
| addr_name | 城市名称 |
| business_type | 1=社保，2=公积金 |
| increase/decrease/adjust_base/supplement _pending/processing | 8个时间字段（小时），覆盖系统默认值 |
| status | 0=禁用，1=启用 |
| create_id | 创建人ID |
| create_time | 创建时间 |
| update_id | 更新人ID |
| update_time | 更新时间 |

> `(customer_monitor_id, addr_code, business_type)` 唯一约束。

## 3. 流程重复执行客户自定义次数 (`ticket_monitor_flow_customer_config`)

| 字段 | 说明 |
|---|---|
| customer_monitor_id | 关联 ticket_monitor_customer_config.id |
| service_item | 服务项目 DICT_CODE（40015xxx） |
| fail_count | 自定义失败次数阈值 |
| create_id | 创建人ID |
| create_time | 创建时间 |
| update_id | 更新人ID |
| update_time | 更新时间 |

> `(customer_monitor_id, service_item)` 唯一约束。

## 4. 缴费异常客户自定义时间 (`ticket_monitor_pay_fee_customer_config`)

| 字段 | 说明 |
|---|---|
| customer_monitor_id | 关联 ticket_monitor_customer_config.id |
| status_type | 缴费状态：1=获取待缴，2=核定，3=缴费，4=获取凭证 |
| social_time | 社保自定义时间（小时） |
| fund_time | 公积金自定义时间（小时） |
| create_id | 创建人ID |
| create_time | 创建时间 |
| update_id | 更新人ID |
| update_time | 更新时间 |

> `(customer_monitor_id, status_type)` 唯一约束，每客户固定4条。

## 5. Ukey异常客户城市监控配置 (`ticket_monitor_ukey_customer_city_config`)

| 字段 | 说明 |
|---|---|
| customer_monitor_id | 关联 ticket_monitor_customer_config.id |
| addr_code | 城市编码 |
| addr_name | 城市名称 |
| social_monitor | 社保监控：0=否，1=是 |
| fund_monitor | 公积金监控：0=否，1=是 |
| status | 0=禁用，1=启用 |
| create_id | 创建人ID |
| create_time | 创建时间 |
| update_id | 更新人ID |
| update_time | 更新时间 |

> `(customer_monitor_id, addr_code)` 唯一约束。