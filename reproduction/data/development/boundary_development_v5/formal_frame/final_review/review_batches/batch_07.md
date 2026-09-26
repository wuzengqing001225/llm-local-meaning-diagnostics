# 正式来源规则复核 第7批

> **暂停填写：**旧生成器把定义判据写进事实句。这批材料仅作失败审计，不进入正式实验。

此包按来源文本生成，没有读新A分数或B读者结果。模型意见是预筛，不是金标准。
你只需核原文引文、自动规则概括和4个固定事实；这4个事实正是后续A题候选。程序字段和布尔表达式由我核。
**不要**根据你预计哪个模型会答错来决定收录。自动审查为`revise`的条目可以填`待改`，写明哪一条件不对，无需你改JSON。

## cuadfull:76:Purchase Order

- 合同编号：`76`；[完整合同](contracts/ci76.txt)
- 来源组：`challenge_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/rule_program_proposals.jsonl`
- 程序SHA256：`15eb8a63c02e34012139f34a9e10c98bd279479a74575962a2e54b53fdb95463`
- 规则原文：

> "Purchase Order" means a written order submitted by EMV to purchase a specific quantity of a Product or Products in accordance with this Agreement. Each Purchase Order shall include the quantity and type of Products to be manufactured and purchased; the unit price; the Product revision level; scheduled delivery dates; and "sold to," "invoice to," and "ship to" address.

- 自动概括：A Purchase Order is a written order submitted by EMV in accordance with this Agreement that includes quantity, Product type, unit price, Product revision level, scheduled delivery dates, and sold-to, invoice-to, and ship-to addresses. All listed attributes must be true.
- 模型指出的问题：The predicate omits the definition’s independent requirement that the written order be to purchase a specific quantity of a Product or Products. `includes_quantity` implements the separate mandatory-content clause ('shall include the quantity') and is not an exact substitute for an order being to purchase a specific quantity.；The predicate has no field or condition for the order being to purchase a Product or Products. The existing product-type field only covers a required item of PO content, not the definitional purchase-object requirement.；The cases do not test the omitted definitional elements independently; every case presupposes a purchase of a specific quantity of a Product (or Products).

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`po_in_hardware_revision`）：A written order was submitted by EMV to purchase a specific quantity of a hardware Product in accordance with this Agreement; it includes the quantity, the product type, the unit price, the revision level, scheduled delivery dates, a sold-to address, an invoice-to address, and a ship-to address.
  - 按完整合同，它属于`Purchase Order`吗？`是/否/无法唯一判断`：
- 例2（`po_in_software_product`）：A written order was submitted by EMV to purchase a specific quantity of a software Product in accordance with this Agreement; it includes the quantity, the product type, the unit price, the product revision level, scheduled delivery dates, a sold-to address, an invoice-to address, and a ship-to address.
  - 按完整合同，它属于`Purchase Order`吗？`是/否/无法唯一判断`：
- 例3（`po_out_missing_quantity`）：A written order was submitted by EMV to purchase a specific quantity of a Product in accordance with this Agreement; it includes the type of Product to be manufactured and purchased, the unit price, the Product revision level, scheduled delivery dates, a sold-to address, an invoice-to address, and a ship-to address, but it does not include the quantity.
  - 按完整合同，它属于`Purchase Order`吗？`是/否/无法唯一判断`：
- 例4（`po_out_missing_delivery_dates`）：A written order was submitted by EMV to purchase a specific quantity of a Product in accordance with this Agreement; it includes the quantity, the type of Product to be manufactured and purchased, the unit price, the Product revision level, a sold-to address, an invoice-to address, and a ship-to address, but it does not include scheduled delivery dates.
  - 按完整合同，它属于`Purchase Order`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:426:Prospectus

- 合同编号：`426`；[完整合同](contracts/ci426.txt)
- 来源组：`challenge_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/rule_program_proposals.jsonl`
- 程序SHA256：`7e18d66b05ddf0b7bdebe2bfa00be22f29725455ba98f97d96fa25fff161d1ac`
- 规则原文：

> except that if any Prospectus is filed by the Company pursuant to Rule 424(b) or (c) of the rules and regulations of the Commission under the 1933 Act (the "1933 Act Regulations") differing from the prospectus on file at the time the Registration Statement initially becomes effective, the term "Prospectus" shall refer to the prospectus filed pursuant to Rule 424(b) or (c) from and after the time said prospectus is filed with the Commission.

- 自动概括：A document is the Prospectus under the exception if it is filed by the Company under Rule 424(b) or (c), filed with the Commission, the Registration Statement has initially become effective, it differs from the prospectus on file at that initial effective time, and the reference time is at or after the document's filing time with the Commission.
- 模型指出的问题：The source says the replacement applies "from and after" the time the prospectus is filed with the Commission. This is a strictly post-filing condition and excludes the exact instant of filing. The predicate instead uses an inclusive "at_or_after_filing_time" field and treats the exact filing time as satisfying the exception.；Accordingly, the two exact-time cases are incorrectly admitted by the predicate and rule summary.；The predicate adds registration_statement_initially_effective as an independent Boolean requirement. The source uses the initial-effective-time prospectus as the comparison benchmark; it does not separately state that initial effectiveness is an additional conjunct apart from the stated differing-from-that-prospectus condition.；The cases asserting that the Registration Statement had not initially become effective while also asserting a difference from the prospectus on file at that initial-effective time are internally problematic, because the identified comparison-time prospectus is not coherently established under those stated facts.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`in_424c_after`）：A prospectus document was filed by the Company under Rule 424(c); it was filed with the Commission; the Registration Statement had initially become effective; the document differs from the prospectus on file at that initial effective time; and the current reference time is after the document was filed with the Commission.
  - 按完整合同，它属于`Prospectus`吗？`是/否/无法唯一判断`：
- 例2（`in_424c_exact_time`）：A prospectus document was filed by the Company under Rule 424(c); it was filed with the Commission; the Registration Statement had initially become effective; the document differs from the prospectus on file at that initial effective time; and the current reference time is exactly the time the document was filed with the Commission.
  - 按完整合同，它属于`Prospectus`吗？`是/否/无法唯一判断`：
- 例3（`out_not_commission`）：A prospectus document was filed by the Company under Rule 424(b); it was not filed with the Commission; the Registration Statement had initially become effective; the document differs from the prospectus on file at that initial effective time; and the current reference time is after the document was filed with the Commission.
  - 按完整合同，它属于`Prospectus`吗？`是/否/无法唯一判断`：
- 例4（`out_registration_not_effective`）：A prospectus document was filed by the Company under Rule 424(b); it was filed with the Commission; the Registration Statement had not initially become effective; the document differs from the prospectus on file at that initial effective time; and the current reference time is after the document was filed with the Commission.
  - 按完整合同，它属于`Prospectus`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:153:Reseller

- 合同编号：`153`；[完整合同](contracts/ci153.txt)
- 来源组：`challenge_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/rule_program_proposals.jsonl`
- 程序SHA256：`0207d7df4fdfadaed982d1ea0dd50ab19be76e669362cbab08a9c464a19cecf8`
- 规则原文：

> In the event Cisco enters into authorization agreements whereby Cisco authorizes particular resellers to purchase Products or Services from Distributor and to resell Products or Services to End User, then "Reseller" shall mean a reseller that is a party to such an authorization agreement.

- 自动概括：An entity is a Reseller only if it is a reseller, is a party to an authorization agreement, Cisco is the authorizing party, and the agreement authorizes purchase of Products or Services from Distributor and resale of Products or Services to End User.
- 模型指出的问题：The source requires that Cisco enter into the authorization agreements. The predicate instead tests only whether Cisco is the 'authorizing party.' Cisco's authorization of a party is not necessarily identical to Cisco entering into the agreement, so the predicate omits an express source condition.；case_05 codes both authorization fields as true for Elliot, but its text states only that the agreement authorizes unspecified 'particular resellers' and expressly says Elliot is not a party. It does not explicitly state that Elliot is among the resellers authorized to purchase from Distributor or resell to End User.；The rule summary's 'only if' phrasing is weaker than the definitional formulation 'shall mean,' which establishes the definition rather than merely a necessary condition.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`case_03`）：Casey is a reseller. Casey is a party to a Cisco authorization agreement. The agreement authorizes Casey to purchase Products or Services from Distributor and to resell Products or Services to End User.
  - 按完整合同，它属于`Reseller`吗？`是/否/无法唯一判断`：
- 例2（`case_01`）：Alex is a reseller. Alex is a party to an authorization agreement. The authorizing party to the agreement is Cisco. The agreement authorizes Alex to purchase Products from Distributor and to resell Products to End User.
  - 按完整合同，它属于`Reseller`吗？`是/否/无法唯一判断`：
- 例3（`case_07`）：Glen is a reseller. Glen is a party to a Cisco authorization agreement. The agreement does not authorize Glen to purchase Products or Services from Distributor. The agreement authorizes Glen to resell Products to End User.
  - 按完整合同，它属于`Reseller`吗？`是/否/无法唯一判断`：
- 例4（`case_13`）：Morgan is a reseller. Morgan is a party to an authorization agreement. The authorizing party is Distributor, not Cisco. The agreement authorizes Morgan to purchase Products from Distributor and to resell Products to End User.
  - 按完整合同，它属于`Reseller`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:265:Non-standard Products

- 合同编号：`265`；[完整合同](contracts/ci265.txt)
- 来源组：`challenge_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/rule_program_proposals_nonthinking.jsonl`
- 程序SHA256：`4d421cb366d182cf4abe8441f8aaeed677eea722c6354e2edc77c4e93b3a208b`
- 规则原文：

> 1.5 "Non-standard Products" shall mean those Products that are not standard mining rigs that require special testing, packaging or otherwise to be modified as requested by the Distributor and approved by JRVS in writing.

- 自动概括：A Product is a Non-standard Product if it is not a standard mining rig and either (a) requires special testing, (b) requires special packaging, or (c) is modified as requested by the Distributor with JRVS written approval.
- 模型指出的问题：The source does not expressly state that packaging must be 'special'; the proposed predicate adds a special-packaging qualifier to the bare term 'packaging.'；The unpunctuated source is syntactically ambiguous as to the scope of 'not standard mining rigs,' the testing/packaging/modification alternatives, and JRVS's written approval. The proposed grouping is a plausible reading but cannot be confirmed as the exact rule from this wording alone.；Cases c01 and c02 code jrvs_written_approval_of_modification=false, but their fact text does not expressly say that JRVS did not approve a modification in writing.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`c12`）：A Product is not a standard mining rig, requires special testing, does not require special packaging, is modified as requested by the Distributor, and JRVS has approved the modification in writing.
  - 按完整合同，它属于`Non-standard Products`吗？`是/否/无法唯一判断`：
- 例2（`c04`）：A Product is not a standard mining rig, requires special testing, requires special packaging, is modified as requested by the Distributor, and JRVS has approved the modification in writing.
  - 按完整合同，它属于`Non-standard Products`吗？`是/否/无法唯一判断`：
- 例3（`c15`）：A Product is a standard mining rig, does not require special testing, does not require special packaging, is modified as requested by the Distributor, and JRVS has approved the modification in writing.
  - 按完整合同，它属于`Non-standard Products`吗？`是/否/无法唯一判断`：
- 例4（`c05`）：A Product is a standard mining rig, requires special testing, requires special packaging, is modified as requested by the Distributor, and JRVS has approved the modification in writing.
  - 按完整合同，它属于`Non-standard Products`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:340:Documentation

- 合同编号：`340`；[完整合同](contracts/ci340.txt)
- 来源组：`challenge_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/rule_program_proposals.jsonl`
- 程序SHA256：`f808b30d1847e3f8541ea8b58ba8101bbea816aaa35c005829adcd4e60542f1b`
- 规则原文：

> 1.2 "Documentation" means all visually readable materials published or made available by Licensor during the term of this Agreement for use by Customers in connection with the Licensed Products.

- 自动概括：Documentation means all visually readable materials published or made available by Licensor during the Agreement term for use by Customers in connection with the Licensed Products.
- 模型指出的问题：The predicate exactly captures the four conjunctive requirements stated in Section 1.2; 'published or made available' is correctly represented by a single affirmative field.；The source is insufficient to fully operationalize the incorporated terms: the Customer definition in Section 1.1, Licensed Product definition in Section 1.4, and Exhibit A are absent. The Licensor identity and Agreement term are also not supplied.；Each case text expressly states the coded value for every predicate field; no case-specific fact vector is unsupported by its text.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`in_published`）：A printed manual is visually readable; it was published by Licensor during the Agreement term; it is for use by Customers; and it is in connection with Licensed Products.
  - 按完整合同，它属于`Documentation`吗？`是/否/无法唯一判断`：
- 例2（`in_training_handout`）：A training handout is visually readable; it was published by Licensor during the Agreement term; it is for use by Customers; and it is in connection with Licensed Products.
  - 按完整合同，它属于`Documentation`吗？`是/否/无法唯一判断`：
- 例3（`out_third_party_and_unrelated`）：A guide is visually readable; it was made available by a third party, not by Licensor during the Agreement term; it is for use by Customers; and it concerns unrelated services, not Licensed Products.
  - 按完整合同，它属于`Documentation`吗？`是/否/无法唯一判断`：
- 例4（`out_never_available_and_unrelated`）：A memo is visually readable; it was never published or made available by Licensor during the Agreement term; it is for use by Customers; and it concerns internal policies, not Licensed Products.
  - 按完整合同，它属于`Documentation`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:371:Calendar Year

- 合同编号：`371`；[完整合同](contracts/ci371.txt)
- 来源组：`challenge_topup2_candidate`；自动审查：`revise`
- 程序来源：`topup2_rule_program_proposals_nonthinking.jsonl`
- 程序SHA256：`26a26d73b4e152839b7634982bf7c8ab07e22b6fd6dd7265cd981f8d51bac81b`
- 规则原文：

> "Calendar Year" means, for the first calendar year, the period commencing on the Effective Date and ending on December 31 of the calendar year during which the Effective Date occurs, and each successive period beginning on January 1 and ending twelve (12) consecutive calendar months later on December 31.

- 自动概括：A period is a Calendar Year if either (a) it is the first calendar year, commences on the Effective Date, and ends on December 31 of the calendar year in which the Effective Date occurs, or (b) it is a successive period, begins on January 1, and ends twelve consecutive calendar months later on December 31.
- 模型指出的问题：The successive-period branch is not exact: it tests is_first_calendar_year=false rather than an affirmative fact that the period is a successive period. The source requires 'each successive period'; a period that is neither first nor successive is not made qualifying by the definition. Case c09 expressly demonstrates that is_first_calendar_year=false can mean neither first nor successive, so the field cannot serve as an exact substitute.；Several case vectors code negative facts that are not explicitly stated and do not necessarily follow from the case text. In particular, an Effective Date can be January 1, so commencement on the Effective Date does not necessarily mean the period does not begin on January 1, and a December 31 ending does not by itself establish or negate the twelve-consecutive-calendar-month condition.；c01 codes period_starts_on_jan_1=false and period_ends_twelve_months_later_on_dec_31=false without stating those negatives.；c02 codes period_starts_on_effective_date=false and period_ends_on_dec_31_of_effective_year=false without expressly stating them.；c05 codes period_starts_on_jan_1=false without stating it.；c06 codes period_ends_twelve_months_later_on_dec_31=false without stating it.；c07 codes period_starts_on_effective_date=false without stating it.；c08 codes period_starts_on_effective_date=false and period_ends_on_dec_31_of_effective_year=false without stating them.；c09 codes period_starts_on_jan_1=false and period_ends_twelve_months_later_on_dec_31=false without stating them; it also exposes the missing successive-period field.；The supplied quote is sufficient and no required external attachment or redacted source fact is apparent.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`c01`）：This is the first calendar year under the agreement; the period commences on the Effective Date and ends on December 31 of the calendar year in which the Effective Date occurs.
  - 按完整合同，它属于`Calendar Year`吗？`是/否/无法唯一判断`：
- 例2（`c04`）：This is a successive calendar year; the period begins on January 1 and ends twelve consecutive calendar months later on December 31, and it also commences on the Effective Date and ends on December 31 of the Effective Date's calendar year.
  - 按完整合同，它属于`Calendar Year`吗？`是/否/无法唯一判断`：
- 例3（`c09`）：This is neither the first calendar year nor a successive calendar year; the period commences on the Effective Date and ends on December 31 of the Effective Date's calendar year.
  - 按完整合同，它属于`Calendar Year`吗？`是/否/无法唯一判断`：
- 例4（`c05`）：This is the first calendar year; the period commences on the Effective Date but ends on June 30 of the following year rather than December 31 of the Effective Date's calendar year.
  - 按完整合同，它属于`Calendar Year`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:289:Training Materials

- 合同编号：`289`；[完整合同](contracts/ci289.txt)
- 来源组：`challenge_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/rule_program_proposals.jsonl`
- 程序SHA256：`d53e031f768ce1f063d08a38f17029084f9d5aeaa9734bbf12dbb1dce497c3cf`
- 规则原文：

> "Training Materials" means any and all materials, documentation, notebooks, forms, diagrams, manuals and other written materials and tangible objects, describing how to maintain the Facilities, including any corrections, improvements and enhancements thereto to the Bloom Systems which are delivered by Operator to Owner, but excluding any data and reports delivered to Owner.

- 自动概括：An item is a Training Material if it is one of the listed materials, documentation, notebooks, forms, diagrams, manuals, other written materials, or tangible objects; it describes how to maintain the Facilities; it is delivered by Operator to Owner; and it is not data or a report delivered to Owner.
- 模型指出的问题：The predicate incorrectly requires every Training Material to be delivered by Operator to Owner. Grammatically, the relative clause "which are delivered by Operator to Owner" modifies the immediately preceding "corrections, improvements and enhancements thereto to the Bloom Systems," not the entire preceding list of Training Materials.；The predicate omits the express included class of "corrections, improvements and enhancements thereto to the Bloom Systems". No field or fact vector captures whether an item is such a correction, improvement, or enhancement.；The closed item_form_category whitelist is not an exact implementation of "any and all materials" and can improperly exclude qualifying materials not fitting one of the selected categories. It also treats data as categorically excluded, although the source excludes only data and reports delivered to Owner.；out_not_delivered_08 is rejected solely because the notebook was not delivered by Operator to Owner, although the source does not impose that delivery requirement on ordinary listed Training Materials.；out_data_not_delivered_14 is rejected because it is categorized as data and was not delivered by Operator. The stated exclusion is limited to data delivered to Owner; the broad included term "materials" is not implemented faithfully by a categorical data exclusion.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`in_documentation_06`）：A documentation item describes how to maintain the Facilities and was delivered by Operator to Owner; it is not data or a report delivered to Owner.
  - 按完整合同，它属于`Training Materials`吗？`是/否/无法唯一判断`：
- 例2（`in_manual_01`）：A manual describes how to maintain the Facilities and was delivered by Operator to Owner; it is not data or a report delivered to Owner.
  - 按完整合同，它属于`Training Materials`吗？`是/否/无法唯一判断`：
- 例3（`out_not_describing_not_delivered_13`）：A form does not describe how to maintain the Facilities and was not delivered by Operator to Owner; it is not data or a report delivered to Owner.
  - 按完整合同，它属于`Training Materials`吗？`是/否/无法唯一判断`：
- 例4（`out_report_exclusion_10`）：A documentation item describes how to maintain the Facilities and was delivered by Operator to Owner, but it is a report delivered to Owner.
  - 按完整合同，它属于`Training Materials`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:444:Discloser

- 合同编号：`444`；[完整合同](contracts/ci444.txt)
- 来源组：`challenge_topup_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/topup_rule_program_proposals_nonthinking.jsonl`
- 程序SHA256：`d8b0c212b3757a6b290b91360e167ce4977722b636faf04121713fb538302ddf`
- 规则原文：

> "Discloser" shall mean the Party that is disclosing Confidential Information under this Agreement, regardless of whether such Confidential Information is being provided directly by such Party, by a Representative of the Party, or by any other person that has an obligation of confidentiality with respect to the Confidential Information being disclosed.

- 自动概括：A Party is a Discloser if it is disclosing Confidential Information under the Agreement, and the disclosure is made directly by the Party, by a Representative of the Party, or by another person who has an obligation of confidentiality with respect to the Confidential Information being disclosed.
- 模型指出的问题：The predicate faithfully reflects the quoted definition: Party status, disclosure of Confidential Information under the Agreement, and any of the stated provision routes, with a confidentiality obligation required for the 'any other person' route.；Case party_no_ci codes disclosure_directly_by_party=true even though its text states that Zeta is not disclosing Confidential Information; it does not expressly state a direct disclosure. Its disclosure_under_agreement=true is also not an affirmative fact, but part of the negated disclosure statement.；Case party_no_ci_other_obligated codes disclosure_by_other_person=true and disclosure_under_agreement=true despite text expressly stating that Mu is not disclosing Confidential Information under the Agreement. Further, the asserted obligation concerns 'some Confidential Information,' not necessarily Confidential Information being disclosed under the Agreement.；Several false values for route-specific or obligation-specific fields are implicit rather than expressly stated. This is less material where the fields are inapplicable, but the two identified cases contain affirmative coded facts that conflict with, or are not established by, their texts.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`rep_party`）：Beta is a Party to the Agreement. Beta is disclosing Confidential Information under the Agreement through a Representative of Beta.
  - 按完整合同，它属于`Discloser`吗？`是/否/无法唯一判断`：
- 例2（`rep_and_other_obligated`）：Kappa is a Party to the Agreement. Kappa is disclosing Confidential Information under the Agreement through a Representative of Kappa and also through another person who has an obligation of confidentiality with respect to that Confidential Information.
  - 按完整合同，它属于`Discloser`吗？`是/否/无法唯一判断`：
- 例3（`party_no_ci`）：Zeta is a Party to the Agreement. Zeta is not disclosing Confidential Information under the Agreement.
  - 按完整合同，它属于`Discloser`吗？`是/否/无法唯一判断`：
- 例4（`party_no_ci_other_obligated`）：Mu is a Party to the Agreement. Mu is not disclosing Confidential Information under the Agreement, but Mu is acting through another person who has an obligation of confidentiality with respect to some Confidential Information.
  - 按完整合同，它属于`Discloser`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:500:Confidential Information

- 合同编号：`500`；[完整合同](contracts/ci500.txt)
- 来源组：`challenge_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/rule_program_proposals.jsonl`
- 程序SHA256：`6b78e75929d8f3c36cffa659152efdd01430a070d8c8e9119ca28a1d3ff664f8`
- 规则原文：

> A. "Confidential Information" shall mean any confidential technical data, trade secret, know-how or other confidential information disclosed by any party hereunder in writing, orally, by drawing or otherwise. B. Notwithstanding the foregoing, Confidential Information shall not include information which: (i) is known to the receiving party at the time of disclosure or becomes known to the receiving party without breach of this Agreement; (ii) is or becomes publicly known through no wrongful act of the Source: MIDWEST ENERGY EMISSIONS CORP., 8-K, 6/4/2008 receiving party or any subsidiary of the receiving party; (iii) is rightfully received from a third partywithout restriction on disclosure; (iv) is independently developed by the receiving party or any of its subsidiaries; (v) is furnished to any third party by the disclosing party without restriction on its disclosure; (vi) is approved for release upon a prior written consent of the disclosing party; or, (vii) is disclosed pursuant to judicial order, requirement of a governmental agency or by operation of law.

- 自动概括：Information qualifies as Confidential Information if it is confidential technical data, trade secret, know-how, or other confidential information, and is disclosed by a party hereunder, unless any of exclusions (i)-(vii) applies.
- 模型指出的问题：The predicate correctly implements the definition’s two requirements (confidential-information type and disclosure by a party hereunder) and excludes information when any of exclusions (i)–(vii) applies.；Case c08 codes publicly_known_no_wrongful_act=true, but its text establishes only that public knowledge occurred through no wrongful act of the receiving party. The source condition also covers wrongful acts by any subsidiary of the receiving party; the case text does not state the subsidiary fact.；The supplied source does not include the referenced definitions for party, receiving party, disclosing party, subsidiary, hereunder, third party, judicial order, governmental agency, operation of law, or prior written consent. Those definitions may be required to apply the fields exactly in real cases.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`c02`）：Oral know-how was disclosed by a party hereunder; the receiving party did not know it at disclosure and did not later learn it without breach; it is not publicly known through no wrongful act; it was not rightfully received from a third party without restriction; it was not independently developed; it was not furnished to a third party by the disclosing party without restriction; it was not approved for release by prior written consent; and it was not disclosed under judicial order, governmental agency requirement, or operation of law.
  - 按完整合同，它属于`Confidential Information`吗？`是/否/无法唯一判断`：
- 例2（`c16`）：A drawing of confidential technical data was disclosed by a party hereunder; the receiving party did not know it at disclosure and did not later learn it without breach; it is not publicly known through no wrongful act; it was not rightfully received from a third party without restriction; it was not independently developed; it was not furnished to a third party by the disclosing party without restriction; it was not approved for release by prior written consent; and it was not disclosed under judicial order, governmental agency requirement, or operation of law.
  - 按完整合同，它属于`Confidential Information`吗？`是/否/无法唯一判断`：
- 例3（`c09`）：Know-how was disclosed by a party hereunder; the receiving party rightfully received the information from a third party without restriction on disclosure; the receiving party did not know it at disclosure and did not later learn it without breach; it is not publicly known through no wrongful act; it was not independently developed; it was not furnished to a third party by the disclosing party without restriction; it was not approved for release by prior written consent; and it was not disclosed under judicial order, governmental agency requirement, or operation of law.
  - 按完整合同，它属于`Confidential Information`吗？`是/否/无法唯一判断`：
- 例4（`c06`）：A trade secret exists but it was not disclosed by any party hereunder; the receiving party did not know it at disclosure and did not later learn it without breach; it is not publicly known through no wrongful act; it was not rightfully received from a third party without restriction; it was not independently developed; it was not furnished to a third party by the disclosing party without restriction; it was not approved for release by prior written consent; and it was not disclosed under judicial order, governmental agency requirement, or operation of law.
  - 按完整合同，它属于`Confidential Information`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:245:Applicable Law

- 合同编号：`245`；[完整合同](contracts/ci245.txt)
- 来源组：`challenge_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/rule_program_proposals.jsonl`
- 程序SHA256：`9576f0fa6382c5af50b36d5dd6b5fad99408b4683f0c57de3a1547b8697b8760`
- 规则原文：

> "Applicable Law" shall mean any law, statute, rule, regulation, order, judgment, ordinance, administrative code, decree, directive, injunction or permit (including Regulatory Approvals) of any court, arbitral body, agency, department, authority or other instrumentality of any national, state, county, city or other political subdivision applicable to a Party's activities to be performed under this Agreement. For the avoidance of doubt, any specific references to any Applicable Law or any portion thereof, shall be deemed to include all amendments, replacements or successors thereto.

- 自动概括：A thing is an Applicable Law if it is a listed instrument (law, statute, rule, regulation, order, judgment, ordinance, administrative code, decree, directive, injunction, permit, or regulatory approval) issued by a qualifying court, arbitral body, agency, department, authority, or other instrumentality of a qualifying national, state, county, city, or other political subdivision and is applicable to a Party's activities under the Agreement. Alternatively, it is an amendment, replacement, or successor of an Applicable Law and is applicable to a Party's activities under the Agreement.
- 模型指出的问题：The second sentence is a reference-incorporation rule: a specific reference to an Applicable Law (or portion) includes that referenced law's amendments, replacements, and successors. It does not create an independent alternative definition under which any amendment, replacement, or successor of an Applicable Law is itself an Applicable Law.；The predicate's second disjunct improperly classifies case_07 and case_08 as Applicable Laws despite the cases lacking the listed-instrument, qualifying-issuer, and qualifying-political-subdivision elements required by the definitional sentence.；The predicate also adds an independent applicability condition to the amendment/replacement/successor incorporation rule. The source's second sentence does not state that condition; rather, it operates on a particular referenced Applicable Law or portion thereof.；The program lacks facts for the necessary contextual relationship: that a specific contractual reference identifies a particular Applicable Law or portion and that the amendment, replacement, or successor is thereto. A boolean field saying an instrument is an amendment/replacement/successor of an Applicable Law is not an exact substitute for that reference-specific rule.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`case_05`）：A decree is issued by an arbitral body of another political subdivision and is applicable to a Party's activities to be performed under this Agreement; it is not an amendment, replacement, or successor of an Applicable Law.
  - 按完整合同，它属于`Applicable Law`吗？`是/否/无法唯一判断`：
- 例2（`case_15`）：A directive is issued by a city department and is applicable to a Party's activities to be performed under this Agreement; it is not an amendment, replacement, or successor of an Applicable Law.
  - 按完整合同，它属于`Applicable Law`吗？`是/否/无法唯一判断`：
- 例3（`case_09`）：A successor of an Applicable Law is not applicable to a Party's activities to be performed under this Agreement; the successor is not itself a listed instrument type and is not issued by a listed body or political subdivision.
  - 按完整合同，它属于`Applicable Law`吗？`是/否/无法唯一判断`：
- 例4（`case_11`）：A statute is issued by a private company rather than by a court, arbitral body, agency, department, authority, or other instrumentality; it is of a national political subdivision, is applicable to a Party's activities to be performed under this Agreement, and is not an amendment, replacement, or successor of an Applicable Law.
  - 按完整合同，它属于`Applicable Law`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:178:Person

- 合同编号：`178`；[完整合同](contracts/ci178.txt)
- 来源组：`challenge_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/rule_program_proposals.jsonl`
- 程序SHA256：`c30a19512ec2a89b653ed547d1af5df627c7addf0de5ac804c4eec673ca55704`
- 规则原文：

> "Person" means and includes (i) an individual, (ii) a legal entity, including a partnership, a joint venture, a corporation, a trust, a limited liability company, a limited duration company, or a limited liability partnership, (iii) companies or associations or bodies of persons, whether or not incorporated, and (iv) a Governmental Authority.

- 自动概括：A Person is any individual, legal entity, company, association, body of persons, or Governmental Authority.
- 模型指出的问题：The Person definition incorporates the capitalized term "Governmental Authority," but its underlying definition is not provided. That missing dependency prevents a complete source-level determination of when the governmental-authority limb applies outside cases that expressly stipulate the fact.；All supplied case narratives explicitly state each Boolean classification used in their fact vectors. The rule's disjunctive predicate tracks each enumerated Person category, including companies, associations, and bodies of persons whether or not incorporated.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`in_body_of_persons`）：Theta Council is a body of persons, whether or not incorporated; it is not an individual, legal entity, company, association, or governmental authority.
  - 按完整合同，它属于`Person`吗？`是/否/无法唯一判断`：
- 例2（`in_company_unincorporated`）：Zeta Group is an unincorporated company; it is not an individual, legal entity, association, body of persons, or governmental authority.
  - 按完整合同，它属于`Person`吗？`是/否/无法唯一判断`：
- 例3（`out_casual_group`）：Mu Volunteers is a casual group of friends that is not classified as an individual, legal entity, company, association, body of persons, or Governmental Authority.
  - 按完整合同，它属于`Person`吗？`是/否/无法唯一判断`：
- 例4（`out_animal`）：Luna is a dog; it is not an individual, legal entity, company, association, body of persons, or governmental authority.
  - 按完整合同，它属于`Person`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:172:KFDA

- 合同编号：`172`；[完整合同](contracts/ci172.txt)
- 来源组：`challenge_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/rule_program_proposals_nonthinking.jsonl`
- 程序SHA256：`c2c4e9d38b2a4cd39163888b22b1d219d1c7fafa8ce16c53686f5c92f10a2880`
- 规则原文：

> 1.59 "KFDA" means Korean Food and Drug Administration, or any successor agency thereto.

- 自动概括：An entity is KFDA if it is the Korean Food and Drug Administration or any successor agency thereto.
- 模型指出的问题：Case kfda_korea_fda codes is_korean_food_and_drug_administration=true, but its text identifies the entity as "Korea Food and Drug Administration," not the source-defined "Korean Food and Drug Administration," and does not expressly state that the two names refer to the same entity.；The source definition requires an external factual determination of successor-agency status; the program properly identifies this as a dependency, and the individual case texts expressly state their assumed successor-status facts.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`kfda_successor`）：The entity is the Ministry of Food and Drug Safety, which is a successor agency to the Korean Food and Drug Administration. It is not the Korean Food and Drug Administration itself.
  - 按完整合同，它属于`KFDA`吗？`是/否/无法唯一判断`：
- 例2（`kfda_mfds_successor`）：The entity is the Korea Ministry of Food and Drug Safety, which is a successor agency to the Korean Food and Drug Administration. It is not the Korean Food and Drug Administration itself.
  - 按完整合同，它属于`KFDA`吗？`是/否/无法唯一判断`：
- 例3（`kfda_fda`）：The entity is the FDA. It is not the Korean Food and Drug Administration and is not a successor agency to the Korean Food and Drug Administration.
  - 按完整合同，它属于`KFDA`吗？`是/否/无法唯一判断`：
- 例4（`kfda_neither`）：The entity is the United States Food and Drug Administration. It is not the Korean Food and Drug Administration and is not a successor agency to the Korean Food and Drug Administration.
  - 按完整合同，它属于`KFDA`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:190:Board

- 合同编号：`190`；[完整合同](contracts/ci190.txt)
- 来源组：`challenge_topup_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/topup_rule_program_proposals.jsonl`
- 程序SHA256：`034d4aa6f8a51e43058746f8bde2acc821512ec88087bd840670ce79db439d27`
- 规则原文：

> 1.6 "Board" means the board of directors of the Company.

- 自动概括：An entity is the Board only if it is both the board of directors and of the Company.
- 模型指出的问题：The quoted definition makes Board mean the board of directors of the Company, and the conjunction of being a board of directors and being of the Company faithfully reflects that definition.；The source window does not include the definition or identity of "Company." This is an external dependency needed to apply the term outside the stipulated case facts, although the cases expressly state the relevant Company relationship.；All case fact vectors are explicitly supported by their accompanying fact text for the two coded fields.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`in_board_directors_company`）：Entity Y is the board of directors of the Company and is not a committee or individual director.
  - 按完整合同，它属于`Board`吗？`是/否/无法唯一判断`：
- 例2（`in_company_board_phrase`）：The Company's board of directors is the entity being tested, and it is the board of directors of the Company.
  - 按完整合同，它属于`Board`吗？`是/否/无法唯一判断`：
- 例3（`out_board_of_company_subsidiary`）：Entity K is the board of directors of the Company's subsidiary, and K is not of the Company.
  - 按完整合同，它属于`Board`吗？`是/否/无法唯一判断`：
- 例4（`out_individual_director`）：Entity D is an individual director of the Company, not the board of directors.
  - 按完整合同，它属于`Board`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

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
- 例1（`c01`）：A registered copyright on a novel, and it is not a trademark.
  - 按完整合同，它属于`Copyrights`吗？`是/否/无法唯一判断`：
- 例2（`c13`）：An unregistered copyright application that is not a trademark.
  - 按完整合同，它属于`Copyrights`吗？`是/否/无法唯一判断`：
- 例3（`c06`）：A pending copyright application that is also a trademark.
  - 按完整合同，它属于`Copyrights`吗？`是/否/无法唯一判断`：
- 例4（`c10`）：An unregistered trade secret that is not a copyright, not a copyright application, and not a trademark.
  - 按完整合同，它属于`Copyrights`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:403:Boxlot Banners

- 合同编号：`403`；[完整合同](contracts/ci403.txt)
- 来源组：`challenge_topup2_candidate`；自动审查：`revise`
- 程序来源：`topup2_rule_program_proposals_nonthinking.jsonl`
- 程序SHA256：`d948853fa485c6e686a22b3402737eaf6164a316bd2688841643e2228fb2585e`
- 规则原文：

> (a) "Boxlot Banners" means any banner, button, text or similar ads Boxlot provides to theglobe in connection with this Agreement.

- 自动概括：An item is a Boxlot Banner if and only if it is a banner, button, text, or similar ad; Boxlot provides it; it is provided to theglobe; and it is provided in connection with this Agreement.
- 模型指出的问题：c08 is internally inconsistent: its text says Boxlot provides a banner, while also saying the item is a video; the coded item_type of other does not faithfully represent the stated banner fact.；c13 expressly states that the item is both a banner and a button, but the single-valued item_type field records only button, losing a stated relevant classification.；c14 is internally contradictory: it first states that Boxlot provides the banner, then states that it is not provided by Boxlot. The coded false value selects one side of the contradiction rather than representing a coherent fact pattern.；The predicate itself faithfully implements the quoted definition: a qualifying item must be a banner, button, text, or similar ad that Boxlot provides to theglobe in connection with the Agreement.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`c04`）：Boxlot provides a similar ad to theglobe in connection with this Agreement.
  - 按完整合同，它属于`Boxlot Banners`吗？`是/否/无法唯一判断`：
- 例2（`c13`）：Boxlot provides a banner to theglobe in connection with this Agreement, and the item is also a button.
  - 按完整合同，它属于`Boxlot Banners`吗？`是/否/无法唯一判断`：
- 例3（`c12`）：Boxlot provides a video to theglobe in connection with this Agreement.
  - 按完整合同，它属于`Boxlot Banners`吗？`是/否/无法唯一判断`：
- 例4（`c07`）：A banner is provided to theglobe in connection with this Agreement, but not by Boxlot.
  - 按完整合同，它属于`Boxlot Banners`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

