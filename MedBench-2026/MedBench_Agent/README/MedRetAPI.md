## 介绍

MedRetAPI数据集包含多样化的临床信息需求场景，涵盖临床医护人员和患者，包含诊断支持、用药咨询、指南查询、检验解读、健康科普、日常护理、治疗方案选择、需求咨询八大场景等。每个场景提供详细的查询背景和知识需求描述。模型需要生成精准的检索查询语句，从医学知识库中获取相关信息。数据集旨在评估模型的查询准确性、检索效率和结果相关性。

MedBench评测榜单：该任务的评测采用评价模型LLM-as-a-Judge作为评估指标。

## 元数据

数据集中包含以下信息

```
<div><p>question：临床信息需求场景
answer：检索查询过程
</p></div>
```

## 示例

```
<div><p><span>{</span>
    <span>"question"</span><span>:</span> <span>"你正在开发一个医疗智能助手应用，你的角色是成人呼吸科医疗助手。你可以调用以下 5 个 API 来完成成人社区获得性肺炎（CAP）的评估与用药指导：

API1：fetch_emr_data（电子病历拉取）

描述：获取患者基础信息、病史、过敏史、肝肾功能等核心数据，支撑病情评估与禁忌排查。

输入参数：patient_id (string, 必填): 患者唯一标识；required_fields (list, 必填): 需获取的字段列表

API2：search_medical_guidelines（诊疗指南检索）

描述：获取国内权威成人 CAP 诊疗指南（含病情评分、用药推荐、过敏替代方案），确保方案合规。

输入参数：disease (string, 必填): 疾病名称；guideline_type (list, 必填): 指南类型（诊断 / 治疗 / 用药）；population (string, 必填): 目标人群；region (string, 必填): 地区；version (string, 必填): 指南版本（latest 为最新）

API3：retrieve_lab_results（检验结果获取）

描述：获取患者 72 小时内 CAP 相关检验 / 影像结果（血常规、CRP、胸片等），支撑病情评分计算。

输入参数：patient_id (string, 必填): 患者唯一标识；lab_items (list, 必填): 检验项目列表；result_type (string, 必填): 结果类型（latest 为最新）

API4：query_drug_contraindications（药物禁忌检索）
描述：排查指定抗生素在患者个体情况（过敏史、肝肾功能）下的使用禁忌，筛选可用药物。

输入参数：drug_class (string, 必填): 药物类别；patient_allergy (string, 必填): 患者过敏史；patient_renal_function (string, 必填): 肾功能状态；patient_hepatic_function (string, 必填): 肝功能状态

API5：generate_cap_medication（CAP 用药推荐）
描述：基于病情严重程度、可用药物、感染类型，生成具体口服 / 注射用药方案（剂量、疗程、监测事项）。

输入参数：patient_id (string, 必填): 患者唯一标识；cap_severity (string, 必填): CAP 严重程度；available_drugs (list, 必填): 可用药物列表；infection_type (string, 必填): 感染类型；admin_route (string, 必填): 给药途径

你需要处理以下患者需求：患者女性，62 岁，主诉 “咳嗽伴发热 3 天（最高 38.5℃）、咳黄痰”，既往有高血压病史，自述 “青霉素过敏”，未记录肝肾功能。需完成：1. 评估病情严重程度；2. 排查抗生素禁忌；3. 生成门诊用药建议；4. 若检验结果超过 72 小时，需触发重新检验流程。

请根据需求，选择合适的 API 并填写对应的参数，详细说明为实现目标需要调用的 API 步骤，以及每一步所需传入的参数值。"</span><span>,</span>
    <span>"answer"</span><span>:</span> <span>"下面给出实现 “62 岁青霉素过敏成人 CAP 患者病情评估 + 禁忌排查 + 用药指导” 的分步调用方案。为便于复用，先约定判定规则：

一、核心判定规则

病情严重程度：采用 CURB-65 评分（C = 意识障碍，U = 尿素氮≥7mmol/L，R = 呼吸频率≥30 次 / 分，B = 收缩压 &lt; 90 / 舒张压≤60mmHg，65 = 年龄≥65 岁）：≥2 分→中度及以上 CAP（建议住院）；&lt;2 分→轻度 CAP（门诊治疗）。

药物禁忌：① 青霉素过敏→禁用青霉素类抗生素；② 肝功能异常（ALT&gt;2 倍正常值）→慎用大环内酯类；③ 肾功能异常（eGFR&lt;30ml/min）→调整呼吸喹诺酮类剂量。

检验有效性：血常规、CRP、胸片结果需在 72 小时内，超过则判定为 “结果过期”，需重新开具检验申请。

二、分步 API 调用方案

步骤 1：拉取患者基线数据（电子病历）

API：API1（fetch_emr_data）

用途：获取患者年龄、病史、过敏史、血压等基础信息，为评分与禁忌排查提供基线。

调用与参数（单次调用）：

patient_id(string, 必填): P20250905008（患者唯一标识）

required_fields(list, 必填): ["</span>age<span>", "</span>comorbidity<span>", "</span>allergy_history<span>", "</span>blood_pressure<span>", "</span>consciousness_status<span>"]

说明：

从返回结果提取关键信息：如 “age=62 岁，comorbidity = 高血压（规律服药），allergy_history = 青霉素过敏，blood_pressure=125/80mmHg，consciousness_status = 清醒（无异常）”；

若返回 “肝肾功能未记录”，后续步骤需在检验 API 中补充肝肾功能项目。

步骤 2：检索成人 CAP 诊疗指南（规范依据）

API：API2（search_medical_guidelines）

用途：获取国内最新 CAP 指南，明确门诊轻度 CAP 用药推荐与过敏替代方案。

调用与参数（单次调用）：

disease(string, 必填): 成人社区获得性肺炎（CAP）

guideline_type(list, 必填): ["</span>diagnosis<span>", "</span>treatment<span>", "</span>medication<span>"]

population(string, 必填): 成人（年龄 &lt; 65 岁，有高血压基础病）

region(string, 必填): China

version(string, 必填): latest

说明：

预期返回《中国成人社区获得性肺炎诊治指南 2023》核心内容：① 轻度 CAP 门诊用药推荐（青霉素类、大环内酯类、呼吸喹诺酮类）；② 青霉素过敏者替代药物（多西环素、左氧氟沙星）；③ CURB-65 评分标准；

提取 “门诊轻度 CAP 可用药物清单”（排除青霉素类），作为后续禁忌排查的目标药物。

步骤 3：拉取 CAP 相关检验 / 影像结果（疗效与评分依据）

API：API3（retrieve_lab_results）

用途：获取 72 小时内血常规、CRP、尿素氮、胸片、肝肾功能结果，支撑 CURB-65 评分与感染类型判断。

调用与参数（单次调用）：

patient_id(string, 必填): P20250905008

lab_items(list, 必填): ["</span>血常规（白细胞 + 中性粒细胞百分比）<span>", "</span>C 反应蛋白（CRP）<span>", "</span>血尿素氮（BUN）<span>", "</span>胸部 X 线片（肺部浸润影）<span>", "</span>肝功能（ALT）<span>", "</span>肾功能（eGFR）<span>"]
result_type(string, 必填): latest

说明：

若返回结果显示 “胸片为 5 天前（超过 72 小时）”，触发 “检验过期处理”：自动调用 API3 的 “检验申请生成” 子参数（apply_lab_items=["</span>胸部X线片<span>"], apply_reason="</span>CAP评估，旧结果过期<span>"），推送医生确认后执行；

若返回有效结果：如 “白细胞 13×10⁹/L↑，中性粒细胞 86%↑，CRP 55mg/L↑，BUN 6.8mmol/L，胸片示右肺下叶浸润影，ALT 32U/L（正常），eGFR 82ml/min（正常）”，进入下一步评分。

步骤 4：本地判定病情严重程度（非 API 调用，逻辑计算）

用途：结合步骤 1（病历）与步骤 3（检验）数据，计算 CURB-65 评分，确定 CAP 严重程度。


计算逻辑：

评分维度赋值：

C（意识障碍）：病历记录 “清醒”→0 分；

U（BUN≥7mmol/L）：检验 6.8mmol/L→0 分；

R（呼吸频率≥30 次 / 分）：病历未记录→暂计 0 分（触发步骤 4 补充：调用 API1 的 “supplement_consult” 子参数，推送医生补充问诊 “呼吸频率”）；

B（血压异常）：病历 125/80mmHg→0 分；

65（年龄≥65 岁）：病历 62 岁→0 分；

初步判定：CURB-65 评分 0 分（待补充呼吸频率后确认），暂归为 “轻度 CAP（门诊治疗）”。

步骤 5：排查目标药物禁忌（筛选可用药物）

API：API4（query_drug_contraindications）

用途：针对步骤 2 指南推荐的 “非青霉素类药物”，排查患者禁忌（青霉素过敏、肝肾功能正常）。

调用与参数（对 2 类目标药物各调用 1 次）：

大环内酯类（阿奇霉素）：

drug_class(string, 必填): 大环内酯类抗生素

patient_allergy(string, 必填): 青霉素过敏（无大环内酯类过敏）

patient_renal_function(string, 必填): 正常（eGFR 82ml/min）

patient_hepatic_function(string, 必填): 正常（ALT 32U/L）

呼吸喹诺酮类（左氧氟沙星）：

drug_class(string, 必填): 呼吸喹诺酮类抗生素

patient_allergy(string, 必填): 青霉素过敏（无喹诺酮类过敏）

patient_renal_function(string, 必填): 正常（eGFR 82ml/min）

patient_hepatic_function(string, 必填): 正常（ALT 32U/L）

说明：

预期返回结果：① 阿奇霉素→“无禁忌”；② 左氧氟沙星→“无禁忌（无需调整剂量）”；

筛选可用药物列表：["</span>阿奇霉素<span>", "</span>左氧氟沙星<span>"]。

步骤 6：生成门诊用药建议（最终方案）

API：API5（generate_cap_medication）

用途：整合 “轻度 CAP + 可用药物 + 细菌性感染倾向”，生成具体用药方案。

调用与参数（单次调用）：

patient_id(string, 必填): P20250905008

cap_severity(string, 必填): 轻度（CURB-65 评分 0 分，呼吸频率补充后为 22 次 / 分）

available_drugs(list, 必填): ["</span>阿奇霉素<span>", "</span>左氧氟沙星<span>"]

infection_type(string, 必填): 细菌性感染倾向（白细胞 + CRP 升高，黄痰）

admin_route(string, 必填): 口服（门诊治疗）

说明：

预期返回用药建议：① 首选：阿奇霉素片，0.5g qd（每日 1 次），疗程 5 天；② 备选：左氧氟沙星片，0.5g qd，疗程 7 天；③ 监测事项：用药期间若出现腹泻、皮疹需停药，3 天后随访评估症状缓解情况；

自动关联 API1，将用药建议写入患者电子病历（write_emr=true子参数），完成闭环。

三、异常情况处理（API 联动）

检验过期：步骤 3 返回 “胸片过期”→自动调用 API3 的 “检验申请” 子参数，推送医生确认后生成新检验单；

呼吸频率补充：步骤 4 发现 “呼吸频率缺失”→调用 API1 的 “补充问诊” 子参数，获取数据后更新评分；

药物禁忌新增：若步骤 5 返回 “左氧氟沙星过敏”→重新调用 API2 检索 “青霉素 + 喹诺酮过敏替代方案”，补充多西环素禁忌排查。"</span>
<span>}</span>
</p></div>
```