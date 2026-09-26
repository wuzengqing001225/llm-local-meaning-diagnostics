# 正式来源规则复核 第4批

> **暂停填写：**旧生成器把定义判据写进事实句。这批材料仅作失败审计，不进入正式实验。

此包按来源文本生成，没有读新A分数或B读者结果。模型意见是预筛，不是金标准。
你只需核原文引文、自动规则概括和4个固定事实；这4个事实正是后续A题候选。程序字段和布尔表达式由我核。
**不要**根据你预计哪个模型会答错来决定收录。自动审查为`revise`的条目可以填`待改`，写明哪一条件不对，无需你改JSON。

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
- 例1（`in_own_100`）：Beta LLC is a company. CERES indirectly owns 100% of Beta LLC's voting stock. Beta LLC is not under common control with CERES, does not control CERES, and has no power to nominate at least half of CERES's directors.
  - 按完整合同，它属于`AFFILIATED COMPANY`吗？`是/否/无法唯一判断`：
- 例2（`in_nominate`）：Epsilon GmbH is a company. Epsilon GmbH has the power to nominate at least half of CERES's directors. CERES owns 0% of Epsilon GmbH's voting shares, Epsilon GmbH is not under common control with CERES, and Epsilon GmbH does not control CERES.
  - 按完整合同，它属于`AFFILIATED COMPANY`吗？`是/否/无法唯一判断`：
- 例3（`out_own_50`）：Eta Corp is a company. CERES directly owns exactly 50% of Eta Corp's voting shares. Eta Corp is not under common control with CERES, does not control CERES, and has no power to nominate at least half of CERES's directors.
  - 按完整合同，它属于`AFFILIATED COMPANY`吗？`是/否/无法唯一判断`：
- 例4（`out_own_50_common_false`）：Lambda Corp is a company. CERES directly owns 50% of Lambda Corp's voting shares. Lambda Corp is not under common control with CERES, does not control CERES, and has no power to nominate at least half of CERES's directors.
  - 按完整合同，它属于`AFFILIATED COMPANY`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:102:Internet

- 合同编号：`102`；[完整合同](contracts/ci102.txt)
- 来源组：`challenge_topup_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/topup_rule_program_proposals.jsonl`
- 程序SHA256：`43dce9a20800cb622cb7728a4df19b4c634c0b04161ac6f784a11c0349bf4918`
- 规则原文：

> "Internet" means any systems for distributing digital electronic content and information to end users via transmission, broadcast, public display, or other forms of delivery, whether direct or indirect, whether over telephone lines, cable television systems, optical fiber connections, cellular telephones, satellites, wireless broadcast, or other mode of transmission now known or subsequently developed.

- 自动概括：Membership in 'Internet' requires that the entity is a system, distributes digital electronic content and information to end users, has a delivery mode, and has a transmission medium.
- 模型指出的问题：The predicate improperly makes `has_transmission_medium` an independent mandatory condition. The source uses 'whether over' specified media or another transmission mode as an inclusive, non-limiting qualification, not as a separate element that must be established in addition to qualifying delivery.；The source expressly includes delivery 'via transmission, broadcast, public display, or other forms of delivery.' A public-display or other qualifying-delivery system need not be excluded merely because a separate transmission-medium fact is false; case_12 exposes this overrestriction.；`has_delivery_mode` is only a vague proxy for the source requirement that the system distribute content via transmission, broadcast, public display, or another form of delivery. The cases state that a mode exists, rather than explicitly stating that the described distribution occurs via a qualifying form of delivery.；The listed telephone/cable/fiber/cellular/satellite/wireless items are examples within a nonexclusive 'whether over ... or other mode of transmission' clause, not independent conjunctive requirements. The field structure incorrectly treats delivery form and transmission medium as two universally required elements.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`case_01_telephone_network`）：A telephone network system distributes digital electronic content and information to end users, and it has a delivery mode and a transmission medium.
  - 按完整合同，它属于`Internet`吗？`是/否/无法唯一判断`：
- 例2（`case_06_cellular`）：A cellular system distributes digital electronic content and information to end users, and it has a delivery mode and a transmission medium.
  - 按完整合同，它属于`Internet`吗？`是/否/无法唯一判断`：
- 例3（`case_10_not_to_end_users`）：A system distributes digital electronic content and information only to intermediaries, not to end users, and it has a delivery mode and a transmission medium.
  - 按完整合同，它属于`Internet`吗？`是/否/无法唯一判断`：
- 例4（`case_08_not_a_system`）：A non-system entity distributes digital electronic content and information to end users, and it has a delivery mode and a transmission medium.
  - 按完整合同，它属于`Internet`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:501:Agreement

- 合同编号：`501`；[完整合同](contracts/ci501.txt)
- 来源组：`challenge_topup_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/topup_rule_program_proposals_nonthinking.jsonl`
- 程序SHA256：`d34a118a7199649bd5bc931dd10092811abf44cdfaf3ab5afed4d736fc8bd36f`
- 规则原文：

> (b) "Agreement" means this Joint Venture Agreement, dated December 19, 2019.

- 自动概括：A document is the 'Agreement' if and only if it is a Joint Venture Agreement dated December 19, 2019.
- 模型指出的问题：The source defines Agreement as a particular referential document: "this Joint Venture Agreement." The predicate instead applies to any Joint Venture Agreement bearing the stated date and does not encode that the evaluated document is the document denoted by "this."；The stated dependencies acknowledge the necessary identification of the document referred to by "this," but no predicate field or condition implements that dependency.；The quoted clause alone does not establish which actual instrument is denoted by "this"; the relevant agreement context or attachment is absent. Date and document type cannot by themselves establish identity where multiple instruments could share both attributes.；The case fact vectors accurately reflect the stated document types and dates, including the use of "other" for unstated or nonmatching dates. However, the case set does not test the material distinction between the particular document denoted by "this" and a different same-titled, same-dated document.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`c03`）：The document referred to as 'this' is the Joint Venture Agreement, dated December 19, 2019.
  - 按完整合同，它属于`Agreement`吗？`是/否/无法唯一判断`：
- 例2（`c02`）：The operative document is a Joint Venture Agreement dated December 19, 2019, executed by the parties.
  - 按完整合同，它属于`Agreement`吗？`是/否/无法唯一判断`：
- 例3（`c08`）：The operative document is a Share Purchase Agreement dated December 19, 2019.
  - 按完整合同，它属于`Agreement`吗？`是/否/无法唯一判断`：
- 例4（`c09`）：The operative document is a Limited Liability Company Agreement dated December 19, 2019.
  - 按完整合同，它属于`Agreement`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:138:Intellectual Property Rights

- 合同编号：`138`；[完整合同](contracts/ci138.txt)
- 来源组：`challenge_topup_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/topup_rule_program_proposals.jsonl`
- 程序SHA256：`ebbbf4d186a03da346fc65de2be4a66f54bd7a27232b76b5bd7eb323fbb4c122`
- 规则原文：

> "Intellectual Property Rights" means all patents (including all reissues, divisions, continuations, and extensions thereof) and patent applications, trade names, trademarks, service marks, logos, trade dress, copyrights, trade secrets, mask works, rights in technology, know-how, rights in content (including performance and synchronization rights), or other intellectual property rights that are in each case protected under the Laws of any governmental authority having jurisdiction.

- 自动概括：A right qualifies as 'Intellectual Property Rights' if its right_category is one of the enumerated IP categories (patent, patent application, trade name, trademark, service mark, logo, trade dress, copyright, trade secret, mask work, rights in technology, know-how, rights in content, performance rights, synchronization rights, or other intellectual property right) and it is protected under the Laws of any governmental authority having jurisdiction.
- 模型指出的问题：The quoted definition depends on the capitalized term "Laws," but its definition or governing attachment is not supplied. The predicate preserves the phrase as a factual condition, but the full contractual scope of what counts as "Laws" cannot be audited from the provided source alone.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`synchronization_rights_protected`）：Synchronization rights for a song in a movie are protected under the laws of a governmental authority having jurisdiction; right_category is synchronization_rights and protected_under_laws_of_government is true.
  - 按完整合同，它属于`Intellectual Property Rights`吗？`是/否/无法唯一判断`：
- 例2（`trade_secret_protected`）：A trade secret for a manufacturing process is protected under the laws of a governmental authority having jurisdiction; right_category is trade_secret and protected_under_laws_of_government is true.
  - 按完整合同，它属于`Intellectual Property Rights`吗？`是/否/无法唯一判断`：
- 例3（`non_ip_real_property_protected`）：Ownership of a parcel of land is protected under the laws of a governmental authority having jurisdiction; right_category is non_ip_right and protected_under_laws_of_government is true.
  - 按完整合同，它属于`Intellectual Property Rights`吗？`是/否/无法唯一判断`：
- 例4（`patent_not_protected`）：A patent for a business method is not protected under the laws of any governmental authority having jurisdiction; right_category is patent and protected_under_laws_of_government is false.
  - 按完整合同，它属于`Intellectual Property Rights`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:129:Showtime

- 合同编号：`129`；[完整合同](contracts/ci129.txt)
- 来源组：`challenge_topup_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/topup_rule_program_proposals.jsonl`
- 程序SHA256：`c89fa95493cf44e68c468e27fd8e5ea86efc8cf09b69165bb0613526355ed367`
- 规则原文：

> "Showtime" means the advertised showtime for a feature film.

- 自动概括：The term 'Showtime' means an advertised showtime for a feature film; thus membership requires that the time be advertised and be a screening of a feature film.
- 模型指出的问题：The predicate omits the source's distinct requirement that the item be a 'showtime.' It tests only whether something is advertised and is a feature-film screening; the quoted definition is limited to an advertised showtime for a feature film.；case_05 describes an online premiere, not explicitly a screening or a showtime. Coding it as is_feature_film_screening=true is therefore unsupported by the stated text, and the program would include it without establishing the omitted showtime element.；Several positive examples use related terms such as 'showing' or 'presentation' rather than expressly stating that the advertised item is a showtime; the program should either code and support a showtime fact or narrow/rewrite the case texts.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`case_06`）：A local theater advertises a 10:00 AM feature film screening.
  - 按完整合同，它属于`Showtime`吗？`是/否/无法唯一判断`：
- 例2（`case_05`）：A streaming platform advertises a 6:00 PM online premiere of a feature film.
  - 按完整合同，它属于`Showtime`吗？`是/否/无法唯一判断`：
- 例3（`case_11`）：A theater advertises a 4:00 PM stage play, which is not a feature film screening.
  - 按完整合同，它属于`Showtime`吗？`是/否/无法唯一判断`：
- 例4（`case_10`）：A cinema has an unadvertised 10:00 PM feature film screening.
  - 按完整合同，它属于`Showtime`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:176:Agreement

- 合同编号：`176`；[完整合同](contracts/ci176.txt)
- 来源组：`challenge_topup2_candidate`；自动审查：`revise`
- 程序来源：`topup2_rule_program_proposals_nonthinking.jsonl`
- 程序SHA256：`9407dcc6015c38c40c71446bb847f21dc1f3f6d00d77c6ee44208c633157b25f`
- 规则原文：

> 1.2 "Agreement" shall mean the Mobile Virtual Network Enabler(MVNE) hosting agreement together with the Appendices attached to this MVNE hosting agreement.

- 自动概括：A document is the 'Agreement' if and only if it is the Mobile Virtual Network Enabler (MVNE) hosting agreement and an appendix is attached to that MVNE hosting agreement.
- 模型指出的问题：The source defines the Agreement as the MVNE hosting agreement together with whatever Appendices are attached to it; it does not expressly make the existence of at least one attached appendix a condition for something to qualify as the Agreement.；The proposed predicate converts the descriptive phrase 'together with the Appendices attached' into a mandatory Boolean requirement that an appendix be attached. This excludes an MVNE hosting agreement with no attached appendices, although the quoted definition does not clearly impose that exclusion.；The source describes a composite defined term (the hosting agreement together with its attached appendices), whereas the proposed rule classifies a single 'document' as the Agreement. The object being evaluated should be modeled as the agreement package/composite, or the rule should otherwise account for the included appendices.；The binary attachment field loses the source's inclusion relationship: the definition refers to the Appendices attached to the agreement, not merely whether one or more appendices exist.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`c01`）：A document is the Mobile Virtual Network Enabler (MVNE) hosting agreement, and an appendix is attached to it.
  - 按完整合同，它属于`Agreement`吗？`是/否/无法唯一判断`：
- 例2（`c11`）：A document is the Mobile Virtual Network Enabler (MVNE) hosting agreement, and an appendix is attached to it as an attachment.
  - 按完整合同，它属于`Agreement`吗？`是/否/无法唯一判断`：
- 例3（`c12`）：A document is the Mobile Virtual Network Enabler (MVNE) hosting agreement, and an appendix is not attached to it.
  - 按完整合同，它属于`Agreement`吗？`是/否/无法唯一判断`：
- 例4（`c02`）：A document is the Mobile Virtual Network Enabler (MVNE) hosting agreement, and no appendix is attached to it.
  - 按完整合同，它属于`Agreement`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:176:Appendices

- 合同编号：`176`；[完整合同](contracts/ci176.txt)
- 来源组：`challenge_topup_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/topup_rule_program_proposals.jsonl`
- 程序SHA256：`11a3eed2427536588a9264b52dc20689e5811e166ccc2475dd9f098c2aebc5a5`
- 规则原文：

> 1.3 "Appendix" and "Appendices" shall mean the appendix or appendices attached to this Agreement.

- 自动概括：A document is included in "Appendices" if and only if it is an appendix and it is attached to this Agreement.
- 模型指出的问题：The quoted definition refers to "this Agreement," but the identified Section 1.2 definition of "Agreement" is not supplied. That external definition is required to resolve the contractual referent and verify attachment to the relevant agreement.；No external document set or attachment schedule is supplied to independently establish which documents are attached; the case texts themselves explicitly assert the coded attachment facts, but the underlying source support is absent.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`app_electronic`）：Appendix D is an appendix and is attached to this Agreement electronically.
  - 按完整合同，它属于`Appendices`吗？`是/否/无法唯一判断`：
- 例2（`app_bound`）：Document A is an appendix and it is attached to this Agreement.
  - 按完整合同，它属于`Appendices`吗？`是/否/无法唯一判断`：
- 例3（`app_amendment_not_this`）：Appendix O is attached to an amendment to this Agreement but is not attached to this Agreement itself.
  - 按完整合同，它属于`Appendices`吗？`是/否/无法唯一判断`：
- 例4（`app_not_attached`）：Schedule G is an appendix but is not attached to this Agreement.
  - 按完整合同，它属于`Appendices`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:463:Parties

- 合同编号：`463`；[完整合同](contracts/ci463.txt)
- 来源组：`challenge_topup_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/topup_rule_program_proposals_nonthinking.jsonl`
- 程序SHA256：`08f167d7b8caf61d4c058bf21cc9a7f721914c18a30f9a73e859f1911a7c9b3a`
- 规则原文：

> "Parties" shall mean IMPCO, MIL and MINDA collectively, and the term "Party" shall individually refer to IMPCO, MIL and/or MINDA, as the case may be.

- 自动概括：An entity is a Party if and only if it is one of IMPCO, MIL, or MINDA.
- 模型指出的问题：The single-valued entity field cannot represent the source's express 'IMPCO, MIL and/or MINDA' formulation where more than one named Party may apply.；Cases c04-c06 explicitly state two named entities, but each fact vector codes only one entity and omits the other stated entity.；Because the predicate is evaluated over a mutually exclusive single entity value, it does not exactly model cases in which IMPCO, MIL, and/or MINDA jointly apply.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`c01`）：The entity is IMPCO.
  - 按完整合同，它属于`Parties`吗？`是/否/无法唯一判断`：
- 例2（`c05`）：The entity is MINDA and also IMPCO.
  - 按完整合同，它属于`Parties`吗？`是/否/无法唯一判断`：
- 例3（`c09`）：The entity is a joint venture between MIL and MINDA.
  - 按完整合同，它属于`Parties`吗？`是/否/无法唯一判断`：
- 例4（`c12`）：The entity is a third party unrelated to IMPCO, MIL, and MINDA.
  - 按完整合同，它属于`Parties`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:98:Services

- 合同编号：`98`；[完整合同](contracts/ci98.txt)
- 来源组：`challenge_topup2_candidate`；自动审查：`revise`
- 程序来源：`topup2_rule_program_proposals_nonthinking.jsonl`
- 程序SHA256：`89a88c68c823464fee1e5973687fe8c4d838d87ca4e67fe65f564366e800d451`
- 规则原文：

> "Services" shall mean the transportation and, if applicable, compression services provided by Transporter to Customer hereunder.

- 自动概括：A service is 'Services' if it is transportation provided by Transporter to Customer under the agreement, or if it is compression provided by Transporter to Customer under the agreement and compression services are applicable.
- 模型指出的问题：The predicate faithfully reflects the definition: transportation services qualify when provided by Transporter to Customer hereunder; compression services additionally require applicability.；Several case vectors code compression_applicable:false although their fact text does not state that compression services are not applicable. This affects in_transport_full, out_storage, out_marketing, out_transport_by_other, out_transport_to_other, and out_transport_outside_agreement.；Although the unstated compression-applicability fact is immaterial to the transportation, storage, and marketing outcomes in those cases, the requirement is that every coded fact be explicitly stated in the case text.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`in_transport_full`）：Transporter provides transportation service to Customer under the agreement.
  - 按完整合同，它属于`Services`吗？`是/否/无法唯一判断`：
- 例2（`in_transport_compress_yes`）：Transporter provides transportation service to Customer under the agreement, and compression services are applicable.
  - 按完整合同，它属于`Services`吗？`是/否/无法唯一判断`：
- 例3（`out_compress_not_applicable`）：Transporter provides compression service to Customer under the agreement, but compression services are not applicable.
  - 按完整合同，它属于`Services`吗？`是/否/无法唯一判断`：
- 例4（`out_transport_to_other`）：Transporter provides transportation service to a different shipper under the agreement.
  - 按完整合同，它属于`Services`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:8:Calendar Quarter

- 合同编号：`8`；[完整合同](contracts/ci8.txt)
- 来源组：`challenge_topup2_candidate`；自动审查：`revise`
- 程序来源：`topup2_rule_program_proposals_nonthinking.jsonl`
- 程序SHA256：`c46faf4eec35ebdb72386d0e22cb3620d46e55b57c3ac48cb6f0aa661a1728ae`
- 规则原文：

> 1.9 "Calendar Quarter" shall mean each successive period of three (3) calendar months commencing on January 1, April 1, July 1 and October 1, except that the first Calendar Quarter of the Term shall commence on the Effective Date and end on the day immediately prior to the first to occur of January 1, April 1, July 1 or October 1 after the Effective Date, and the last Calendar Quarter shall end on the last day of the Term.

- 自动概括：A period is a Calendar Quarter if it is the first quarter (starting on Effective Date and ending the day before the next standard quarter start), or the last quarter (ending on the last day of the Term), or a regular quarter (starting on Jan 1, Apr 1, Jul 1, or Oct 1 and ending on the corresponding Mar 31, Jun 30, Sep 30, or Dec 31).
- 模型指出的问题：The regular-quarter predicate independently permits any standard start date with any standard end date. The source requires successive periods of three calendar months, which requires corresponding start/end pairs (January 1–March 31, April 1–June 30, July 1–September 30, or October 1–December 31).；c09 is accepted by the predicate despite describing January 1 through June 30, a six-month period rather than a three-calendar-month quarter.；c10 is accepted by the predicate despite describing April 1 through March 31, a twelve-month period rather than a three-calendar-month quarter.；The last-quarter branch requires only last-quarter status and an end on the last day of the Term; it omits the general commencement/successive-period requirements applicable to a last quarter, subject to any overlap with the first-quarter exception.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`c09`）：A period is neither the first nor the last Calendar Quarter. It starts on January 1 and ends on June 30.
  - 按完整合同，它属于`Calendar Quarter`吗？`是/否/无法唯一判断`：
- 例2（`c02`）：A period is the last Calendar Quarter of the Term. It starts on October 1 and ends on the last day of the Term.
  - 按完整合同，它属于`Calendar Quarter`吗？`是/否/无法唯一判断`：
- 例3（`c07`）：A period is the first Calendar Quarter of the Term. It starts on January 1 and ends on March 31.
  - 按完整合同，它属于`Calendar Quarter`吗？`是/否/无法唯一判断`：
- 例4（`c12`）：A period is the last Calendar Quarter of the Term. It starts on October 1 and ends on December 31.
  - 按完整合同，它属于`Calendar Quarter`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:283:Licensed Products

- 合同编号：`283`；[完整合同](contracts/ci283.txt)
- 来源组：`challenge_topup2_candidate`；自动审查：`revise`
- 程序来源：`topup2_rule_program_proposals_nonthinking.jsonl`
- 程序SHA256：`8d0068e0ff334dab61fbf0aef495755e0ca1fa09b6f0628b779ed45c0784996f`
- 规则原文：

> F. "Licensed Products" shall mean BlackMP Living Water, BlackMP Concentrate, Zezel Probiotic Water, Zayin Sports Water, Gridiron MVP™ and Gridiron MVP™ Concentrate using the Pro Football Legends Logo on the Licensed Products' affixed labels, hang-tags or packaging. Other products of the Company may be added to the list of Licensed Products during the Contract Period by written amendment to this Agreement. All amendments to this Agreement must be signed by all parties to this Agreement.

- 自动概括：A product is a Licensed Product if it is one of the six named products and uses the Pro Football Legends Logo on its affixed labels, hang-tags, or packaging; or if it is another product added to the Licensed Products list during the Contract Period by a written amendment signed by all parties.
- 模型指出的问题：The amendment branch omits the express requirement that an added product be a product of the Company. The source permits addition only of "Other products of the Company." None of the cases involving an other product states or codes that the product is a Company product.；The source makes the amendment route available only during the Contract Period. Although several case narratives mention the period, the predicate has no dedicated Contract-Period condition, and the coded added_by_written_amendment field does not expressly encode it.；Cases c07 and c13 evaluate true under the predicate without an explicit or coded Company-product fact, despite that being required by the source.；Cases c08 and c14 likewise lack the required Company-product fact; c14 also illustrates that the amendment-related facts are being evaluated without a complete representation of all express amendment-route conditions.；The source refers to "the Company" and the Contract Period, but the supplied excerpt does not define the Company or Contract Period. Those definitions/attachments are necessary to evaluate whether a particular other product is eligible for amendment-based addition.；The named-product branch is generally consistent with the quoted definition: each listed product must use the Pro Football Legends Logo on affixed labels, hang-tags, or packaging.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`c04`）：Zayin Sports Water is sold with the Pro Football Legends Logo on its affixed labels.
  - 按完整合同，它属于`Licensed Products`吗？`是/否/无法唯一判断`：
- 例2（`c08`）：A new energy drink is added to the Licensed Products list by a written amendment during the Contract Period, and all parties signed that amendment.
  - 按完整合同，它属于`Licensed Products`吗？`是/否/无法唯一判断`：
- 例3（`c09`）：BlackMP Living Water is sold without the Pro Football Legends Logo on its labels, hang-tags, or packaging.
  - 按完整合同，它属于`Licensed Products`吗？`是/否/无法唯一判断`：
- 例4（`c14`）：A new ginger ale is added to the Licensed Products list by a written amendment during the Contract Period, but not all parties signed that amendment, and it is sold with the Pro Football Legends Logo on its labels.
  - 按完整合同，它属于`Licensed Products`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:130:Affiliate

- 合同编号：`130`；[完整合同](contracts/ci130.txt)
- 来源组：`challenge_topup_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/topup_rule_program_proposals.jsonl`
- 程序SHA256：`8a75338d81f17ec68e99e1569b658dda45d5d1e77141096b74d3ef362c4533b6`
- 规则原文：

> 1.1 "Affiliate" means, when used with reference to a party, any individual or entity directly or indirectly Controlling, Controlled by or under common Control with such party.

- 自动概括：An Affiliate of a party is any individual or entity that directly or indirectly controls the party, is controlled by the party, or is under common control with the party. Membership requires both being an individual or entity and having at least one of those three control relationships.
- 模型指出的问题：The quoted Affiliate definition supports the predicate structure: individual-or-entity status is required and at least one of Controlling, Controlled by, or common Control must exist.；The incorporated definition of "Control" (identified as Section 1.3) is not provided. Therefore, the source does not establish the operative thresholds and rights that determine whether the coded control facts are true (including the referenced voting-securities and policy-decision criteria).；The meaning/scope of "individual or entity" is not separately defined in the supplied source, although the case texts expressly state the corresponding coded status.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`in_individual_controls_direct`）：Alice is a natural person who directly controls Party A.
  - 按完整合同，它属于`Affiliate`吗？`是/否/无法唯一判断`：
- 例2（`in_individual_common_control`）：Evan is an individual under common control with Party A.
  - 按完整合同，它属于`Affiliate`吗？`是/否/无法唯一判断`：
- 例3（`out_not_individual_no_control`）：An unincorporated association is not an individual or entity and has no control relationship to Party A.
  - 按完整合同，它属于`Affiliate`吗？`是/否/无法唯一判断`：
- 例4（`out_not_individual_controls_and_controlled`）：A statutory committee is not an individual or entity but both controls and is controlled by Party A.
  - 按完整合同，它属于`Affiliate`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:8:Know-How

- 合同编号：`8`；[完整合同](contracts/ci8.txt)
- 来源组：`challenge_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/rule_program_proposals.jsonl`
- 程序SHA256：`d0dd284b6015b13b1881c582cacc5a65e07d6114458b2ed5213d90802365468f`
- 规则原文：

> "Know-How" shall mean information, whether or not in written form, including biological, chemical, pharmacological, toxicological, medical or clinical, analytical, quality, manufacturing, research, or sales and marketing information, including processes, methods, procedures, techniques, plans, programs and data.

- 自动概括：An item is Know-How when it is information and either its category is one of the listed categories or its form is one of the listed forms.
- 模型指出的问题：The source defines Know-How as "information, whether or not in written form" and then uses "including" for listed subject-matter examples and forms. "Including" is non-exhaustive and does not make a listed category or form a necessary condition.；The predicate improperly excludes information that is neither in a listed category nor a listed form. The explicitly stated unlisted information in c14_financial_info and c15_legal_info therefore fails the proposed predicate despite falling within the source's general definition of information.；The source does not support treating the listed categories and forms as an exhaustive classification or requiring either list to be satisfied.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`c07_quality_program`）：A quality program is information; its category is quality and its form is program.
  - 按完整合同，它属于`Know-How`吗？`是/否/无法唯一判断`：
- 例2（`c05_sales_plan`）：A sales and marketing plan is information; its category is sales and marketing and its form is plan.
  - 按完整合同，它属于`Know-How`吗？`是/否/无法唯一判断`：
- 例3（`c15_legal_info`）：A legal argument is information; its category is unlisted and its form is unlisted.
  - 按完整合同，它属于`Know-How`吗？`是/否/无法唯一判断`：
- 例4（`c16_noninfo_procedure`）：A physical repair procedure is not information; its category is unlisted and its form is procedure.
  - 按完整合同，它属于`Know-How`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:48:Agent

- 合同编号：`48`；[完整合同](contracts/ci48.txt)
- 来源组：`challenge_topup_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/topup_rule_program_proposals_nonthinking.jsonl`
- 程序SHA256：`e4e76a84f8c545cbe4f58087228b9af0ed1a776acc976181893a2375921903ed`
- 规则原文：

> "Agent" means Midtown Madison Management LLC, as agent under the Loan Agreement.

- 自动概括：An entity is the Agent if and only if it is Midtown Madison Management LLC and its role is agent under the Loan Agreement.
- 模型指出的问题：out_6 states that Midtown Madison Management LLC is not the agent, but its coded role is borrower under the Loan Agreement; the coded fact is not stated in the case text.；out_7 states that Other LLC is not the agent, but its coded role is lender under the Loan Agreement; the coded fact is not stated in the case text.；The stated dependency on external factual identity/status is unnecessary for this definitional rule: the provided definition itself identifies Midtown Madison Management LLC as the Agent in its capacity as agent under the Loan Agreement.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`in_3`）：Midtown Madison Management LLC is designated agent under the Loan Agreement.
  - 按完整合同，它属于`Agent`吗？`是/否/无法唯一判断`：
- 例2（`in_2`）：The entity Midtown Madison Management LLC acts as agent under the Loan Agreement.
  - 按完整合同，它属于`Agent`吗？`是/否/无法唯一判断`：
- 例3（`out_6`）：Midtown Madison Management LLC is not the agent under the Loan Agreement.
  - 按完整合同，它属于`Agent`吗？`是/否/无法唯一判断`：
- 例4（`out_3`）：Other LLC is the agent under the Loan Agreement.
  - 按完整合同，它属于`Agent`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

## cuadfull:481:Contracts

- 合同编号：`481`；[完整合同](contracts/ci481.txt)
- 来源组：`challenge_candidate`；自动审查：`revise`
- 程序来源：`outputs/local_meaning_v5_development/formal_frame/rule_program_proposals_nonthinking.jsonl`
- 程序SHA256：`4d93459d7193268990586aadf3afd28ae634812b71364b377601bc00c2fbc557`
- 规则原文：

> For purposes of this Agreement, "Contracts" means all contracts, consulting agreements, leases, non-governmental licenses and other agreements (including leases for personal or real property and employment agreements), written or oral (including any amendments and other modifications thereto), to which WYZZ is a party or that are binding upon WYZZ and that relate to or effect the assets, properties, business, or operations of WYZZ-TV that are in effect as of the Effective Date.

- 自动概括：An item is a Contract if it is a contract, consulting agreement, lease, non-governmental license, or other agreement; it is written or oral; WYZZ is a party to it or it is binding upon WYZZ; it relates to or affects the assets, properties, business, or operations of WYZZ-TV; and it is in effect as of the Effective Date.
- 模型指出的问题：The predicate does not represent the source's express inclusion of "any amendments and other modifications thereto." Merely listing amendment/modification status as a dependency does not incorporate that inclusion into the Boolean rule.；The source says agreements that "relate to or effect" the specified WYZZ-TV interests, while the rule summary and field semantics substitute "affect." That may be an intended correction, but it is not an exact textual predicate without a defined equivalence or source correction.；For every listed fatal case, the fact text identifies one agreement category but does not expressly establish that all other category fields are false. The source categories can overlap; for example, a consulting agreement or lease may also be a contract. Therefore the coded negative category facts are unsupported by the case text.；The out_not_agreement case does expressly negate each enumerated agreement category, but the other cases do not. Their vectors should omit unsupported negative classifications, state them expressly, or use a data model that permits overlapping categories.

- ① 原文引文及其紧邻续句完整吗？`是/否/不确定`：
- ② 自动概括忠于原文吗？`是/否/不确定`：
- ③ 需补的附件、其他定义或事实是什么？无则填`无`：
- 例1（`in_lease_written`）：A written lease to which WYZZ is a party relates to the assets of WYZZ-TV and is in effect as of the Effective Date.
  - 按完整合同，它属于`Contracts`吗？`是/否/无法唯一判断`：
- 例2（`in_lease_oral_bound`）：An oral lease binding upon WYZZ relates to the operations of WYZZ-TV and is in effect as of the Effective Date.
  - 按完整合同，它属于`Contracts`吗？`是/否/无法唯一判断`：
- 例3（`out_not_agreement`）：A written document that is not a contract, consulting agreement, lease, non-governmental license, or other agreement is binding upon WYZZ, relates to the business of WYZZ-TV, and is in effect as of the Effective Date.
  - 按完整合同，它属于`Contracts`吗？`是/否/无法唯一判断`：
- 例4（`out_no_relation_to_wyzz_tv`）：A written contract to which WYZZ is a party is in effect as of the Effective Date, but it does not relate to or affect the assets, properties, business, or operations of WYZZ-TV.
  - 按完整合同，它属于`Contracts`吗？`是/否/无法唯一判断`：
- ④ 建议：`收录/待改/排除`，理由一句：

