## 介绍

MedDBOps数据集包含临床数据管理和查询需求场景，涵盖病历检索、统计分析、数据更新、数据校验、数据导出、数据关联查询、隶属版本追溯七大操作类型等。每个场景提供数据结构说明和操作目标描述。模型需要生成准确的数据库查询和操作语句，实现数据提取和分析目标。数据集旨在评估模型的语句规范性、操作准确性和效率优化。

MedBench评测榜单：该任务的评测采用评价模型LLM-as-a-Judge作为评估指标。

## 元数据

数据集中包含以下信息

```
<div><p>question：数据库操作需求
answer：数据库查询和操作语句
</p></div>
```

## 示例

```
<div><p><span>{</span>
    <span>"question"</span><span>:</span> <span>"查询 “2023-01-01 至 2023-12-31 期间，心内科收治的‘急性心肌梗死’患者病历，需包含患者姓名、年龄、入院时间、主治医生”。

数据结构说明

1. 患者表（patient）

字段名：patient_id（数据类型：VARCHAR (20)）：患者唯一标识（主键）

字段名：name（数据类型：VARCHAR (50)）：患者姓名

字段名：age（数据类型：INT）：患者年龄

字段名：dept（数据类型：VARCHAR (30)）：患者所属科室（关联病历表）


2. 病历表（medical_record）

字段名：record_id（数据类型：VARCHAR (20)）：病历唯一标识（主键）

字段名：patient_id（数据类型：VARCHAR (20)）：关联患者表的外键（关联患者唯一标识）

字段名：dept（数据类型：VARCHAR (30)）：患者收治科室

字段名：diagnosis（数据类型：VARCHAR (50)）：患者诊断结果

字段名：admit_date（数据类型：DATE）：患者入院时间

字段名：doctor_name（数据类型：VARCHAR (50)）：患者主治医生姓名"</span><span>,</span>
    <span>"answer"</span><span>:</span> <span>"SELECT 
    p.name AS 患者姓名,
    p.age AS 患者年龄,
    mr.admit_date AS 入院时间,
    mr.doctor_name AS 主治医生
FROM 
    patient p
INNER JOIN 
    medical_record mr ON p.patient_id = mr.patient_id
WHERE 
    mr.dept = '心内科'
    AND mr.diagnosis = '急性心肌梗死'
    AND mr.admit_date BETWEEN '2023-01-01' AND '2023-12-31'
ORDER BY 
    mr.admit_date DESC; -- 按入院时间倒序，优先显示近期患者"</span>
<span>}</span>
</p></div>
```