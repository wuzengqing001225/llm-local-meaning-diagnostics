# 正式来源规则复核 第3批

> **暂停填写：**旧生成器把定义判据写进事实句。这批材料仅作失败审计，不进入正式实验。

此包按来源文本生成，没有读新A分数或B读者结果。模型意见是预筛，不是金标准。
你只需核原文引文、自动规则概括和4个固定事实；这4个事实正是后续A题候选。程序字段和布尔表达式由我核。
**不要**根据你预计哪个模型会答错来决定收录。自动审查为`revise`的条目可以填`待改`，写明哪一条件不对，无需你改JSON。

## cuadfull:187:TERRITORY

- 合同编号：`187`；[完整合同](contracts/ci187.txt)
- 来源组：`challenge_topup2_candidate`；自动审查：`accept`
- 程序来源：`topup2_rule_program_proposals_nonthinking.jsonl`
- 程序SHA256：`49ccdacdc9e8793c35c3cd890a9b902775981a359390e32b3c3b5c0c33b56d70`
- 规则原文：

> 1.4 "TERRITORY" shall mean all countries of the world except the United Kingdom.

- 自动概括：A location is TERRITORY if and only if it is a country of the world and it is not the United Kingdom.
- 模型指出的问题：无

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`in_france`）：The location is France, which is a country of the world and is not the United Kingdom.
  - 按完整合同，它属于`TERRITORY`吗？`是/否/无法唯一判断`：
- 例2（`in_brazil`）：The location is Brazil, which is a country of the world and is not the United Kingdom.
  - 按完整合同，它属于`TERRITORY`吗？`是/否/无法唯一判断`：
- 例3（`out_mars`）：The location is Mars, which is not a country of the world and is not the United Kingdom.
  - 按完整合同，它属于`TERRITORY`吗？`是/否/无法唯一判断`：
- 例4（`out_uk_noncountry`）：The location is a fictional United Kingdom that is not a country of the world and is the United Kingdom.
  - 按完整合同，它属于`TERRITORY`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:21:Excluded Goods

- 合同编号：`21`；[完整合同](contracts/ci21.txt)
- 来源组：`challenge_candidate`；自动审查：`accept`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/rule_program_proposals.jsonl`
- 程序SHA256：`ede1de29aee169eacfd70e3d21d748af25636e27fadabf42cfda5cd340083952`
- 规则原文：

> "Excluded Goods" means all (1) goods that are not owned by Merchant, including but not limited to goods that belong to sublessees, licensees, department lessees, or concessionaires of Merchant and (2) goods held by Merchant on memo, on consignment (except to the extent otherwise agreed by the applicable consignor), or as bailee.

- 自动概括：Excluded Goods are goods that are (1) not owned by Merchant, (2) held by Merchant on memo, (3) held by Merchant as bailee, or (4) held by Merchant on consignment unless the applicable consignor has agreed otherwise.
- 模型指出的问题：无

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`in_bailee_and_memo`）：Good G is owned by Merchant. It is held by Merchant on memo. It is not held by Merchant on consignment. The applicable consignor has not agreed otherwise. It is held by Merchant as bailee.
  - 按完整合同，它属于`Excluded Goods`吗？`是/否/无法唯一判断`：
- 例2（`in_not_owned_and_bailee`）：Good H is not owned by Merchant. It is not held by Merchant on memo. It is not held by Merchant on consignment. The applicable consignor has not agreed otherwise. It is held by Merchant as bailee.
  - 按完整合同，它属于`Excluded Goods`吗？`是/否/无法唯一判断`：
- 例3（`out_owned_no_holds`）：Good I is owned by Merchant. It is not held by Merchant on memo. It is not held by Merchant on consignment. The applicable consignor has not agreed otherwise. It is not held by Merchant as bailee.
  - 按完整合同，它属于`Excluded Goods`吗？`是/否/无法唯一判断`：
- 例4（`out_owned_no_holds_alt`）：Good L is owned by Merchant. It is not held by Merchant on memo. It is not held by Merchant on consignment. The applicable consignor has not agreed otherwise. It is not held by Merchant as bailee.
  - 按完整合同，它属于`Excluded Goods`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:242:Third Party

- 合同编号：`242`；[完整合同](contracts/ci242.txt)
- 来源组：`challenge_candidate`；自动审查：`accept`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/rule_program_proposals.jsonl`
- 程序SHA256：`62227acfdc1ddebe1ff1af3cdaff1e59c0d14348183534091535c1bc349e6903`
- 规则原文：

> 1.23 "Third Party" means any Person other than SutroVax, Sutro, or their respective Affiliates.

- 自动概括：A Third Party is any Person other than SutroVax, Sutro, or their respective Affiliates.
- 模型指出的问题：无

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`c01_alpha_person_no_exclusions`）：Alpha is a Person. Alpha is not SutroVax. Alpha is not Sutro. Alpha is not an Affiliate of SutroVax. Alpha is not an Affiliate of Sutro.
  - 按完整合同，它属于`Third Party`吗？`是/否/无法唯一判断`：
- 例2（`c02_beta_person_no_exclusions`）：Beta is a Person. Beta is not SutroVax. Beta is not Sutro. Beta is not an Affiliate of SutroVax. Beta is not an Affiliate of Sutro.
  - 按完整合同，它属于`Third Party`吗？`是/否/无法唯一判断`：
- 例3（`c09_non_person_no_exclusions`）：Iota is not a Person. Iota is not SutroVax. Iota is not Sutro. Iota is not an Affiliate of SutroVax. Iota is not an Affiliate of Sutro.
  - 按完整合同，它属于`Third Party`吗？`是/否/无法唯一判断`：
- 例4（`c13_person_affiliate_of_both`）：Nu is a Person. Nu is not SutroVax. Nu is not Sutro. Nu is an Affiliate of SutroVax. Nu is an Affiliate of Sutro.
  - 按完整合同，它属于`Third Party`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:386:Parties

- 合同编号：`386`；[完整合同](contracts/ci386.txt)
- 来源组：`challenge_candidate`；自动审查：`accept`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/rule_program_proposals.jsonl`
- 程序SHA256：`9aa6e991764d41047139e167f90b98f5dfa2075c569528b348c4544b4a8c679a`
- 规则原文：

> 1.39 Parties. The term "Parties" refers to PHLVIC, PLIC, PEPCO, and ICC collectively and the term "Party" refers to each of them individually.

- 自动概括：The term Parties denotes the finite set containing PHLVIC, PLIC, PEPCO, and ICC. An entity is in that set if it is PHLVIC, PLIC, PEPCO, or ICC; otherwise it is not in that set.
- 模型指出的问题：无

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`phlvic_only`）：Entity A is PHLVIC and is not PLIC, PEPCO, or ICC.
  - 按完整合同，它属于`Parties`吗？`是/否/无法唯一判断`：
- 例2（`all_four`）：Entity A is PHLVIC, PLIC, PEPCO, and ICC.
  - 按完整合同，它属于`Parties`吗？`是/否/无法唯一判断`：
- 例3（`none_individual`）：Entity A is an individual employee and is not PHLVIC, not PLIC, not PEPCO, and not ICC.
  - 按完整合同，它属于`Parties`吗？`是/否/无法唯一判断`：
- 例4（`none_unidentified`）：Entity A is an unidentified entity and is not PHLVIC, not PLIC, not PEPCO, and not ICC.
  - 按完整合同，它属于`Parties`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:177:Third Party

- 合同编号：`177`；[完整合同](contracts/ci177.txt)
- 来源组：`challenge_topup_candidate`；自动审查：`accept`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/topup_rule_program_proposals.jsonl`
- 程序SHA256：`ba11d5487eb27c52e96e7afbc5251289c7e31a5d85bdd1c6401bce41020c70a8`
- 规则原文：

> 1.1.187 "Third Party" means any Person other than PB, SFJ and their Affiliates.

- 自动概括：A Third Party is a Person that is not PB, not SFJ, and not an Affiliate of PB or SFJ.
- 模型指出的问题：无

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`in_person_no_exclusions_4`）：Delta Partnership is a Person. Delta Partnership is not PB. Delta Partnership is not SFJ. Delta Partnership is not an Affiliate of PB. Delta Partnership is not an Affiliate of SFJ.
  - 按完整合同，它属于`Third Party`吗？`是/否/无法唯一判断`：
- 例2（`in_person_no_exclusions_1`）：Acme LLC is a Person. Acme LLC is not PB. Acme LLC is not SFJ. Acme LLC is not an Affiliate of PB. Acme LLC is not an Affiliate of SFJ.
  - 按完整合同，它属于`Third Party`吗？`是/否/无法唯一判断`：
- 例3（`out_is_sfj_1`）：SFJ is a Person. SFJ is not PB. SFJ is SFJ. SFJ is not an Affiliate of PB. SFJ is not an Affiliate of SFJ.
  - 按完整合同，它属于`Third Party`吗？`是/否/无法唯一判断`：
- 例4（`out_not_person_but_pb_1`）：PB Subsidiary is not a Person. PB Subsidiary is PB. PB Subsidiary is not SFJ. PB Subsidiary is not an Affiliate of PB. PB Subsidiary is not an Affiliate of SFJ.
  - 按完整合同，它属于`Third Party`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:113:Applicable Laws and Regulations

- 合同编号：`113`；[完整合同](contracts/ci113.txt)
- 来源组：`challenge_topup_candidate`；自动审查：`accept`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/topup_rule_program_proposals.jsonl`
- 程序SHA256：`329f9aa6508b58d246df2f4d9b650108c1969bef60c1b6338d7ac537e85b0789`
- 规则原文：

> (a) "Applicable Laws and Regulations" shall mean any law, statute, rule, regulation, ordinance or other binding pronouncements of any duly authorized court, tribunal, arbitrator, agency, commission, official or other instrumentality of any federal, state, province, county, city or other political subdivision (domestic or foreign) having the effect of law in the United States, any foreign country or territory or any domestic or foreign state, province, county, city or other political subdivision applicable to the Company or its business.

- 自动概括：Applicable Laws and Regulations are instruments that are a law, statute, rule, regulation, ordinance, or other binding pronouncement; issued by a duly authorized court, tribunal, arbitrator, agency, commission, official, or other instrumentality; of a federal, state, province, county, city, or other political subdivision; have the effect of law in the United States, a foreign country or territory, or a domestic or foreign political subdivision; and apply to the Company or its business.
- 模型指出的问题：无

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`in_state_commission_regulation`）：A state regulation issued by a duly authorized state commission has the effect of law in a state political subdivision and applies to the Company.
  - 按完整合同，它属于`Applicable Laws and Regulations`吗？`是/否/无法唯一判断`：
- 例2（`in_foreign_county_ordinance`）：A county ordinance enacted by a duly authorized foreign county instrumentality has the effect of law in a foreign political subdivision and applies to the Company or its business.
  - 按完整合同，它属于`Applicable Laws and Regulations`吗？`是/否/无法唯一判断`：
- 例3（`out_wrong_issuer_type_private`）：A rule issued by a private trade association, which is not a court, tribunal, arbitrator, agency, commission, official, or instrumentality, is not duly authorized, has the effect of law in the United States, and applies to the Company.
  - 按完整合同，它属于`Applicable Laws and Regulations`吗？`是/否/无法唯一判断`：
- 例4（`out_no_effect_of_law`）：A regulation issued by a duly authorized state agency applies to the Company but lacks the effect of law and has no effect-of-law location.
  - 按完整合同，它属于`Applicable Laws and Regulations`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:455:Business Day

- 合同编号：`455`；[完整合同](contracts/ci455.txt)
- 来源组：`challenge_candidate`；自动审查：`accept`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/rule_program_proposals_nonthinking.jsonl`
- 程序SHA256：`419176c34feea68e3317bce4be734737ab0cae57c96321fbdbc2035badb89aef`
- 规则原文：

> "Business Day" shall mean any day on which the New York Stock Exchange is open for trading and on which the Fund calculates it net asset value pursuant to the rules of the SEC.

- 自动概括：A day is a Business Day if and only if the New York Stock Exchange is open for trading on that day and the Fund calculates its net asset value on that day pursuant to the rules of the SEC.
- 模型指出的问题：无

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`both_true`）：On Monday, the New York Stock Exchange is open for trading, and the Fund calculates its net asset value pursuant to the rules of the SEC.
  - 按完整合同，它属于`Business Day`吗？`是/否/无法唯一判断`：
- 例2（`nyse_open_calc_sec`）：On Friday, the New York Stock Exchange is open for trading, and the Fund calculates its net asset value pursuant to the rules of the SEC.
  - 按完整合同，它属于`Business Day`吗？`是/否/无法唯一判断`：
- 例3（`nyse_open_fund_no_calc`）：On Tuesday, the New York Stock Exchange is open for trading, but the Fund does not calculate its net asset value pursuant to the rules of the SEC.
  - 按完整合同，它属于`Business Day`吗？`是/否/无法唯一判断`：
- 例4（`closed_calc_rule`）：On a non-business day, the New York Stock Exchange is not open for trading, but the Fund calculates its net asset value pursuant to the rules of the SEC.
  - 按完整合同，它属于`Business Day`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:488:Confidential Information

- 合同编号：`488`；[完整合同](contracts/ci488.txt)
- 来源组：`challenge_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/rule_program_proposals.jsonl`
- 程序SHA256：`3c98c3c1e7958897ee1eb629fe1c68afca9e78a8d624721f1eadfcb02b43224a`
- 规则原文：

> "Confidential Information" means information disclosed to the Contractor as a consequence of or through its, his or her position as a director, officer, employee or consultant of Emerald, which information is not generally known in the industry in which Emerald operates.

- 自动概括：Information is Confidential Information if it was disclosed to the Contractor as a consequence of or through the Contractor's position as a director, officer, employee, or consultant of Emerald and is not generally known in Emerald's industry.
- 模型指出的问题：The predicate faithfully requires disclosure to the Contractor, a causal/through-position connection, an enumerated director/officer/employee/consultant position of Emerald, and information not generally known in Emerald's industry.；c07 codes position_type='director' and position_of_emerald=true, but its text only negates disclosure through a qualifying position; it does not expressly affirm that the Contractor actually held a director position of Emerald.；c11 similarly codes position_type='officer' and position_of_emerald=true, but the text negates disclosure through a purported officer position rather than expressly stating that the Contractor was an officer of Emerald.；The source definition is sufficient to evaluate the logical rule; the listed dependencies are evidentiary inputs for real-world application, not missing contractual source material.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`c03_employee_in`）：Information C was disclosed to the Contractor as a consequence of or through the Contractor's position as an employee of Emerald, and the information is not generally known in the industry in which Emerald operates.
  - 按完整合同，它属于`Confidential Information`吗？`是/否/无法唯一判断`：
- 例2（`c02_officer_in`）：Information B was disclosed to the Contractor as a consequence of or through the Contractor's position as an officer of Emerald, and the information is not generally known in the industry in which Emerald operates.
  - 按完整合同，它属于`Confidential Information`吗？`是/否/无法唯一判断`：
- 例3（`c11_officer_not_disclosed_out`）：Information K was disclosed to the public, not to the Contractor, and the disclosure was not as a consequence of or through the Contractor's position as an officer of Emerald; the information is not generally known in the industry in which Emerald operates.
  - 按完整合同，它属于`Confidential Information`吗？`是/否/无法唯一判断`：
- 例4（`c09_position_other_out`）：Information I was disclosed to the Contractor as a consequence of or through the Contractor's position as a manager of Emerald, which is not a director, officer, employee, or consultant position, and the information is not generally known in the industry in which Emerald operates.
  - 按完整合同，它属于`Confidential Information`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:501:Law

- 合同编号：`501`；[完整合同](contracts/ci501.txt)
- 来源组：`challenge_topup_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/topup_rule_program_proposals_nonthinking.jsonl`
- 程序SHA256：`3d77fc225493ea5074feac659ac1e76905f5b13dc75431b529113db775d78449`
- 规则原文：

> (i) "Law" means any domestic or foreign, federal, state, provincial, municipal or local law, statute, ordinance, code, rule, or regulation having the force of law.

- 自动概括：An instrument is a Law if it is a law, statute, ordinance, code, rule, or regulation, it has the force of law, and its jurisdiction is domestic, foreign, federal, state, provincial, municipal, or local.
- 模型指出的问题：The source permits compound jurisdictional descriptors (for example, "domestic federal," "foreign provincial," and "foreign municipal"), but the program models jurisdiction as one mutually exclusive scalar value. This is not an exact representation of the quoted definition.；Cases c01, c02, and c13 expressly state two jurisdictional attributes, while their fact vectors retain only one (federal, provincial, and municipal, respectively) and omit domestic or foreign. Thus the vectors do not fully match the case text.；The predicate's requirement that jurisdiction equal exactly one member of its listed set is an unsupported narrowing if the source's listed jurisdiction terms can combine, as the case texts themselves demonstrate.；The source quote itself is present and does not identify any necessary external attachment or redacted factual dependency.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`c03`）：A municipal ordinance that has the force of law.
  - 按完整合同，它属于`Law`吗？`是/否/无法唯一判断`：
- 例2（`c05`）：A state code that has the force of law.
  - 按完整合同，它属于`Law`吗？`是/否/无法唯一判断`：
- 例3（`c13`）：A foreign municipal ordinance that does not have the force of law.
  - 按完整合同，它属于`Law`吗？`是/否/无法唯一判断`：
- 例4（`c12`）：A contract that has the force of law.
  - 按完整合同，它属于`Law`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:245:Senior Officers

- 合同编号：`245`；[完整合同](contracts/ci245.txt)
- 来源组：`challenge_topup2_candidate`；自动审查：`revise`
- 程序来源：`topup2_rule_program_proposals_nonthinking.jsonl`
- 程序SHA256：`686d769556609a462e1e8dddfb2f0ff0e9b31f7dee2ef6d1868b889461ee416f`
- 规则原文：

> 1.98 "Senior Officers" shall mean, with respect to Exact, the Chief Executive Officer of Exact and, with respect to Pfizer, Regional President, North America, Internal Medicine, Pfizer Innovative Health.

- 自动概括：A person is a Senior Officer if and only if they are either the Chief Executive Officer of Exact or the Regional President, North America, Internal Medicine, Pfizer Innovative Health.
- 模型指出的问题：The predicate correctly treats the two listed offices as alternative ways for a person to be a Senior Officer; the definition's conjunction lists the respective Exact and Pfizer offices and does not require one person to hold both.；Case pfizer_role_acting does not explicitly support coding the Pfizer-role field false. It states that Casey is 'acting Regional President, North America, Internal Medicine, Pfizer Innovative Health,' while the source contains no exception excluding acting holders. The text neither expressly denies the specified role nor establishes that acting status is outside it.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`both_roles`）：Alex is both the Chief Executive Officer of Exact and the Regional President, North America, Internal Medicine, Pfizer Innovative Health.
  - 按完整合同，它属于`Senior Officers`吗？`是/否/无法唯一判断`：
- 例2（`pfizer_role_but_exact_other`）：Taylor holds the Regional President, North America, Internal Medicine, Pfizer Innovative Health role and is an officer of Exact, but not its Chief Executive Officer.
  - 按完整合同，它属于`Senior Officers`吗？`是/否/无法唯一判断`：
- 例3（`neither_but_exact_officer`）：Quinn is an officer of Exact but not its Chief Executive Officer, and does not hold the Pfizer role.
  - 按完整合同，它属于`Senior Officers`吗？`是/否/无法唯一判断`：
- 例4（`pfizer_role_acting`）：Casey is acting Regional President, North America, Internal Medicine, Pfizer Innovative Health and is not the Chief Executive Officer of Exact.
  - 按完整合同，它属于`Senior Officers`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:243:Person

- 合同编号：`243`；[完整合同](contracts/ci243.txt)
- 来源组：`challenge_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/rule_program_proposals.jsonl`
- 程序SHA256：`54b6e04b552a21234924dfac1840822b491fd36e74913d9581d34fb46117eba6`
- 规则原文：

> "Person" shall mean an individual, partnership, corporation, limited liability company, joint venture, association or other form of business organization (whether or not regarded as a legal entity under applicable law), trust or other entity or organization.

- 自动概括：A Person is any individual, partnership, corporation, limited liability company, joint venture, association, other form of business organization, trust, or other entity or organization.
- 模型指出的问题：The predicate faithfully implements the source's disjunctive definition: any listed form qualifies as a Person. The parenthetical concerning legal-entity status creates no additional condition and is not omitted materially.；Except for c01, the case texts do not explicitly support every false value coded in their fact vectors. For example, stating that an entity is a partnership does not explicitly establish that it is not also an association, corporation, trust, or another organization category.；The source does not state that its listed categories are mutually exclusive. Several examples, particularly c09 and c10, code only is_other_entity_or_organization=true while affirmatively setting all listed forms false, although the text merely calls the subject an organization and does not exclude corporation, association, or other listed statuses.；The non-Person examples (c11 through c15) state that the subject is not an entity or organization, but do not explicitly state every individual negative categorical fact represented in the vectors. Their all-false vectors therefore rely on unstated inference rather than explicit case facts.；c07's description supports that the sole proprietorship is an unlisted business organization, but it does not explicitly establish every remaining negative field, particularly is_individual=false.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`c05_joint_venture`）：Epsilon JV is a joint venture.
  - 按完整合同，它属于`Person`吗？`是/否/无法唯一判断`：
- 例2（`c04_llc`）：Delta LLC is a limited liability company.
  - 按完整合同，它属于`Person`吗？`是/否/无法唯一判断`：
- 例3（`c11_real_property`）：A parcel of land is real property, not an entity or organization.
  - 按完整合同，它属于`Person`吗？`是/否/无法唯一判断`：
- 例4（`c13_contract`）：A contract is a legal agreement, not an entity or organization.
  - 按完整合同，它属于`Person`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:286:Billing Party

- 合同编号：`286`；[完整合同](contracts/ci286.txt)
- 来源组：`challenge_topup_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/topup_rule_program_proposals_nonthinking.jsonl`
- 程序SHA256：`1a254bb16f81df2ad24577f6d83e38b7806aa8da845d42c39c68c6183cbd3b39`
- 规则原文：

> 1.2 "Billing Party" means the party responsible for all billing and collection matters associated with the Co-Branded Service.

- 自动概括：A party is a Billing Party if and only if that party is responsible for all billing and collection matters associated with the Co-Branded Service.
- 模型指出的问题：The quoted Billing Party definition is supplied and the predicate faithfully captures its stated condition: responsibility for all billing and collection matters associated with the Co-Branded Service.；The required referenced definition of "Co-Branded Service" in section 1.5 is not provided. Its scope, exclusions, or qualifications therefore cannot be audited.；The case texts explicitly state each coded responsibility and association fact; no case-specific factual vector mismatch is apparent.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`c05`）：Epsilon Ltd is responsible for all billing and collection matters associated with the Co-Branded Service.
  - 按完整合同，它属于`Billing Party`吗？`是/否/无法唯一判断`：
- 例2（`c04`）：Delta Co is responsible for all billing and collection matters associated with the Co-Branded Service.
  - 按完整合同，它属于`Billing Party`吗？`是/否/无法唯一判断`：
- 例3（`c06`）：Zeta Partners is not responsible for all billing and collection matters associated with the Co-Branded Service.
  - 按完整合同，它属于`Billing Party`吗？`是/否/无法唯一判断`：
- 例4（`c08`）：Theta Holdings is not responsible for all billing and collection matters, and those matters are not associated with the Co-Branded Service.
  - 按完整合同，它属于`Billing Party`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:251:Contract

- 合同编号：`251`；[完整合同](contracts/ci251.txt)
- 来源组：`challenge_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/rule_program_proposals.jsonl`
- 程序SHA256：`0f5cd9254dbe1d2e9ae14bc19b72cc418021181b2656601d771f0e2c7a0b1269`
- 规则原文：

> "Contract" shall mean any contract, agreement, instrument, undertaking, indenture, commitment, loan, license or other legally binding obligation, whether written or oral.

- 自动概括：Contract includes any instrument_kind of contract, agreement, instrument, undertaking, indenture, commitment, loan, or license; or any other instrument_kind that is a legally binding obligation. Written or oral form does not affect inclusion.
- 模型指出的问题：The predicate faithfully reflects the enumerated alternatives: contract, agreement, instrument, undertaking, indenture, commitment, loan, and license qualify without a separate legally-binding condition; only the residual 'other' category must be a legally binding obligation. The written/oral clause does not add a condition.；Cases c1 through c8 code legally_binding_obligation=true, but their texts do not expressly state that fact. They identify an enumerated instrument type, which is sufficient for the predicate, but the supplied fact vectors contain unsupported binding-status values.；No external attachments, incorporated definitions, or redacted facts are needed to interpret the quoted definition.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`c4_written_undertaking`）：A company gives a written undertaking to complete environmental remediation.
  - 按完整合同，它属于`Contract`吗？`是/否/无法唯一判断`：
- 例2（`c10_written_other_binding`）：A written guarantee does not fit the named categories but is a legally binding obligation.
  - 按完整合同，它属于`Contract`吗？`是/否/无法唯一判断`：
- 例3（`c12_social_promise`）：A person promises to attend a dinner party, and the promise is not a legally binding obligation.
  - 按完整合同，它属于`Contract`吗？`是/否/无法唯一判断`：
- 例4（`c14_nonbinding_intent`）：A party issues a written statement of intent that is not a legally binding obligation and is not one of the named categories.
  - 按完整合同，它属于`Contract`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:85:Seller

- 合同编号：`85`；[完整合同](contracts/ci85.txt)
- 来源组：`challenge_topup_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/topup_rule_program_proposals_nonthinking.jsonl`
- 程序SHA256：`1122499f463326db0293273c91ab95de87c8977873ca20e7caf1fdcb3a94c385`
- 规则原文：

> As used in these Terms and Conditions, the terms (a) "Seller" shall mean Nanophase Technologies Corporation and (b) "Buyer" shall mean the party ordering shipment of Seller's products under the Order.

- 自动概括：A party is the Seller if and only if the party is Nanophase Technologies Corporation.
- 模型指出的问题：The predicate exactly states the source definition of Seller: a party is Seller when it is Nanophase Technologies Corporation; the source supplies no additional conditions or exceptions.；c07 does not expressly state that the shipped products are Seller's products. The source's Buyer definition includes that qualification, so coding the case as party_ordering_shipment requires an unsupported inference.；c11 states only that the party is Nanophase Technologies Corporation's parent company; it does not state that the party ordered shipment of Seller's products under an Order.；c12 states that the logistics provider ships products, not that it orders shipment of Seller's products under an Order.；c09 expressly supports the coded Nanophase identity, but it also states facts satisfying the Buyer definition. A single categorical party_role field cannot represent possible overlap between the independently defined Seller and Buyer terms; this does not alter the Seller predicate but is a modeling limitation.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`c02`）：The agreement identifies the entity as Nanophase Technologies Corporation, a Delaware corporation.
  - 按完整合同，它属于`Seller`吗？`是/否/无法唯一判断`：
- 例2（`c01`）：A contract clause states that the party is Nanophase Technologies Corporation.
  - 按完整合同，它属于`Seller`吗？`是/否/无法唯一判断`：
- 例3（`c05`）：The party is the party ordering shipment of Seller's products under the Order.
  - 按完整合同，它属于`Seller`吗？`是/否/无法唯一判断`：
- 例4（`c08`）：The entity is described as the purchaser that ordered shipment of Seller's products under the Order.
  - 按完整合同，它属于`Seller`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:313:Governmental or Regulatory Authority

- 合同编号：`313`；[完整合同](contracts/ci313.txt)
- 来源组：`challenge_topup_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/topup_rule_program_proposals_nonthinking.jsonl`
- 程序SHA256：`9fc624880b2c6be0d3068a73ed3f30c9d777e63ec2b4d2a657ae03aa55319ae5`
- 规则原文：

> "Governmental or Regulatory Authority" means governments, regulatory authorities, governmental departments, agencies, agents, commissions, bureaus, officials, courts, bodies, boards, tribunals or dispute settlement panels or other law, rule or regulation-making organizations or entities (a) having or purporting to have jurisdiction on behalf of any nation, territory or state or any other geographic or political subdivision of any of them, or (b) exercising, or entitled or purporting to exercise any administrative, executive, judicial, legislative, policy, regulatory or taxing authority or power.

- 自动概括：An entity is a Governmental or Regulatory Authority if it is one of the listed entity types (government, regulatory authority, governmental department, agency, agent, commission, bureau, official, court, body, board, tribunal, dispute settlement panel, or other law/rule/regulation-making organization or entity) AND either (a) it has or purports to have jurisdiction on behalf of a nation, territory, state, or geographic/political subdivision, or (b) it exercises, is entitled to exercise, or purports to exercise administrative, executive, judicial, legislative, policy, regulatory, or taxing authority or power.
- 模型指出的问题：The predicate treats `other_entity` as an unrestricted residual entity category. The source instead refers to “other law, rule or regulation-making organizations or entities”; it does not extend coverage to every other kind of entity that has jurisdiction or exercises authority. Thus, for example, a non-law/rule/regulation-making private entity with qualifying authority would be included by the proposed predicate but is not expressly included by the definition.；The field/value design should distinguish the specifically covered residual category of other law-, rule-, or regulation-making organizations/entities from entities outside the enumerated and residual covered categories. The existing `other_entity` value is overbroad.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`c03`）：The entity is a court that purports to have jurisdiction on behalf of a state.
  - 按完整合同，它属于`Governmental or Regulatory Authority`吗？`是/否/无法唯一判断`：
- 例2（`c02`）：The entity is a regulatory authority that exercises regulatory authority.
  - 按完整合同，它属于`Governmental or Regulatory Authority`吗？`是/否/无法唯一判断`：
- 例3（`c15`）：The entity is a dispute settlement panel that has no jurisdiction on behalf of any nation, territory, state, or political subdivision and does not exercise, is not entitled to exercise, and does not purport to exercise any administrative, executive, judicial, legislative, policy, regulatory, or taxing authority.
  - 按完整合同，它属于`Governmental or Regulatory Authority`吗？`是/否/无法唯一判断`：
- 例4（`c11`）：The entity is a tribunal that has no jurisdiction on behalf of any nation, territory, state, or political subdivision and does not exercise, is not entitled to exercise, and does not purport to exercise any administrative, executive, judicial, legislative, policy, regulatory, or taxing authority.
  - 按完整合同，它属于`Governmental or Regulatory Authority`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

