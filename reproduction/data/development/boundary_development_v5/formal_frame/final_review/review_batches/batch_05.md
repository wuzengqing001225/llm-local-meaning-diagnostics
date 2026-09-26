# 正式来源规则复核 第5批

> **暂停填写：**旧生成器把定义判据写进事实句。这批材料仅作失败审计，不进入正式实验。

此包按来源文本生成，没有读新A分数或B读者结果。模型意见是预筛，不是金标准。
你只需核原文引文、自动规则概括和4个固定事实；这4个事实正是后续A题候选。程序字段和布尔表达式由我核。
**不要**根据你预计哪个模型会答错来决定收录。自动审查为`revise`的条目可以填`待改`，写明哪一条件不对，无需你改JSON。

## cuadfull:478:Seizure

- 合同编号：`478`；[完整合同](contracts/ci478.txt)
- 来源组：`challenge_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/rule_program_proposals.jsonl`
- 程序SHA256：`1d30dfaab4b156c7b71c86864a430b0546db588403ee7ea21dc0359ba1f3800c`
- 规则原文：

> "Seizure" means any action by an Applicable Regulatory Authority in any jurisdiction, to detain or destroy any Product or any intermediate or finished products containing the Product or prevent release of the Product or finished products containing the Product. "Seized" and "Seizing" shall have comparable meanings;

- 自动概括：A Seizure is an action by an Applicable Regulatory Authority in any jurisdiction that is either (1) detention or destruction of the Product or an intermediate/finished product containing the Product, or (2) prevention of release of the Product or a finished product containing the Product.
- 模型指出的问题：The operative predicate and all coded case distinctions faithfully reflect the quoted Seizure definition, including the exclusion of prevention of release of an intermediate product containing the Product.；The quoted definition relies on the externally defined terms “Applicable Regulatory Authority” and “Product.” Those definitions are identified as dependencies but are not supplied, so the source is insufficient to verify the full contractual scope of those terms.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`in_destroy_product_za`）：An Applicable Regulatory Authority acting in South Africa destroys a Product.
  - 按完整合同，它属于`Seizure`吗？`是/否/无法唯一判断`：
- 例2（`in_prevent_release_product_jp`）：An Applicable Regulatory Authority acting in Japan prevents release of the Product.
  - 按完整合同，它属于`Seizure`吗？`是/否/无法唯一判断`：
- 例3（`out_actor_other_detain_us`）：A non-regulatory private party acting in the United States detains a Product.
  - 按完整合同，它属于`Seizure`吗？`是/否/无法唯一判断`：
- 例4（`out_action_other_inspect_es`）：An Applicable Regulatory Authority acting in Spain inspects a Product but does not detain, destroy, or prevent its release.
  - 按完整合同，它属于`Seizure`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:39:CytoDyn Patents

- 合同编号：`39`；[完整合同](contracts/ci39.txt)
- 来源组：`challenge_topup2_candidate`；自动审查：`revise`
- 程序来源：`topup2_rule_program_proposals_nonthinking.jsonl`
- 程序SHA256：`365c06376fcc541917067a942c8ba0f5679bd5e7bb067092d8afa5b5939134a4`
- 规则原文：

> "CytoDyn Patents" means any and all Patents Controlled by CytoDyn either or both as of the Effective Date or during the Term that claim any CytoDyn Know-How or Inventions. The CytoDyn Patents as of the Effective Date include those set forth on Attachment A. CytoDyn may update Attachment A from time to time to remove reference to expired Patents and to include reference to additional Patents.

- 自动概括：A Patent is a CytoDyn Patent if either (A) it is Controlled by CytoDyn as of the Effective Date or during the Term and claims any CytoDyn Know-How or Inventions, or (B) it is listed on Attachment A as of the Effective Date.
- 模型指出的问题：The operative definition requires all of: CytoDyn control, qualifying timing, and claims to CytoDyn Know-How or Inventions. The program treats listing on Attachment A as an unconditional alternative qualification path, even where the Patent is not Controlled and does not make a qualifying claim. 'Include those set forth on Attachment A' does not expressly eliminate the stated control-and-claim requirements, so this alternative is not an exact rule.；Cases in_listed_effective and in_listed_effective_controlled are classified in solely because of Attachment A listing despite expressly lacking qualifying claims; in_listed_effective also lacks CytoDyn control.；The source permits 'either or both' timing states. Case in_controlled_claims_both expressly states both Effective-Date and Term control, but its vector encodes only as_of_effective_date. The timing field has no 'both' value.；Case in_controlled_claims_term_listed states different temporal facts for separate propositions: CytoDyn control during the Term and Attachment A listing as of the Effective Date. Its single timing field encodes only during_term, losing the explicitly stated Effective-Date qualification of the listing.；Attachment A is expressly incorporated and may be updated, but neither the attachment nor any update history/content is supplied. Consequently, source support for actual listed-patent status and the effect of updates cannot be audited from the provided materials.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`in_listed_effective_controlled`）：Patent P5 is listed on Attachment A as of the Effective Date and is Controlled by CytoDyn, but does not claim any CytoDyn Know-How or Inventions.
  - 按完整合同，它属于`CytoDyn Patents`吗？`是/否/无法唯一判断`：
- 例2（`in_controlled_claims_term`）：Patent P2 is Controlled by CytoDyn during the Term and claims an Invention.
  - 按完整合同，它属于`CytoDyn Patents`吗？`是/否/无法唯一判断`：
- 例3（`out_controlled_claims_neither_timing`）：Patent P8 is Controlled by CytoDyn and claims CytoDyn Know-How, but the timing is neither as of the Effective Date nor during the Term, and it is not listed on Attachment A.
  - 按完整合同，它属于`CytoDyn Patents`吗？`是/否/无法唯一判断`：
- 例4（`out_not_controlled_no_claims_neither`）：Patent P11 is not Controlled by CytoDyn, does not claim any CytoDyn Know-How or Inventions, the timing is neither as of the Effective Date nor during the Term, and it is not listed on Attachment A.
  - 按完整合同，它属于`CytoDyn Patents`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:298:Territory

- 合同编号：`298`；[完整合同](contracts/ci298.txt)
- 来源组：`challenge_topup_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/topup_rule_program_proposals_nonthinking.jsonl`
- 程序SHA256：`4114967265e145f2e99b7fcdf47af4ed7f061ac4512b313dcf6f5c157b1b1b6a`
- 规则原文：

> 1.7 The term "Territory" means exclusively the United States of America and Canada.

- 自动概括：The term 'Territory' means exclusively the United States of America and Canada.
- 模型指出的问题：The source defines the contractual term "Territory," but the predicate instead evaluates a distinct field, "jurisdiction." The source does not state that applicable jurisdiction determines Territory, so this substitution is not an exact implementation.；The cases in_usa_territory and in_canada_territory state facts about the relevant territory but code those facts as jurisdiction; their coded field is not explicitly stated in the case text.；The source gives no basis for treating jurisdictions outside the United States and Canada as a defined exhaustive value universe, although testing them as nonmembers would be acceptable only after correcting the field to Territory.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`in_canada_territory`）：The relevant territory is Canada.
  - 按完整合同，它属于`Territory`吗？`是/否/无法唯一判断`：
- 例2（`in_usa_territory`）：The relevant territory is the United States of America.
  - 按完整合同，它属于`Territory`吗？`是/否/无法唯一判断`：
- 例3（`out_japan`）：The applicable jurisdiction is Japan.
  - 按完整合同，它属于`Territory`吗？`是/否/无法唯一判断`：
- 例4（`out_germany`）：The applicable jurisdiction is Germany.
  - 按完整合同，它属于`Territory`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:232:Tariff

- 合同编号：`232`；[完整合同](contracts/ci232.txt)
- 来源组：`challenge_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/rule_program_proposals.jsonl`
- 程序SHA256：`2c0245e2a40e3179c2af1ca38d9d284a33c79413cb918a5e4f1f5193e79b822e`
- 规则原文：

> "Tariff" means the intrastate and/or interstate tariffs that set forth the rules, regulations and rates for services on the Pipeline, including supplements thereto and reissues thereof, under which Product is transported through the Pipeline.

- 自动概括：A Tariff is an intrastate, interstate, or both-scope tariff, or a supplement or reissue thereof, that sets forth rules, regulations, and rates for services on the Pipeline, and under which Product is transported through the Pipeline.
- 模型指出的问题：The source includes supplements to, and reissues of, qualifying intrastate and/or interstate tariffs. The predicate instead treats a supplement or reissue as an independently qualifying instrument merely because its instrument_nature is 'supplement' or 'reissue'. It does not require a stated relationship to a qualifying underlying tariff ('thereto'/'thereof').；The predicate requires every supplement and reissue itself to be an intrastate/interstate tariff that independently sets forth all rules, regulations, and rates. The text can include a supplement or reissue of a qualifying tariff even where the incorporated underlying tariff supplies those contents; this relationship/incorporation structure is not represented.；'original_tariff' is not a category stated in the definition. The definition refers to tariffs and then includes their supplements and reissues; treating 'original tariff' as a required alternative classification is an unsupported modeling gloss unless separately defined.；The supplement/reissue case texts do not explicitly state that the item is a supplement to or reissue of the qualifying tariff described, so the necessary 'thereto'/'thereof' fact is absent from those cases.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`in_both_original`）：The instrument is both an intrastate and interstate tariff; it sets forth rules, regulations, and rates for services on the Pipeline; it is an original tariff; Product is the product; it is transported under the instrument; and it is transported through the Pipeline.
  - 按完整合同，它属于`Tariff`吗？`是/否/无法唯一判断`：
- 例2（`in_both_reissue`）：The instrument is both an intrastate and interstate tariff; it sets forth rules, regulations, and rates for services on the Pipeline; it is a reissue; Product is the product; it is transported under the instrument; and it is transported through the Pipeline.
  - 按完整合同，它属于`Tariff`吗？`是/否/无法唯一判断`：
- 例3（`out_other_instrument`）：The instrument is an intrastate tariff; it sets forth rules, regulations, and rates for services on the Pipeline; it is an other instrument, not an original tariff, supplement, or reissue; Product is the product; it is transported under the instrument; and it is transported through the Pipeline.
  - 按完整合同，它属于`Tariff`吗？`是/否/无法唯一判断`：
- 例4（`out_not_through_pipeline`）：The instrument is an intrastate tariff; it sets forth rules, regulations, and rates for services on the Pipeline; it is an original tariff; Product is the product; Product is transported under the instrument, but not through the Pipeline.
  - 按完整合同，它属于`Tariff`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:299:Business Entity

- 合同编号：`299`；[完整合同](contracts/ci299.txt)
- 来源组：`challenge_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/rule_program_proposals.jsonl`
- 程序SHA256：`acfdf3474f60755b239f45b6e16c8410a3a99fce38ce6ca5b81620affdbb9ddc`
- 规则原文：

> "Business Entity" means a corporation, partnership, or enterprise that acquires Services from Channel Partner for use by its employees and contractors. A Business Entity is not authorized to resell the Services to any third parties.

- 自动概括：An entity is a Business Entity when all of the following hold: its entity_type is corporation, partnership, or enterprise; it acquires Services from Channel Partner; and the Services are for use by its employees and contractors. The no-resale sentence is not encoded as a membership condition because the provided dependencies_to_close do not include resale authorization.
- 模型指出的问题：The membership predicate faithfully tracks the quoted definitional clause: qualifying entity type, acquisition of Services from Channel Partner, and use by the entity's employees and contractors are all required. The separate no-resale sentence is a restriction on Business Entities, not an additional criterion for becoming one.；The definitions of the capitalized terms "Services" and "Channel Partner" are identified as dependencies but are not supplied. Their absence prevents a complete audit of the incorporated contractual meaning and of whether the case descriptions actually satisfy those defined terms.；Several purported nonqualifying entity-type scenarios rely on an unstated exclusivity assumption. A limited liability company, sole proprietorship, or nonprofit organization is not expressly stated to be outside the contractual category "corporation, partnership, or enterprise"; in particular, a nonprofit may be a corporation and "enterprise" may have a defined or broader meaning. This does not contradict the coded fact text, but it limits the cases' ability to establish exclusion without the missing definitions or express negative facts.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`in_partnership_employees_contractors`）：Beta Partnership is a partnership. It acquires Services from Channel Partner. The Services are for use by Beta Partnership's employees and contractors.
  - 按完整合同，它属于`Business Entity`吗？`是/否/无法唯一判断`：
- 例2（`in_enterprise_employees_contractors`）：Gamma Enterprise is an enterprise. It acquires Services from Channel Partner. The Services are for use by Gamma Enterprise's employees and contractors.
  - 按完整合同，它属于`Business Entity`吗？`是/否/无法唯一判断`：
- 例3（`out_corp_employees_only`）：Acme Corporation is a corporation. It acquires Services from Channel Partner. The Services are for use by Acme Corporation's employees only, not its contractors.
  - 按完整合同，它属于`Business Entity`吗？`是/否/无法唯一判断`：
- 例4（`out_nonprofit_type`）：Zeta Nonprofit is a nonprofit organization. It acquires Services from Channel Partner. The Services are for use by Zeta Nonprofit's employees and contractors.
  - 按完整合同，它属于`Business Entity`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:299:Response

- 合同编号：`299`；[完整合同](contracts/ci299.txt)
- 来源组：`challenge_topup2_candidate`；自动审查：`revise`
- 程序来源：`topup2_rule_program_proposals_nonthinking.jsonl`
- 程序SHA256：`f36dc779b3a6b0c8c03730f1bfab6712b71e175d206853d60bf971b9dcc627fe`
- 规则原文：

> "Response" means the iPass' acknowledgment of its receipt of a Trouble Report from Channel Partner.

- 自动概括：A Response is an acknowledgment by iPass that it received a Trouble Report from Channel Partner.
- 模型指出的问题：The predicate faithfully expresses the quoted definition as a conjunction: an acknowledgment by iPass, of receipt, of a Trouble Report, from Channel Partner.；c07 codes the received item as a Trouble Report and its sender as Channel Partner, but the text says iPass sent a Trouble Report to Channel Partner and expressly denies receipt.；c08 codes the sender as Channel Partner, but the text states that iPass sent the Trouble Report to Channel Partner.；c09 is internally inconsistent for is_ipass_acknowledgment: it initially says iPass acknowledges receipt, then says the acknowledgment was made by Channel Partner on iPass's behalf. The coded false value is not unambiguously established without an agency/attribution rule.；The definitions of Trouble Report, Channel Partner, and iPass are identified as dependencies but are not supplied. Their absence prevents verification that the case labels and actor/status terms correspond to the incorporated contract definitions.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`c03`）：iPass acknowledges receipt of a Trouble Report, and the report was sent by Channel Partner.
  - 按完整合同，它属于`Response`吗？`是/否/无法唯一判断`：
- 例2（`c10`）：iPass acknowledges receipt of a Trouble Report from Channel Partner, but the acknowledgment is only an internal note never communicated.
  - 按完整合同，它属于`Response`吗？`是/否/无法唯一判断`：
- 例3（`c06`）：iPass acknowledges receipt of a general inquiry from Channel Partner, not a Trouble Report.
  - 按完整合同，它属于`Response`吗？`是/否/无法唯一判断`：
- 例4（`c08`）：Channel Partner acknowledges receipt of a Trouble Report from iPass.
  - 按完整合同，它属于`Response`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:427:Company Site

- 合同编号：`427`；[完整合同](contracts/ci427.txt)
- 来源组：`challenge_topup_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/topup_rule_program_proposals_nonthinking.jsonl`
- 程序SHA256：`6dff20fa32f5863f4d2efb197963abad7b1e78f7e74b1c720c6f92c3519feb91`
- 规则原文：

> (g) "Company Site" shall mean the web site or sites of the Company on the ------------ Internet, one of which is currently located at www.iship.com.

- 自动概括：A Company Site is any web site or sites of the Company that are on the Internet.
- 模型指出的问题：The predicate correctly captures the definition: a web site of the Company that is on the Internet. The www.iship.com clause identifies a currently existing example and does not add a predicate condition or exception.；The field is_company_site is redundant and circular: its stated source basis is the defined term itself, while the predicate independently determines that conclusion. It should be removed from case fact vectors or renamed to a non-conclusory underlying fact.；Cases in_basic and in_second_site refer to Acme Corp rather than the contractual Company. Neither case expressly states that Acme Corp is the Company, and no supplied attachment or dependency definition establishes that identity. Their is_web_site_of_company=true coding is therefore unsupported by the stated facts.；The remaining cases generally expressly state, or directly negate, the two operative underlying facts: that the item is a web site of the Company and that it is on the Internet.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`in_intranet_web`）：The Company's internal web site is accessible on the Internet.
  - 按完整合同，它属于`Company Site`吗？`是/否/无法唯一判断`：
- 例2（`in_third_party_hosted`）：A web site hosted by a third party is a web site of the Company and is on the Internet.
  - 按完整合同，它属于`Company Site`吗？`是/否/无法唯一判断`：
- 例3（`out_neither`）：A web site owned by another company is not on the Internet.
  - 按完整合同，它属于`Company Site`吗？`是/否/无法唯一判断`：
- 例4（`out_other_web_offline`）：Another company owns a web site that is not on the Internet.
  - 按完整合同，它属于`Company Site`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:402:Domain Names

- 合同编号：`402`；[完整合同](contracts/ci402.txt)
- 来源组：`challenge_topup2_candidate`；自动审查：`revise`
- 程序来源：`topup2_rule_program_proposals_nonthinking.jsonl`
- 程序SHA256：`27d7f2dc3d7b21cf15a73980a895c6e103604e9edaff820e162907770bc7f35c`
- 规则原文：

> "Domain Names" means Internet domain names, including top level domain names and global top level domain names, URLs, social media identifiers, handles and tags.

- 自动概括：An item is a Domain Name if and only if its item_type is one of: internet_domain_name, top_level_domain_name, global_top_level_domain_name, url, social_media_identifier, handle, or tag.
- 模型指出的问题：The source uses "including," which ordinarily introduces non-exhaustive examples or included subcategories. The proposed predicate converts that wording into an exhaustive if-and-only-if list and excludes every unlisted item_type.；The source does not expressly state that items outside the seven coded categories are not Domain Names. Therefore the programmed negative result for item_type "other" is not established by the quote.；The individual case texts explicitly state their coded item_type facts, and no external attachment or redacted case fact is needed for those stated classifications.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`c05`）：The asset is @exampleco, a social media identifier.
  - 按完整合同，它属于`Domain Names`吗？`是/否/无法唯一判断`：
- 例2（`c03`）：The asset is .museum, a global top level domain name.
  - 按完整合同，它属于`Domain Names`吗？`是/否/无法唯一判断`：
- 例3（`c12`）：The asset is a generic software product name, which is not an Internet domain name, top level domain name, global top level domain name, URL, social media identifier, handle, or tag.
  - 按完整合同，它属于`Domain Names`吗？`是/否/无法唯一判断`：
- 例4（`c10`）：The asset is a telephone number, which is not an Internet domain name, top level domain name, global top level domain name, URL, social media identifier, handle, or tag.
  - 按完整合同，它属于`Domain Names`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:194:Intellectual Property

- 合同编号：`194`；[完整合同](contracts/ci194.txt)
- 来源组：`challenge_topup2_candidate`；自动审查：`revise`
- 程序来源：`topup2_rule_program_proposals_nonthinking.jsonl`
- 程序SHA256：`ca7495b7fb2b158344e989b11a16b4a2b4cc45241b4016a8fb3c5939fc075224`
- 规则原文：

> "Intellectual Property" means, with respect to any Person, all unpatented ideas, inventions, processes, discoveries trademarks, patents, copyrights, and any applications for registration thereof, and trade secrets and know-how of that Person, whether owned, used, or licensed by that Person as licensee or licensor.

- 自动概括：An item is Intellectual Property of a Person if it is one of the listed categories (unpatented idea, invention, process, discovery, trademark, patent, copyright, registration application, trade secret, or know-how) and it is owned, used, or licensed by that Person as licensee or licensor.
- 模型指出的问题：The predicate treats every `registration_application` as covered. The source covers only applications for registration 'thereof'—i.e., applications connected to the enumerated intellectual-property subject matter. The program lacks a field or condition establishing that connection, so it is overbroad.；Case c07 states only that Person G owns 'a registration application.' It does not state that the application is for registration of an enumerated item, so its coded listed-category fact is not explicitly established under the source text.；Cases c12 and c16 state that the person owns a trademark while coding `person_relation` as `none`; ownership is a covered relation and contradicts the coded fact.；Case c13 states that Person M owns a patent while coding `person_relation` as `none`; ownership contradicts the coded fact.；Case c14 states that Person N uses a copyright while coding `person_relation` as `none`; use contradicts the coded fact.；Case c15 states that Person O is a licensee of a trade secret while coding `person_relation` as `none`; licensing as licensee contradicts the coded fact.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`c04`）：Person D is a licensor of know-how.
  - 按完整合同，它属于`Intellectual Property`吗？`是/否/无法唯一判断`：
- 例2（`c09`）：Person I owns a discovery.
  - 按完整合同，它属于`Intellectual Property`吗？`是/否/无法唯一判断`：
- 例3（`c11`）：Person K owns a building.
  - 按完整合同，它属于`Intellectual Property`吗？`是/否/无法唯一判断`：
- 例4（`c14`）：Person N uses a copyright but the copyright is not owned, used, or licensed by Person N.
  - 按完整合同，它属于`Intellectual Property`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:1:Google Toolbar

- 合同编号：`1`；[完整合同](contracts/ci1.txt)
- 来源组：`challenge_topup_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/topup_rule_program_proposals.jsonl`
- 程序SHA256：`ccad637e684bd00bb17918057203e02fa85029a58e98a7cba7d22c3e3a7f8cfc`
- 规则原文：

> "Google Toolbar" means the machine-readable binary code version of the Google toolbar for Internet Explorer provided to Distributor in connection with this Agreement, and any modifications or updates to it that Google may provide to Distributor.

- 自动概括：An item is Google Toolbar if either (A) it is a machine-readable binary code version of the Google toolbar for Internet Explorer provided to Distributor in connection with this Agreement, or (B) it is a modification or update to the Google toolbar for Internet Explorer provided by Google to Distributor.
- 模型指出的问题：The update branch substitutes the source's modal qualifier—modifications or updates that Google 'may provide to Distributor'—with the distinct past-tense factual condition 'provided by Google to Distributor.' The supplied fields and cases do not represent whether Google may provide an update, so the predicate is not an exact implementation of the quoted definition.；All fact vectors accurately reflect their respective fact_text statements, but update-related cases encode actual provision rather than the source's stated modal qualification.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`in_google_update`）：The item is not a machine-readable binary code version; it is not the Google toolbar for Internet Explorer; it was not provided to Distributor; it was not provided in connection with this Agreement; it is a modification or update; it is a modification or update to the Google toolbar for Internet Explorer; it was provided by Google to Distributor.
  - 按完整合同，它属于`Google Toolbar`吗？`是/否/无法唯一判断`：
- 例2（`in_original_binary`）：The item is a machine-readable binary code version; it is the Google toolbar for Internet Explorer; it was provided to Distributor; it was provided in connection with this Agreement; it is not a modification or update; it is not a modification or update to the Google toolbar for Internet Explorer; it was not provided by Google to Distributor.
  - 按完整合同，它属于`Google Toolbar`吗？`是/否/无法唯一判断`：
- 例3（`out_not_binary`）：The item is not a machine-readable binary code version; it is the Google toolbar for Internet Explorer; it was provided to Distributor; it was provided in connection with this Agreement; it is not a modification or update; it is not a modification or update to the Google toolbar for Internet Explorer; it was not provided by Google to Distributor.
  - 按完整合同，它属于`Google Toolbar`吗？`是/否/无法唯一判断`：
- 例4（`out_update_not_to_ie_toolbar`）：The item is not a machine-readable binary code version; it is not the Google toolbar for Internet Explorer; it was not provided to Distributor; it was not provided in connection with this Agreement; it is a modification or update; it is not a modification or update to the Google toolbar for Internet Explorer; it was provided by Google to Distributor.
  - 按完整合同，它属于`Google Toolbar`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:340:Redistributor

- 合同编号：`340`；[完整合同](contracts/ci340.txt)
- 来源组：`challenge_topup_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/topup_rule_program_proposals_nonthinking.jsonl`
- 程序SHA256：`02a33e18abb71375471d9574a1e6317a189ac9bfcf6766dc096d0103d0124714`
- 规则原文：

> "Redistributor" means any individual or entity that is granted a license by Licensee to copy and sublicense one or more Licensed Products to Customers.

- 自动概括：A Redistributor is an individual or entity that is granted a license by Licensee to copy and sublicense one or more Licensed Products to Customers.
- 模型指出的问题：The predicate faithfully encodes the quoted Redistributor definition as a conjunction of individual-or-entity status, a grant by Licensee, and authority to copy and sublicense one or more Licensed Products to Customers.；Each case text expressly supports its coded positive and negative scope/grant facts.；Definitions or source materials for the referenced defined terms "Licensee," "Licensed Products," and "Customers" are not provided. The program identifies these dependencies, but the supplied source is insufficient to verify their underlying contractual meaning or any qualifications contained in those definitions.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`c15`）：Omicron Corp is an entity. Licensee granted Omicron Corp a license to copy and sublicense one or more Licensed Products to Customers.
  - 按完整合同，它属于`Redistributor`吗？`是/否/无法唯一判断`：
- 例2（`c03`）：Beta Corp is an entity. Licensee granted Beta Corp a license to copy and sublicense one or more Licensed Products to Customers.
  - 按完整合同，它属于`Redistributor`吗？`是/否/无法唯一判断`：
- 例3（`c09`）：Iota LLC is an entity. A third party, not Licensee, granted Iota LLC a license to copy and sublicense one or more Licensed Products to Customers.
  - 按完整合同，它属于`Redistributor`吗？`是/否/无法唯一判断`：
- 例4（`c07`）：Sigma LLC is an entity. Licensee granted Sigma LLC a license to copy and sublicense one or more Licensed Products to distributors, but not to Customers.
  - 按完整合同，它属于`Redistributor`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:498:Confidential Information

- 合同编号：`498`；[完整合同](contracts/ci498.txt)
- 来源组：`challenge_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/rule_program_proposals.jsonl`
- 程序SHA256：`60026fdcec4713617d3b9909f84c8aa082377c82e7a6c6124c0ac9754d481e1c`
- 规则原文：

> Definition. "Confidential Information" shall mean, with respect to a party, all non-public written, electronic, and oral proprietary information communicated to the other party (or obtained by such other party while at the party's premises) during the Term in connection with this Agreement including information relating to a party's products, services, designs, methodologies, business plans, finances, marketing plans, customers or prospects and the terms of this Agreement. Confidential Information will not include information that (a) was known by the Receiving Party without an obligation of confidentiality before its receipt from the Disclosing Party, (b) is independently developed by the Receiving Party, (c) is or becomes publicly available without a breach by the Receiving Party of this Agreement, or (d) is disclosed to the Receiving Party by a third person who is not required to maintain its confidentiality.

- 自动概括：Information qualifies as Confidential Information if it is non-public, proprietary, in written/electronic/oral form, communicated to the Receiving Party or obtained at the Disclosing Party's premises, during the Term, in connection with the Agreement, and none of exclusions (a)-(d) applies.
- 模型指出的问题：The quoted source expressly relies on externally defined capitalized terms (Term, Disclosing Party, Receiving Party, and Agreement), but their definitions are not included. The program accurately records these dependencies, yet the source package is incomplete for applying the rule to real facts.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`c04`）：During the Term, in connection with this Agreement, the Disclosing Party communicated written non-public proprietary information to the Receiving Party; the Receiving Party did not obtain it at the Disclosing Party's premises; the Receiving Party did not know it without a confidentiality obligation before receipt; it was not independently developed by the Receiving Party; it was not publicly available without a Receiving Party breach; and it was disclosed to the Receiving Party by a third person who is required to maintain confidentiality, so it was not disclosed by a third person not required to maintain confidentiality.
  - 按完整合同，它属于`Confidential Information`吗？`是/否/无法唯一判断`：
- 例2（`c03`）：During the Term, in connection with this Agreement, the Disclosing Party communicated oral non-public proprietary information to the Receiving Party; the Receiving Party did not obtain it at the Disclosing Party's premises; the Receiving Party did not know it without a confidentiality obligation before receipt; it was not independently developed by the Receiving Party; it was not publicly available without a Receiving Party breach; and it was not disclosed to the Receiving Party by a third person not required to maintain confidentiality.
  - 按完整合同，它属于`Confidential Information`吗？`是/否/无法唯一判断`：
- 例3（`c15`）：During the Term, in connection with this Agreement, the Disclosing Party communicated written non-public proprietary information to the Receiving Party; the Receiving Party did not obtain it at the Disclosing Party's premises; the Receiving Party did not know it without a confidentiality obligation before receipt; it was not independently developed by the Receiving Party; it was not publicly available without a Receiving Party breach; and it was disclosed to the Receiving Party by a third person not required to maintain confidentiality.
  - 按完整合同，它属于`Confidential Information`吗？`是/否/无法唯一判断`：
- 例4（`c11`）：During the Term, not in connection with this Agreement, the Disclosing Party communicated written non-public proprietary information to the Receiving Party; the Receiving Party did not obtain it at the Disclosing Party's premises; the Receiving Party did not know it without a confidentiality obligation before receipt; it was not independently developed by the Receiving Party; it was not publicly available without a Receiving Party breach; and it was not disclosed to the Receiving Party by a third person not required to maintain confidentiality.
  - 按完整合同，它属于`Confidential Information`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:243:Licensee Party

- 合同编号：`243`；[完整合同](contracts/ci243.txt)
- 来源组：`challenge_topup2_candidate`；自动审查：`revise`
- 程序来源：`topup2_rule_program_proposals_nonthinking.jsonl`
- 程序SHA256：`e25cc1af66937a51c4f5054e917c151b5712cc02b36b967a5151e7049e659bba`
- 规则原文：

> "Licensee Party" shall mean one of the Parties, as the context requires, other than the Licensor Party, to whom Licensed Intellectual Property Rights are granted from the Licensor Party pursuant to the terms hereof.

- 自动概括：A Licensee Party is a Party that is not the Licensor Party and to whom Licensed Intellectual Property Rights are granted from the Licensor Party pursuant to the terms of the agreement.
- 模型指出的问题：The source includes the qualifier 'as the context requires.' The predicate omits any contextual-applicability condition, so it is not an exact implementation of the definition.；The provided source does not supply the referenced definitions of Party, Licensor Party, or Licensed Intellectual Property Rights, nor any contextual facts needed to apply 'as the context requires.'；The four purported in-scope cases do not state that the context requires treating the identified Party as a Licensee Party; their source-defined status is therefore not fully established.；In out_no_grant, out_licensor_and_no_grant, and out_nonparty_no_grant, the text denies that the subject was granted the rights, but the vectors nevertheless set grant_from_licensor_party and pursuant_to_terms to true. A denial of the composite grant does not explicitly establish affirmative provenance or contractual-pursuance facts.；The source phrase 'to whom Licensed Intellectual Property Rights are granted from the Licensor Party pursuant to the terms hereof' is a single qualified grant condition. Decomposing it into separate affirmative provenance and terms fields is acceptable only where the case text expressly supports each component; the no-grant cases do not.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`in_second_party`）：Beta is a Party. Beta is not the Licensor Party. Beta received a grant of Licensed Intellectual Property Rights from the Licensor Party under the terms hereof.
  - 按完整合同，它属于`Licensee Party`吗？`是/否/无法唯一判断`：
- 例2（`in_full`）：Alpha is a Party. Alpha is not the Licensor Party. Alpha has been granted Licensed Intellectual Property Rights from the Licensor Party pursuant to the terms of the agreement.
  - 按完整合同，它属于`Licensee Party`吗？`是/否/无法唯一判断`：
- 例3（`out_no_grant`）：Eta is a Party. Eta is not the Licensor Party. Eta has not been granted Licensed Intellectual Property Rights from the Licensor Party pursuant to the terms hereof.
  - 按完整合同，它属于`Licensee Party`吗？`是/否/无法唯一判断`：
- 例4（`out_nonparty_no_grant`）：Lambda is not a Party. Lambda is not the Licensor Party. Lambda has not been granted Licensed Intellectual Property Rights from the Licensor Party pursuant to the terms hereof.
  - 按完整合同，它属于`Licensee Party`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:138:Litigation Expense

- 合同编号：`138`；[完整合同](contracts/ci138.txt)
- 来源组：`challenge_topup2_candidate`；自动审查：`revise`
- 程序来源：`topup2_rule_program_proposals_nonthinking.jsonl`
- 程序SHA256：`7d55fb2fcaecb724bb4b15cee5d14bef7d9983f51181c5d842a4b9a95f81cb42`
- 规则原文：

> 2.26 Litigation Expense. "Litigation Expense" means any court filing fee, court cost, arbitration fee, and each other fee and cost of investigating or defending an indemnified claim or asserting any claim for indemnification or defense under this Agreement, including Attorney's Fees, other professionals' fees, and disbursements.

- 自动概括：A fee or cost is a Litigation Expense if it is a court filing fee, court cost, or arbitration fee, or if it is another fee or cost (including Attorney's Fees, other professionals' fees, or disbursements) incurred for investigating or defending an indemnified claim or asserting a claim for indemnification or defense under this Agreement.
- 模型指出的问题：The predicate correctly treats court filing fees, court costs, and arbitration fees as included without a stated purpose limitation, while applying the investigation/defense or indemnification/defense-assertion purpose limitation to each other fee and cost.；The three listed categories of Attorney's Fees, other professionals' fees, and disbursements are expressly included within 'each other fee and cost.' The identified cases code is_other_fee_or_cost=false despite their texts identifying such included fee/cost types, so the fact vectors do not faithfully reflect the source terminology.；The quoted definition depends on unprovided Agreement materials to determine the meaning and scope of 'indemnified claim,' the definition of 'Attorney's Fees,' and the referenced indemnification and defense provisions. Those dependencies are identified but not supplied.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`other_professional_fee_defending_yes`）：An expert witness fee, as another professional's fee, was incurred to defend an indemnified claim.
  - 按完整合同，它属于`Litigation Expense`吗？`是/否/无法唯一判断`：
- 例2（`court_cost_yes`）：A $250 court cost was incurred while defending an indemnified claim.
  - 按完整合同，它属于`Litigation Expense`吗？`是/否/无法唯一判断`：
- 例3（`no_fee_no`）：No fee or cost of any kind was incurred.
  - 按完整合同，它属于`Litigation Expense`吗？`是/否/无法唯一判断`：
- 例4（`attorney_fee_other_purpose_no`）：Attorney's fees were incurred for general corporate advice unrelated to any indemnified claim or claim for indemnification or defense.
  - 按完整合同，它属于`Litigation Expense`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:196:Project

- 合同编号：`196`；[完整合同](contracts/ci196.txt)
- 来源组：`challenge_topup_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/topup_rule_program_proposals.jsonl`
- 程序SHA256：`646755387ccd66ead23d3b3e28395416b4a2170ffe462ddb891679668f4f108a`
- 规则原文：

> "Project" shall mean any undertaking involving the provision of nuclear consulting or strategic advisory services to any entity in the United Arab Emirates.

- 自动概括：A fact is a Project if it is an undertaking, it involves the provision of services, the service type is nuclear consulting or strategic advisory, the recipient is an entity, and the recipient is in the United Arab Emirates.
- 模型指出的问题：The predicate faithfully expresses the quoted definition: an undertaking must involve providing either nuclear consulting or strategic advisory services to an entity in the United Arab Emirates.；Several cases code service_type as "other" solely from labels such as oil-and-gas, financial, strategic-planning, or environmental consulting. Those labels do not explicitly establish that the services are not strategic advisory services; this requires an unsupported classification gloss.；Several cases code recipient_is_entity=false from statements that the recipient is not a "legal entity." The source says "any entity," not "any legal entity," so the equivalence between not being a legal entity and not being an entity is not established by the supplied text.；The UAE-ministry case codes recipient_is_entity=true without expressly stating that the ministry is an entity. Whether a ministry qualifies as an entity may depend on an applicable definition or legal characterization.；The supplied quote is sufficient to state the structural rule, but undefined terms such as "undertaking," "entity," and "strategic advisory services" must not be resolved through unstated assumptions when encoding fact vectors.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`in_nuclear_uae_entity_3`）：An undertaking provides nuclear consulting services to a UAE ministry located in the United Arab Emirates.
  - 按完整合同，它属于`Project`吗？`是/否/无法唯一判断`：
- 例2（`in_nuclear_uae_entity`）：An undertaking involves providing nuclear consulting services to a UAE-based corporate entity located in the United Arab Emirates.
  - 按完整合同，它属于`Project`吗？`是/否/无法唯一判断`：
- 例3（`out_other_and_not_entity`）：An undertaking provides strategic planning services to an informal group in the United Arab Emirates; the group is not a legal entity.
  - 按完整合同，它属于`Project`吗？`是/否/无法唯一判断`：
- 例4（`out_strategic_non_entity_uae`）：An undertaking provides strategic advisory services to an unincorporated association in the United Arab Emirates, and the association is not a legal entity.
  - 按完整合同，它属于`Project`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

