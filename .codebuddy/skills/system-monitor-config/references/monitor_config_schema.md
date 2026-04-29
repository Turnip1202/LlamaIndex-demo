# 监控配置表结构

## 1. 主表 (`ticket_monitor_config`)

| 字段 | 类型 | 说明 |
|---|---|---|
| id | int | 主键 |
| ticket_type | varchar(50) | 工单类型，存 DICT_CODE（40010xxx） |
| trigger_mechanism | varchar(50) | 触发机制，存 DICT_CODE（40011xxx） |
| trigger_rule | varchar(500) | 触发规则，多选逗号分隔（40012xxx），**仅设备离线和Ukey类型使用** |
| notify_method | varchar(50) | 通知方式：1=短信，2=邮件，多选逗号分隔 |
| status | int | 0=禁用，1=启用 |
| create_id | int(11) | 创建人ID |
| create_time | datetime | 创建时间 |
| update_id | int(11) | 更新人ID |
| update_time | datetime | 更新时间 |

## 2. 通知人配置 (`ticket_monitor_notify_person`)

| 字段 | 说明 |
|---|---|
| monitor_id | 关联主表 id |
| user_id | 用户ID |
| user_name | 用户名（登录账号） |
| name | 用户姓名 |
| roles | 角色列表，多个用顿号分隔（如"工程师、管理员"） |
| create_id | 创建人ID |
| create_time | 创建时间 |
| update_id | 更新人ID |
| update_time | 更新时间 |

## 3. 网站异常配置 (`ticket_monitor_website_config`)

| 字段 | 说明 |
|---|---|
| monitor_id | 关联主表 id |
| schedule_time | 定时执行时间，格式 HH:mm |
| create_id | 创建人ID |
| create_time | 创建时间 |
| update_id | 更新人ID |
| update_time | 更新时间 |

## 4. 申报数据异常城市配置 (`ticket_monitor_city_config`)

| 字段 | 说明 |
|---|---|
| monitor_id | 关联主表 id |
| addr_code | 城市 code |
| addr_name | 城市名称 |
| business_type | 业务类型：1=社保，2=公积金 |
| increase_pending/processing | 增员-待申报/申报中触发时间（小时） |
| decrease_pending/processing | 减员-待申报/申报中触发时间（小时） |
| adjust_base_pending/processing | 调基-待申报/申报中触发时间（小时） |
| supplement_pending/processing | 补缴-待申报/申报中触发时间（小时） |
| status | 0=禁用，1=启用 |
| create_id | 创建人ID |
| create_time | 创建时间 |
| update_id | 更新人ID |
| update_time | 更新时间 |

## 5. 流程重复执行配置 (`ticket_monitor_flow_config`)

| 字段 | 说明 |
|---|---|
| monitor_id | 关联主表 id |
| service_item | 服务项目，存 DICT_CODE（40015xxx），共16项 |
| fail_count | 触发失败次数阈值，默认10 |
| use_customer_config | 是否按客户配置次数：0=否，1=是 |
| create_id | 创建人ID |
| create_time | 创建时间 |
| update_id | 更新人ID |
| update_time | 更新时间 |

> `(monitor_id, service_item)` 唯一约束。

## 6. 缴费异常配置 (`ticket_monitor_pay_fee_config`)

| 字段 | 说明 |
|---|---|
| monitor_id | 关联主表 id |
| status_type | 缴费状态：1=获取待缴，2=核定，3=缴费，4=获取凭证 |
| social_time | 社保定时时间（小时） |
| fund_time | 公积金定时时间（小时） |
| use_customer_config | 0=否，1=是 |
| create_id | 创建人ID |
| create_time | 创建时间 |
| update_id | 更新人ID |
| update_time | 更新时间 |

> 每个 monitor_id 固定4条记录，`(monitor_id, status_type)` 唯一约束。

## 7. Ukey监控客户范围 (`ticket_monitor_ukey_customer`)

| 字段 | 说明 |
|---|---|
| monitor_id | 关联主表 id |
| customer_id | 客户ID |
| customer_name | 客户名称 |
| create_id | 创建人ID |
| create_time | 创建时间 |
| update_id | 更新人ID |
| update_time | 更新时间 |

## 8. 网址监控忽略清单 (`ticket_monitor_website_ignore_list`)

| 字段 | 说明 |
|---|---|
| id | 主键 id |
| monitor_id | 关联主表 id |
| website_url | 网站地址 |
| website_domain | 网站域名 |
| status | 0=禁用，1=启用 |
| create_id | 创建人ID |
| create_time | 创建时间 |
| update_id | 更新人ID |
| update_time | 更新时间 |