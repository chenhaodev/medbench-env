## 介绍

SMDoc是一个专门用于医学领域文本结构化的数据集。这个数据集的主要目的是评估和测试模型从真实的医学文书中提取特定实体信息的能力。SMDoc中的医学文书均来自真实病历，内容包含病人的基本信息、症状描述以及各类检验检查结果。

MedBench评测榜单：该任务的评测采用精准度Accuracy作为评估指标。

MedBench评测榜单 2024年1月-5月：该任务的评测采用Micro-F1作为评估指标。

## 元数据

数据集中包含以下信息

```
<div><p>question：医学文本
answer：结构化结果，包括一般健康状况、高血压病史、糖尿病病史、传染病史、预防接种史、手术外伤史、输血史、食物过敏史、药物过敏史
</p></div>
```

## 示例

```
<div><p><span>{</span>
  <span>"question"</span><span>:</span> <span>"主诉：经期腹痛加重 3 月，发现右侧卵巢囊肿 2 月。

现病史：患者 3 月前无明显诱因出现经期腹痛，呈阵发性胀痛，可忍受，未就医。2 月前于社区医院体检行 B 超提示 “右侧卵巢囊性回声（约 35*30mm）”，建议定期复查。近 1 月腹痛加重，影响日常活动，经期延长至 7 天，伴少量血块。今年 2 月曾因 “经期紊乱” 于外院行 “妇科超声检查”，提示 “子宫内膜增厚”，予益母草颗粒口服治疗，症状无明显缓解。为进一步诊治来我院。患者末次月经 2023-03-05，病程中无发热、恶心呕吐，精神、食纳可，睡眠稍差，二便正常。

既往史：否认高血压、糖尿病、心脏病等慢性病史，否认慢性支气管炎病史。2 年前因急性阑尾炎行 “阑尾切除术”，无外伤、输血史。

月经婚育史：月经周期 6/28 天，量中等，近 3 月经期腹痛时伴少量血块。有痛经，近 3 月加重。孕 2 产 1 流产 1 存活 1。已婚，配偶体健。

体格检查：T 36.8℃，P 78 次 / 分，R 19 次 / 分，BP 115/75mmHg。神清，心肺听诊未闻及异常。腹部平软，右下腹可见长约 3cm 手术瘢痕，无压痛及反跳痛，未扪及包块。

专科检查：外阴、阴道正常。宫颈光滑，无举痛。宫体正常大小，质中，活动可，无压痛。右侧附件区可触及直径约 4cm 囊性包块，无压痛，左侧附件区未触及异常。

辅助检查：

本院 B 超（03/12）：右侧卵巢囊肿（42*38mm），子宫内膜厚 5mm，回声均匀，子宫未见明显肌瘤。

初步诊断：右侧卵巢囊肿、原发性痛经（加重期）、陈旧性阑尾切除术后

需要提取的实体字段：

主诉

末次月经

月经周期 (天)

经期 (天)

月经量

有无痛经

孕产次 (G-P-A-L)

高血压病史

糖尿病病史

手术史

体温 (℃)

脉搏 (次 / 分)

呼吸 (次 / 分)

血压 (mmHg)

妇科检查 - 宫体大小

妇科检查 - 有无宫体压痛

B 超 - 子宫肌瘤描述

B 超 - 子宫腺肌瘤描述

B 超 - 子宫内膜描述

B 超 - 卵巢描述
"</span><span>,</span>

  <span>"answer"</span><span>:</span> <span>{</span>
    <span>"主诉"</span><span>:</span> <span>"经期腹痛加重 3 月，发现右侧卵巢囊肿 2 月。"</span><span>,</span>
    <span>"末次月经"</span><span>:</span> <span>"2023-03-05"</span><span>,</span>
    <span>"月经周期 (天)"</span><span>:</span> <span>"28"</span><span>,</span>
    <span>"经期 (天)"</span><span>:</span> <span>"6"</span><span>,</span>
    <span>"月经量"</span><span>:</span> <span>"中等，近 3 月经期腹痛时伴少量血块"</span><span>,</span>
    <span>"有无痛经"</span><span>:</span> <span>"有，近 3 月加重"</span><span>,</span>
    <span>"孕产次 (G-P-A-L)"</span><span>:</span> <span>"2-1-1-1"</span><span>,</span>
    <span>"高血压病史"</span><span>:</span> <span>"否"</span><span>,</span>
    <span>"糖尿病病史"</span><span>:</span> <span>"否"</span><span>,</span>
    <span>"手术史"</span><span>:</span> <span>"2 年前因急性阑尾炎行阑尾切除术"</span><span>,</span>
    <span>"体温 (℃)"</span><span>:</span> <span>"36.8"</span><span>,</span>
    <span>"脉搏 (次 / 分)"</span><span>:</span> <span>"78"</span><span>,</span>
    <span>"呼吸 (次 / 分)"</span><span>:</span> <span>"19"</span><span>,</span>
    <span>"血压 (mmHg)"</span><span>:</span> <span>"115/75"</span><span>,</span>
    <span>"妇科检查 - 宫体大小"</span><span>:</span> <span>"正常大小"</span><span>,</span>
    <span>"妇科检查 - 有无宫体压痛"</span><span>:</span> <span>"无"</span><span>,</span>
    <span>"B 超 - 子宫肌瘤描述"</span><span>:</span> <span>"子宫未见明显肌瘤"</span><span>,</span>
    <span>"B 超 - 子宫腺肌瘤描述"</span><span>:</span> <span>"未知"</span><span>,</span>
    <span>"B 超 - 子宫内膜描述"</span><span>:</span> <span>"厚 5mm，回声均匀"</span><span>,</span>
    <span>"B 超 - 卵巢描述"</span><span>:</span><span>"右侧卵巢囊肿（42*38mm）"</span>
<span>}</span>
</p></div>
```