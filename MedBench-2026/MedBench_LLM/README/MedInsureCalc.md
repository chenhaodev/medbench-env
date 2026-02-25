## 介绍

MedInsureCalc数据集面向医保费用的精准核算与支付管理，该数据集模型在多样化医保场景下的精准核算能力，涵盖从基础门诊住院结算、复杂规则应用（如乙类先自付、起付线与封顶线联动），到非标准术语识别、信息缺失处理等鲁棒性测试，以及全自费案例、政策未覆盖项目等边缘场景，全面检验模型的政策理解准确性、逻辑推理能力和边界情况处理可靠性。

MedBench评测榜单：该任务的评测采用精准度Accuracy作为评估指标。

## 元数据

数据集中包含以下信息

```
<div><p>question：患者费用明细清单
answer：医保结算金额
</p></div>
```

## 示例

```
<div><p><span>{</span>
  <span>"question"</span><span>:</span> <span>"患者陈某某，在职职工，在三级医院住院。本年度住院起付线已过，本次住院费用明细如下（均为政策未覆盖项目）：进口未备案抗肿瘤药（政策未覆盖药品）：6800 元；特需护理费（全自费服务）：2200 元 / 天（共 3 天）。根据当地 2024 年医保政策：在职职工三级医院住院报销比例 85%。请计算本次住院的医保结算结果，并严格按照以下 JSON 格式输出，不要包含任何其他文字：{"</span>总费用<span>": 0,"</span>纳入报销范围金额<span>": 0,"</span>医保报销金额<span>": 0,"</span>乙类项目自负金额<span>": 0,"</span>完全自费金额<span>": 0,"</span>个人支付总金额<span>": 0,"</span>结算后起付线剩余<span>": 0}"</span><span>,</span>
  <span>"answer"</span><span>:</span> <span>{</span>
<span>"总费用"</span><span>:</span> <span>13400</span><span>,</span>
<span>"纳入报销范围金额"</span><span>:</span> <span>0</span><span>,</span>
<span>"医保报销金额"</span><span>:</span> <span>0</span><span>,</span>
<span>"乙类项目自负金额"</span><span>:</span> <span>0</span><span>,</span>
<span>"完全自费金额"</span><span>:</span> <span>13400</span><span>,</span>
<span>"个人支付总金额"</span><span>:</span> <span>13400</span><span>,</span>
<span>"结算后起付线剩余"</span><span>:</span> <span>0</span><span>}</span>
<span>}</span>
</p></div>
```