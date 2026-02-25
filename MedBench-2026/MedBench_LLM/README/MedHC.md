## 介绍

MedHC健康咨询数据集旨在评估模型在医学咨询中的知识问答能力，该数据集包含内外科检查、实验室检查、基因检测等各项常见医学检验检查，涵盖心脑血管系统疾病、恶性肿瘤、代谢疾病、营养疾病等多种疾病，并由经验丰富的专业医生和健康专家审核校验，确保数据集的准确和可靠。

MedBench评测榜单：该任务的评测采用基于要点信息计算Macro-Recall以及评价模型LLM-as-a-Judge作为评估指标。

MedBench评测榜单 2025年3月-2025年10月：该任务的评测采用语义相似度BERTScore和基于要点信息计算Macro-Recall作为评估指标。

MedBench评测榜单 2024年6月-2025年2月：该任务的评测采用基于要点信息计算Macro-Recall作为评估指标。

MedBench评测榜单 2024年1月-5月：该任务的评测采用BLEU和Rouge-L作为评估指标。

## 元数据

数据集中包含以下信息

```
<div><p>question：健康和体检管理相关的问题
answer：答案
</p></div>
```

## 示例

```
<div><p><span>{</span>
  <span>"question"</span><span>:</span> <span>"体检时，血压测量时的正常范围是多少？"</span><span>,</span>
  <span>"answer"</span><span>:</span> <span>"理想血压(BP) 收缩压&lt;120mmHg且舒张压&lt;80mmHg。 未使用降压药物的情况下,非同日3次血压测量收缩压≥140mmHg和(或)舒张压≥90mmHg,可诊断为高血压。 血压偏高是指收缩压120~139mmHg和/或舒张压80~89mmHg。"</span>
<span>}</span>
</p></div>
```