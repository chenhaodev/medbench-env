## 介绍

MedCallAPI数据集包含需要调用外部系统的临床操作场景，如医嘱执行类、检验检查类、会诊协作类、药品调配类、床位管理类、报告流转类六大临床需求等场景。每个场景提供完整的操作需求和参数要求。模型需要生成符合系统规范的API调用请求，包括参数格式化和错误处理。数据集旨在评估模型的接口调用准确性、参数完整性和异常处理能力。

MedBench评测榜单：该任务的评测采用评价模型LLM-as-a-Judge作为评估指标。

## 元数据

数据集中包含以下信息

```
<div><p>question：临床操作需求
answer：API调用请求
</p></div>
```

## 示例

```
<div><p><span>{</span>
    <span>"question"</span><span>:</span> <span>"API 描述：
    
    GetDiabetesMedicationRecommend（糖尿病用药建议查询）描述：根据用户年龄、糖尿病类型、血糖水平、并发症、药物过敏史，返回适配的用药建议（含药物名称、推荐剂量、注意事项），符合最新糖尿病诊疗指南。
    
    输入参数：
    
    age (number，必填)：患者年龄（岁）
    
    diabetes_type (string，必填)：糖尿病类型（"</span>type1<span>"=1 型，"</span>type2<span>"=2 型）
    
    fasting_glucose (number，必填)：空腹血糖值（单位：mmol/L）
    
    complications (list，必填)：并发症列表（例如：["</span>hypertension<span>", "</span>nephropathy<span>"]）
    
    allergy_drugs (list，必填)：药物过敏史（例如：["</span>sulfonamides<span>", "</span>penicillin<span>"]）
    
    输出：
    {
  "</span>medications<span>": [
    {
      "</span>name<span>": "</span><span>",// 药物名称
      "</span>recommended_dosage<span>": "</span><span>",// 推荐剂量
      "</span>precautions<span>": "</span><span>"// 用药注意事项
    }
  ],
  "</span>note<span>": "</span><span>"// 备注（如指南依据、复查建议）
}
    用户问题：我今年 55 岁，是 2 型糖尿病患者，最近测空腹血糖大概 8.5mmol/L，有高血压并发症，之前吃磺胺类药物会过敏，想知道现在适合吃"</span><span>,</span>
    <span>"answer"</span><span>:</span> <span>"
    一、用户意图分析用户为 55 岁 2 型糖尿病患者，已知空腹血糖 8.5mmol/L（高于目标值 4.4-7.0mmol/L），合并高血压并发症，且对磺胺类药物过敏，核心需求是获取 “适配自身情况、规避过敏风险、兼顾并发症” 的合法降糖用药建议，以控制血糖并减少副作用。
    
    二、API 调用方案
    
    1. 所选 API 名称：GetDiabetesMedicationRecommend（糖尿病用药建议查询）
   
    2. 调用该 API 的原因：该 API 专为糖尿病患者设计，可结合 “年龄、糖尿病类型、血糖水平、并发症、过敏史” 核心信息，输出符合《中国 2 型糖尿病防治指南（2023 年版）》的个性化用药建议，能精准规避用户过敏的磺胺类药物，同时兼顾高血压并发症的用药安全性（如优先推荐对心血管有保护作用的药物），完全契合用户需求。
    
    3. API 输入参数：{
        "</span>age<span>": 55,
        "</span>diabetes_type<span>": "</span>type2<span>",
        "</span>fasting_glucose<span>": 8.5,
        "</span>complications<span>": [
            "</span>hypertension<span>"
        ],
        "</span>allergy_drugs<span>": [
            "</span>sulfonamides<span>"
        ]
    }
    
    三、预期输出{
        "</span>medications<span>": [
            {
                "</span>name<span>": "</span>二甲双胍缓释片<span>",
                "</span>recommended_dosage<span>": "</span>初始剂量 <span>0.5</span>g / 次，每日 <span>1</span> 次（晚餐时服用），<span>1</span> 周后无胃肠道不适可增至 <span>1.0</span>g / 次，每日 <span>1</span> 次<span>",
                "</span>precautions<span>": "</span>避免空腹服用，定期监测肝肾功能（每 <span>3</span> 个月 <span>1</span> 次）；若出现腹泻、恶心，可调整为餐中服用<span>"
            },
            {
                "</span>name<span>": "</span>达格列净片<span>",
                "</span>recommended_dosage<span>": "</span><span>5</span>mg / 次，每日 <span>1</span> 次（晨起服用）<span>",
                "</span>precautions<span>": "</span>每日饮水量需≥<span>1500</span>ml（预防泌尿感染）；定期监测血压（可能轻度降压，需避免与降压药叠加导致低血压）、肾功能及尿糖<span>"
            }
        ],
        "</span>note<span>": "</span><span>1.</span> 用药建议依据《中国 <span>2</span> 型糖尿病防治指南（<span>2023</span> 年版）》，二甲双胍为 <span>2</span> 型糖尿病首选基础用药，达格列净可同时保护心血管（适配高血压并发症），且均不含磺胺成分（规避过敏风险）；<span>2.</span> 用药 <span>2</span> 周后需复查空腹血糖，若仍≥<span>7.0</span>mmol/L，建议就医调整剂量；<span>3.</span> 禁止自行联用其他降糖药（如格列齐特，含磺胺结构）。<span>"
    }"</span>
<span>}</span>
</p></div>
```