# 正式来源规则复核 第5批

此包按来源文本生成，没有读新A分数或B读者结果。模型意见是预筛，不是金标准。
你只需核原文引文、中文规则概括和4个固定事实；程序字段和布尔表达式由我核。
**不要**根据你预计哪个模型会答错来决定收录。自动审查为`revise`的条目可以填`待改`，写明哪一条件不对，无需你改JSON。

## cuadfull:332:Copyrights

- 合同编号：`332`；[完整合同](contracts/ci332.txt)
- 来源组：`challenge_topup_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/topup_rule_program_proposals_nonthinking.jsonl`
- 程序SHA256：`19c02e5a319fb87b88c96fb409e508fa54bba3a6e128b0c33515ae728acac0dd`
- 规则原文：

> (t) "Copyrights" means copyrights (whether registered or unregistered) including applications for copyright (excluding, for clarity, Trademarks).

- 自动概括：A work qualifies as a Copyright if it is a copyright (registered or unregistered) or an application for copyright, and it is not a Trademark.
- 模型指出的问题：The predicate faithfully implements the quoted definition: a Copyright is a copyright or copyright application, excluding Trademarks.；The definition of the capitalized dependent term "Trademarks" is not supplied. Its scope cannot be verified from the provided source quote alone.；c01, c02, c04, and c05 code is_copyright_application=false, but their texts do not expressly state that no copyright application exists.；c03 and c06 code is_copyright=false and is_registered=false. A pending copyright application does not expressly state either coded negative fact.；c11 and c12 code is_copyright=false, but a registered copyright application does not expressly state that it is not also a copyright.；c13 and c14 code is_copyright=false, but an unregistered copyright application does not expressly state that it is not also a copyright.；The source does not establish that registration status applies to copyright applications; although is_registered is not used by the predicate, application-registration case characterizations are unsupported by the quoted text.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1：A registered copyright on a novel, and it is not a trademark.
  - 按完整合同，它属于`Copyrights`吗？`是/否/无法唯一判断`：
- 例2：An unregistered copyright on a song, and it is not a trademark.
  - 按完整合同，它属于`Copyrights`吗？`是/否/无法唯一判断`：
- 例3：A registered copyright application that is also a trademark.
  - 按完整合同，它属于`Copyrights`吗？`是/否/无法唯一判断`：
- 例4：An unregistered trade secret that is not a copyright, not a copyright application, and not a trademark.
  - 按完整合同，它属于`Copyrights`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:298:Field of Use

- 合同编号：`298`；[完整合同](contracts/ci298.txt)
- 来源组：`challenge_topup_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/topup_rule_program_proposals_nonthinking.jsonl`
- 程序SHA256：`ae8f90174e564449c1cffc577be2ed75252e47a45f1485a110cf0270a47c2504`
- 规则原文：

> 1.3 The term "Field of Use" means exclusively transport refrigeration systems for vehicles and trailers.

- 自动概括：The term 'Field of Use' means exclusively transport refrigeration systems for vehicles and trailers. An item is in the Field of Use if it is a transport refrigeration system and it is for vehicles or trailers.
- 模型指出的问题：The source says systems 'for vehicles and trailers.' The proposed predicate substitutes an inclusive OR condition ('for vehicles or trailers'). This is a plausible commercial reading but is not an exact logical consequence of the quoted conjunction; the source does not resolve whether both vehicle and trailer use is required or whether the phrase names alternative categories.；The source is insufficient to validate the proposed OR predicate exactly without a definition, surrounding contract language, or other authoritative clarification of 'for vehicles and trailers.'；Case in_vehicle_unspecified_trailer expressly leaves trailer compatibility unspecified but codes is_for_trailers=false.；Case in_trailer_unspecified_vehicle expressly leaves vehicle compatibility unspecified but codes is_for_vehicles=false.；Cases out_not_refrigeration and out_vehicle_but_not_refrigeration do not expressly state that the systems are not for trailers, although is_for_trailers=false is coded.；Case out_trailer_but_not_refrigeration does not expressly state that the system is not for vehicles, although is_for_vehicles=false is coded.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1：A transport refrigeration system for trailers; vehicle compatibility is not specified.
  - 按完整合同，它属于`Field of Use`吗？`是/否/无法唯一判断`：
- 例2：A transport refrigeration system designed for vehicles, not trailers.
  - 按完整合同，它属于`Field of Use`吗？`是/否/无法唯一判断`：
- 例3：A trailer lighting system, not a transport refrigeration system.
  - 按完整合同，它属于`Field of Use`吗？`是/否/无法唯一判断`：
- 例4：A vehicle and trailer washing system, not a transport refrigeration system.
  - 按完整合同，它属于`Field of Use`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:429:Confidential Information

- 合同编号：`429`；[完整合同](contracts/ci429.txt)
- 来源组：`challenge_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/rule_program_proposals.jsonl`
- 程序SHA256：`280b4823234600ba972f650f104a517a292429514a9e3f8afae3276272a09563`
- 规则原文：

> "Confidential Information" means any data, materials or information that is disclosed by either party to the other party during the term hereof, in oral or written form, and which is marked or otherwise reasonably identified as "confidential" or "proprietary". Confidential Information also includes any information described in this Section which either party obtains from a third party under an obligation of confidentiality. Confidential Information does not include any data or information which the receiving party can demonstrate with competent written proof: (i) was already known to it at the time of disclosure; (ii) was independently developed by it without reference to the disclosing party's Confidential Information; (iii) is in the public domain; (iv) was rightfully disclosed to it by a third party without obligation of confidentiality; or (v) is required to be disclosed pursuant to any statutory or regulatory authority or court order, provided the disclosing party is given prompt written notice of such requirement and the scope of such disclosure is limited to the extent possible.

- 自动概括：Confidential Information if either (a) information is disclosed by one party to the other during the term in oral or written form and is marked or reasonably identified as confidential or proprietary, or (b) information is obtained from a third party under a confidentiality obligation; unless the receiving party can demonstrate with competent written proof that an exclusion applies: prior knowledge, independent development, public domain, rightful third-party disclosure without confidentiality obligation, or legally required disclosure with prompt written notice and limited scope.
- 模型指出的问题：The predicate faithfully implements the stated inclusion routes and the five exclusions, including the competent-written-proof requirement and the notice-and-scope proviso for compelled disclosure.；The case fact vectors are not fully text-grounded. Across the cases, numerous fields are coded false although the accompanying fact text does not explicitly state their negation. For example, cases involving a third-party receipt set disclosed_by_party_to_other, oral_or_written_form, and other exclusion-related facts to false without expressly establishing those facts; a third-party receipt does not itself establish that no party-to-party disclosure also occurred or that the information was not oral or written.；Similarly, exclusion-focused cases generally establish one proven exclusion but do not expressly state false values for all other coded exclusion predicates. Statements such as 'no exclusion applies' or inability to demonstrate an exclusion may establish the operative outcome, but do not explicitly establish every underlying raw fact encoded false (for example, that information is not actually public-domain rather than merely unproven).；The source quote itself is sufficient to encode the rule; no required external attachment or redacted contract language is apparent.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1：Party A discloses marked written information during the term; Party B can demonstrate with competent written proof that disclosure is required by statute, but Party B does not give prompt written notice to Party A and limits the scope of disclosure.
  - 按完整合同，它属于`Confidential Information`吗？`是/否/无法唯一判断`：
- 例2：Party A discloses marked oral information during the term; Party B can demonstrate with competent written proof that disclosure is required by regulatory authority and gives prompt written notice to Party A, but does not limit the scope of disclosure to the extent possible.
  - 按完整合同，它属于`Confidential Information`吗？`是/否/无法唯一判断`：
- 例3：Party A discloses marked oral information during the term; Party B can demonstrate with competent written proof that it independently developed the information without reference to Party A's Confidential Information.
  - 按完整合同，它属于`Confidential Information`吗？`是/否/无法唯一判断`：
- 例4：No party discloses information to the other during the term, no information is obtained from a third party under a confidentiality obligation, and no exclusion can be demonstrated with competent written proof.
  - 按完整合同，它属于`Confidential Information`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:474:Users

- 合同编号：`474`；[完整合同](contracts/ci474.txt)
- 来源组：`source_sample_candidate`；自动审查：`accept`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/rule_program_proposals.jsonl`
- 程序SHA256：`604a2b0cfdfc0d411b2097ae92718758f21dbdeaf0142441e579caa56ba942cf`
- 规则原文：

> (p) "Users" shall mean all subscribers to Licensee's services.

- 自动概括：A party is a User exactly when it is a subscriber to Licensee's services.
- 模型指出的问题：无

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1：Dana subscribes to only one of Licensee's services and is a subscriber to Licensee's services.
  - 按完整合同，它属于`Users`吗？`是/否/无法唯一判断`：
- 例2：Epsilon LLC is a business entity that is a subscriber to Licensee's services.
  - 按完整合同，它属于`Users`吗？`是/否/无法唯一判断`：
- 例3：Omega Corp is an affiliate of Licensee but is not a subscriber to Licensee's services.
  - 按完整合同，它属于`Users`吗？`是/否/无法唯一判断`：
- 例4：Leo uses a friend's login but is not a subscriber to Licensee's services.
  - 按完整合同，它属于`Users`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:268:EMA

- 合同编号：`268`；[完整合同](contracts/ci268.txt)
- 来源组：`source_sample_candidate`；自动审查：`accept`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/rule_program_proposals.jsonl`
- 程序SHA256：`f288814e60bef587b550b84a83f8f92c3b377e1601b79d5f7b0f8df39a996c38`
- 规则原文：

> "EMA" means the European Medicines Agency or any successor entity.

- 自动概括：An entity is EMA if its entity_status is either 'European Medicines Agency' or 'successor entity'.
- 模型指出的问题：无

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1：After a merger, an entity is the successor entity to the European Medicines Agency; its entity_status is successor entity.
  - 按完整合同，它属于`EMA`吗？`是/否/无法唯一判断`：
- 例2：An entity is the European Medicines Agency; its entity_status is European Medicines Agency.
  - 按完整合同，它属于`EMA`吗？`是/否/无法唯一判断`：
- 例3：An entity has a name similar to the European Medicines Agency but is not the European Medicines Agency and is not a successor entity; its entity_status is other entity.
  - 按完整合同，它属于`EMA`吗？`是/否/无法唯一判断`：
- 例4：An entity is a successor entity to a different medicines agency, not the European Medicines Agency and not a successor entity to the European Medicines Agency; its entity_status is other entity.
  - 按完整合同，它属于`EMA`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:323:Applicant

- 合同编号：`323`；[完整合同](contracts/ci323.txt)
- 来源组：`source_sample_candidate`；自动审查：`accept`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/rule_program_proposals.jsonl`
- 程序SHA256：`0d6d7e67be9de3e75d66776ce18a53ef17234dd77156f92305bd8390fece9755`
- 规则原文：

> "Applicant" shall mean a Merchant who submits an Application.

- 自动概括："Applicant" means an entity that is a Merchant and submits an Application.
- 模型指出的问题：无

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1：A retail store is a Merchant and submits an Application.
  - 按完整合同，它属于`Applicant`吗？`是/否/无法唯一判断`：
- 例2：An online seller qualifies as a Merchant and submits an Application.
  - 按完整合同，它属于`Applicant`吗？`是/否/无法唯一判断`：
- 例3：An individual consumer submits an Application but is not a Merchant.
  - 按完整合同，它属于`Applicant`吗？`是/否/无法唯一判断`：
- 例4：A Merchant drafts an Application but does not submit it.
  - 按完整合同，它属于`Applicant`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:205:Manning Identification

- 合同编号：`205`；[完整合同](contracts/ci205.txt)
- 来源组：`source_sample_candidate`；自动审查：`accept`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/rule_program_proposals.jsonl`
- 程序SHA256：`0a19fc050d6b2c2b80b11a96f0308692f12f1e2806504b2a87f1b30cf565a0e6`
- 规则原文：

> (e) "Manning Identification" shall mean any words or symbols or photographic or graphic representations or combinations thereof which identify Manning such as, for example, the name and likeness of Manning.

- 自动概括：A Manning Identification is an item that is words, symbols, photographic representations, graphic representations, or a combination of those, and that identifies Manning.
- 模型指出的问题：无

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1：A photograph of Manning's jersey with his name identifies Manning.
  - 按完整合同，它属于`Manning Identification`吗？`是/否/无法唯一判断`：
- 例2：A cartoon graphic drawing of Manning identifies Manning.
  - 按完整合同，它属于`Manning Identification`吗？`是/否/无法唯一判断`：
- 例3：A word 'Manning' used only as a street name does not identify the person Manning.
  - 按完整合同，它属于`Manning Identification`吗？`是/否/无法唯一判断`：
- 例4：A photograph of Tom Brady does not identify Manning.
  - 按完整合同，它属于`Manning Identification`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:509:Contract Period

- 合同编号：`509`；[完整合同](contracts/ci509.txt)
- 来源组：`source_sample_candidate`；自动审查：`accept`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/rule_program_proposals_nonthinking.jsonl`
- 程序SHA256：`a4c2c42b96ad9891680874916d9bfd89172ffccb429e28d6ac5a488529ccc69b`
- 规则原文：

> "Contract Period" shall mean that period of time from February 21, 2011 through December 31, 2012.

- 自动概括：The Contract Period is the interval from February 21, 2011 through December 31, 2012, inclusive. A scenario is in the definition only if its start date is exactly 2011-02-21 and its end date is exactly 2012-12-31.
- 模型指出的问题：无

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1：The period of time is from February 21, 2011 through December 31, 2012.
  - 按完整合同，它属于`Contract Period`吗？`是/否/无法唯一判断`：
- 例2：The contract period starts on February 21, 2011 and concludes on December 31, 2012.
  - 按完整合同，它属于`Contract Period`吗？`是/否/无法唯一判断`：
- 例3：The contract period runs from February 20, 2011 through January 1, 2013.
  - 按完整合同，它属于`Contract Period`吗？`是/否/无法唯一判断`：
- 例4：The contract period runs from February 22, 2011 through December 31, 2012.
  - 按完整合同，它属于`Contract Period`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:296:STASCO

- 合同编号：`296`；[完整合同](contracts/ci296.txt)
- 来源组：`source_sample_candidate`；自动审查：`accept`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/rule_program_proposals.jsonl`
- 程序SHA256：`7d7fc2fbd09350a973411dba95b7367dd1fc6937e34f4666d43a77c668f9dfda`
- 规则原文：

> "STASCO" means Shell Trading International Limited acting through its agent Shell International Trading and Shipping Company Limited.

- 自动概括：A party is STASCO only when it is Shell Trading International Limited acting through its agent, where the role is agent and the agent is Shell International Trading and Shipping Company Limited.
- 模型指出的问题：无

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1：In the bill of lading, the principal is Shell Trading International Limited, the intermediary is acting as agent, and the agent is Shell International Trading and Shipping Company Limited.
  - 按完整合同，它属于`STASCO`吗？`是/否/无法唯一判断`：
- 例2：A notice is given by Shell Trading International Limited acting through its agent Shell International Trading and Shipping Company Limited, and the stated role is agent.
  - 按完整合同，它属于`STASCO`吗？`是/否/无法唯一判断`：
- 例3：Shell Trading International Limited is the principal and acts through its agent Shell International Shipping Company Limited, whose role is agent.
  - 按完整合同，它属于`STASCO`吗？`是/否/无法唯一判断`：
- 例4：Shell Trading International plc is the principal and acts through its agent Shell International Trading and Shipping Company Limited, whose role is agent.
  - 按完整合同，它属于`STASCO`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:348:Entity

- 合同编号：`348`；[完整合同](contracts/ci348.txt)
- 来源组：`source_sample_candidate`；自动审查：`accept`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/rule_program_proposals.jsonl`
- 程序SHA256：`0bcb5bb7541f1ed4a62daa8f2a8dc32aa5aaa07555a8a97e34cf5aab35f738d9`
- 规则原文：

> "Entity" means an individual or a corporation, partnership, sole proprietorship, limited liability company, joint venture, or other form of organization, and includes the parties hereto.

- 自动概括：An Entity is any individual, corporation, partnership, sole proprietorship, limited liability company, joint venture, or other form of organization; it also includes any party to this Agreement.
- 模型指出的问题：无

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1：Alice, a natural person, is a party to this Agreement.
  - 按完整合同，它属于`Entity`吗？`是/否/无法唯一判断`：
- 例2：Delta Joint Venture, a joint venture, is not a party to this Agreement.
  - 按完整合同，它属于`Entity`吗？`是/否/无法唯一判断`：
- 例3：A weather pattern is not a party to this Agreement.
  - 按完整合同，它属于`Entity`吗？`是/否/无法唯一判断`：
- 例4：A standalone software program is not a party to this Agreement.
  - 按完整合同，它属于`Entity`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:152:Territory

- 合同编号：`152`；[完整合同](contracts/ci152.txt)
- 来源组：`source_sample_candidate`；自动审查：`accept`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/rule_program_proposals.jsonl`
- 程序SHA256：`e42c79e56addaeade908597cd6b4a39d40f341355ebd73ee67a741098c4f2161`
- 规则原文：

> 1.37 "Territory" shall mean the fifty states of the United States of America, the District of Columbia, the Commonwealth of Puerto Rico, Guam, American Samoa, the U.S. Virgin Islands and all territories and possessions of the United States of America and United States military bases.

- 自动概括：Territory includes the fifty U.S. states, the District of Columbia, Puerto Rico, Guam, American Samoa, the U.S. Virgin Islands, any U.S. territory or possession, and any U.S. military base.
- 模型指出的问题：无

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1：The location is the Commonwealth of Puerto Rico.
  - 按完整合同，它属于`Territory`吗？`是/否/无法唯一判断`：
- 例2：The location is American Samoa.
  - 按完整合同，它属于`Territory`吗？`是/否/无法唯一判断`：
- 例3：The location is a United States federal courthouse building located in Canada.
  - 按完整合同，它属于`Territory`吗？`是/否/无法唯一判断`：
- 例4：The location is French Polynesia, a territory of France.
  - 按完整合同，它属于`Territory`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:34:Platform Rules

- 合同编号：`34`；[完整合同](contracts/ci34.txt)
- 来源组：`source_sample_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/rule_program_proposals.jsonl`
- 程序SHA256：`f6e7ef6ee3e817cd67a03ce6a459fb1c7ebd83a9bce02eea9f2ecdbd098f2589`
- 规则原文：

> 1.2 "Platform Rules" refers to normative documents related to the platform noticed to Party B by Party A by E-mail or other means as well as the various normative documents published on the platform such as the Regulations on Vehicle Rental Service Business of Xiaoju Online Ride-hailing Marketplace and Code of Conduct and Risk Notification of Vehicle Service Company.

- 自动概括：A document is a Platform Rule iff it is a normative document AND it is related to the platform AND (it was noticed to Party B by Party A by E-mail or other means OR it was published on the platform).
- 模型指出的问题：The source defines two coordinated categories: (1) normative documents related to the platform and noticed to Party B by Party A by E-mail or other means, and (2) various normative documents published on the platform. The proposed predicate incorrectly requires platform-relatedness for the publication category as well.；Accordingly, a normative document that is not stated to be related to the platform but is published on the platform is excluded by the proposed predicate, although it falls within the separately stated published-documents category.；The referenced Definition of Platform (1.1) is not supplied. That external definition is required to operationalize the terms 'platform,' 'related to the platform,' and 'published on the platform' with contractual precision.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1：Document D17 is a normative document. It is related to the platform. It was noticed by Party A to Party B by other means. It was not published on the platform.
  - 按完整合同，它属于`Platform Rules`吗？`是/否/无法唯一判断`：
- 例2：Document D2 is a normative document. It is related to the platform. It was noticed by Party A to Party B by E-mail. It was not published on the platform.
  - 按完整合同，它属于`Platform Rules`吗？`是/否/无法唯一判断`：
- 例3：Document D16 is not a normative document. It is not related to the platform. It was not noticed by Party A to Party B by E-mail or other means. It was not published on the platform.
  - 按完整合同，它属于`Platform Rules`吗？`是/否/无法唯一判断`：
- 例4：Document D6 is a normative document. It is not related to the platform. It was noticed by Party A to Party B by other means. It was not published on the platform.
  - 按完整合同，它属于`Platform Rules`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:462:Content

- 合同编号：`462`；[完整合同](contracts/ci462.txt)
- 来源组：`source_sample_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/rule_program_proposals.jsonl`
- 程序SHA256：`e81a5be26e7487f94e6fc73c4c657a671eb5c4bf12f9b10f13da251023315eaa`
- 规则原文：

> For purposes herein, "Content" shall mean, with respect to each party, the proprietary content delivered by such party to the other party pursuant to this Agreement, including, Sponsor Advertising Content, but only to the extent that such content is not altered by the receiving party, and the proprietary content contained on such party's Site, and shall include only that content created by such party, its employees or other persons contractually bound to such party to create such content.

- 自动概括：Content means, with respect to a party, proprietary content that is created by that party, its employees, or contractually bound persons, and that is either (a) delivered by that party to the other party under the Agreement and not altered by the receiving party, or (b) contained on that party's Site. Sponsor Advertising Content is included within the delivered proprietary content category.
- 模型指出的问题：The predicate does not represent the express inclusion of the defined term "Sponsor Advertising Content." Treating it merely as an example of already-proprietary delivered content is a plausible gloss, but the source does not state that Sponsor Advertising Content is necessarily proprietary or otherwise collapsible into the proprietary_content field.；The definition or operative facts for the capitalized dependency "Sponsor Advertising Content" are absent. Without that attachment, it cannot be determined whether it creates an independent included category or how it relates to the proprietary-content requirement.；All supplied case narratives explicitly support their coded Boolean facts, but none tests the stated Sponsor Advertising Content inclusion.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1：Party A delivered proprietary content to Party B pursuant to the Agreement; Party B did not alter it; the content was created by Party A's employee; it is not on Party A's Site.
  - 按完整合同，它属于`Content`吗？`是/否/无法唯一判断`：
- 例2：Proprietary content is contained on Party A's Site; it was created by a person contractually bound to Party A to create such content; Party A did not deliver it to Party B; Party B did not alter it.
  - 按完整合同，它属于`Content`吗？`是/否/无法唯一判断`：
- 例3：Proprietary content was delivered by Party A to Party B pursuant to the Agreement; Party B altered it; it was created by Party A's employee; it is not on Party A's Site.
  - 按完整合同，它属于`Content`吗？`是/否/无法唯一判断`：
- 例4：Content is contained on Party A's Site; it is not proprietary and was not created by Party A, its employees, or any person contractually bound to Party A; Party A did not deliver it to Party B; Party B did not alter it.
  - 按完整合同，它属于`Content`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:284:Contract Year

- 合同编号：`284`；[完整合同](contracts/ci284.txt)
- 来源组：`source_sample_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/rule_program_proposals.jsonl`
- 程序SHA256：`64d815ea8a4b3fc211649440a55dedf0ccf795f688c1d19b0fe9a643ef9b2a34`
- 规则原文：

> (b) "Contract Year" shall mean the consecutive 12-month period beginning on any January 1st during the Contract Period.

- 自动概括：A period is a Contract Year if and only if it is a consecutive 12-month period that begins on January 1 and that January 1 start date falls during the Contract Period.
- 模型指出的问题：The quoted source defines Contract Year by reference to the separately defined Contract Period, but the actual Contract Period definition is not supplied as source text. The dependency description is an unverified assertion rather than the underlying contract language.；The dated Contract Period boundaries and early-termination condition used in the case narratives cannot be independently verified without the referenced definition, although each case explicitly states its coded starts_during_contract_period fact.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1：A period begins on January 1, 2000, runs for 12 consecutive months, and the January 1 start date is during the Contract Period.
  - 按完整合同，它属于`Contract Year`吗？`是/否/无法唯一判断`：
- 例2：A period begins on January 1, 2002, runs for 12 consecutive months, and the January 1 start date is during the Contract Period.
  - 按完整合同，它属于`Contract Year`吗？`是/否/无法唯一判断`：
- 例3：A period begins on January 1, 2001, spans 12 months but is not consecutive because it has a gap, and the start date is during the Contract Period.
  - 按完整合同，它属于`Contract Year`吗？`是/否/无法唯一判断`：
- 例4：A period begins on January 1, 2002, has a 12-month total span but is not consecutive because of an interruption, and the start date is during the Contract Period.
  - 按完整合同，它属于`Contract Year`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:396:Confidential Information

- 合同编号：`396`；[完整合同](contracts/ci396.txt)
- 来源组：`source_sample_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/rule_program_proposals.jsonl`
- 程序SHA256：`764448febe1d7121d351a08bddc040f33bfa84708d0f859dc987a87f76b679f7`
- 规则原文：

> 1.9 "Confidential Information" means any and all trade secrets, proprietary or confidential information of either party and includes, without limitation: (a) any information, software, material, data or business, financial, operational, customer, vendor, and other information disclosed by one party to the other, (b) the terms of this Agreement, and/or (c) the fact of the existence of this Agreement except as specifically permitted in Section 7. Confidential Information will not include information that the receiving party can prove: (w) was already in such party's possession prior to receipt; (x) was independently developed by such party; (y) was obtained from a third party who had the right to disclose such information to such party, and/or (z) was or became generally available to the public other than as a result of disclosure by such party.

- 自动概括：Confidential Information includes trade secrets, proprietary or confidential information of either party, information disclosed by one party to the other, the terms of the Agreement, and the fact of the Agreement's existence unless Section 7 permits that existence disclosure; it excludes information the receiving party can prove was already in its possession prior to receipt, was independently developed, was obtained from a third party with the right to disclose it, or was or became generally available to the public other than by the party's disclosure.
- 模型指出的问题：The public-availability exclusion is not modeled exactly. The source requires that the information be generally available other than as a result of disclosure by 'such party'—the receiving party. The proposed field and predicate instead use generic 'party disclosure,' losing the identity of the receiving party and potentially changing the exclusion's result.；The Section 7 attachment is absent. The definition expressly conditions treatment of the Agreement-existence fact on what is specifically permitted in Section 7, so the asserted Section 7 facts and the exact operation of that exception cannot be audited from the supplied source quote alone.；Case out_public_availability does not expressly establish the source-required receiving-party-specific qualification. It says availability was other than through disclosure 'by a party,' and Pi is not expressly identified as the receiving party or as the relevant party whose disclosure is excluded.；Several public-availability case narratives similarly refer to disclosure by the disclosing party or by an unspecified party rather than specifically by the receiving party. This may not affect their coded false values in every case, but it does not support an exact implementation of source item (z).

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1：Gamma and Delta are parties to this Agreement; the payment schedule is a term of this Agreement. It is not a trade secret, proprietary, or confidential information of either party. It was not disclosed by one party to the other. It is not the fact of the Agreement's existence. Section 7 does not permit existence disclosure. Receiving party cannot prove prior possession, independent development, third-party right to disclose, or public availability other than by a party's disclosure.
  - 按完整合同，它属于`Confidential Information`吗？`是/否/无法唯一判断`：
- 例2：Beta received a customer list from Alpha; Alpha disclosed the customer list to Beta. It is not a trade secret, proprietary, or confidential information of either party. It is not a term of this Agreement. It is not the fact of the Agreement's existence. Section 7 does not permit existence disclosure. Beta cannot prove prior possession, independent development, third-party right to disclose, or public availability other than by Alpha's disclosure.
  - 按完整合同，它属于`Confidential Information`吗？`是/否/无法唯一判断`：
- 例3：Pi knows the fact of the existence of this Agreement; Section 7 does not permit existence disclosure. Pi can prove the fact became generally available to the public other than as a result of disclosure by a party. It is not a trade secret, proprietary, or confidential information of either party. It was not disclosed by one party to the other. It is not a term of this Agreement. Pi cannot prove prior possession, independent development, or third-party right to disclose.
  - 按完整合同，它属于`Confidential Information`吗？`是/否/无法唯一判断`：
- 例4：Lambda disclosed a trade secret to Mu; the information is a trade secret of Lambda. Mu can prove that it already possessed the information prior to receipt. It was not independently developed. It was not obtained from a third party with a right to disclose. It did not become generally available to the public other than by Lambda's disclosure. It is not a term of this Agreement. It is not the fact of the Agreement's existence. Section 7 does not permit existence disclosure.
  - 按完整合同，它属于`Confidential Information`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:253:Allscripts Customer

- 合同编号：`253`；[完整合同](contracts/ci253.txt)
- 来源组：`source_sample_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/rule_program_proposals_nonthinking.jsonl`
- 程序SHA256：`86d3179a97f9f85ef73e3bd0c30dfa14e4f6420cb5f47d3e13824ca9f8738b32`
- 规则原文：

> "Allscripts Customer" means a customer that has contracted for or receiving any of Allscripts' products or services.

- 自动概括：An entity is an Allscripts Customer if and only if it is a customer and either has contracted for any Allscripts products or services or is receiving any Allscripts products or services.
- 模型指出的问题：The predicate faithfully expresses the definition: an Allscripts Customer must be a customer and must either have contracted for or be receiving any Allscripts products or services.；Cases c01 and c06 code is_receiving_allscripts_products_or_services=false, but their text only affirmatively states contracting and does not explicitly state that the entity is not receiving products or services.；Cases c02 and c07 code has_contracted_for_allscripts_products_or_services=false, but their text only affirmatively states receipt and does not explicitly state that the entity has not contracted for products or services.；The source quote itself is sufficient to define the Boolean condition; no external attachment or redacted condition is required.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1：Lambda NV is a customer that has not contracted for Allscripts products or services but is receiving Allscripts services.
  - 按完整合同，它属于`Allscripts Customer`吗？`是/否/无法唯一判断`：
- 例2：Delta Co is a customer that has contracted for Allscripts products and is receiving Allscripts services.
  - 按完整合同，它属于`Allscripts Customer`吗？`是/否/无法唯一判断`：
- 例3：Epsilon Ltd is a customer that has not contracted for Allscripts products or services and is not receiving Allscripts products or services.
  - 按完整合同，它属于`Allscripts Customer`吗？`是/否/无法唯一判断`：
- 例4：Eta SA is a non-customer that is receiving Allscripts services.
  - 按完整合同，它属于`Allscripts Customer`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:465:Event

- 合同编号：`465`；[完整合同](contracts/ci465.txt)
- 来源组：`source_sample_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/rule_program_proposals.jsonl`
- 程序SHA256：`3f0c4b1bac1c1b17bc4876cc85eabdb25a2ae89a6fcf241db7cb2a55a2f2334b`
- 规则原文：

> In this Agreement, "Event" means the FLOODfest Event at the Virgin Hotel Chicago. The Event is scheduled for Thursday July 30, 2015 thru Saturday, August 1st, 2015 (the "Event Date(s)").

- 自动概括：The Event is the FLOODfest Event at the Virgin Hotel Chicago scheduled from July 30, 2015 through August 1, 2015. A candidate qualifies only if event_name is FLOODfest, venue_name is Virgin Hotel Chicago, start_date is 2015-07-30, and end_date is 2015-08-01.
- 模型指出的问题：The source defines the term as the specific "FLOODfest Event," whereas the predicate substitutes an unqualified event_name of "FLOODfest." The source does not expressly establish that every event or festival called FLOODfest is necessarily the defined "FLOODfest Event."；Cases in_exact_2 and in_exact_3 state only that an event/festival is called FLOODfest; they do not explicitly state that it is the defined "FLOODfest Event." Nevertheless, the proposed predicate accepts them.；The event-name coding also omits the source's "Event" component, so the rule should represent the defined event identity directly (for example, "FLOODfest Event") or provide an explicit source-supported normalization establishing FLOODfest as the exact defined-event identifier.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1：Candidate event is the FLOODfest Event at the Virgin Hotel Chicago, scheduled from 2015-07-30 to 2015-08-01.
  - 按完整合同，它属于`Event`吗？`是/否/无法唯一判断`：
- 例2：The event is FLOODfest, occurs at Virgin Hotel Chicago, and its scheduled dates are July 30, 2015 through August 1, 2015.
  - 按完整合同，它属于`Event`吗？`是/否/无法唯一判断`：
- 例3：FLOODfest is at the Virgin Hotel Chicago, scheduled from 2015-07-29 to 2015-08-01.
  - 按完整合同，它属于`Event`吗？`是/否/无法唯一判断`：
- 例4：Lollapalooza is at the Virgin Hotel Chicago, scheduled from 2015-07-30 to 2015-08-01.
  - 按完整合同，它属于`Event`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:249:Licensed Users

- 合同编号：`249`；[完整合同](contracts/ci249.txt)
- 来源组：`source_sample_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/rule_program_proposals.jsonl`
- 程序SHA256：`7ab6e24c08132105ae2714f39e43981b468d5f5747713e392a4097b0402ccd79`
- 规则原文：

> 1.8 "Licensed User" and "Licensed Users" means Licensee and Licensee's subsidiaries.

- 自动概括：An entity is a Licensed User if it is the Licensee or a subsidiary of the Licensee.
- 模型指出的问题：The quoted definition supports the predicate exactly: a Licensed User is the Licensee or any subsidiary of the Licensee, with no stated exclusions or additional conditions.；All case texts explicitly state the two coded facts, and the fact vectors match those statements.；The stated source dependency identifying HERTZ GROUP REALTY TRUST, INC. as the contractual Licensee refers to the contract header, but that header is not provided in the source material. Therefore the named-party assertion in the licensee_itself case cannot be independently verified from the supplied source.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1：Alpha Subsidiary LLC is a wholly owned subsidiary of the Licensee and is not the Licensee.
  - 按完整合同，它属于`Licensed Users`吗？`是/否/无法唯一判断`：
- 例2：Delta Subsidiary LLC is a majority-owned subsidiary of the Licensee and is not the Licensee.
  - 按完整合同，它属于`Licensed Users`吗？`是/否/无法唯一判断`：
- 例3：Successor Corp is an assignee of the Licensee's contract rights, is not the Licensee, and is not a subsidiary of the Licensee.
  - 按完整合同，它属于`Licensed Users`吗？`是/否/无法唯一判断`：
- 例4：Customer Co. purchases services from the Licensee but is not the Licensee and is not a subsidiary of the Licensee.
  - 按完整合同，它属于`Licensed Users`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:389:Affiliates

- 合同编号：`389`；[完整合同](contracts/ci389.txt)
- 来源组：`source_sample_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/rule_program_proposals.jsonl`
- 程序SHA256：`ae1ba557e824f1adfefe22902e6d484ef6d6b2d695b81a5dfe11fa8cd56294a2`
- 规则原文：

> "Affiliates" means any individual, company, partnership or other entity which directly or indirectly, at present or in the future, controls, is controlled by or is under common control of a Party, and "control" will mean direct or indirect beneficial ownership of at least fifty per cent (50%) of the voting share capital in such company or other business entity, or to hold the effective power to appoint or dismiss members of the management.

- 自动概括：An entity is an Affiliate of a Party if the entity is an individual, company, partnership or other entity and either (1) the Party directly or indirectly beneficially owns at least 50% of the entity's voting share capital, (2) the Party holds effective power to appoint or dismiss the entity's management, (3) the entity directly or indirectly beneficially owns at least 50% of the Party's voting share capital, (4) the entity holds effective power to appoint or dismiss the Party's management, or (5) the entity is under common control of the Party.
- 模型指出的问题：The predicate faithfully implements the stated disjunction: an enumerated entity type is an Affiliate when it controls the Party, is controlled by the Party, or is under common control, with control defined by at least 50% direct or indirect beneficial voting ownership or effective management appointment/dismissal power.；Several ownership facts use 'owns' rather than the source's required 'beneficial ownership.' Direct ownership is not an exact explicit statement of beneficial ownership under a conservative audit: in_party_voting_50 and in_entity_voting_60 therefore do not expressly support their true voting-control codes.；The 49% and 49.9% negative ownership cases do not expressly negate all possible direct and indirect beneficial ownership at or above 50%. Stating one direct or indirect holding below 50% does not exclude additional holdings or another ownership route: out_party_owns_49, out_entity_owns_49, and out_boundary_49_9.；out_common_control_third_party denies only direct voting and management control between Party A and Entity L. The source includes indirect control, which is not expressly negated.；out_management_control_different_entity expressly denies Party A's management power over Entity M and Entity M's ownership/control of Party A, but does not deny Party A's direct or indirect beneficial voting ownership of Entity M. Its false party_voting_control code is unsupported.；No external attachment, incorporated definition, score, or redacted fact is necessary to interpret the quoted Affiliate definition.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1：Entity E, an other entity, holds effective power to appoint or dismiss management of Party A. No voting ownership, no party control, no common control.
  - 按完整合同，它属于`Affiliates`吗？`是/否/无法唯一判断`：
- 例2：Party A directly owns 50% of the voting share capital of Entity B, a company. Party A has no management appointment power, Entity B controls neither Party A nor common control.
  - 按完整合同，它属于`Affiliates`吗？`是/否/无法唯一判断`：
- 例3：Entity K, an individual, directly owns 49% of voting share capital of Party A. Entity K has no management appointment power over Party A. No party control, no common control.
  - 按完整合同，它属于`Affiliates`吗？`是/否/无法唯一判断`：
- 例4：Party A has effective power to appoint management of Entity N, but no such power over Entity M, a partnership. Entity M has no voting ownership in Party A, no management control over Party A, and is not under common control of Party A.
  - 按完整合同，它属于`Affiliates`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:303:Confidential Information

- 合同编号：`303`；[完整合同](contracts/ci303.txt)
- 来源组：`source_sample_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/rule_program_proposals_nonthinking.jsonl`
- 程序SHA256：`e3f17f8f80c704fa0b15dcd803894c436c45a4a47d84f7d675b0917d36db5028`
- 规则原文：

> For purposes of this Agreement, "Confidential Information" shall mean information in written or other tangible form specifically labeled as such when disclosed by a Party.

- 自动概括：Information qualifies as Confidential Information only if it is in written or other tangible form, specifically labeled as Confidential Information when disclosed, and disclosed by a Party.
- 模型指出的问题：The predicate faithfully captures the quoted definition as a conjunction: information, written or other tangible form, specifically labeled as Confidential Information, and disclosed by a Party.；Every case codes is_information=true, but none expressly states that the disclosed item is 'information.' Describing an item as a report, memo, statement, prototype, disk, or draft is not an express stipulation of that coded fact; in particular, a tangible prototype or disk need not itself be information without further facts.；The definition of the capitalized term 'Party' is identified as required but is not supplied. Therefore the source record is insufficient to determine Party status independently of the case assertions.；The stated dependencies also refer to definitions of Agreement and Service, but neither definition is provided; Service does not appear in the quoted rule, while the missing Party definition is material.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1：Party A disclosed a tangible prototype to Party B; the prototype was specifically labeled Confidential Information when disclosed.
  - 按完整合同，它属于`Confidential Information`吗？`是/否/无法唯一判断`：
- 例2：Party A disclosed a written memo to Party B; the memo was specifically labeled Confidential Information at the time of disclosure.
  - 按完整合同，它属于`Confidential Information`吗？`是/否/无法唯一判断`：
- 例3：Party A disclosed a written report to Party B; the report was specifically labeled Confidential Information, but the disclosure was not by a Party.
  - 按完整合同，它属于`Confidential Information`吗？`是/否/无法唯一判断`：
- 例4：Party A disclosed an oral statement to Party B; the statement was specifically labeled Confidential Information, but the disclosure was not by a Party.
  - 按完整合同，它属于`Confidential Information`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

