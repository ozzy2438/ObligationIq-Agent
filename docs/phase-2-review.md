# Phase 2 — source review decisions

**32 records; 32 APPROVED (2 human, 30 authorised agent); 0 pending; 0 operational controls enabled.**

Approval means the requirement, trigger, action and timing match the cited authoritative text in the 12 September 2026 snapshot. It is not a customer-level legal determination, proof of every jurisdictional modification, or permission to disconnect/deregister. State lists identify source coverage; concrete applicability and calendar logic remain separate implementation gates.

The owner explicitly authorised autonomous source review after personally approving OIQ-024 and OIQ-025. Authorised agent approvals do not set verified_by_human=true. Every decision is bound to the reviewed candidate and source digests; changes require review again.

Candidate snapshot SHA-256: `effee735c19f466d1c53ad57cdaa77ef9d51113e0d86adb2f8d29335733434af`.

[Versioned candidates](../data/obligation-candidates.json) · [Human decisions](../data/human-reviews.json) · [Agent decision audit](../data/source-reviews.json) · [Consolidated review](review-summary.md)

<a id="oiq-001"></a>

## OIQ-001 — NERL_NERR / life support

**Trigger:** Customer advises that a person residing or intending to reside at the premises requires life support equipment.

**Action:** Register that a residing or intending resident requires life support equipment and record the date from which it is required.

**Timing:** No numerical deadline asserted.

**Source:** [National Energy Retail Rules, version 51, clause 124(1)(a)](https://aemc-dra-production-s3.s3.ap-southeast-2.amazonaws.com/rules/ee0c0f923d57687aba955f6f97a974077ed27515/assets/files/NERR%20-%20v51%20-%20Full.pdf#page=117); physical PDF pages 117–121.

**Proposed evidence:** customer_advice, registration_event, required_supply_date.

**Context and implementation notes:** No numerical registration deadline is asserted by this subclause. Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm local adoption and modifications for the selected state/territory; the core instrument alone does not establish jurisdictional applicability.

**Decision:** APPROVED — 2026-09-12; agent_source_review; reviewer: Codex (user-authorised source reviewer).

**Reasoning:** The 124(1) chapeau includes existing and intending residents; paragraph (a) requires registration and the equipment-required date without its own numerical deadline.

**Correction:** Restored the explicit resident/intending-resident scope and the equipment-required date from 124(1)(a).

<a id="oiq-002"></a>

## OIQ-002 — NERL_NERR / life support

**Trigger:** Retailer receives the customer advice described in rule 124(1).

**Action:** Within five business days provide the written information and medical-confirmation items in 124(1)(b)(i)-(ix). If all three conditions of 124(2) hold, only items (iii) and (vi) remain required under this paragraph.

**Timing:** at most 5 business days; anchor: customer advice received.

**Source:** [National Energy Retail Rules, version 51, clause 124(1)(b)](https://aemc-dra-production-s3.s3.ap-southeast-2.amazonaws.com/rules/ee0c0f923d57687aba955f6f97a974077ed27515/assets/files/NERR%20-%20v51%20-%20Full.pdf#page=117); physical PDF pages 117–121.

**Proposed evidence:** advice_received_at, package_version, package_sent_at, delivery_record.

**Context and implementation notes:** Rule 124(2) requires prior advice to the distributor, customer advice of prior medical confirmation, and retailer confirmation with that distributor. Items (iii) and (vi) remain required. This is a source-content approval; determine concrete customer/contract applicability and the applicable business-day calendar before control execution.

**Decision:** APPROVED — 2026-09-12; agent_source_review; reviewer: Codex (user-authorised source reviewer).

**Reasoning:** Paragraph 124(1)(b) sets an upper limit of five business days after customer advice. Its package and the all-conditions exception in 124(2) are explicit; items (iii) and (vi) survive that exception.

**Correction:** Made the 124(2) exception and its two retained information duties explicit instead of leaving the exception solely in a review note.

<a id="oiq-003"></a>

## OIQ-003 — NERL_NERR / life support

**Trigger:** Retailer provides a medical confirmation form under rule 124(1)(b)(i).

**Action:** Allow the customer the minimum confirmation period.

**Timing:** at least 50 business days; anchor: date of medical confirmation form.

**Source:** [National Energy Retail Rules, version 51, clause 124A(1)(a)](https://aemc-dra-production-s3.s3.ap-southeast-2.amazonaws.com/rules/ee0c0f923d57687aba955f6f97a974077ed27515/assets/files/NERR%20-%20v51%20-%20Full.pdf#page=121); physical PDF pages 121–121.

**Proposed evidence:** dated_medical_form, confirmation_due_date.

**Context and implementation notes:** Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm applicable business-day calendar and counting rule before any timing control. Confirm local adoption and modifications for the selected state/territory; the core instrument alone does not establish jurisdictional applicability.

**Decision:** APPROVED — 2026-09-12; agent_source_review; reviewer: Codex (user-authorised source reviewer).

**Reasoning:** Rule 124A(1)(a) gives at least 50 business days from the dated medical form, not a 50-day maximum.

**Correction:** Specified the retailer medical-form pathway from the chapeau of 124A(1); no timing value changed.

<a id="oiq-004"></a>

## OIQ-004 — NERL_NERR / life support

**Trigger:** Retailer provides a medical confirmation form under rule 124(1)(b)(i).

**Action:** Provide at least two written reminders.

**Timing:** No numerical deadline asserted.

**Source:** [National Energy Retail Rules, version 51, clause 124A(1)(b)](https://aemc-dra-production-s3.s3.ap-southeast-2.amazonaws.com/rules/ee0c0f923d57687aba955f6f97a974077ed27515/assets/files/NERR%20-%20v51%20-%20Full.pdf#page=121); physical PDF pages 121–121.

**Proposed evidence:** first_reminder, second_reminder, delivery_records.

**Context and implementation notes:** Read with timing, extension and confirmation-receipt provisions; reminder count alone does not authorise deregistration. Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm local adoption and modifications for the selected state/territory; the core instrument alone does not establish jurisdictional applicability.

**Decision:** APPROVED — 2026-09-12; agent_source_review; reviewer: Codex (user-authorised source reviewer).

**Reasoning:** Rule 124A(1)(b) expressly requires at least two written confirmation reminders. No separate numerical deadline is present in this paragraph.

**Correction:** Specified the 124A(1) form trigger; the two-notice minimum does not set a response deadline.

<a id="oiq-005"></a>

## OIQ-005 — NERL_NERR / life support

**Trigger:** The first medical-confirmation reminder is provided to the customer under rule 124A.

**Action:** Ensure the first reminder is provided no earlier than 15 business days from the medical form issue date.

**Timing:** at least 15 business days; anchor: medical form issue date.

**Source:** [National Energy Retail Rules, version 51, clause 124A(1)(c)](https://aemc-dra-production-s3.s3.ap-southeast-2.amazonaws.com/rules/ee0c0f923d57687aba955f6f97a974077ed27515/assets/files/NERR%20-%20v51%20-%20Full.pdf#page=121); physical PDF pages 121–121.

**Proposed evidence:** medical_form_issue_date, first_reminder_provided_at, delivery_record.

**Context and implementation notes:** Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm applicable business-day calendar and counting rule before any timing control. Confirm local adoption and modifications for the selected state/territory; the core instrument alone does not establish jurisdictional applicability.

**Decision:** APPROVED — 2026-09-12; agent_source_review; reviewer: Codex (user-authorised source reviewer).

**Reasoning:** Rule 124A(1)(c) measures first-reminder provision no earlier than 15 business days from form issue; provision and issue are distinct events.

**Correction:** Corrected the measured event from notice issue to notice provision: the source measures when the reminder is provided, while the interval begins on the earlier document issue date.

<a id="oiq-006"></a>

## OIQ-006 — NERL_NERR / life support

**Trigger:** The second medical-confirmation reminder is provided to the customer under rule 124A.

**Action:** Ensure the second reminder is provided no earlier than 15 business days from the first reminder issue date.

**Timing:** at least 15 business days; anchor: first reminder issue date.

**Source:** [National Energy Retail Rules, version 51, clause 124A(1)(d)](https://aemc-dra-production-s3.s3.ap-southeast-2.amazonaws.com/rules/ee0c0f923d57687aba955f6f97a974077ed27515/assets/files/NERR%20-%20v51%20-%20Full.pdf#page=121); physical PDF pages 121–121.

**Proposed evidence:** first_reminder_issue_date, second_reminder_provided_at, delivery_record.

**Context and implementation notes:** Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm applicable business-day calendar and counting rule before any timing control. Confirm local adoption and modifications for the selected state/territory; the core instrument alone does not establish jurisdictional applicability.

**Decision:** APPROVED — 2026-09-12; agent_source_review; reviewer: Codex (user-authorised source reviewer).

**Reasoning:** Rule 124A(1)(d) measures second-reminder provision no earlier than 15 business days from first-reminder issue.

**Correction:** Corrected the measured event from notice issue to notice provision: the source measures when the reminder is provided, while the interval begins on the earlier document issue date.

<a id="oiq-007"></a>

## OIQ-007 — NERL_NERR / life support

**Trigger:** Customer requests extra time for medical confirmation.

**Action:** Give at least one extension of the minimum duration.

**Timing:** at least 25 business days; anchor: extension duration.

**Source:** [National Energy Retail Rules, version 51, clause 124A(1)(e)](https://aemc-dra-production-s3.s3.ap-southeast-2.amazonaws.com/rules/ee0c0f923d57687aba955f6f97a974077ed27515/assets/files/NERR%20-%20v51%20-%20Full.pdf#page=121); physical PDF pages 121–121.

**Proposed evidence:** extension_request, extension_decision, original_and_revised_due_dates.

**Context and implementation notes:** This is an extension length, not a 25-day response deadline. Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm applicable business-day calendar and counting rule before any timing control. Confirm local adoption and modifications for the selected state/territory; the core instrument alone does not establish jurisdictional applicability.

**Decision:** APPROVED — 2026-09-12; agent_source_review; reviewer: Codex (user-authorised source reviewer).

**Reasoning:** Rule 124A(1)(e) requires at least one requested extension of at least 25 business days; the number is extension duration, not a response deadline.

**Correction:** None; requirement, trigger, action and timing match the cited source.

<a id="oiq-008"></a>

## OIQ-008 — NERL_NERR / life support

**Trigger:** Retailer has deregistered the premises under a permitted pathway.

**Action:** Notify the distributor of the deregistration date and reason.

**Timing:** at most 5 business days; anchor: retailer deregistration.

**Source:** [National Energy Retail Rules, version 51, clause 125(2)(a)](https://aemc-dra-production-s3.s3.ap-southeast-2.amazonaws.com/rules/ee0c0f923d57687aba955f6f97a974077ed27515/assets/files/NERR%20-%20v51%20-%20Full.pdf#page=124); physical PDF pages 124–127.

**Proposed evidence:** lawful_deregistration_review, deregistration_event, distributor_notification.

**Context and implementation notes:** This downstream notification requirement grants no permission to deregister or disconnect. Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm applicable business-day calendar and counting rule before any timing control. Confirm local adoption and modifications for the selected state/territory; the core instrument alone does not establish jurisdictional applicability.

**Decision:** APPROVED — 2026-09-12; agent_source_review; reviewer: Codex (user-authorised source reviewer).

**Reasoning:** Rule 125(2)(a) explicitly sets five business days after retailer deregistration for a distributor notice containing date and reason; it grants no permission to deregister.

**Correction:** None; requirement, trigger, action and timing match the cited source.

<a id="oiq-009"></a>

## OIQ-009 — NERL_NERR / life support

**Trigger:** Life support registration details or required communications change.

**Action:** Keep the required supply date, medical confirmation receipt, deregistration date/reason and communications required by rules 124A and 125 up to date.

**Timing:** No numerical deadline asserted.

**Source:** [National Energy Retail Rules, version 51, clause 126(b)](https://aemc-dra-production-s3.s3.ap-southeast-2.amazonaws.com/rules/ee0c0f923d57687aba955f6f97a974077ed27515/assets/files/NERR%20-%20v51%20-%20Full.pdf#page=127); physical PDF pages 127–128.

**Proposed evidence:** registration_history, confirmation_receipt, deregistration_history, communication_log.

**Context and implementation notes:** Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm local adoption and modifications for the selected state/territory; the core instrument alone does not establish jurisdictional applicability.

**Decision:** APPROVED — 2026-09-12; agent_source_review; reviewer: Codex (user-authorised source reviewer).

**Reasoning:** Rule 126(b)(i)-(iv) enumerates the four categories of current registration records; communication records are those under 124A and 125. It supplies no standalone numerical deadline.

**Correction:** Limited the communication component to the communications identified by 126(b)(iv), under rules 124A and 125.

<a id="oiq-010"></a>

## OIQ-010 — NERL_NERR / life support

**Trigger:** Medical confirmation is held for a registration specified in rule 126A.

**Action:** Keep a copy throughout the customer relationship for those premises and for the required period after it ends.

**Timing:** at least 110 business days; anchor: customer relationship for registered premises ends.

**Source:** [National Energy Retail Rules, version 51, clause 126A](https://aemc-dra-production-s3.s3.ap-southeast-2.amazonaws.com/rules/ee0c0f923d57687aba955f6f97a974077ed27515/assets/files/NERR%20-%20v51%20-%20Full.pdf#page=128); physical PDF pages 128–129.

**Proposed evidence:** confirmation_copy_reference, customer_tenure, retention_metadata.

**Context and implementation notes:** Retention applies during tenure as well; this is not a command to delete on day 110. Do not store medical content in this public register. Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm applicable business-day calendar and counting rule before any timing control. Confirm local adoption and modifications for the selected state/territory; the core instrument alone does not establish jurisdictional applicability.

**Decision:** APPROVED — 2026-09-12; agent_source_review; reviewer: Codex (user-authorised source reviewer).

**Reasoning:** Rule 126A(a)-(d) requires the medical confirmation copy during the customer relationship for those premises and for 110 business days after it ends. The record states a retention obligation, not automatic deletion.

**Correction:** None; requirement, trigger, action and timing match the cited source.

<a id="oiq-011"></a>

## OIQ-011 — NERL_NERR / hardship

**Trigger:** A hardship customer payment plan is being established.

**Action:** Account for capacity to pay, arrears and expected energy needs over the next 12 months.

**Timing:** No numerical deadline asserted.

**Source:** [National Energy Retail Rules, version 51, clause 72(1)(a)](https://aemc-dra-production-s3.s3.ap-southeast-2.amazonaws.com/rules/ee0c0f923d57687aba955f6f97a974077ed27515/assets/files/NERR%20-%20v51%20-%20Full.pdf#page=82); physical PDF pages 82–83.

**Proposed evidence:** capacity_assessment, arrears_snapshot, consumption_forecast, plan_calculation.

**Context and implementation notes:** Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm local adoption and modifications for the selected state/territory; the core instrument alone does not establish jurisdictional applicability.

**Decision:** APPROVED — 2026-09-12; agent_source_review; reviewer: Codex (user-authorised source reviewer).

**Reasoning:** Rule 72(1)(a)(i)-(iii) lists capacity, arrears and expected 12-month energy needs. The candidate covers the hardship-customer limb; rule 33(4) also applies rule 72 to specified other residential customers.

**Correction:** Replaced the generic licensed-retailer label with the instrument-neutral electricity-retailer description; this record does not establish a licence or authorisation.

<a id="oiq-012"></a>

## OIQ-012 — NERL_NERR / hardship

**Trigger:** A payment plan is established for a hardship customer.

**Action:** Offer instalments for energy consumption in advance or in arrears.

**Timing:** No numerical deadline asserted.

**Source:** [National Energy Retail Rules, version 51, clause 72(1)(b)](https://aemc-dra-production-s3.s3.ap-southeast-2.amazonaws.com/rules/ee0c0f923d57687aba955f6f97a974077ed27515/assets/files/NERR%20-%20v51%20-%20Full.pdf#page=82); physical PDF pages 82–83.

**Proposed evidence:** options_presented, customer_selection, payment_plan.

**Context and implementation notes:** Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm local adoption and modifications for the selected state/territory; the core instrument alone does not establish jurisdictional applicability.

**Decision:** APPROVED — 2026-09-12; agent_source_review; reviewer: Codex (user-authorised source reviewer).

**Reasoning:** Rule 72(1)(b) expressly includes an offer of consumption instalments in advance or arrears. The candidate covers the hardship limb and does not assert this is the only customer group protected by rule 72.

**Correction:** Replaced the generic licensed-retailer label with the instrument-neutral electricity-retailer description; this record does not establish a licence or authorisation.

<a id="oiq-013"></a>

## OIQ-013 — NERL_NERR / hardship

**Trigger:** Retailer offers a payment plan under rule 72, including its application through rule 33(4).

**Action:** Inform the customer of plan duration, each instalment amount/frequency/due date, the number of instalments to clear arrears if in arrears, and the calculation basis if paying in advance.

**Timing:** No numerical deadline asserted.

**Source:** [National Energy Retail Rules, version 51, clause 72(2)](https://aemc-dra-production-s3.s3.ap-southeast-2.amazonaws.com/rules/ee0c0f923d57687aba955f6f97a974077ed27515/assets/files/NERR%20-%20v51%20-%20Full.pdf#page=82); physical PDF pages 82–83.

**Proposed evidence:** plan_schedule, customer_information, calculation_basis.

**Context and implementation notes:** Subclauses 72(2)(c) and (d) depend on whether payments are in arrears or in advance. Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm local adoption and modifications for the selected state/territory; the core instrument alone does not establish jurisdictional applicability.

**Decision:** APPROVED — 2026-09-12; agent_source_review; reviewer: Codex (user-authorised source reviewer).

**Reasoning:** Rule 72(2) attaches the information duty to the retailer offering a plan; its arrears and advance-payment items are conditional, not universally cumulative.

**Correction:** Replaced a circular information-giving trigger with the actual rule 72(2) trigger: the retailer offers a payment plan. Replaced the generic licensed-retailer label with the instrument-neutral electricity-retailer description; this record does not establish a licence or authorisation.

<a id="oiq-014"></a>

## OIQ-014 — NERL_NERR / hardship

**Trigger:** It appears that a residential customer has not paid because of hardship-related payment difficulties.

**Action:** Inform the customer about the retailer hardship policy in accordance with the Rules.

**Timing:** No numerical deadline asserted.

**Source:** [National Energy Retail Law (South Australia) Act 2011, Schedule: National Energy Retail Law, version 18 December 2025 consolidation, clause 46](https://legislation.sa.gov.au/_legislation-documents/lz/c/a/national-energy-retail-law-south-australia-act-2011/current/2011.6.auth.pdf#page=61); physical PDF pages 61–61.

**Proposed evidence:** hardship_indicator, policy_version, communication_record.

**Context and implementation notes:** Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm local adoption and modifications for the selected state/territory; the core instrument alone does not establish jurisdictional applicability.

**Decision:** APPROVED — 2026-09-12; agent_source_review; reviewer: Codex (user-authorised source reviewer).

**Reasoning:** Section 46 ties the policy-information duty to the retailer apparent hardship-related reason for non-payment and expressly requires compliance with the Rules. No numerical deadline is specified.

**Correction:** Replaced the generic licensed-retailer label with the instrument-neutral electricity-retailer description; this record does not establish a licence or authorisation.

<a id="oiq-015"></a>

## OIQ-015 — NERL_NERR / hardship

**Trigger:** Customer is a hardship customer, reports payment difficulties in writing or by telephone, or the retailer believes they repeatedly struggle to pay or require payment assistance.

**Action:** Offer and apply a payment plan in accordance with section 50 and applicable Rules. Assess the rule 33(2) exceptions and affected-customer proviso before treating the offer as excused.

**Timing:** No numerical deadline asserted.

**Source:** [National Energy Retail Law (South Australia) Act 2011, Schedule: National Energy Retail Law, version 18 December 2025 consolidation, clause 50(1)-(2)](https://legislation.sa.gov.au/_legislation-documents/lz/c/a/national-energy-retail-law-south-australia-act-2011/current/2011.6.auth.pdf#page=62); physical PDF pages 62–62.

**Proposed evidence:** trigger_evidence, plan_offer, plan_application, exception_assessment.

**Context and implementation notes:** For customers within rule 33(1), rule 33(2) concerns two plans cancelled for non-payment in the previous 12 months or an illegal-energy-use conviction in the previous two years; its affected-customer/joint-or-several-responsibility proviso must also be applied. The rule 33(2) exception is not a blanket exception for every customer identified in section 50(1)(b). Its own scope must be established. A recorded belief, conviction or affected-customer status needs actual evidence; this review does not establish those customer facts.

**Decision:** APPROVED — 2026-09-12; agent_source_review; reviewer: Codex (user-authorised source reviewer).

**Reasoning:** Section 50(1)-(2) provides the offer/apply duty, eligible trigger alternatives and Rules qualification. Rule 33(1)-(2) supplies scoped exceptions, including a proviso for affected customers; the correction retains those conditions rather than creating an automatic refusal rule.

**Correction:** Expanded the statutory trigger and documented the rule 33(2) exceptions, including its affected-customer proviso; no deadline invented. Replaced the generic licensed-retailer label with the instrument-neutral electricity-retailer description; this record does not establish a licence or authorisation.

<a id="oiq-016"></a>

## OIQ-016 — VIC / life support

**Trigger:** Medical confirmation form is provided.

**Action:** Allow the minimum medical-confirmation period.

**Timing:** at least 50 business days; anchor: date of medical confirmation form.

**Source:** [Energy Retail Code of Practice, version 6, clause 164(1)(a)](https://www.esc.vic.gov.au/sites/default/files/documents/Energy%20Retail%20Code%20of%20Practice%20%28version%206%29_2.pdf#page=116); physical PDF pages 116–117.

**Proposed evidence:** dated_medical_form, confirmation_due_date.

**Context and implementation notes:** Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm applicable business-day calendar and counting rule before any timing control. Confirm residential electricity scope under the Code and any Electricity Industry Act cross-references; exempt sellers and gas are excluded from this pilot.

**Decision:** APPROVED — 2026-09-12; agent_source_review; reviewer: Codex (user-authorised source reviewer).

**Reasoning:** Clause 164(1)(a) gives a relevant customer at least 50 business days from the medical-form date. Its minimum direction and trigger match.

**Correction:** None; requirement, trigger, action and timing match the cited source.

<a id="oiq-017"></a>

## OIQ-017 — VIC / life support

**Trigger:** The first medical-confirmation reminder is provided to the customer under clause 164.

**Action:** Ensure the first reminder is provided no earlier than 15 business days from the medical form issue date.

**Timing:** at least 15 business days; anchor: medical form issue date.

**Source:** [Energy Retail Code of Practice, version 6, clause 164(1)(c)](https://www.esc.vic.gov.au/sites/default/files/documents/Energy%20Retail%20Code%20of%20Practice%20%28version%206%29_2.pdf#page=116); physical PDF pages 116–117.

**Proposed evidence:** medical_form_issue_date, first_reminder_provided_at, delivery_record.

**Context and implementation notes:** Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm applicable business-day calendar and counting rule before any timing control. Confirm residential electricity scope under the Code and any Electricity Industry Act cross-references; exempt sellers and gas are excluded from this pilot.

**Decision:** APPROVED — 2026-09-12; agent_source_review; reviewer: Codex (user-authorised source reviewer).

**Reasoning:** Clause 164(1)(c) concerns provision of the first reminder no earlier than 15 business days after form issue, not the first reminder issue date alone.

**Correction:** Corrected the measured event from notice issue to notice provision: the source measures when the reminder is provided, while the interval begins on the earlier document issue date.

<a id="oiq-018"></a>

## OIQ-018 — VIC / life support

**Trigger:** The second medical-confirmation reminder is provided to the customer under clause 164.

**Action:** Ensure the second reminder is provided no earlier than 15 business days from the first reminder issue date.

**Timing:** at least 15 business days; anchor: first reminder issue date.

**Source:** [Energy Retail Code of Practice, version 6, clause 164(1)(d)](https://www.esc.vic.gov.au/sites/default/files/documents/Energy%20Retail%20Code%20of%20Practice%20%28version%206%29_2.pdf#page=116); physical PDF pages 116–117.

**Proposed evidence:** first_reminder_issue_date, second_reminder_provided_at, delivery_record.

**Context and implementation notes:** Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm applicable business-day calendar and counting rule before any timing control. Confirm residential electricity scope under the Code and any Electricity Industry Act cross-references; exempt sellers and gas are excluded from this pilot.

**Decision:** APPROVED — 2026-09-12; agent_source_review; reviewer: Codex (user-authorised source reviewer).

**Reasoning:** Clause 164(1)(d) concerns provision of the second reminder no earlier than 15 business days after first-reminder issue.

**Correction:** Corrected the measured event from notice issue to notice provision: the source measures when the reminder is provided, while the interval begins on the earlier document issue date.

<a id="oiq-019"></a>

## OIQ-019 — VIC / life support

**Trigger:** Customer requests a medical-confirmation extension.

**Action:** Give at least one extension of the minimum duration.

**Timing:** at least 25 business days; anchor: extension duration.

**Source:** [Energy Retail Code of Practice, version 6, clause 164(1)(e)](https://www.esc.vic.gov.au/sites/default/files/documents/Energy%20Retail%20Code%20of%20Practice%20%28version%206%29_2.pdf#page=116); physical PDF pages 116–117.

**Proposed evidence:** extension_request, original_and_revised_due_dates.

**Context and implementation notes:** Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm applicable business-day calendar and counting rule before any timing control. Confirm residential electricity scope under the Code and any Electricity Industry Act cross-references; exempt sellers and gas are excluded from this pilot.

**Decision:** APPROVED — 2026-09-12; agent_source_review; reviewer: Codex (user-authorised source reviewer).

**Reasoning:** Clause 164(1)(e) mandates at least one requested extension lasting at least 25 business days; no response deadline is inferred.

**Correction:** None; requirement, trigger, action and timing match the cited source.

<a id="oiq-020"></a>

## OIQ-020 — VIC / life support

**Trigger:** Medical confirmation is sought under clause 164.

**Action:** Provide at least two written confirmation reminders.

**Timing:** No numerical deadline asserted.

**Source:** [Energy Retail Code of Practice, version 6, clause 164(1)(b)](https://www.esc.vic.gov.au/sites/default/files/documents/Energy%20Retail%20Code%20of%20Practice%20%28version%206%29_2.pdf#page=116); physical PDF pages 116–117.

**Proposed evidence:** first_reminder, second_reminder, delivery_records.

**Context and implementation notes:** Apply the remaining timing and content rules; two reminders are not permission to deregister. Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm residential electricity scope under the Code and any Electricity Industry Act cross-references; exempt sellers and gas are excluded from this pilot.

**Decision:** APPROVED — 2026-09-12; agent_source_review; reviewer: Codex (user-authorised source reviewer).

**Reasoning:** Clause 164(1)(b) requires at least two written confirmation reminders. Timing and required content are separate subclauses, not an authority to deregister.

**Correction:** None; requirement, trigger, action and timing match the cited source.

<a id="oiq-021"></a>

## OIQ-021 — VIC / life support

**Trigger:** Relevant life support or contact information is received for an electricity registration under section 40SG(1) or 40SH(1).

**Action:** Within one business day send relevant life support information, including medical confirmation, or contact-detail updates to the distributor unless that information was received from the distributor.

**Timing:** at most 1 business day; anchor: relevant information received.

**Source:** [Energy Retail Code of Practice, version 6, clause 165(1)(a)](https://www.esc.vic.gov.au/sites/default/files/documents/Energy%20Retail%20Code%20of%20Practice%20%28version%206%29_2.pdf#page=117); physical PDF pages 117–117.

**Proposed evidence:** registration_pathway, information_received_at, information_origin, distributor_notification.

**Context and implementation notes:** Electricity Industry Act 2000 version 107, sections 40SG(1) and 40SH(1), establish the customer/advised-by-distributor registration pathways. Supplemental source metadata is in data/review-sources.json. This candidate covers the retailer duty in 165(1), not the exempt-seller pathway in 165(2) or the distributor own-register duties.

**Decision:** APPROVED — 2026-09-12; agent_source_review; reviewer: Codex (user-authorised source reviewer).

**Reasoning:** Clause 165(1)(a) imposes one business day after receipt, includes medical confirmation and excludes distributor-origin information. The cited Act version 107 confirms the 40SG(1)/40SH(1) registration pathways.

**Correction:** Made inclusion of medical confirmation explicit and resolved the Act registration-pathway dependency using authorised Act version 107, sections 40SG(1) and 40SH(1).

<a id="oiq-022"></a>

## OIQ-022 — VIC / life support

**Trigger:** A relevant customer or distributor advises updated life support requirements or contact details for a registration under Electricity Industry Act section 40SG(1) or 40SH(1).

**Action:** Update the retailer life support register.

**Timing:** at most 1 business day; anchor: update advice received.

**Source:** [Energy Retail Code of Practice, version 6, clause 165(1)(b)](https://www.esc.vic.gov.au/sites/default/files/documents/Energy%20Retail%20Code%20of%20Practice%20%28version%206%29_2.pdf#page=117); physical PDF pages 117–117.

**Proposed evidence:** registration_pathway, update_advice_received_at, register_update.

**Context and implementation notes:** Act sections 40SG(1) and 40SH(1) checked against authorised version 107; retain evidence of the actual registration pathway. The separate exempt-seller pathway in clause 165(2) is outside this candidate.

**Decision:** APPROVED — 2026-09-12; agent_source_review; reviewer: Codex (user-authorised source reviewer).

**Reasoning:** Clause 165(1)(b) sets one business day after update advice from the relevant customer or distributor to update the register. Act registration pathways were checked; no distributor-origin exemption is imported from paragraph (a).

**Correction:** Made the customer/distributor update trigger and Act registration pathways explicit after checking the cited Act.

<a id="oiq-023"></a>

## OIQ-023 — VIC / life support

**Trigger:** Retailer has deregistered a customer through a permitted pathway.

**Action:** Notify the distributor of the date and reason.

**Timing:** at most 5 business days; anchor: retailer deregistration.

**Source:** [Energy Retail Code of Practice, version 6, clause 166(2)(a)](https://www.esc.vic.gov.au/sites/default/files/documents/Energy%20Retail%20Code%20of%20Practice%20%28version%206%29_2.pdf#page=117); physical PDF pages 117–120.

**Proposed evidence:** lawful_deregistration_review, deregistration_event, distributor_notification.

**Context and implementation notes:** Notification timing does not establish that the deregistration was lawful. Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm applicable business-day calendar and counting rule before any timing control. Confirm residential electricity scope under the Code and any Electricity Industry Act cross-references; exempt sellers and gas are excluded from this pilot.

**Decision:** APPROVED — 2026-09-12; agent_source_review; reviewer: Codex (user-authorised source reviewer).

**Reasoning:** Clause 166(2)(a) requires a retailer that deregisters a customer to send the distributor the deregistration date and reason within five business days. This is separate from the one-day register update in paragraph (b).

**Correction:** None; requirement, trigger, action and timing match the cited source.

<a id="oiq-024"></a>

## OIQ-024 — VIC / life support

**Trigger:** Retailer has deregistered a customer through a permitted pathway.

**Action:** Update its life support register.

**Timing:** at most 1 business day; anchor: retailer deregistration.

**Source:** [Energy Retail Code of Practice, version 6, clause 166(2)(b)](https://www.esc.vic.gov.au/sites/default/files/documents/Energy%20Retail%20Code%20of%20Practice%20%28version%206%29_2.pdf#page=117); physical PDF pages 117–120.

**Proposed evidence:** deregistration_event, register_update.

**Context and implementation notes:** This is recording a completed event, not permission to deregister or disconnect. Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm applicable business-day calendar and counting rule before any timing control. Confirm residential electricity scope under the Code and any Electricity Industry Act cross-references; exempt sellers and gas are excluded from this pilot.

**Decision:** APPROVED — 2026-09-12; human_content_review; reviewer: Osman Orka (project owner).

**Reasoning:** Explicit human approval in the project conversation: OIQ-024 review completed, APPROVED. Reviewer confirmed clause 166(2)(b) requires the register update within one business day after retailer deregistration, with clause 166(2)(a) and clause 167 as context. The same message expressly withholds approval of OIQ-025.

**Correction:** None; explicit human approval of the bound draft.

<a id="oiq-025"></a>

## OIQ-025 — VIC / life support

**Trigger:** Life support registration details or required communications change.

**Action:** Keep required supply dates, medical confirmation receipt, deregistration dates/reasons and communications required by clauses 164 and 166 current in the life support customer/resident register.

**Timing:** No numerical deadline asserted.

**Source:** [Energy Retail Code of Practice, version 6, clause 167(1)(b)](https://www.esc.vic.gov.au/sites/default/files/documents/Energy%20Retail%20Code%20of%20Practice%20%28version%206%29_2.pdf#page=120); physical PDF pages 120–120.

**Proposed evidence:** registration_history, confirmation_receipt, deregistration_history, communication_log.

**Context and implementation notes:** Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm residential electricity scope under the Code and any Electricity Industry Act cross-references; exempt sellers and gas are excluded from this pilot. Clause 167 sets no standalone numerical deadline; do not apply the separate 166(2)(b) deregistration-update deadline to every record change.

**Decision:** APPROVED — 2026-09-12; human_content_review; reviewer: Osman Orka (project owner).

**Reasoning:** Explicit user decision in the project conversation: OIQ-025 APPROVED; record the decision and update the verification flag/date. Approval applies to the clarified clause 167(1)(b) candidate, including communications under clauses 164 and 166.

**Correction:** None; explicit human approval of the bound draft.

<a id="oiq-026"></a>

## OIQ-026 — VIC / hardship

**Trigger:** Retailer offers standard assistance under clause 125.

**Action:** Make available at least three of: equal payments over a specified period; different payment intervals; a specified pay-by-date extension for at least one billing cycle in any 12 months; advance payment for energy use.

**Timing:** No numerical deadline asserted.

**Source:** [Energy Retail Code of Practice, version 6, clause 125(2)](https://www.esc.vic.gov.au/sites/default/files/documents/Energy%20Retail%20Code%20of%20Practice%20%28version%206%29_2.pdf#page=99); physical PDF pages 99–99.

**Proposed evidence:** assistance_offer_catalogue, option_mapping.

**Context and implementation notes:** The retailer elects the standard-assistance forms under 125(1), subject to the three-of-four minimum in 125(2). The source does not say the pay-by-date extension must itself last an entire billing cycle. No numerical extension length is asserted.

**Decision:** APPROVED — 2026-09-12; agent_source_review; reviewer: Codex (user-authorised source reviewer).

**Reasoning:** Clause 125(2) requires three of four listed forms. Clause 125(1) places election with the retailer. Paragraph (2)(c) specifies a pay-by extension for at least one billing cycle in 12 months, not an extension lasting a full billing cycle.

**Correction:** Corrected the review note: under clause 125(1) the retailer elects which forms to make available, not the customer. Enumerated the four options without inventing an extension length.

<a id="oiq-027"></a>

## OIQ-027 — VIC / hardship

**Trigger:** A residential customer cannot pay the full cost of ongoing energy use.

**Action:** Provide the applicable initial arrears hold and reduced ongoing-payment assistance for at least six months while energy costs are reduced.

**Timing:** at least 6 months; anchor: initial assistance period starts.

**Source:** [Energy Retail Code of Practice, version 6, clause 128(1)(g), (3)-(5)](https://www.esc.vic.gov.au/sites/default/files/documents/Energy%20Retail%20Code%20of%20Practice%20%28version%206%29_2.pdf#page=99); physical PDF pages 99–101.

**Proposed evidence:** ongoing_affordability_assessment, arrears_hold, assistance_start_and_end, cost_reduction_support.

**Context and implementation notes:** Six months is a minimum initial assistance period, not a maximum repayment-plan term. Apply eligibility and interaction with clauses 130 and 131. Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm residential electricity scope under the Code and any Electricity Industry Act cross-references; exempt sellers and gas are excluded from this pilot.

**Decision:** APPROVED — 2026-09-12; agent_source_review; reviewer: Codex (user-authorised source reviewer).

**Reasoning:** Clause 128(3) entitles customers unable to pay full ongoing use to measures (1)(c)-(g). Paragraph (g) gives an initial period of at least six months combining an arrears hold with payment below ongoing costs while lowering them. Paragraphs (4)-(5) describe extension and transition; this is not a maximum plan duration.

**Correction:** None; requirement, trigger, action and timing match the cited source.

<a id="oiq-028"></a>

## OIQ-028 — VIC / hardship

**Trigger:** A residential customer misses the pay-by date and arrears exceed AUD 55 inclusive of GST.

**Action:** Contact the customer with assistance entitlement and access information.

**Timing:** at most 21 business days; anchor: bill pay-by date.

**Source:** [Energy Retail Code of Practice, version 6, clause 129(2)](https://www.esc.vic.gov.au/sites/default/files/documents/Energy%20Retail%20Code%20of%20Practice%20%28version%206%29_2.pdf#page=101); physical PDF pages 101–102.

**Proposed evidence:** bill_pay_by_date, arrears_including_gst, contact_attempt_and_delivery, assistance_information.

**Context and implementation notes:** Threshold is strictly greater than 55 AUD, not greater than or equal to 55. Check evidence of contact. Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm applicable business-day calendar and counting rule before any timing control. Confirm residential electricity scope under the Code and any Electricity Industry Act cross-references; exempt sellers and gas are excluded from this pilot.

**Decision:** APPROVED — 2026-09-12; agent_source_review; reviewer: Codex (user-authorised source reviewer).

**Reasoning:** Clause 129(2) uses arrears strictly greater than AUD 55 including GST and contact/information within 21 business days after the pay-by date. Equality at 55 is not the stated trigger.

**Correction:** None; requirement, trigger, action and timing match the cited source.

<a id="oiq-029"></a>

## OIQ-029 — VIC / hardship

**Trigger:** Information is provided under clause 129(1) or (2).

**Action:** Allow the customer the minimum period to consider it, seek more information and propose payments.

**Timing:** at least 6 business days; anchor: assistance information provided.

**Source:** [Energy Retail Code of Practice, version 6, clause 129(3)](https://www.esc.vic.gov.au/sites/default/files/documents/Energy%20Retail%20Code%20of%20Practice%20%28version%206%29_2.pdf#page=101); physical PDF pages 101–102.

**Proposed evidence:** information_provided_at, consideration_window, proposal_record.

**Context and implementation notes:** Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm applicable business-day calendar and counting rule before any timing control. Confirm residential electricity scope under the Code and any Electricity Industry Act cross-references; exempt sellers and gas are excluded from this pilot.

**Decision:** APPROVED — 2026-09-12; agent_source_review; reviewer: Codex (user-authorised source reviewer).

**Reasoning:** Clause 129(3) allows at least six business days after information under (1) or (2) for consideration, further information and a clause 130 proposal. It is a protected minimum window.

**Correction:** None; requirement, trigger, action and timing match the cited source.

<a id="oiq-030"></a>

## OIQ-030 — VIC / hardship

**Trigger:** Retailer accepts a payment proposal or revision under clause 130 for a residential customer whose arrears repayment is not on hold under 128(1)(g)(i).

**Action:** Give a written schedule stating total payment count, period, due dates and amounts.

**Timing:** No numerical deadline asserted.

**Source:** [Energy Retail Code of Practice, version 6, clause 130(5)](https://www.esc.vic.gov.au/sites/default/files/documents/Energy%20Retail%20Code%20of%20Practice%20%28version%206%29_2.pdf#page=102); physical PDF pages 102–103.

**Proposed evidence:** accepted_proposal, written_schedule, delivery_record.

**Context and implementation notes:** Clause 130(1) excludes customers whose arrears are on hold under 128(1)(g)(i). Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm residential electricity scope under the Code and any Electricity Industry Act cross-references; exempt sellers and gas are excluded from this pilot.

**Decision:** APPROVED — 2026-09-12; agent_source_review; reviewer: Codex (user-authorised source reviewer).

**Reasoning:** Clause 130(5) requires the written count, period, due dates and amounts on accepting a proposal. Clause 130(1) excludes arrears-on-hold customers; the corrected trigger preserves it.

**Correction:** Moved the clause 130(1) exclusion into the trigger so an arrears-on-hold customer cannot be treated as eligible solely from an accepted proposal.

<a id="oiq-031"></a>

## OIQ-031 — VIC / hardship

**Trigger:** A residential customer receiving assistance under this Division, whose arrears repayment is not on hold under 128(1)(g)(i), misses a payment by its due date.

**Action:** Contact the customer to discuss a revised payment proposal.

**Timing:** No numerical deadline asserted.

**Source:** [Energy Retail Code of Practice, version 6, clause 130(6)](https://www.esc.vic.gov.au/sites/default/files/documents/Energy%20Retail%20Code%20of%20Practice%20%28version%206%29_2.pdf#page=102); physical PDF pages 102–103.

**Proposed evidence:** applicable_plan, missed_payment, contact_record.

**Context and implementation notes:** Read scope in 130(1); clause 131 addresses the different arrears-on-hold pathway. No numerical contact deadline is asserted here. Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm residential electricity scope under the Code and any Electricity Industry Act cross-references; exempt sellers and gas are excluded from this pilot.

**Decision:** APPROVED — 2026-09-12; agent_source_review; reviewer: Codex (user-authorised source reviewer).

**Reasoning:** Clause 130(6) requires contact to discuss a revised proposal after a missed payment. The clause 130(1) scope applies, while clause 131 supplies the distinct on-hold pathway; no contact deadline is invented.

**Correction:** Moved the clause 130(1) arrears-hold exclusion into the trigger and retained the different clause 131 pathway.

<a id="oiq-032"></a>

## OIQ-032 — VIC / hardship

**Trigger:** Any residential customer asks to be sent a copy of the retailer financial hardship policy.

**Action:** Send a copy of the policy.

**Timing:** No numerical deadline asserted.

**Source:** [Energy Retail Code of Practice, version 6, clause 138(2)](https://www.esc.vic.gov.au/sites/default/files/documents/Energy%20Retail%20Code%20of%20Practice%20%28version%206%29_2.pdf#page=105); physical PDF pages 105–106.

**Proposed evidence:** policy_request, policy_version, copy_sent.

**Context and implementation notes:** Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm residential electricity scope under the Code and any Electricity Industry Act cross-references; exempt sellers and gas are excluded from this pilot.

**Decision:** APPROVED — 2026-09-12; agent_source_review; reviewer: Codex (user-authorised source reviewer).

**Reasoning:** Clause 138(2) requires sending the policy to any residential customer asking for a copy. It does not limit the right to enrolled hardship customers or give a numerical deadline.

**Correction:** Restored the clause 138(2) scope: any residential customer requesting a copy, not only customers already experiencing hardship.
