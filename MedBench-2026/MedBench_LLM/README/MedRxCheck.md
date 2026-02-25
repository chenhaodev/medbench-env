## 介绍

MedRxCheck数据集面向处方开具前的智能化审核需求，涵盖单选题、多选题和问答题类型，聚焦于评估模型对处方内容合理性、安全性与规范性的智能审核能力。数据集覆盖常见和易错处方类型，单选题和多选择着重考察模型对不同处方审核规则的理解与药学知识的应用。问答题考量模型在真实处方场景中的综合能力，处方审核不通过类型包含用药剂量/频次/疗程不合理、适用人群不适宜、适应证不适宜、剂型/给药途径不适宜、配伍禁忌/严重相互作用、溶媒使用不当、重复给药、用药时间/时机不适宜、用药禁忌、皮试药物未标注过敏试验或结果、开具过敏史中可能导致过敏的药物、遴选药物不适宜、不规范处方、超说明书用药等核心审方要点。任务形式涵盖全局合理性分类、不合理问题多标签识别、问题药品定位及审核依据生成等多维度评测。

MedBench评测榜单：该任务的评测采用基于精准度Accuracy，以及要点信息计算Macro-Recall结合评价模型LLM-as-a-Judge作为评估指标。

相关论文/技术报告：[Human-Level and Beyond: Benchmarking Large Language Models Against Clinical Pharmacists in Prescription Review](https://arxiv.org/abs/2512.02024)

## 元数据

数据集中包含以下信息

```
<div><p>question：处方信息
answer：错误类型、问题药品定位及审核依据
</p></div>
```

## 示例

**a. 单选题**

```
<div><p><span>{</span>
  <span>"question"</span><span>:</span> <span>"以下说法错误的是 ()
    
    A. 处方审核在临床合理用药与保障用药安全的过程中扮演关键角色
    
    B. 处方审核是医疗机构药师体现药学专业技术价值的核心环节
    
    C. 处方审核并非随意进行，而是需遵循特定的审核规则
    
    D. 处方审核的工作内容可被处方点评完全替代
    
    E. 通过规范的处方审核，能够为患者安全用药提供保障"</span><span>,</span>
  <span>"answer"</span><span>:</span> <span>"&lt;D&gt;"</span>
<span>}</span>
</p></div>
```

**b. 多选题**

```
<div><p><span>{</span>
  <span>"question"</span><span>:</span> <span>"有关血管紧张素转化酶抑制剂 (ACEI) 的描述，正确的是 ()
    
    A. 能降低体内血管紧张素 II 的水平
    
    B. 对缓激肽的降解过程有抑制作用
    
    C. 有助于减轻心肌肥厚程度
    
    D. 会促进醛固酮的合成与释放"</span><span>,</span>
  <span>"answer"</span><span>:</span> <span>"&lt;A, B, C&gt;"</span>
<span>}</span>
</p></div>
```

**c. 问答题**

```
<div><p><span>{</span>
  <span>"question"</span><span>:</span> <span>"患者信息

性别：女；年龄：58 岁临床诊断：子宫内膜癌

处方

5% 葡萄糖注射液 250ml，静脉滴注，临时医嘱

紫杉醇脂质体冻干粉针 180mg，静脉滴注，临时医嘱

5% 葡萄糖注射液 100ml，静脉滴注，临时医嘱

卡铂注射液 0.4g，静脉滴注，临时医嘱

5% 葡萄糖注射液 100ml，静脉滴注，临时医嘱

贝伐珠单抗注射液 750mg，静脉滴注，临时医嘱"</span><span>,</span>
  <span>"answer"</span><span>:</span> <span>"错误类型：配伍禁忌 / 严重相互作用。

  干预建议： 建议选择 100ml 的 0.9% 氯化钠注射液作为贝伐珠单抗注射液的溶媒。"</span>
<span>}</span>
</p></div>
```