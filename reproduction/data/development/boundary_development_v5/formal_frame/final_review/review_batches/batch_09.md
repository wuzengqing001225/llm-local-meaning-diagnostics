# 正式来源规则复核 第9批

> **暂停填写：**旧生成器把定义判据写进事实句。这批材料仅作失败审计，不进入正式实验。

此包按来源文本生成，没有读新A分数或B读者结果。模型意见是预筛，不是金标准。
你只需核原文引文、自动规则概括和4个固定事实；这4个事实正是后续A题候选。程序字段和布尔表达式由我核。
**不要**根据你预计哪个模型会答错来决定收录。自动审查为`revise`的条目可以填`待改`，写明哪一条件不对，无需你改JSON。

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
- 例1（`in_trade_and_disclosed`）：Zeta disclosed proprietary financial data to Eta; the data is proprietary or confidential information of Zeta, and Zeta disclosed it to Eta. It is not a term of this Agreement. It is not the fact of the Agreement's existence. Section 7 does not permit existence disclosure. Eta cannot prove prior possession, independent development, third-party right to disclose, or public availability other than by Zeta's disclosure.
  - 按完整合同，它属于`Confidential Information`吗？`是/否/无法唯一判断`：
- 例2（`in_trade_secret`）：Alpha has a secret formula; the formula is a trade secret of Alpha. It was not disclosed by one party to the other. It is not a term of this Agreement. It is not the fact of the Agreement's existence. Section 7 does not permit existence disclosure. Beta cannot prove that it already possessed the formula prior to receipt, independently developed it, obtained it from a third party with a right to disclose, or that it became generally available to the public other than by Alpha's disclosure.
  - 按完整合同，它属于`Confidential Information`吗？`是/否/无法唯一判断`：
- 例3（`out_not_included`）：Rho knows a random fact. It was not disclosed by one party to the other. It is not a trade secret, proprietary, or confidential information of either party. It is not a term of this Agreement. It is not the fact of the Agreement's existence. Section 7 does not permit existence disclosure. Rho cannot prove prior possession, independent development, third-party right to disclose, or public availability other than by a party's disclosure.
  - 按完整合同，它属于`Confidential Information`吗？`是/否/无法唯一判断`：
- 例4（`out_s7_permits_fact`）：Kappa knows that this Agreement exists; this is the fact of the existence of this Agreement. Section 7 permits disclosure of the Agreement's existence. It is not a trade secret, proprietary, or confidential information of either party. It was not disclosed by one party to the other. It is not a term of this Agreement. Receiving party cannot prove prior possession, independent development, third-party right to disclose, or public availability other than by a party's disclosure.
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
- 例1（`c10`）：Kappa BV is a customer that has contracted for Allscripts products but is not receiving Allscripts products or services.
  - 按完整合同，它属于`Allscripts Customer`吗？`是/否/无法唯一判断`：
- 例2（`c14`）：Xi AS is a customer that has contracted for Allscripts products and is receiving Allscripts products.
  - 按完整合同，它属于`Allscripts Customer`吗？`是/否/无法唯一判断`：
- 例3（`c09`）：Iota AG is a non-customer that has not contracted for Allscripts products or services and is not receiving Allscripts products or services.
  - 按完整合同，它属于`Allscripts Customer`吗？`是/否/无法唯一判断`：
- 例4（`c15`）：Omicron DA is a non-customer that has contracted for Allscripts services and is receiving Allscripts services.
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
- 例1（`in_exact_2`）：The event is FLOODfest, occurs at Virgin Hotel Chicago, and its scheduled dates are July 30, 2015 through August 1, 2015.
  - 按完整合同，它属于`Event`吗？`是/否/无法唯一判断`：
- 例2（`in_exact_3`）：A festival named FLOODfest is held at the Virgin Hotel Chicago with a schedule spanning 2015-07-30 to 2015-08-01.
  - 按完整合同，它属于`Event`吗？`是/否/无法唯一判断`：
- 例3（`out_wrong_all_dates`）：FLOODfest is at the Virgin Hotel Chicago, scheduled from 2015-07-29 to 2015-08-02.
  - 按完整合同，它属于`Event`吗？`是/否/无法唯一判断`：
- 例4（`out_end_too_late`）：FLOODfest is at the Virgin Hotel Chicago, scheduled from 2015-07-30 to 2015-08-02.
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
- 例1（`both_licensee_and_subsidiary`）：Gamma Entity is the Licensee and is also a subsidiary of the Licensee.
  - 按完整合同，它属于`Licensed Users`吗？`是/否/无法唯一判断`：
- 例2（`wholly_owned_subsidiary`）：Alpha Subsidiary LLC is a wholly owned subsidiary of the Licensee and is not the Licensee.
  - 按完整合同，它属于`Licensed Users`吗？`是/否/无法唯一判断`：
- 例3（`employee_jane_doe`）：Jane Doe is an employee of the Licensee, is not the Licensee, and is not a subsidiary of the Licensee.
  - 按完整合同，它属于`Licensed Users`吗？`是/否/无法唯一判断`：
- 例4（`city_agency`）：City Agency is a government agency that regulates the Licensee, is not the Licensee, and is not a subsidiary of the Licensee.
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
- 例1（`in_party_mgmt_other`）：Party A has effective power to appoint or dismiss management of Entity H, an other entity. No voting ownership, no entity control, no common control.
  - 按完整合同，它属于`Affiliates`吗？`是/否/无法唯一判断`：
- 例2（`in_party_voting_50`）：Party A directly owns 50% of the voting share capital of Entity B, a company. Party A has no management appointment power, Entity B controls neither Party A nor common control.
  - 按完整合同，它属于`Affiliates`吗？`是/否/无法唯一判断`：
- 例3（`out_common_control_third_party`）：Entity L, a company, is under common control of Party Z, not Party A. No direct voting or management control between Entity L and Party A.
  - 按完整合同，它属于`Affiliates`吗？`是/否/无法唯一判断`：
- 例4（`out_boundary_49_9`）：Party A indirectly owns 49.9% of voting share capital of Entity P, a company. No management power, no entity control, no common control.
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
- 例1（`in_004`）：Party A disclosed a tangible disk to Party B; the disk was specifically labeled Confidential Information when disclosed.
  - 按完整合同，它属于`Confidential Information`吗？`是/否/无法唯一判断`：
- 例2（`in_001`）：Party A disclosed a written report to Party B; the report was specifically labeled Confidential Information at disclosure.
  - 按完整合同，它属于`Confidential Information`吗？`是/否/无法唯一判断`：
- 例3（`out_003`）：Party A disclosed a written report to Party B; the report was specifically labeled Confidential Information, but the disclosure was not by a Party.
  - 按完整合同，它属于`Confidential Information`吗？`是/否/无法唯一判断`：
- 例4（`out_008`）：Party A disclosed a tangible disk to Party B; the disk was not specifically labeled Confidential Information, and the disclosure was not by a Party.
  - 按完整合同，它属于`Confidential Information`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:359:Contract Year

- 合同编号：`359`；[完整合同](contracts/ci359.txt)
- 来源组：`source_sample_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/rule_program_proposals.jsonl`
- 程序SHA256：`9eb473de788f1606fe3011caa3d10dbce33034c990382db6fb38b36b02897dc6`
- 规则原文：

> "Contract Year" means for the first Contract Year of the Agreement, the period commencing on the Effective Date hereof and ending one year thereafter and for subsequent Contract Years, the successive twelve (12) month period thereafter.

- 自动概括：A period is a Contract Year if it either (i) commences on the Effective Date and ends one year thereafter, or (ii) starts immediately after a prior Contract Year and is a twelve-month period.
- 模型指出的问题：The subsequent-Contract-Year branch is not an exact transcription of the source. The source defines subsequent Contract Years as 'the successive twelve (12) month period thereafter'; it does not expressly require a period to 'start immediately after a prior Contract Year.'；The predicate introduces the distinct and stronger concepts of 'immediately' and a 'prior Contract Year.' Those may be a plausible interpretation of 'successive ... thereafter,' but they are not stated in the quoted definition and therefore should not be substituted in an exact-rule program.；The first-Contract-Year branch is faithfully represented by commencement on the Effective Date and ending one year thereafter. All case fact vectors are explicitly stated in their respective fact text.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`in_later_subsequent`）：A subsequent twelve-month period begins immediately after the preceding Contract Year; it does not commence on the Effective Date and does not end one year after the Effective Date.
  - 按完整合同，它属于`Contract Year`吗？`是/否/无法唯一判断`：
- 例2（`in_first_one_year_not_twelve`）：A period commences on the Effective Date and ends one year thereafter; it does not commence immediately after a prior Contract Year and is not a twelve-month period.
  - 按完整合同，它属于`Contract Year`吗？`是/否/无法唯一判断`：
- 例3（`out_missing_start_but_end`）：A period does not commence on the Effective Date but ends one year after the Effective Date; it does not begin immediately after a prior Contract Year and is a twelve-month period.
  - 按完整合同，它属于`Contract Year`吗？`是/否/无法唯一判断`：
- 例4（`out_end_effective_after_prior_not_twelve`）：A period does not commence on the Effective Date but ends one year after the Effective Date; it starts immediately after a prior Contract Year but is not a twelve-month period.
  - 按完整合同，它属于`Contract Year`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

