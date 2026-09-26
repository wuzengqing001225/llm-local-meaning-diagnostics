# 正式来源规则复核 第2批

此包按来源文本生成，没有读新A分数或B读者结果。模型意见是预筛，不是金标准。
你只需核原文引文、中文规则概括和4个固定事实；程序字段和布尔表达式由我核。
**不要**根据你预计哪个模型会答错来决定收录。自动审查为`revise`的条目可以填`待改`，写明哪一条件不对，无需你改JSON。

## cuadfull:210:Registered Bidder

- 合同编号：`210`；[完整合同](contracts/ci210.txt)
- 来源组：`challenge_topup_candidate`；自动审查：`accept`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/topup_rule_program_proposals_nonthinking.jsonl`
- 程序SHA256：`fe7f66db3f675666aa0e5f03d9d8a9ec9629effe23b5c526707fbb2b51269164`
- 规则原文：

> "Registered Bidder" means a person or entity that executed an agreement with Kubient in order to use the Auction Platform to participate in Auction and to deliver Impressions in Inventory.

- 自动概括：A Registered Bidder is a person or entity that executed an agreement with Kubient in order to use the Auction Platform to participate in Auction and to deliver Impressions in Inventory. All five conditions must be true.
- 模型指出的问题：无

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1：Jordan is a person. Jordan executed an agreement with Kubient. The agreement's purpose was to use the Auction Platform. The agreement's purpose was to participate in Auction. The agreement's purpose was to deliver Impressions in Inventory.
  - 按完整合同，它属于`Registered Bidder`吗？`是/否/无法唯一判断`：
- 例2：Gamma Partners is an entity. Gamma Partners executed an agreement with Kubient. The agreement's purpose was to use the Auction Platform. The agreement's purpose was to participate in Auction. The agreement's purpose was to deliver Impressions in Inventory.
  - 按完整合同，它属于`Registered Bidder`吗？`是/否/无法唯一判断`：
- 例3：Iota LLC is an entity. Iota LLC executed an agreement with Kubient. The agreement's purpose was to use the Auction Platform. The agreement's purpose was not to participate in Auction. The agreement's purpose was not to deliver Impressions in Inventory.
  - 按完整合同，它属于`Registered Bidder`吗？`是/否/无法唯一判断`：
- 例4：Zeta LLC is an entity. Zeta LLC executed an agreement with Kubient. The agreement's purpose was to use the Auction Platform. The agreement's purpose was not to participate in Auction. The agreement's purpose was to deliver Impressions in Inventory.
  - 按完整合同，它属于`Registered Bidder`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:71:Third Party

- 合同编号：`71`；[完整合同](contracts/ci71.txt)
- 来源组：`challenge_topup_candidate`；自动审查：`accept`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/topup_rule_program_proposals_nonthinking.jsonl`
- 程序SHA256：`908ce3f66f0e6a080401fd4e74cc22961715333949d8b9a3d443b1d3e7139d82`
- 规则原文：

> 1.117 "Third Party" means a Person other than Manufacturer, Customer or their respective Affiliates.

- 自动概括：A Third Party is a Person who is not the Manufacturer, not the Customer, and not an Affiliate of either the Manufacturer or the Customer.
- 模型指出的问题：Several case IDs suggest distinctions not stated in their fact text (for example, 'in_person_affiliate_of_other'), but the coded fields and stated facts themselves are consistent.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1：Blair is a Person. Blair is not the Manufacturer. Blair is not the Customer. Blair is not an Affiliate of the Manufacturer. Blair is not an Affiliate of the Customer.
  - 按完整合同，它属于`Third Party`吗？`是/否/无法唯一判断`：
- 例2：Dana is a Person. Dana is not the Manufacturer. Dana is not the Customer. Dana is not an Affiliate of the Manufacturer. Dana is not an Affiliate of the Customer.
  - 按完整合同，它属于`Third Party`吗？`是/否/无法唯一判断`：
- 例3：Morgan is a Person. Morgan is the Manufacturer. Morgan is the Customer. Morgan is not an Affiliate of the Manufacturer. Morgan is not an Affiliate of the Customer.
  - 按完整合同，它属于`Third Party`吗？`是/否/无法唯一判断`：
- 例4：Sam is not a Person. Sam is not the Manufacturer. Sam is not the Customer. Sam is an Affiliate of the Manufacturer. Sam is not an Affiliate of the Customer.
  - 按完整合同，它属于`Third Party`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:265:Territory

- 合同编号：`265`；[完整合同](contracts/ci265.txt)
- 来源组：`challenge_topup_candidate`；自动审查：`accept`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/topup_rule_program_proposals_nonthinking.jsonl`
- 程序SHA256：`5e3583cdfcddac13346f8187614a533bebdd4c1cb2a061cc0da04d32d8c61206`
- 规则原文：

> 1.8 "Territory" shall mean the geographic area of Taiwan.

- 自动概括：A location is in the Territory if and only if it is within the geographic area of Taiwan.
- 模型指出的问题：无

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1：A customer location is in Matsu, which is within the geographic area of Taiwan.
  - 按完整合同，它属于`Territory`吗？`是/否/无法唯一判断`：
- 例2：A customer location is in Hsinchu, which is within the geographic area of Taiwan.
  - 按完整合同，它属于`Territory`吗？`是/否/无法唯一判断`：
- 例3：A customer location is in Shanghai, which is not within the geographic area of Taiwan.
  - 按完整合同，它属于`Territory`吗？`是/否/无法唯一判断`：
- 例4：A customer location is in Singapore, which is not within the geographic area of Taiwan.
  - 按完整合同，它属于`Territory`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:150:PARTY

- 合同编号：`150`；[完整合同](contracts/ci150.txt)
- 来源组：`challenge_candidate`；自动审查：`accept`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/rule_program_proposals_nonthinking.jsonl`
- 程序SHA256：`6f3bc0e803118cbc2599c40a92c8d9258b0377fcbfcb3c192176c0d84d519621`
- 规则原文：

> 1.28. "PARTY" shall mean each of T&L and Igene, and "PARTIES" shall mean both T&L and Igene.

- 自动概括：An entity is a PARTY if and only if it is T&L or Igene.
- 模型指出的问题：无

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1：The entity is T&L, and it is not Igene.
  - 按完整合同，它属于`PARTY`吗？`是/否/无法唯一判断`：
- 例2：The entity is T&L.
  - 按完整合同，它属于`PARTY`吗？`是/否/无法唯一判断`：
- 例3：The entity is Beta, a sole proprietorship.
  - 按完整合同，它属于`PARTY`吗？`是/否/无法唯一判断`：
- 例4：The entity is Beta.
  - 按完整合同，它属于`PARTY`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:1:Application

- 合同编号：`1`；[完整合同](contracts/ci1.txt)
- 来源组：`challenge_topup_candidate`；自动审查：`accept`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/topup_rule_program_proposals.jsonl`
- 程序SHA256：`31d71c9d109c8ba341651e71fa72db90b7826086f116e6b12f8cf8384ad6700c`
- 规则原文：

> (b) "Application" means any application, plug-in, helper, component or other executable code that runs on a user's computer, examples of which include those that provide browser helper objects, instant messaging, chat, email, data, file viewing, media playing, file sharing, games, internet navigation, search and other services.

- 自动概括：An item qualifies as an Application only if it is an application, plug-in, helper, component, or other executable code AND it runs on a user's computer.
- 模型指出的问题：无

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1：A chat software component runs on a user's computer.
  - 按完整合同，它属于`Application`吗？`是/否/无法唯一判断`：
- 例2：A spreadsheet application runs on a user's computer.
  - 按完整合同，它属于`Application`吗？`是/否/无法唯一判断`：
- 例3：A media component runs only inside a cloud service, not on a user's computer.
  - 按完整合同，它属于`Application`吗？`是/否/无法唯一判断`：
- 例4：A website provides search services through a browser, but the website itself is not an application, plug-in, helper, component, or other executable code and does not run on the user's computer.
  - 按完整合同，它属于`Application`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:72:Third Person

- 合同编号：`72`；[完整合同](contracts/ci72.txt)
- 来源组：`challenge_candidate`；自动审查：`accept`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/rule_program_proposals.jsonl`
- 程序SHA256：`0c61de462f0aadad9b73baaea60eef22209f5ea948d8df3d6af96aef9deaaf33`
- 规则原文：

> "Third Person" means any Person or entity other than AMAG, Antares, or an Affiliate or sublicensee of either Party with respect to this Agreement and/or the Development and License Agreement.

- 自动概括：A Third Person is any Person or entity that is not AMAG, not Antares, not an Affiliate of either Party with respect to this Agreement and/or the Development and License Agreement, and not a sublicensee of either Party with respect to this Agreement and/or the Development and License Agreement.
- 模型指出的问题：无

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1：Omicron is a Person or entity; Omicron is not AMAG; Omicron is not Antares; Omicron is an Affiliate of a non-Party and a sublicensee of a non-Party, but is not an Affiliate of either Party with respect to this Agreement and/or the Development and License Agreement and is not a sublicensee of either Party with respect to this Agreement and/or the Development and License Agreement.
  - 按完整合同，它属于`Third Person`吗？`是/否/无法唯一判断`：
- 例2：Epsilon is a Person or entity; Epsilon is not AMAG; Epsilon is not Antares; Epsilon is an Affiliate of an unrelated non-Party, but is not an Affiliate of either Party with respect to this Agreement and/or the Development and License Agreement; Epsilon is not a sublicensee of either Party with respect to this Agreement and/or the Development and License Agreement.
  - 按完整合同，它属于`Third Person`吗？`是/否/无法唯一判断`：
- 例3：Antares is a Person or entity; Antares is not AMAG; Antares is Antares; Antares is not an Affiliate of either Party with respect to this Agreement and/or the Development and License Agreement; Antares is not a sublicensee of either Party with respect to this Agreement and/or the Development and License Agreement.
  - 按完整合同，它属于`Third Person`吗？`是/否/无法唯一判断`：
- 例4：Iota is a Person or entity; Iota is not AMAG; Iota is not Antares; Iota is not an Affiliate of either Party with respect to this Agreement and/or the Development and License Agreement; Iota is a sublicensee of AMAG with respect to this Agreement.
  - 按完整合同，它属于`Third Person`吗？`是/否/无法唯一判断`：
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
- 例1：Good H is not owned by Merchant. It is not held by Merchant on memo. It is not held by Merchant on consignment. The applicable consignor has not agreed otherwise. It is held by Merchant as bailee.
  - 按完整合同，它属于`Excluded Goods`吗？`是/否/无法唯一判断`：
- 例2：Good A is not owned by Merchant. It is not held by Merchant on memo. It is not held by Merchant on consignment. The applicable consignor has not agreed otherwise. It is not held by Merchant as bailee.
  - 按完整合同，它属于`Excluded Goods`吗？`是/否/无法唯一判断`：
- 例3：Good I is owned by Merchant. It is not held by Merchant on memo. It is not held by Merchant on consignment. The applicable consignor has not agreed otherwise. It is not held by Merchant as bailee.
  - 按完整合同，它属于`Excluded Goods`吗？`是/否/无法唯一判断`：
- 例4：Good L is owned by Merchant. It is not held by Merchant on memo. It is not held by Merchant on consignment. The applicable consignor has not agreed otherwise. It is not held by Merchant as bailee.
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
- 例1：Gamma is a Person. Gamma is not SutroVax. Gamma is not Sutro. Gamma is not an Affiliate of SutroVax. Gamma is not an Affiliate of Sutro.
  - 按完整合同，它属于`Third Party`吗？`是/否/无法唯一判断`：
- 例2：Delta is a Person. Delta is not SutroVax. Delta is not Sutro. Delta is not an Affiliate of SutroVax. Delta is not an Affiliate of Sutro.
  - 按完整合同，它属于`Third Party`吗？`是/否/无法唯一判断`：
- 例3：Lambda is not a Person. Lambda is not SutroVax. Lambda is not Sutro. Lambda is an Affiliate of SutroVax. Lambda is not an Affiliate of Sutro.
  - 按完整合同，它属于`Third Party`吗？`是/否/无法唯一判断`：
- 例4：Omicron is a Person. Omicron is not SutroVax. Omicron is Sutro. Omicron is not an Affiliate of SutroVax. Omicron is an Affiliate of Sutro.
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
- 例1：Entity A is PHLVIC, PLIC, PEPCO, and ICC.
  - 按完整合同，它属于`Parties`吗？`是/否/无法唯一判断`：
- 例2：Entity A is PEPCO and is not PHLVIC, PLIC, or ICC.
  - 按完整合同，它属于`Parties`吗？`是/否/无法唯一判断`：
- 例3：Entity A is an affiliate of PHLVIC but is not PHLVIC itself and is not PLIC, PEPCO, or ICC.
  - 按完整合同，它属于`Parties`吗？`是/否/无法唯一判断`：
- 例4：Entity A is an individual employee and is not PHLVIC, not PLIC, not PEPCO, and not ICC.
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
- 例1：Acme LLC is a Person. Acme LLC is not PB. Acme LLC is not SFJ. Acme LLC is not an Affiliate of PB. Acme LLC is not an Affiliate of SFJ.
  - 按完整合同，它属于`Third Party`吗？`是/否/无法唯一判断`：
- 例2：Gamma Foundation is a Person. Gamma Foundation is not PB. Gamma Foundation is not SFJ. Gamma Foundation is not an Affiliate of PB. Gamma Foundation is not an Affiliate of SFJ.
  - 按完整合同，它属于`Third Party`吗？`是/否/无法唯一判断`：
- 例3：Global Affiliate is not a Person. Global Affiliate is not PB. Global Affiliate is not SFJ. Global Affiliate is an Affiliate of PB. Global Affiliate is an Affiliate of SFJ.
  - 按完整合同，它属于`Third Party`吗？`是/否/无法唯一判断`：
- 例4：SFJ is a Person. SFJ is not PB. SFJ is SFJ. SFJ is not an Affiliate of PB. SFJ is not an Affiliate of SFJ.
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
- 例1：A county ordinance enacted by a duly authorized foreign county instrumentality has the effect of law in a foreign political subdivision and applies to the Company or its business.
  - 按完整合同，它属于`Applicable Laws and Regulations`吗？`是/否/无法唯一判断`：
- 例2：A city ordinance enacted by a duly authorized city instrumentality of a city political subdivision has the effect of law in a domestic or foreign political subdivision and applies to the Company.
  - 按完整合同，它属于`Applicable Laws and Regulations`吗？`是/否/无法唯一判断`：
- 例3：Nonbinding guidance issued by a duly authorized federal agency has no effect of law, has no effect-of-law location, and applies to the Company.
  - 按完整合同，它属于`Applicable Laws and Regulations`吗？`是/否/无法唯一判断`：
- 例4：A federal statute enacted by a duly authorized U.S. Congress instrumentality has the effect of law in the United States but applies only to other companies, not to the Company or its business.
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
- 例1：On Friday, the New York Stock Exchange is open for trading, and the Fund calculates its net asset value pursuant to the rules of the SEC.
  - 按完整合同，它属于`Business Day`吗？`是/否/无法唯一判断`：
- 例2：On Monday, the New York Stock Exchange is open for trading, and the Fund calculates its net asset value pursuant to the rules of the SEC.
  - 按完整合同，它属于`Business Day`吗？`是/否/无法唯一判断`：
- 例3：On Saturday, the New York Stock Exchange is not open for trading, and the Fund does not calculate its net asset value pursuant to the rules of the SEC.
  - 按完整合同，它属于`Business Day`吗？`是/否/无法唯一判断`：
- 例4：On Sunday, the New York Stock Exchange is not open for trading, but the Fund calculates its net asset value pursuant to the rules of the SEC.
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
- 例1：Information B was disclosed to the Contractor as a consequence of or through the Contractor's position as an officer of Emerald, and the information is not generally known in the industry in which Emerald operates.
  - 按完整合同，它属于`Confidential Information`吗？`是/否/无法唯一判断`：
- 例2：Information C was disclosed to the Contractor as a consequence of or through the Contractor's position as an employee of Emerald, and the information is not generally known in the industry in which Emerald operates.
  - 按完整合同，它属于`Confidential Information`吗？`是/否/无法唯一判断`：
- 例3：Information F was disclosed to the Contractor as a consequence of or through the Contractor's position as a director of a different company, not Emerald, and the information is not generally known in the industry in which Emerald operates.
  - 按完整合同，它属于`Confidential Information`吗？`是/否/无法唯一判断`：
- 例4：Information H was disclosed to a third party, not to the Contractor, as a consequence of or through the Contractor's position as a director of Emerald, and the information is not generally known in the industry in which Emerald operates.
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
- 例1：A foreign provincial regulation that has the force of law.
  - 按完整合同，它属于`Law`吗？`是/否/无法唯一判断`：
- 例2：A local rule that has the force of law.
  - 按完整合同，它属于`Law`吗？`是/否/无法唯一判断`：
- 例3：A contract that has the force of law.
  - 按完整合同，它属于`Law`吗？`是/否/无法唯一判断`：
- 例4：A domestic rule that has no jurisdiction classification.
  - 按完整合同，它属于`Law`吗？`是/否/无法唯一判断`：
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
- 例1：Epsilon JV is a joint venture.
  - 按完整合同，它属于`Person`吗？`是/否/无法唯一判断`：
- 例2：Delta LLC is a limited liability company.
  - 按完整合同，它属于`Person`吗？`是/否/无法唯一判断`：
- 例3：A tort claim is a legal claim, not an entity or organization.
  - 按完整合同，它属于`Person`吗？`是/否/无法唯一判断`：
- 例4：A contract is a legal agreement, not an entity or organization.
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
- 例1：Acme Corp is responsible for all billing and collection matters associated with the Co-Branded Service.
  - 按完整合同，它属于`Billing Party`吗？`是/否/无法唯一判断`：
- 例2：Gamma Inc is responsible for all billing and collection matters associated with the Co-Branded Service.
  - 按完整合同，它属于`Billing Party`吗？`是/否/无法唯一判断`：
- 例3：Eta Group is responsible for all billing and collection matters, but those matters are not associated with the Co-Branded Service.
  - 按完整合同，它属于`Billing Party`吗？`是/否/无法唯一判断`：
- 例4：Zeta Partners is not responsible for all billing and collection matters associated with the Co-Branded Service.
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
- 例1：A company gives a written undertaking to complete environmental remediation.
  - 按完整合同，它属于`Contract`吗？`是/否/无法唯一判断`：
- 例2：A written guarantee does not fit the named categories but is a legally binding obligation.
  - 按完整合同，它属于`Contract`吗？`是/否/无法唯一判断`：
- 例3：A person makes an unenforceable gratuitous promise to give a gift, and it is not a legally binding obligation.
  - 按完整合同，它属于`Contract`吗？`是/否/无法唯一判断`：
- 例4：A person promises to attend a dinner party, and the promise is not a legally binding obligation.
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
- 例1：The agreement identifies the entity as Nanophase Technologies Corporation, a Delaware corporation.
  - 按完整合同，它属于`Seller`吗？`是/否/无法唯一判断`：
- 例2：The preamble defines the seller as Nanophase Technologies Corporation.
  - 按完整合同，它属于`Seller`吗？`是/否/无法唯一判断`：
- 例3：The party is an unrelated logistics provider that ships products under the Order.
  - 按完整合同，它属于`Seller`吗？`是/否/无法唯一判断`：
- 例4：The party is a distributor that orders shipment of Seller's products under the Order.
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
- 例1：The entity is a commission that has jurisdiction on behalf of a territory and also exercises administrative authority.
  - 按完整合同，它属于`Governmental or Regulatory Authority`吗？`是/否/无法唯一判断`：
- 例2：The entity is a bureau that purports to exercise taxing authority.
  - 按完整合同，它属于`Governmental or Regulatory Authority`吗？`是/否/无法唯一判断`：
- 例3：The entity is a board that has no jurisdiction on behalf of any nation, territory, state, or political subdivision and does not exercise, is not entitled to exercise, and does not purport to exercise any administrative, executive, judicial, legislative, policy, regulatory, or taxing authority.
  - 按完整合同，它属于`Governmental or Regulatory Authority`吗？`是/否/无法唯一判断`：
- 例4：The entity is a bureau that has no jurisdiction on behalf of any nation, territory, state, or political subdivision and does not exercise, is not entitled to exercise, and does not purport to exercise any administrative, executive, judicial, legislative, policy, regulatory, or taxing authority.
  - 按完整合同，它属于`Governmental or Regulatory Authority`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:187:AFFILIATED COMPANY

- 合同编号：`187`；[完整合同](contracts/ci187.txt)
- 来源组：`challenge_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/rule_program_proposals_nonthinking.jsonl`
- 程序SHA256：`9e55bc33e20e079eaecb11de0325ab4dce9482339ba3060e8f516d3727de5da3`
- 规则原文：

> 1.16 "AFFILIATED COMPANY" shall mean any company owned or controlled by, under common control with or controlling CERES, "control" meaning in this context the direct or indirect ownership of more than fifty percent (50%) of the voting stock/shares of a company, or the power to nominate at least half of the directors.

- 自动概括：An entity is an AFFILIATED COMPANY if it is a company and at least one of the following holds: (1) CERES directly or indirectly owns more than 50% of its voting stock/shares; (2) it is under common control with CERES; (3) it controls CERES; or (4) it has the power to nominate at least half of CERES's directors.
- 模型指出的问题：The ownership test is not an exact implementation of 'more than fifty percent': it enumerates selected numeric values (50.1, 51, 75, 100) rather than applying a greater-than-50 comparison, so ownership percentages such as 50.5% or 60% would incorrectly fail.；The source-defined meaning of control includes the power to nominate at least half of a company's directors. The predicate omits the route under which CERES controls an entity by having nomination power over that entity's directors.；Case in_nominate states that Epsilon has power to nominate at least half of CERES's directors while coding controls_ceres as false. Under the quoted definition, that power constitutes control of CERES, making the coded facts inconsistent with the source-defined term.；A bare controls_ceres field can represent the source-defined conclusion, but the program does not separately model the corresponding CERES-to-entity nomination-power control route required by 'controlled by ... CERES'.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1：Delta SA is a company. Delta SA controls CERES. CERES owns 0% of Delta SA's voting shares, Delta SA is not under common control with CERES, and Delta SA has no power to nominate at least half of CERES's directors.
  - 按完整合同，它属于`AFFILIATED COMPANY`吗？`是/否/无法唯一判断`：
- 例2：Zeta Ltd is a company. CERES directly owns 50.1% of Zeta Ltd's voting shares. Zeta Ltd is not under common control with CERES, does not control CERES, and has no power to nominate at least half of CERES's directors.
  - 按完整合同，它属于`AFFILIATED COMPANY`吗？`是/否/无法唯一判断`：
- 例3：Mu is not a company. Mu is under common control with CERES. CERES owns 0% of Mu's voting shares, Mu does not control CERES, and Mu has no power to nominate at least half of CERES's directors.
  - 按完整合同，它属于`AFFILIATED COMPANY`吗？`是/否/无法唯一判断`：
- 例4：Kappa LLC is a company. CERES owns 0% of Kappa LLC's voting shares. Kappa LLC is not under common control with CERES, does not control CERES, and has no power to nominate at least half of CERES's directors.
  - 按完整合同，它属于`AFFILIATED COMPANY`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

