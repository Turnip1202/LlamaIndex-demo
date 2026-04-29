# 监控配置导入导出

## 1. 申报数据异常城市配置导入

### 实现逻辑

```
1. fileId → ISysFileService.downloadFile() → byte[]
2. 校验 sheet 名是否为"城市配置导入模板"
3. EasyExcel 解析为 List<TicketMonitorCityConfigExcelVO>
4. 业务类型"社保"→"1"、"公积金"→"2"
5. 城市名通过 declareAddrDao.findByAddrName() 查 addrCode
6. (addrName + "_" + businessType) 去重，部分成功模式
7. 返回 CityConfigImportResultVO
```

### 导入模板格式

| 列名 | 说明 | 示例 |
|---|---|---|
| 城市名称 | 城市名称 | 北京 |
| 业务类型 | 业务类型，下拉选项：社保/公积金 | 社保 |
| 增员-待申报 | 增员待申报触发时间（小时） | 24 |
| 增员-申报中 | 增员申报中触发时间（小时） | 48 |
| 减员-待申报 | 减员待申报触发时间（小时） | 24 |
| 减员-申报中 | 减员申报中触发时间（小时） | 48 |
| 调基-待申报 | 调基待申报触发时间（小时） | 24 |
| 调基-申报中 | 调基申报中触发时间（小时） | 48 |
| 补缴-待申报 | 补缴待申报触发时间（小时） | 24 |
| 补缴-申报中 | 补缴申报中触发时间（小时） | 48 |

## 2. 客户申报数据异常城市明细导入

### 实现逻辑

```
1. fileId → ISysFileService.downloadFile() → byte[]
2. 校验 sheet 名是否为"城市配置导入模板"
3. EasyExcel 解析为 List<TicketMonitorCityConfigExcelVO>
4. 查已有记录构建 existKeys Set（key = addrName_businessType）
5. 业务类型"社保"→"1"、"公积金"→"2"，8个时间字段各自 isPositiveInteger 校验
6. (addrName + "_" + businessType) 去重，部分成功模式
7. 返回 CityConfigImportResultVO
```

## 3. Ukey城市监控配置导入

### 实现逻辑

```
1. fileId → ISysFileService.downloadFile() → byte[]
2. 校验 sheet 名是否为"Ukey城市监控配置导入模板"
3. EasyExcel 解析为 List<TicketMonitorUkeyCityConfigExcelVO>（城市名称 + 业务类型）
4. 查已有记录构建 existAddrCodes Set（去重 key = addrCode）
5. 按城市名 groupingBy 聚合多行：
   - 出现"社保"行 → socialMonitor=1；出现"公积金"行 → fundMonitor=1
   - 同城市只插一条记录（customerMonitorId + addrCode 唯一）
6. 已存在城市计为失败，返回 CityConfigImportResultVO
```

### 导入模板格式

| 列名 | 说明 | 示例 |
|---|---|---|
| 城市名称 | 城市名称 | 北京 |
| 业务类型 | 业务类型，下拉选项：社保/公积金 | 社保 |

### 导出格式

- 每城市按 `socialMonitor`/`fundMonitor` 各自拆一行
- 两列：城市名称、业务类型（"社保"/"公积金"）

## 4. 网址监控忽略清单导入

### 实现逻辑

1. `fileId → ISysFileService.downloadFile() → byte[]`
2. 校验 sheet 名是否为"网址监控忽略清单导入模板"
3. EasyExcel 解析为 `List<TicketMonitorWebsiteIgnoreListExcelVO>`
4. 网站地址格式校验：必须以 http:// 或 https:// 开头
5. 去重校验：检查是否已存在相同的网站地址
6. 部分成功模式，返回 `WebsiteIgnoreListImportResultVO`

### 导入模板格式

| 列名 | 说明 | 示例 |
|---|---|---|
| 网站地址 | 完整的网站 URL | https://www.example.com |
| 网站域名 | 网站域名 | example.com |

## 5. 导出功能

### 申报数据异常城市配置导出
- 支持查询条件过滤
- 导出所有字段，包括城市名称、业务类型、8个时间字段等

### Ukey城市监控配置导出
- 支持查询条件过滤
- 每城市按社保/公积金拆成两行
- 导出城市名称、业务类型两列

### 网址监控忽略清单导出
- 支持查询条件过滤
- 导出网站地址、网站域名两列

## 6. 注意事项

1. **导入接口不接收文件直传**：前端先上传文件获取 `fileId`，Service 层用 `ISysFileService.downloadFile(fileId)` 获取字节流。

2. **模板校验**：导入前需校验 sheet 名是否正确。

3. **部分成功模式**：导入时采用部分成功模式，即使部分数据有错误，其他数据仍会导入成功。

4. **去重规则**：
   - 申报数据异常：`addrName_businessType`
   - Ukey城市监控：`addrCode`
   - 网址监控忽略清单：`website_url`

5. **格式校验**：
   - 业务类型：转换为 1/2
   - 时间字段：必须为正整数
   - 网站地址：必须以 http:// 或 https:// 开头