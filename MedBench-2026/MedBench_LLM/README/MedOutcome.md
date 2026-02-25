## 介绍

MedOutcome数据集面向临床治疗效果的精准预测与分析，聚焦于评估模型在真实诊疗场景下对治疗方案效果的预判能力与数据挖掘能力。该数据集为限定域回答，整合多维度临床信息体系，考察模型依据提供的患者基础信息以及关键诊疗行为结合相关疾病的诊疗指南预测患者的结局（包含治愈、好转、未愈、死亡）。

MedBench评测榜单：该任务的评测采用精准度Accuracy结合基于要点信息计算Macro-Recall以及评价模型LLM-as-a-Judge作为评估指标。

## 元数据

数据集中包含以下信息

```
<div><p>question：患者多维度临床信息
answer：预测结局及理由
</p></div>
```

## 示例

```
<div><p><span>{</span>
  <span>"question"</span><span>:</span> <span>"患者80岁，男性，因“重症肺炎、Ⅰ型呼吸衰竭”入院。合并慢性心力衰竭、慢性肾功能不全。入院时APACHE II评分30分。经抗感染、无创呼吸机辅助通气等积极治疗1周后，氧合指数（P/F比值）仍为150。

请预测该患者可能的结局并阐述理由。"</span><span>,</span>
  <span>"answer"</span><span>:</span>  <span>{</span>
    <span>"预测结局"</span><span>:</span> <span>"死亡"</span><span>,</span>
    <span>"理由"</span><span>:</span> <span>"患者高龄，存在多种严重基础疾病（心衰、肾衰），入院时病情危重（APACHE II评分高）。经积极治疗后氧合改善不明显（P/F比值&lt;200提示中度ARDS），说明治疗反应差。这些因素共同导致其器官功能储备极差，病情难以逆转，死亡风险极高。"</span>
    <span>}</span>
<span>}</span>
</p></div>
```