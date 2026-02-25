## 介绍

MedPathPlan数据集包含多科室协作的复杂临床案例，涵盖从诊断到治疗的全流程数据。覆盖外科手术路径、内科诊疗路径、急诊抢救路径等多学科有关病种的临床路径。每个案例提供患者基本信息、病情严重程度、并发症情况等关键参数。模型需要生成符合临床指南的个性化诊疗路径，包括检查项目、会诊安排、干预措施和时间节点等。数据集旨在评估路径规划的规范性、个体适配性和时序合理性。

MedBench评测榜单：该任务的评测采用评价模型LLM-as-a-Judge作为评估指标。

## 元数据

数据集中包含以下信息

```
<div><p>question：患者信息和相关参数
answer：诊疗路径
</p></div>
```

## 示例

```
<div><p><span>{</span>
    <span>"question"</span><span>:</span> <span>"
   API列表：
    
    API 1: EarlyPostopeRecovery（术后早期恢复）  // Early postoperative recovery
 
 描述: 获取患者的早期术后恢复注意事项
 
 输入参数:
{
  "</span>PatientID<span>": "</span>string (必填)<span>",
  "</span>ICD<span>": "</span>string (必填)<span>"
}

输出参数:

{
  "</span>SchedulePoint<span>": "</span>string<span>",  // 临床时间点
  "</span>ClinExam<span>": "</span>string<span>",       // 临床检查
  "</span>Medication<span>": "</span>string<span>"      // 用药计划
}

API 2: DischargeCriteria（出院标准判断）  // Discharge criteria
 
 描述: 获取患者的出院标准判断结果
 
 输入参数:
{
  "</span>PatientID<span>": "</span>string (必填)<span>",
  "</span>ICD<span>": "</span>string (必填)<span>",
  "</span>Recovery<span>": "</span>string (必填) 症状、检验检查和病情恢复情况<span>"
}

输出参数:

{
  "</span>SchedulePoint<span>": "</span>string<span>",  // 临床时间点
  "</span>Discharge<span>": "</span>string<span>"       // 是否满足出院标准
}

API 3: Medication（用药）  // Medication
 
 描述: 获取患者的ICD-10诊断和诊断依据
 
 输入参数:

{
  "</span>PatientID<span>": "</span>string (必填)<span>",
  "</span>ICD<span>": "</span>string (必填)<span>"
}

输出参数:

{
  "</span>SchedulePoint<span>": "</span>string<span>",  // 临床时间点
  "</span>DrugType<span>": "</span>string<span>",       // 药物类型
  "</span>DrugName<span>": "</span>string<span>",       // 药物名称
  "</span>DrugSchd<span>": "</span>string<span>",       // 药物时间表
  "</span>DrugDosage<span>": "</span>string<span>",     // 药物剂量
  "</span>DrugCont<span>": "</span>string<span>"        // 禁忌药
}

API 4: AdmCfmDgs（确诊入院）  // Admission after confirmed diagnosis

 描述: 获取患者的ICD-10诊断和诊断依据

 输入参数:

{
  "</span>PatientID<span>": "</span>string (必填)<span>",
  "</span>ICD<span>": "</span>string (必填)<span>",
  "</span>Symptom<span>": "</span>string (必填) 症状<span>",
  "</span>PhySign<span>": "</span>string (选填) 体征<span>",
  "</span>Examination<span>": "</span>string (选填) 辅助检查<span>",
  "</span>MedicalHistory<span>": "</span>string (选填) 病史<span>",
  "</span>MedicationHistory<span>": "</span>string (选填) 用药史<span>"
}

输出参数:

{
  "</span>SchedulePoint<span>": "</span>string<span>",  // 临床时间点
  "</span>ClinExam<span>": "</span>string<span>",       // 临床检查
  "</span>Surgery<span>": "</span>string<span>"         // 手术规划
}

API 5: SurgTreat（手术/主要治疗方案）  // Surgery or Main treatment options

 描述: 获取患者所需的手术

 输入参数:

{
  "</span>PatientID<span>": "</span>string (必填)<span>",
  "</span>ICD<span>": "</span>string (必填)<span>"
}

输出参数:

{
  "</span>SchedulePoint<span>": "</span>string<span>",  // 临床时间点
  "</span>Anesthesia<span>": "</span>string<span>",     // 麻醉方式
  "</span>SurgPrcd<span>": "</span>string<span>",       // 手术方式
  "</span>IntraopeMed<span>": "</span>string<span>",    // 术中用药
  "</span>BloodTrans<span>": "</span>string<span>"      // 术中输血
}

API 6: TreatOpt（治疗方案选择）  // Treatment options

 描述: 获取患者的推荐治疗方案

 输入参数:

{
  "</span>PatientID<span>": "</span>string (必填)<span>",
  "</span>ICD<span>": "</span>string (必填)<span>",
  "</span>Condition<span>": "</span>string (选填) 治疗方案选择依据<span>"
}

输出参数:

{
  "</span>SchedulePoint<span>": "</span>string<span>",  // 临床时间点
  "</span>Precautions<span>": "</span>string<span>",    // 注意事项
  "</span>Treatment<span>": "</span>string<span>"       // 推荐治疗方案
}

API 7: PreopExam（术前检查）  // Preoperative examination

 描述: 获取患者的术前检查项目

 输入参数:

{
  "</span>PatientID<span>": "</span>string (必填)<span>",
  "</span>ICD<span>": "</span>string (必填)<span>"
}

输出参数:

{
  "</span>SchedulePoint<span>": "</span>string<span>",  // 临床时间点
  "</span>PhyExam<span>": "</span>string<span>",        // 生命体征与体格检查
  "</span>LabExam<span>": "</span>string<span>",        // 实验室检查
  "</span>ImageExam<span>": "</span>string<span>",      // 影像学检查
  "</span>CardioExam<span>": "</span>string<span>",     // 心肺功能检查
  "</span>SpecExam<span>": "</span>string<span>",       // 专科特殊检查
  "</span>AnestRisk<span>": "</span>string<span>"       // 麻醉评估及风险评估
}

API 8: AdmExam（入院检查）  // Admission examination

 描述: 获取患者的入院检查项目

 输入参数:

{
  "</span>PatientID<span>": "</span>string (必填)<span>",
  "</span>ICD<span>": "</span>string (必填)<span>"
}

输出参数:

{
  "</span>SchedulePoint<span>": "</span>string<span>",  // 临床时间点
  "</span>PhyExam<span>": "</span>string<span>",        // 生命体征与体格检查
  "</span>LabExam<span>": "</span>string<span>",        // 实验室检查
  "</span>ImageExam<span>": "</span>string<span>",      // 影像学检查
  "</span>ECGFunc<span>": "</span>string<span>",        // 心电与功能检查
  "</span>SpecExam<span>": "</span>string<span>"        // 专科特殊检查
}

API 9: PostHospFollowUp（院后随访）  // Post-hospital follow-up

 描述: 获取患者的院后随访计划

 输入参数:

{
  "</span>PatientID<span>": "</span>string (必填)<span>",
  "</span>ICD<span>": "</span>string (必填)<span>"
}

输出参数:

{
  "</span>SchedulePoint<span>": "</span>string<span>",  // 临床时间点
  "</span>ClinExam<span>": "</span>string<span>"        // 临床检查
}

API 10: PostMonRecovery（术后/治疗后监测恢复）  // Post-operative/post-treatment recovery monitoring

 描述: 获取患者的术后/治疗后的恢复、日常监测注意事项

 输入参数:

{
  "</span>PatientID<span>": "</span>string (必填)<span>",
  "</span>ICD<span>": "</span>string (必填)<span>"
}

输出参数:

{
  "</span>SchedulePoint<span>": "</span>string<span>",  // 临床时间点
  "</span>ClinExam<span>": "</span>string<span>",       // 临床检查
  "</span>Medication<span>": "</span>string<span>"      // 用药计划
}

病例背景信息

阅读以下病例信息：

男性，52岁，因“持续乏力、体重增加伴面部浮肿4个月”入院。患者4个月前无明显诱因出现乏力、精神不振、怕冷，同时体重增加约5 kg。近1个月出现面部及下肢轻度水肿，皮肤干燥、毛发稀疏。实验室检查示：促甲状腺激素（TSH）升高至62.7 mIU/L，游离甲状腺素（FT4）降低至4.1 pmol/L，总胆固醇7.2 mmol/L。甲状腺超声提示弥漫性低回声伴轻度结节形成。

诊断为“原发性甲状腺功能减退症（ICD-10: E03.802）”。既往史：高血压病史3年，规律口服缬沙坦；既往无甲状腺疾病史。

参考指南：《原发性甲状腺功能减退症临床路径（2019年版）》

请根据上述病例信息，规划该患者的指南建议临床治疗路径，填写API调用示例路径。"</span><span>,</span>
    <span>"answer"</span><span>:</span> <span>"
    AdmCfmDgs（确诊入院）
 
 输入参数:

{
  "</span>PatientID<span>": "</span><span>10001</span><span>",
  "</span>ICD<span>": "</span>E03<span>.802</span><span>",
  "</span>Symptom<span>": "</span>持续乏力、体重增加伴面部浮肿<span>4</span>个月，精神不振，怕冷<span>",
  "</span>PhySign<span>": "</span>面部及下肢轻度水肿，皮肤干燥，毛发稀疏<span>",
  "</span>Examination<span>": "</span>TSH <span>62.7</span> mIU/L，FT4 <span>4.1</span> pmol/L，总胆固醇 <span>7.2</span> mmol/L，甲状腺超声：弥漫性低回声伴轻度结节形成<span>",
  "</span>MedicalHistory<span>": "</span>高血压<span>3</span>年，规律口服缬沙坦<span>"
}

输出参数:

{
  "</span>SchedulePoint<span>": "</span>入院当天<span>",
  "</span>ClinExam<span>": "</span>完成病史采集与体格检查，明确原发性甲状腺功能减退症诊断<span>",
  "</span>Surgery<span>": "</span>无手术指征<span>"
}

AdmExam（入院检查）

 输入参数:

{
  "</span>PatientID<span>": "</span><span>10001</span><span>",
  "</span>ICD<span>": "</span>E03<span>.802</span><span>"
}

输出参数:

{
  "</span>SchedulePoint<span>": "</span>入院<span>1</span><span>-2</span>天<span>",
  "</span>PhyExam<span>": "</span>生命体征及系统体格检查<span>",
  "</span>LabExam<span>": "</span>TSH、FT4、FT3、总胆固醇、血常规、肝肾功能、电解质<span>",
  "</span>ImageExam<span>": "</span>甲状腺超声<span>",
  "</span>ECGFunc<span>": "</span>心电图<span>",
  "</span>SpecExam<span>": "</span>如有疑似继发性甲状腺功能减退，可评估抗甲状腺抗体<span>"
}

TreatOpt（治疗方案选择）

 输入参数:

{
  "</span>PatientID<span>": "</span><span>10001</span><span>",
  "</span>ICD<span>": "</span>E03<span>.802</span><span>",
  "</span>Condition<span>": "</span>TSH升高明显，FT4降低，符合甲状腺激素替代治疗指征<span>"
}

输出参数:

{
  "</span>SchedulePoint<span>": "</span>入院<span>2</span><span>-3</span>天<span>",
  "</span>Precautions<span>": "</span>告知患者及家属疾病及治疗方案，强调规律服药及复查<span>",
  "</span>Treatment<span>": "</span>口服左甲状腺素钠（L-T4）替代治疗，根据体重和病情调整剂量<span>"
}

Medication（用药）

 输入参数:

{
  "</span>PatientID<span>": "</span><span>10001</span><span>",
  "</span>ICD<span>": "</span>E03<span>.802</span><span>"
}

输出参数:

{
  "</span>SchedulePoint<span>": "</span>住院及出院后<span>",
  "</span>DrugType<span>": "</span>甲状腺激素替代治疗<span>",
  "</span>DrugName<span>": "</span>左甲状腺素钠片（L-T4）<span>",
  "</span>DrugSchd<span>": "</span>每日口服一次，空腹服用<span>",
  "</span>DrugDosage<span>": "</span>初始<span>25</span><span>-50</span> μg/d，根据TSH动态调整<span>",
  "</span>DrugCont<span>": "</span>对左甲状腺素过敏者禁用<span>"
}

DischargeCriteria（出院标准判断）

 输入参数:

{
  "</span>PatientID<span>": "</span><span>10001</span><span>",
  "</span>ICD<span>": "</span>E03<span>.802</span><span>",
  "</span>Recovery<span>": "</span>症状缓解，体征稳定，已掌握服药及随访知识<span>"
}

输出参数:

{
  "</span>SchedulePoint<span>": "</span>住院第<span>5</span><span>-7</span>天<span>",
  "</span>Discharge<span>": "</span>是，满足出院标准<span>"
}

PostHospFollowUp（院后随访）

 输入参数:

{
  "</span>PatientID<span>": "</span><span>10001</span><span>",
  "</span>ICD<span>": "</span>E03<span>.802</span><span>"
}

输出参数:

{
  "</span>SchedulePoint<span>": "</span>出院后<span>6</span>周、<span>3</span>个月及每<span>6</span><span>-12</span>个月复查<span>",
  "</span>ClinExam<span>": "</span>复查TSH、FT4，评估症状及用药依从性，必要时调整L-T4剂量<span>"
}

PostMonRecovery（术后/治疗后监测恢复）

 输入参数:

{
  "</span>PatientID<span>": "</span><span>10001</span><span>",
  "</span>ICD<span>": "</span>E03<span>.802</span><span>"
}

输出参数:

{
  "</span>SchedulePoint<span>": "</span>治疗后<span>1</span><span>-3</span>个月<span>",
  "</span>ClinExam<span>": "</span>评估乏力、水肿、皮肤干燥等症状改善情况<span>",
  "</span>Medication<span>": "</span>继续左甲状腺素替代治疗，按TSH调整剂量<span>"
}"</span>
<span>}</span>
</p></div>
```