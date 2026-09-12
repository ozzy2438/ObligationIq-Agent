# Phase 2 — human review required

**32 candidates; 0 human approvals; 0 records eligible for controls.**

These are paraphrases for review, not legal conclusions. The linked PDF opens at the physical page containing the parent clause; read the full subclause and its exceptions. Jurisdictional applicability is still pending. This pack does not authorise disconnection or deregistration.

For each record, confirm or correct its trigger, action, timing direction, exceptions, jurisdiction and proposed evidence. Report the obligation ID and corrections; approval must identify the reviewer and date and bind the reviewed content. A source-trace check alone is not approval. No blanket approval is inferred from continuing the build.

Candidate snapshot SHA-256: `a25758efaec3d40df8af2368f2475589ff62aad0ee67dc49bea5776908979d17`.

[Machine-readable records](../data/obligation-candidates.json) · [Implementation and outstanding gates](phase-2-register.md)

## OIQ-001 — NERL_NERR / life support

**Trigger:** Customer advises that a person at the premises needs life support equipment.

**Action:** Register the premises and the date energy supply is required for the equipment.

**Timing:** No numerical deadline asserted.

**Source:** [National Energy Retail Rules, version 51, clause 124(1)(a)](https://aemc-dra-production-s3.s3.ap-southeast-2.amazonaws.com/rules/ee0c0f923d57687aba955f6f97a974077ed27515/assets/files/NERR%20-%20v51%20-%20Full.pdf#page=117); physical PDF pages 117–121.

**Proposed evidence:** customer_advice, registration_event, required_supply_date.

**Review checks:** No numerical registration deadline is asserted by this subclause. Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm local adoption and modifications for the selected state/territory; the core instrument alone does not establish jurisdictional applicability.

**Human decision:** PENDING.

## OIQ-002 — NERL_NERR / life support

**Trigger:** Retailer receives the customer advice described in rule 124(1).

**Action:** Provide the prescribed written information and medical-confirmation package.

**Timing:** at most 5 business days; anchor: customer advice received.

**Source:** [National Energy Retail Rules, version 51, clause 124(1)(b)](https://aemc-dra-production-s3.s3.ap-southeast-2.amazonaws.com/rules/ee0c0f923d57687aba955f6f97a974077ed27515/assets/files/NERR%20-%20v51%20-%20Full.pdf#page=117); physical PDF pages 117–121.

**Proposed evidence:** advice_received_at, package_version, package_sent_at, delivery_record.

**Review checks:** Apply rule 124(2) only when all its conditions are met; specified information remains required. Review every item in 124(1)(b). Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm applicable business-day calendar and counting rule before any timing control. Confirm local adoption and modifications for the selected state/territory; the core instrument alone does not establish jurisdictional applicability.

**Human decision:** PENDING.

## OIQ-003 — NERL_NERR / life support

**Trigger:** Medical confirmation form is provided.

**Action:** Allow the customer the minimum confirmation period.

**Timing:** at least 50 business days; anchor: date of medical confirmation form.

**Source:** [National Energy Retail Rules, version 51, clause 124A(1)(a)](https://aemc-dra-production-s3.s3.ap-southeast-2.amazonaws.com/rules/ee0c0f923d57687aba955f6f97a974077ed27515/assets/files/NERR%20-%20v51%20-%20Full.pdf#page=121); physical PDF pages 121–121.

**Proposed evidence:** dated_medical_form, confirmation_due_date.

**Review checks:** Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm applicable business-day calendar and counting rule before any timing control. Confirm local adoption and modifications for the selected state/territory; the core instrument alone does not establish jurisdictional applicability.

**Human decision:** PENDING.

## OIQ-004 — NERL_NERR / life support

**Trigger:** Medical confirmation is sought under rule 124A.

**Action:** Provide at least two written reminders.

**Timing:** No numerical deadline asserted.

**Source:** [National Energy Retail Rules, version 51, clause 124A(1)(b)](https://aemc-dra-production-s3.s3.ap-southeast-2.amazonaws.com/rules/ee0c0f923d57687aba955f6f97a974077ed27515/assets/files/NERR%20-%20v51%20-%20Full.pdf#page=121); physical PDF pages 121–121.

**Proposed evidence:** first_reminder, second_reminder, delivery_records.

**Review checks:** Read with timing, extension and confirmation-receipt provisions; reminder count alone does not authorise deregistration. Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm local adoption and modifications for the selected state/territory; the core instrument alone does not establish jurisdictional applicability.

**Human decision:** PENDING.

## OIQ-005 — NERL_NERR / life support

**Trigger:** First medical-confirmation reminder is issued.

**Action:** Do not issue the first reminder before the minimum waiting period has elapsed.

**Timing:** at least 15 business days; anchor: medical form issue date.

**Source:** [National Energy Retail Rules, version 51, clause 124A(1)(c)](https://aemc-dra-production-s3.s3.ap-southeast-2.amazonaws.com/rules/ee0c0f923d57687aba955f6f97a974077ed27515/assets/files/NERR%20-%20v51%20-%20Full.pdf#page=121); physical PDF pages 121–121.

**Proposed evidence:** form_issue_date, first_reminder_issue_date.

**Review checks:** Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm applicable business-day calendar and counting rule before any timing control. Confirm local adoption and modifications for the selected state/territory; the core instrument alone does not establish jurisdictional applicability.

**Human decision:** PENDING.

## OIQ-006 — NERL_NERR / life support

**Trigger:** Second medical-confirmation reminder is issued.

**Action:** Do not issue the second reminder before the minimum interval has elapsed.

**Timing:** at least 15 business days; anchor: first reminder issue date.

**Source:** [National Energy Retail Rules, version 51, clause 124A(1)(d)](https://aemc-dra-production-s3.s3.ap-southeast-2.amazonaws.com/rules/ee0c0f923d57687aba955f6f97a974077ed27515/assets/files/NERR%20-%20v51%20-%20Full.pdf#page=121); physical PDF pages 121–121.

**Proposed evidence:** first_reminder_issue_date, second_reminder_issue_date.

**Review checks:** Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm applicable business-day calendar and counting rule before any timing control. Confirm local adoption and modifications for the selected state/territory; the core instrument alone does not establish jurisdictional applicability.

**Human decision:** PENDING.

## OIQ-007 — NERL_NERR / life support

**Trigger:** Customer requests extra time for medical confirmation.

**Action:** Give at least one extension of the minimum duration.

**Timing:** at least 25 business days; anchor: extension duration.

**Source:** [National Energy Retail Rules, version 51, clause 124A(1)(e)](https://aemc-dra-production-s3.s3.ap-southeast-2.amazonaws.com/rules/ee0c0f923d57687aba955f6f97a974077ed27515/assets/files/NERR%20-%20v51%20-%20Full.pdf#page=121); physical PDF pages 121–121.

**Proposed evidence:** extension_request, extension_decision, original_and_revised_due_dates.

**Review checks:** This is an extension length, not a 25-day response deadline. Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm applicable business-day calendar and counting rule before any timing control. Confirm local adoption and modifications for the selected state/territory; the core instrument alone does not establish jurisdictional applicability.

**Human decision:** PENDING.

## OIQ-008 — NERL_NERR / life support

**Trigger:** Retailer has deregistered the premises under a permitted pathway.

**Action:** Notify the distributor of the deregistration date and reason.

**Timing:** at most 5 business days; anchor: retailer deregistration.

**Source:** [National Energy Retail Rules, version 51, clause 125(2)(a)](https://aemc-dra-production-s3.s3.ap-southeast-2.amazonaws.com/rules/ee0c0f923d57687aba955f6f97a974077ed27515/assets/files/NERR%20-%20v51%20-%20Full.pdf#page=124); physical PDF pages 124–127.

**Proposed evidence:** lawful_deregistration_review, deregistration_event, distributor_notification.

**Review checks:** This downstream notification requirement grants no permission to deregister or disconnect. Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm applicable business-day calendar and counting rule before any timing control. Confirm local adoption and modifications for the selected state/territory; the core instrument alone does not establish jurisdictional applicability.

**Human decision:** PENDING.

## OIQ-009 — NERL_NERR / life support

**Trigger:** Life support registration details or required communications change.

**Action:** Maintain the required supply date, medical confirmation receipt, deregistration date/reason and communication records.

**Timing:** No numerical deadline asserted.

**Source:** [National Energy Retail Rules, version 51, clause 126(b)](https://aemc-dra-production-s3.s3.ap-southeast-2.amazonaws.com/rules/ee0c0f923d57687aba955f6f97a974077ed27515/assets/files/NERR%20-%20v51%20-%20Full.pdf#page=127); physical PDF pages 127–128.

**Proposed evidence:** registration_history, confirmation_receipt, deregistration_history, communication_log.

**Review checks:** Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm local adoption and modifications for the selected state/territory; the core instrument alone does not establish jurisdictional applicability.

**Human decision:** PENDING.

## OIQ-010 — NERL_NERR / life support

**Trigger:** Medical confirmation is held for a registration specified in rule 126A.

**Action:** Keep a copy throughout the customer relationship for those premises and for the required period after it ends.

**Timing:** at least 110 business days; anchor: customer relationship for registered premises ends.

**Source:** [National Energy Retail Rules, version 51, clause 126A](https://aemc-dra-production-s3.s3.ap-southeast-2.amazonaws.com/rules/ee0c0f923d57687aba955f6f97a974077ed27515/assets/files/NERR%20-%20v51%20-%20Full.pdf#page=128); physical PDF pages 128–129.

**Proposed evidence:** confirmation_copy_reference, customer_tenure, retention_metadata.

**Review checks:** Retention applies during tenure as well; this is not a command to delete on day 110. Do not store medical content in this public register. Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm applicable business-day calendar and counting rule before any timing control. Confirm local adoption and modifications for the selected state/territory; the core instrument alone does not establish jurisdictional applicability.

**Human decision:** PENDING.

## OIQ-011 — NERL_NERR / hardship

**Trigger:** A hardship customer payment plan is being established.

**Action:** Account for capacity to pay, arrears and expected energy needs over the next 12 months.

**Timing:** No numerical deadline asserted.

**Source:** [National Energy Retail Rules, version 51, clause 72(1)(a)](https://aemc-dra-production-s3.s3.ap-southeast-2.amazonaws.com/rules/ee0c0f923d57687aba955f6f97a974077ed27515/assets/files/NERR%20-%20v51%20-%20Full.pdf#page=82); physical PDF pages 82–83.

**Proposed evidence:** capacity_assessment, arrears_snapshot, consumption_forecast, plan_calculation.

**Review checks:** Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm local adoption and modifications for the selected state/territory; the core instrument alone does not establish jurisdictional applicability.

**Human decision:** PENDING.

## OIQ-012 — NERL_NERR / hardship

**Trigger:** A payment plan is established for a hardship customer.

**Action:** Offer instalments for energy consumption in advance or in arrears.

**Timing:** No numerical deadline asserted.

**Source:** [National Energy Retail Rules, version 51, clause 72(1)(b)](https://aemc-dra-production-s3.s3.ap-southeast-2.amazonaws.com/rules/ee0c0f923d57687aba955f6f97a974077ed27515/assets/files/NERR%20-%20v51%20-%20Full.pdf#page=82); physical PDF pages 82–83.

**Proposed evidence:** options_presented, customer_selection, payment_plan.

**Review checks:** Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm local adoption and modifications for the selected state/territory; the core instrument alone does not establish jurisdictional applicability.

**Human decision:** PENDING.

## OIQ-013 — NERL_NERR / hardship

**Trigger:** Payment plan information is given to the customer.

**Action:** Explain duration, instalment amounts and frequency, due dates and the applicable arrears or advance-payment calculation details.

**Timing:** No numerical deadline asserted.

**Source:** [National Energy Retail Rules, version 51, clause 72(2)](https://aemc-dra-production-s3.s3.ap-southeast-2.amazonaws.com/rules/ee0c0f923d57687aba955f6f97a974077ed27515/assets/files/NERR%20-%20v51%20-%20Full.pdf#page=82); physical PDF pages 82–83.

**Proposed evidence:** plan_schedule, customer_information, calculation_basis.

**Review checks:** Subclauses 72(2)(c) and (d) depend on whether payments are in arrears or in advance. Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm local adoption and modifications for the selected state/territory; the core instrument alone does not establish jurisdictional applicability.

**Human decision:** PENDING.

## OIQ-014 — NERL_NERR / hardship

**Trigger:** It appears that a residential customer has not paid because of hardship-related payment difficulties.

**Action:** Inform the customer about the retailer hardship policy in accordance with the Rules.

**Timing:** No numerical deadline asserted.

**Source:** [National Energy Retail Law (South Australia) Act 2011, Schedule: National Energy Retail Law, version 18 December 2025 consolidation, clause 46](https://legislation.sa.gov.au/_legislation-documents/lz/c/a/national-energy-retail-law-south-australia-act-2011/current/2011.6.auth.pdf#page=61); physical PDF pages 61–61.

**Proposed evidence:** hardship_indicator, policy_version, communication_record.

**Review checks:** Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm local adoption and modifications for the selected state/territory; the core instrument alone does not establish jurisdictional applicability.

**Human decision:** PENDING.

## OIQ-015 — NERL_NERR / hardship

**Trigger:** Hardship status or a qualifying residential payment-difficulty notification/belief exists.

**Action:** Offer and apply a payment plan subject to applicable Rules and their exceptions.

**Timing:** No numerical deadline asserted.

**Source:** [National Energy Retail Law (South Australia) Act 2011, Schedule: National Energy Retail Law, version 18 December 2025 consolidation, clause 50(1)-(2)](https://legislation.sa.gov.au/_legislation-documents/lz/c/a/national-energy-retail-law-south-australia-act-2011/current/2011.6.auth.pdf#page=62); physical PDF pages 62–62.

**Proposed evidence:** trigger_evidence, plan_offer, plan_application, exception_assessment.

**Review checks:** Check Rules governing permitted exceptions; this is not an unconditional offer rule for every unpaid bill. Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm local adoption and modifications for the selected state/territory; the core instrument alone does not establish jurisdictional applicability.

**Human decision:** PENDING.

## OIQ-016 — VIC / life support

**Trigger:** Medical confirmation form is provided.

**Action:** Allow the minimum medical-confirmation period.

**Timing:** at least 50 business days; anchor: date of medical confirmation form.

**Source:** [Energy Retail Code of Practice, version 6, clause 164(1)(a)](https://www.esc.vic.gov.au/sites/default/files/documents/Energy%20Retail%20Code%20of%20Practice%20%28version%206%29_2.pdf#page=116); physical PDF pages 116–117.

**Proposed evidence:** dated_medical_form, confirmation_due_date.

**Review checks:** Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm applicable business-day calendar and counting rule before any timing control. Confirm residential electricity scope under the Code and any Electricity Industry Act cross-references; exempt sellers and gas are excluded from this pilot.

**Human decision:** PENDING.

## OIQ-017 — VIC / life support

**Trigger:** First medical-confirmation reminder is issued.

**Action:** Respect the minimum delay before the first reminder.

**Timing:** at least 15 business days; anchor: medical form issue date.

**Source:** [Energy Retail Code of Practice, version 6, clause 164(1)(c)](https://www.esc.vic.gov.au/sites/default/files/documents/Energy%20Retail%20Code%20of%20Practice%20%28version%206%29_2.pdf#page=116); physical PDF pages 116–117.

**Proposed evidence:** form_issue_date, first_reminder_issue_date.

**Review checks:** Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm applicable business-day calendar and counting rule before any timing control. Confirm residential electricity scope under the Code and any Electricity Industry Act cross-references; exempt sellers and gas are excluded from this pilot.

**Human decision:** PENDING.

## OIQ-018 — VIC / life support

**Trigger:** Second medical-confirmation reminder is issued.

**Action:** Respect the minimum interval before the second reminder.

**Timing:** at least 15 business days; anchor: first reminder issue date.

**Source:** [Energy Retail Code of Practice, version 6, clause 164(1)(d)](https://www.esc.vic.gov.au/sites/default/files/documents/Energy%20Retail%20Code%20of%20Practice%20%28version%206%29_2.pdf#page=116); physical PDF pages 116–117.

**Proposed evidence:** first_reminder_issue_date, second_reminder_issue_date.

**Review checks:** Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm applicable business-day calendar and counting rule before any timing control. Confirm residential electricity scope under the Code and any Electricity Industry Act cross-references; exempt sellers and gas are excluded from this pilot.

**Human decision:** PENDING.

## OIQ-019 — VIC / life support

**Trigger:** Customer requests a medical-confirmation extension.

**Action:** Give at least one extension of the minimum duration.

**Timing:** at least 25 business days; anchor: extension duration.

**Source:** [Energy Retail Code of Practice, version 6, clause 164(1)(e)](https://www.esc.vic.gov.au/sites/default/files/documents/Energy%20Retail%20Code%20of%20Practice%20%28version%206%29_2.pdf#page=116); physical PDF pages 116–117.

**Proposed evidence:** extension_request, original_and_revised_due_dates.

**Review checks:** Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm applicable business-day calendar and counting rule before any timing control. Confirm residential electricity scope under the Code and any Electricity Industry Act cross-references; exempt sellers and gas are excluded from this pilot.

**Human decision:** PENDING.

## OIQ-020 — VIC / life support

**Trigger:** Medical confirmation is sought under clause 164.

**Action:** Provide at least two written confirmation reminders.

**Timing:** No numerical deadline asserted.

**Source:** [Energy Retail Code of Practice, version 6, clause 164(1)(b)](https://www.esc.vic.gov.au/sites/default/files/documents/Energy%20Retail%20Code%20of%20Practice%20%28version%206%29_2.pdf#page=116); physical PDF pages 116–117.

**Proposed evidence:** first_reminder, second_reminder, delivery_records.

**Review checks:** Apply the remaining timing and content rules; two reminders are not permission to deregister. Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm residential electricity scope under the Code and any Electricity Industry Act cross-references; exempt sellers and gas are excluded from this pilot.

**Human decision:** PENDING.

## OIQ-021 — VIC / life support

**Trigger:** Relevant life support or contact information is received for an electricity registration under section 40SG(1) or 40SH(1).

**Action:** Send relevant updated information to the distributor unless it came from that distributor.

**Timing:** at most 1 business days; anchor: relevant information received.

**Source:** [Energy Retail Code of Practice, version 6, clause 165(1)(a)](https://www.esc.vic.gov.au/sites/default/files/documents/Energy%20Retail%20Code%20of%20Practice%20%28version%206%29_2.pdf#page=117); physical PDF pages 117–117.

**Proposed evidence:** registration_pathway, information_received_at, information_origin, distributor_notification.

**Review checks:** Verify Electricity Industry Act registration pathway; distributor-origin exception applies. Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm applicable business-day calendar and counting rule before any timing control. Confirm residential electricity scope under the Code and any Electricity Industry Act cross-references; exempt sellers and gas are excluded from this pilot.

**Human decision:** PENDING.

## OIQ-022 — VIC / life support

**Trigger:** Customer or distributor advises an update for a registration in clause 165(1).

**Action:** Update the retailer life support register.

**Timing:** at most 1 business days; anchor: update advice received.

**Source:** [Energy Retail Code of Practice, version 6, clause 165(1)(b)](https://www.esc.vic.gov.au/sites/default/files/documents/Energy%20Retail%20Code%20of%20Practice%20%28version%206%29_2.pdf#page=117); physical PDF pages 117–117.

**Proposed evidence:** registration_pathway, update_advice_received_at, register_update.

**Review checks:** Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm applicable business-day calendar and counting rule before any timing control. Confirm residential electricity scope under the Code and any Electricity Industry Act cross-references; exempt sellers and gas are excluded from this pilot.

**Human decision:** PENDING.

## OIQ-023 — VIC / life support

**Trigger:** Retailer has deregistered a customer through a permitted pathway.

**Action:** Notify the distributor of the date and reason.

**Timing:** at most 5 business days; anchor: retailer deregistration.

**Source:** [Energy Retail Code of Practice, version 6, clause 166(2)(a)](https://www.esc.vic.gov.au/sites/default/files/documents/Energy%20Retail%20Code%20of%20Practice%20%28version%206%29_2.pdf#page=117); physical PDF pages 117–120.

**Proposed evidence:** lawful_deregistration_review, deregistration_event, distributor_notification.

**Review checks:** Notification timing does not establish that the deregistration was lawful. Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm applicable business-day calendar and counting rule before any timing control. Confirm residential electricity scope under the Code and any Electricity Industry Act cross-references; exempt sellers and gas are excluded from this pilot.

**Human decision:** PENDING.

## OIQ-024 — VIC / life support

**Trigger:** Retailer has deregistered a customer through a permitted pathway.

**Action:** Update its life support register.

**Timing:** at most 1 business days; anchor: retailer deregistration.

**Source:** [Energy Retail Code of Practice, version 6, clause 166(2)(b)](https://www.esc.vic.gov.au/sites/default/files/documents/Energy%20Retail%20Code%20of%20Practice%20%28version%206%29_2.pdf#page=117); physical PDF pages 117–120.

**Proposed evidence:** deregistration_event, register_update.

**Review checks:** This is recording a completed event, not permission to deregister or disconnect. Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm applicable business-day calendar and counting rule before any timing control. Confirm residential electricity scope under the Code and any Electricity Industry Act cross-references; exempt sellers and gas are excluded from this pilot.

**Human decision:** PENDING.

## OIQ-025 — VIC / life support

**Trigger:** Life support registration details or required communications change.

**Action:** Keep required supply dates, confirmation receipt, deregistration dates/reasons and required communications current.

**Timing:** No numerical deadline asserted.

**Source:** [Energy Retail Code of Practice, version 6, clause 167(1)(b)](https://www.esc.vic.gov.au/sites/default/files/documents/Energy%20Retail%20Code%20of%20Practice%20%28version%206%29_2.pdf#page=120); physical PDF pages 120–120.

**Proposed evidence:** registration_history, confirmation_receipt, deregistration_history, communication_log.

**Review checks:** Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm residential electricity scope under the Code and any Electricity Industry Act cross-references; exempt sellers and gas are excluded from this pilot.

**Human decision:** PENDING.

## OIQ-026 — VIC / hardship

**Trigger:** Retailer offers standard assistance under clause 125.

**Action:** Include at least three of the four specified standard-assistance options.

**Timing:** No numerical deadline asserted.

**Source:** [Energy Retail Code of Practice, version 6, clause 125(2)](https://www.esc.vic.gov.au/sites/default/files/documents/Energy%20Retail%20Code%20of%20Practice%20%28version%206%29_2.pdf#page=99); physical PDF pages 99–99.

**Proposed evidence:** assistance_offer_catalogue, option_mapping.

**Review checks:** Check all four options and the clause 125(1) customer election requirement. The current minimum is three, not two. Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm residential electricity scope under the Code and any Electricity Industry Act cross-references; exempt sellers and gas are excluded from this pilot.

**Human decision:** PENDING.

## OIQ-027 — VIC / hardship

**Trigger:** A residential customer cannot pay the full cost of ongoing energy use.

**Action:** Provide the applicable initial arrears hold and reduced ongoing-payment assistance for at least six months while energy costs are reduced.

**Timing:** at least 6 months; anchor: initial assistance period starts.

**Source:** [Energy Retail Code of Practice, version 6, clause 128(1)(g), (3)-(5)](https://www.esc.vic.gov.au/sites/default/files/documents/Energy%20Retail%20Code%20of%20Practice%20%28version%206%29_2.pdf#page=99); physical PDF pages 99–101.

**Proposed evidence:** ongoing_affordability_assessment, arrears_hold, assistance_start_and_end, cost_reduction_support.

**Review checks:** Six months is a minimum initial assistance period, not a maximum repayment-plan term. Apply eligibility and interaction with clauses 130 and 131. Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm residential electricity scope under the Code and any Electricity Industry Act cross-references; exempt sellers and gas are excluded from this pilot.

**Human decision:** PENDING.

## OIQ-028 — VIC / hardship

**Trigger:** A residential customer misses the pay-by date and arrears exceed AUD 55 inclusive of GST.

**Action:** Contact the customer with assistance entitlement and access information.

**Timing:** at most 21 business days; anchor: bill pay-by date.

**Source:** [Energy Retail Code of Practice, version 6, clause 129(2)](https://www.esc.vic.gov.au/sites/default/files/documents/Energy%20Retail%20Code%20of%20Practice%20%28version%206%29_2.pdf#page=101); physical PDF pages 101–102.

**Proposed evidence:** bill_pay_by_date, arrears_including_gst, contact_attempt_and_delivery, assistance_information.

**Review checks:** Threshold is strictly greater than 55 AUD, not greater than or equal to 55. Check evidence of contact. Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm applicable business-day calendar and counting rule before any timing control. Confirm residential electricity scope under the Code and any Electricity Industry Act cross-references; exempt sellers and gas are excluded from this pilot.

**Human decision:** PENDING.

## OIQ-029 — VIC / hardship

**Trigger:** Information is provided under clause 129(1) or (2).

**Action:** Allow the customer the minimum period to consider it, seek more information and propose payments.

**Timing:** at least 6 business days; anchor: assistance information provided.

**Source:** [Energy Retail Code of Practice, version 6, clause 129(3)](https://www.esc.vic.gov.au/sites/default/files/documents/Energy%20Retail%20Code%20of%20Practice%20%28version%206%29_2.pdf#page=101); physical PDF pages 101–102.

**Proposed evidence:** information_provided_at, consideration_window, proposal_record.

**Review checks:** Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm applicable business-day calendar and counting rule before any timing control. Confirm residential electricity scope under the Code and any Electricity Industry Act cross-references; exempt sellers and gas are excluded from this pilot.

**Human decision:** PENDING.

## OIQ-030 — VIC / hardship

**Trigger:** A payment proposal or revised proposal is accepted under clause 130.

**Action:** Give a written schedule stating total payment count, period, due dates and amounts.

**Timing:** No numerical deadline asserted.

**Source:** [Energy Retail Code of Practice, version 6, clause 130(5)](https://www.esc.vic.gov.au/sites/default/files/documents/Energy%20Retail%20Code%20of%20Practice%20%28version%206%29_2.pdf#page=102); physical PDF pages 102–103.

**Proposed evidence:** accepted_proposal, written_schedule, delivery_record.

**Review checks:** Clause 130(1) excludes customers whose arrears are on hold under 128(1)(g)(i). Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm residential electricity scope under the Code and any Electricity Industry Act cross-references; exempt sellers and gas are excluded from this pilot.

**Human decision:** PENDING.

## OIQ-031 — VIC / hardship

**Trigger:** A customer receiving assistance under this Division misses an agreed payment.

**Action:** Contact the customer to discuss a revised payment proposal.

**Timing:** No numerical deadline asserted.

**Source:** [Energy Retail Code of Practice, version 6, clause 130(6)](https://www.esc.vic.gov.au/sites/default/files/documents/Energy%20Retail%20Code%20of%20Practice%20%28version%206%29_2.pdf#page=102); physical PDF pages 102–103.

**Proposed evidence:** applicable_plan, missed_payment, contact_record.

**Review checks:** Read scope in 130(1); clause 131 addresses the different arrears-on-hold pathway. No numerical contact deadline is asserted here. Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm residential electricity scope under the Code and any Electricity Industry Act cross-references; exempt sellers and gas are excluded from this pilot.

**Human decision:** PENDING.

## OIQ-032 — VIC / hardship

**Trigger:** A customer requests the retailer hardship policy.

**Action:** Send a copy of the policy.

**Timing:** No numerical deadline asserted.

**Source:** [Energy Retail Code of Practice, version 6, clause 138(2)](https://www.esc.vic.gov.au/sites/default/files/documents/Energy%20Retail%20Code%20of%20Practice%20%28version%206%29_2.pdf#page=105); physical PDF pages 105–106.

**Proposed evidence:** policy_request, policy_version, copy_sent.

**Review checks:** Confirm complete subclause, definitions, exceptions and evidence sufficiency; this is a candidate paraphrase. Confirm residential electricity scope under the Code and any Electricity Industry Act cross-references; exempt sellers and gas are excluded from this pilot.

**Human decision:** PENDING.
