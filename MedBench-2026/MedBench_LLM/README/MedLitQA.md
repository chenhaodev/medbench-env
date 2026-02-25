## 介绍

MedLitQA文献问答数据集面向医学文献理解与推理的问答，聚焦于评估模型在真实临床文献场景下的知识抽取与逻辑推理能力。该数据集包含多源专业知识体系，覆盖普通外科、妇产科、儿科医学、心脏病学、胃肠病学、血液病学、内分泌学、神经病学、肿瘤学等43个临床专科领域，包括新生儿科、麻醉科、烧伤外科等75个细分亚专科。所有内容均经过医学专家校验，确保专业术语的准确性和临床指南的时效性。

MedBench评测榜单：该任务的评测采用基于要点信息计算Macro-Recall以及评价模型LLM-as-a-Judge作为评估指标。

MedBench评测榜单 2025年3月-2025年10月：该任务的评测采用语义相似度BERTScore和基于要点信息计算Macro-Recall作为评估指标。

## 元数据

数据集中包含以下信息

```
<div><p>question：医学文献段落和相关的问题
answer：答案
</p></div>
```

## 示例

```
<div><p><span>{</span>
  <span>"question"</span><span>:</span> <span>"Asia, had a rate of 11.9, which was lower than the OECD average 4.5 In the United Kingdom, primary care physicians treat 90% of psy- chiatric disorders: and in Japan, some note that primary care physi- cians see patients with mood and anxiety disorders equally or even more than psychiatrists 7.8 Patients with mental health problems are at higher risk of chronid medical resources, and more likely to have disease, use are more There is decreased quality of life due to increased morbidity 9.10.11 an acute need for appropriate mental health care to be provided in primary care worldwide, However, there is a lack of mental health training among primary care providers. 12 There have been numerous on mental health training for primary studies worldwide care providers including family physicians 13.14 Professional I associations of family physicians, such as the World Organization of Family Doctors (WONCA).15 the American Academy of Family Physicians (AAEP) 16 and the Roval College of General Practitioners (RCGP) 17 have also proposed recommendations s for mental health training in their specialty residency The Japan Primary Care Association UPCA) has set the following objectives for mental health training in family medicine residency in Japan: clinical experience in symptomatic psychosis programs dementia addiction. depression, bipolar disorder. schizophrenia disorders anxiety disorders somatoform disorders adjustment and developmental disorders insomnia. perinatal mental health Additionally, portfolios, Obiective Structured Clinical Examinations (OSCEs), and written exams on mental health are regquired as a part of the board certification exam. However, mental health training is not mandatory for residents, and the JPCA has not developed ade quate and systematic training for mental health in primary care. The 2019 WONCA report for the international I accreditation of Japan's e residency programs family medicine enhance recommended the ment of mental health training. 9 For this reason, the JPCA established a Mental Health Committee in 2020. It works to improve the quality of mental health care and train- ing for members of JPCA, especially for its residents. Kawada et al.20 conducted a scoping review of the e competencies required in family medicine residency programs. However, they did not find adequate in formation in the literature to help them comprehensively understand what was offered, internationally, in mental health training programs was inadequate in scope of the study, 14.21 target Existing literature population,22 and types of training.23.24 For example, Leigh et al.4.21 surveyed the status of psychiatry training in family medicine and other specialties; however, the study only covered domestic programs in studied competencies in the US, not internationally. Tsutsumi et al.22 undergraduate medical education in Japan, not family medicine res- Stensrud et al. focused on training in communication skills idents. focused on competencies in addiction disorders and Dove24 This survey was an exploratory descriptive study that is part of the committee's activities. We aimed to overview and compare the actual status of mental health training for family medicine residen- cies internationally. This type of overview has not been conducted to date.
  
  为什么初级保健中需要提供适当的心理健康护理？"</span><span>,</span>
  <span>"answer"</span><span>:</span> <span>"患者有心理健康问题时，他们更有可能使用更多的慢性医疗资源，并且更有可能患有疾病。此外，他们的生活质量会因增加的疾病负担而下降。因此，全球范围内都迫切需要在初级保健中提供适当的心理健康护理。"</span>
<span>}</span>
</p></div>
```