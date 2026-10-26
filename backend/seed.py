"""
KAIZEN FinTech — Deterministic Demo Seed Data
Creates repeatable, consistent demo records for local development.
Never seeds production environments automatically.
"""
import asyncio
import uuid
import json
from datetime import datetime, timezone, timedelta
from app.core.database import async_session_maker, create_tables
from app.core.security import get_password_hash
from app.core.config import settings


def uid():
    return str(uuid.uuid4())


def utc(days_ago=0, hours_ago=0, days_ahead=0):
    return datetime.now(timezone.utc) - timedelta(days=days_ago, hours=hours_ago) + timedelta(days=days_ahead)


async def seed():
    if settings.APP_ENV == "production":
        print("❌ Seeding is disabled in production.")
        return

    await create_tables()

    async with async_session_maker() as db:
        from sqlalchemy import select, delete
        from app.models.base import (
            Organization, User, Account, Beneficiary, Payment, PaymentAttempt,
            Incident, IncidentEvidence, AgentExecution, ReconciliationRun,
            ReconciliationRecord, RiskAlert, AuditLog, PaymentObligation, Notification
        )

        # Clear existing demo data
        for model in [Notification, AuditLog, AgentExecution, IncidentEvidence,
                      ReconciliationRecord, ReconciliationRun, RiskAlert,
                      PaymentAttempt, Incident, PaymentObligation,
                      Payment, Beneficiary, Account, User, Organization]:
            await db.execute(delete(model))
        await db.commit()

        # ----------------------------------------------------------------
        # Organization
        # ----------------------------------------------------------------
        org_id = uid()
        org = Organization(
            id=org_id, name="Acme Corporation", slug="acme-corp",
            settings_json=json.dumps({"timezone": "UTC", "base_currency": "USD"}),
        )
        db.add(org)

        # ----------------------------------------------------------------
        # Users
        # ----------------------------------------------------------------
        admin_id = uid()
        treasury_id = uid()
        ops_id = uid()
        auditor_id = uid()

        users_data = [
            (admin_id, "admin@kaizen.dev", "Sarah Chen", "admin", "SC"),
            (treasury_id, "treasury@kaizen.dev", "Marcus Wells", "treasury_manager", "MW"),
            (ops_id, "ops@kaizen.dev", "Priya Patel", "payment_ops", "PP"),
            (auditor_id, "auditor@kaizen.dev", "James Rodriguez", "auditor", "JR"),
        ]
        user_objs = {}
        for uid_, email, name, role, initials in users_data:
            u = User(
                id=uid_, org_id=org_id, email=email,
                hashed_password=get_password_hash("Demo1234!"),
                full_name=name, role=role, avatar_initials=initials,
                last_login=utc(hours_ago=2),
            )
            db.add(u)
            user_objs[email] = u

        # ----------------------------------------------------------------
        # Accounts
        # ----------------------------------------------------------------
        acc_usd_id = uid()
        acc_eur_id = uid()
        acc_gbp_id = uid()
        acc_sgd_id = uid()

        accounts = [
            Account(id=acc_usd_id, org_id=org_id, name="USD Operating Account",
                    account_number="USD-001-2024", currency="USD",
                    available_balance="487500.00", reserved_balance="62500.00",
                    total_balance="550000.00", provider="Airwallex"),
            Account(id=acc_eur_id, org_id=org_id, name="EUR Supplier Account",
                    account_number="EUR-002-2024", currency="EUR",
                    available_balance="218000.00", reserved_balance="32000.00",
                    total_balance="250000.00", provider="Airwallex"),
            Account(id=acc_gbp_id, org_id=org_id, name="GBP Treasury Reserve",
                    account_number="GBP-003-2024", currency="GBP",
                    available_balance="141000.00", reserved_balance="9000.00",
                    total_balance="150000.00", provider="Airwallex"),
            Account(id=acc_sgd_id, org_id=org_id, name="SGD APAC Operations",
                    account_number="SGD-004-2024", currency="SGD",
                    available_balance="95000.00", reserved_balance="5000.00",
                    total_balance="100000.00", provider="Airwallex"),
        ]
        for a in accounts:
            db.add(a)

        # ----------------------------------------------------------------
        # Beneficiaries
        # ----------------------------------------------------------------
        bens = []
        ben_data = [
            ("GlobalTech Supplies Ltd", "GT-ACC-001", "HSBC", "USD", "accounts@globaltech.com", "critical"),
            ("Apex Manufacturing Co", "AM-ACC-002", "Barclays", "GBP", "finance@apex.co.uk", "high"),
            ("Nordic Components AB", "NC-ACC-003", "SEB", "EUR", "payments@nordic.se", "high"),
            ("Pacific Logistics Pte", "PL-ACC-004", "DBS", "SGD", "ap@pacific.sg", "medium"),
            ("Metro Office Solutions", "MO-ACC-005", "Chase", "USD", "billing@metro.com", "medium"),
            ("EuroTech GmbH", "ET-ACC-006", "Deutsche", "EUR", "rechnungen@eurotech.de", "high"),
            ("Bright Data Services", "BD-ACC-007", "Wells Fargo", "USD", "billing@brightdata.com", "low"),
            ("Quantum Analytics Inc", "QA-ACC-008", "Citi", "USD", "finance@quantum.io", "medium"),
            ("Stellar Freight Ltd", "SF-ACC-009", "Natwest", "GBP", "ap@stellar.co.uk", "critical"),
            ("Atlas Cloud Services", "AC-ACC-010", "Silicon Valley Bank", "USD", "billing@atlas.cloud", "low"),
        ]
        ben_ids = []
        for name, acct, bank, cur, email, crit in ben_data:
            b_id = uid()
            b = Beneficiary(
                id=b_id, org_id=org_id, name=name, account_number=acct,
                bank_name=bank, currency=cur, email=email, criticality=crit,
            )
            db.add(b)
            ben_ids.append(b_id)
            bens.append(b)

        await db.flush()

        # ----------------------------------------------------------------
        # Payments — 28 payments across various states
        # ----------------------------------------------------------------
        pay_data = [
            # (amount, currency, ben_idx, acc_id, status, days_ago, ref)
            ("125000.00", "USD", 0, acc_usd_id, "SUCCEEDED", 15, "INV-2024-001"),
            ("47500.00", "GBP", 1, acc_gbp_id, "SUCCEEDED", 14, "PO-2024-045"),
            ("85000.00", "EUR", 2, acc_eur_id, "SUCCEEDED", 12, "INV-EUR-2024-012"),
            ("32000.00", "SGD", 3, acc_sgd_id, "SUCCEEDED", 10, "LOGIST-2024-007"),
            ("18500.00", "USD", 4, acc_usd_id, "SUCCEEDED", 8, "OFF-2024-023"),
            ("92000.00", "EUR", 5, acc_eur_id, "SUCCEEDED", 7, "TECH-EUR-2024-034"),
            ("7800.00", "USD", 6, acc_usd_id, "SUCCEEDED", 6, "DATA-2024-011"),
            ("156000.00", "USD", 0, acc_usd_id, "PENDING", 3, "INV-2024-089"),
            ("63000.00", "GBP", 8, acc_gbp_id, "PENDING", 2, "FREIGHT-2024-056"),
            ("41000.00", "EUR", 2, acc_eur_id, "PENDING", 1, "INV-EUR-2024-099"),
            ("28500.00", "USD", 7, acc_usd_id, "FAILED", 5, "ANALY-2024-004"),
            ("71000.00", "EUR", 5, acc_eur_id, "FAILED", 4, "TECH-EUR-2024-041"),
            ("15000.00", "USD", 4, acc_usd_id, "FAILED", 3, "OFF-2024-031"),
            ("95000.00", "USD", 0, acc_usd_id, "UNKNOWN", 2, "INV-2024-091"),
            ("38000.00", "GBP", 1, acc_gbp_id, "UNKNOWN", 1, "PO-2024-067"),
            ("52000.00", "EUR", 2, acc_eur_id, "REQUIRES_REVIEW", 3, "INV-EUR-2024-105"),
            ("125000.00", "USD", 0, acc_usd_id, "REQUIRES_REVIEW", 1, "INV-2024-092"),  # dup candidate
            ("8200.00", "USD", 9, acc_usd_id, "SUCCEEDED", 20, "CLOUD-2024-001"),
            ("34000.00", "EUR", 5, acc_eur_id, "SUCCEEDED", 18, "TECH-EUR-2024-019"),
            ("55000.00", "USD", 7, acc_usd_id, "SUCCEEDED", 16, "ANALY-2024-001"),
            ("21000.00", "GBP", 8, acc_gbp_id, "SUCCEEDED", 15, "FREIGHT-2024-033"),
            ("44000.00", "SGD", 3, acc_sgd_id, "SUCCEEDED", 11, "LOGIST-2024-003"),
            ("112000.00", "USD", 0, acc_usd_id, "SUBMITTED", 0, "INV-2024-095"),
            ("67000.00", "EUR", 2, acc_eur_id, "SUBMITTED", 0, "INV-EUR-2024-110"),
            ("29000.00", "USD", 4, acc_usd_id, "CREATED", 0, "OFF-2024-040"),
            ("18000.00", "GBP", 1, acc_gbp_id, "CANCELLED", 9, "PO-2024-058"),
            ("9500.00", "USD", 6, acc_usd_id, "CANCELLED", 13, "DATA-2024-008"),
            ("78000.00", "USD", 0, acc_usd_id, "VALIDATING", 0, "INV-2024-096"),
        ]

        payment_ids = []
        payment_objs = []
        counter = 1
        for amt, cur, ben_idx, acc_id, status, days_ago, ref in pay_data:
            p_id = uid()
            pnum = f"PAY-{2024000 + counter:07d}"
            created = utc(days_ago=days_ago, hours_ago=(counter % 8))
            submitted = created + timedelta(minutes=5) if status not in ("CREATED", "VALIDATING") else None
            completed = submitted + timedelta(minutes=30) if status in ("SUCCEEDED", "FAILED", "CANCELLED") else None

            p = Payment(
                id=p_id, org_id=org_id, payment_number=pnum, status=status,
                amount=amt, currency=cur, beneficiary_id=ben_ids[ben_idx],
                account_id=acc_id, reference=ref,
                description=f"Payment for {ref}",
                idempotency_key=f"idem-{p_id}",
                provider_ref=f"PROV-{pnum}" if status in ("SUCCEEDED", "PENDING", "SUBMITTED") else None,
                retry_count=1 if status == "FAILED" else 0,
                is_demo=True,
                submitted_at=submitted, completed_at=completed,
                created_by=ops_id, created_at=created, updated_at=created,
                error_message="Provider timeout: connection reset" if status == "FAILED" else None,
            )
            db.add(p)
            payment_ids.append(p_id)
            payment_objs.append(p)

            # PaymentAttempt
            attempt = PaymentAttempt(
                id=uid(), payment_id=p_id, attempt_number=1, status=status,
                request_payload=json.dumps({"amount": amt, "currency": cur, "ref": ref}),
                response_payload=json.dumps({"status": status, "provider_ref": f"PROV-{pnum}"}),
                created_at=submitted or created,
            )
            db.add(attempt)
            counter += 1

        await db.flush()

        # ----------------------------------------------------------------
        # Incidents — 10 incidents
        # ----------------------------------------------------------------
        inc_data = [
            (payment_ids[13], "UNKNOWN payment — possible duplicate risk", "critical", "open",
             "Payment PAY-2024000014 returned UNKNOWN status after provider timeout. Potential duplicate risk if retried.",
             utc(days_ago=2), 95000.00, "USD"),
            (payment_ids[14], "Ambiguous GBP transfer outcome", "high", "investigating",
             "GBP transfer to Apex Manufacturing shows UNKNOWN status. Provider confirmation pending.",
             utc(days_ago=1), 38000.00, "GBP"),
            (payment_ids[10], "EUR payment failed — pending retry authorization", "medium", "pending_action",
             "EUR payment to EuroTech failed with provider error. Retry requires treasury manager approval.",
             utc(days_ago=5), 28500.00, "USD"),
            (payment_ids[15], "Payment flagged for compliance review", "high", "investigating",
             "EUR transfer requires additional beneficiary verification per compliance policy.",
             utc(days_ago=3), 52000.00, "EUR"),
            (payment_ids[16], "Potential duplicate — same amount as INV-2024-001", "critical", "open",
             "INV-2024-092 has identical amount ($125,000) to INV-2024-001 which succeeded 15 days ago. Requires investigation before processing.",
             utc(hours_ago=6), 125000.00, "USD"),
            (payment_ids[11], "EUR payment failure — insufficient provider balance", "medium", "resolved",
             "EuroTech EUR payment failed due to insufficient provider account balance. Account topped up and payment retried successfully.",
             utc(days_ago=4), 71000.00, "EUR"),
            (payment_ids[7], "Large pending USD transfer — SLA approaching", "high", "open",
             "USD 156,000 transfer to GlobalTech has been pending for 3 days. SLA deadline in 4 hours.",
             utc(days_ago=3), 156000.00, "USD"),
            (payment_ids[8], "GBP freight payment delayed", "medium", "investigating",
             "Stellar Freight payment pending confirmation from Natwest. Bank processing delay reported.",
             utc(days_ago=2), 63000.00, "GBP"),
            (None, "Reconciliation exception — 3 unmatched transactions", "low", "open",
             "October reconciliation run identified 3 transactions without provider confirmation.",
             utc(days_ago=1), None, None),
            (payment_ids[12], "Small USD payment failed — beneficiary account error", "low", "resolved",
             "Metro Office Solutions payment failed due to invalid account number. Beneficiary record corrected.",
             utc(days_ago=3), 15000.00, "USD"),
        ]

        incident_ids = []
        inc_counter = 1
        severity_sla = {"critical": 4, "high": 24, "medium": 72, "low": 168}
        for pay_id, title, sev, status, desc, created, fin_impact, fin_cur in inc_data:
            i_id = uid()
            inc_num = f"INC-{2024000 + inc_counter:07d}"
            sla = created + timedelta(hours=severity_sla.get(sev, 72))
            priority = {"critical": 95.0, "high": 75.0, "medium": 50.0, "low": 25.0}.get(sev, 50.0)
            resolved_at = utc(days_ago=1) if status == "resolved" else None
            ai_report_text = f"""## Investigation Summary
**Incident**: {inc_num}
**Severity**: {sev.upper()}
**Payment Reference**: {pay_id[:8] + '...' if pay_id else 'N/A'}

### Findings
- Payment state analysis complete
- Provider communication logs reviewed  
- Reconciliation records checked
- Risk scoring applied: {priority}/100

### Root Cause Assessment
{'Provider timeout during payment submission — outcome ambiguous.' if 'UNKNOWN' in title or 'timeout' in desc.lower() else 'Payment processing exception detected during standard workflow.'}

### Recommended Actions
1. {'Verify provider transaction ID before any retry' if 'UNKNOWN' in title else 'Review payment details with beneficiary'}
2. {'Block retry until outcome confirmed' if 'UNKNOWN' in title else 'Obtain approval from treasury manager'}
3. Escalate to payment operations if unresolved within SLA window

### Financial Impact
{'Critical: $' + str(fin_impact) + ' at risk of duplication' if fin_impact else 'Operational impact only — no direct financial risk quantified'}
""" if status != "resolved" else "✅ Incident resolved. See resolution notes."

            inc = Incident(
                id=i_id, org_id=org_id, incident_number=inc_num, payment_id=pay_id,
                title=title, description=desc, severity=sev, status=status,
                priority_score=priority, sla_deadline=sla,
                assigned_to=treasury_id if sev in ("critical", "high") else ops_id,
                root_cause="provider_timeout" if "UNKNOWN" in title else "payment_processing_error" if "failed" in title.lower() else "compliance_review" if "compliance" in title.lower() else "duplicate_risk",
                ai_report=ai_report_text,
                financial_impact=str(fin_impact) if fin_impact else None,
                financial_currency=fin_cur,
                resolution_notes="Issue resolved after provider confirmation received." if status == "resolved" else None,
                created_by=ops_id, created_at=created, updated_at=created,
                resolved_at=resolved_at,
            )
            db.add(inc)
            incident_ids.append(i_id)

            # Evidence
            evidence_items = [
                ("system_event", f"Incident created by system monitoring. Payment {pay_id[:8] if pay_id else 'N/A'} flagged."),
                ("payment_status", f"Payment status: {'UNKNOWN — no definitive confirmation from provider' if 'UNKNOWN' in title else status}"),
                ("agent_finding", f"AI Investigation Pipeline completed. Risk score: {priority}/100. See AI report for details."),
            ]
            if status == "resolved":
                evidence_items.append(("operator_note", "Provider confirmed transaction settled. Records updated."))

            for ev_type, ev_content in evidence_items:
                ev = IncidentEvidence(
                    id=uid(), incident_id=i_id, evidence_type=ev_type,
                    content=ev_content, created_by=ops_id,
                    created_at=created + timedelta(minutes=10),
                )
                db.add(ev)

            inc_counter += 1

        await db.flush()

        # ----------------------------------------------------------------
        # Reconciliation Runs — 3 runs
        # ----------------------------------------------------------------
        recon_run_ids = []
        for i, (matched, unmatched, exc, status, days) in enumerate([
            (22, 2, 1, "completed", 10),
            (18, 4, 3, "completed", 5),
            (8, 6, 2, "completed", 1),
        ]):
            r_id = uid()
            run_num = f"RECON-{2024000 + i + 1:07d}"
            created = utc(days_ago=days)
            recon = ReconciliationRun(
                id=r_id, org_id=org_id, run_number=run_num, status=status,
                matched_count=matched, unmatched_count=unmatched, exception_count=exc,
                period_start=utc(days_ago=days + 7), period_end=utc(days_ago=days),
                created_by=treasury_id, created_at=created, completed_at=created + timedelta(hours=2),
            )
            db.add(recon)
            recon_run_ids.append(r_id)

            # Records for first run
            if i == 0:
                for j, pay_id in enumerate(payment_ids[:5]):
                    match_status = "matched" if j < 3 else ("conflict" if j == 3 else "unmatched")
                    rec = ReconciliationRecord(
                        id=uid(), run_id=r_id, payment_id=pay_id,
                        match_status=match_status,
                        match_confidence=0.99 if match_status == "matched" else (0.65 if match_status == "conflict" else None),
                        provider_reference=f"PROV-PAY-{2024000 + j:07d}",
                        provider_amount=pay_data[j][0],
                        provider_currency=pay_data[j][1],
                        internal_amount=pay_data[j][0],
                        discrepancy_notes="Amount mismatch: $0.01 difference due to FX rounding" if match_status == "conflict" else None,
                        created_at=created,
                    )
                    db.add(rec)

        await db.flush()

        # ----------------------------------------------------------------
        # Risk Alerts — 15 alerts
        # ----------------------------------------------------------------
        risk_data = [
            (payment_ids[16], "duplicate_payment", "critical", 92.0,
             "Potential duplicate payment detected: INV-2024-092 ($125,000 USD) matches amount and beneficiary of INV-2024-001 which succeeded 15 days ago."),
            (payment_ids[13], "payment_uncertainty", "high", 78.0,
             "Payment PAY-2024000014 has UNKNOWN status. Provider confirmation not received within SLA window."),
            (payment_ids[14], "payment_uncertainty", "high", 74.0,
             "GBP payment to Apex Manufacturing (£38,000) shows UNKNOWN status after 24 hours."),
            (payment_ids[7], "amount_limit_exceeded", "medium", 55.0,
             "Payment PAY-2024000008 ($156,000) exceeds single-transaction soft limit of $150,000. Requires treasury manager sign-off."),
            (payment_ids[22], "suspicious_pattern", "medium", 48.0,
             "Back-to-back large USD transfers to GlobalTech detected within 24-hour window."),
            (payment_ids[15], "authorization_required", "high", 70.0,
             "EUR payment to Nordic Components (€52,000) flagged for additional authorization per compliance policy."),
            (payment_ids[11], "insufficient_funds", "medium", 45.0,
             "Previous attempt failed due to insufficient provider balance. Balance has been restored — verify before retry."),
            (payment_ids[10], "payment_uncertainty", "medium", 42.0,
             "USD payment to Quantum Analytics failed after 2 attempts. Root cause: provider connection reset."),
            (None, "suspicious_pattern", "low", 28.0,
             "Unusual payment velocity detected: 8 payments submitted within 2 hours — above baseline of 3/hour."),
            (payment_ids[12], "authorization_required", "low", 22.0,
             "Small USD payment to Metro Office Solutions failed — account number mismatch. Verify beneficiary details."),
            (payment_ids[8], "payment_uncertainty", "medium", 58.0,
             "GBP freight payment to Stellar Freight pending over 48 hours. Bank processing delay reported."),
            (payment_ids[9], "amount_limit_exceeded", "medium", 52.0,
             "EUR payment PAY-2024000010 (€41,000) requires compliance declaration for cross-border transfer."),
            (None, "duplicate_payment", "low", 35.0,
             "Two EUR payments to EuroTech GmbH within 5 days — verify intentional vs duplicate."),
            (payment_ids[23], "suspicious_pattern", "medium", 44.0,
             "EUR payment submitted outside business hours (02:34 UTC). Manual review recommended."),
            (payment_ids[27], "authorization_required", "low", 20.0,
             "USD payment in VALIDATING state for >2 hours — may require manual provider submission."),
        ]

        for pay_id, alert_type, sev, score, desc in risk_data:
            status = "open" if score > 50 else ("dismissed" if score < 30 else "reviewing")
            ra = RiskAlert(
                id=uid(), org_id=org_id, payment_id=pay_id, alert_type=alert_type,
                severity=sev, description=desc, risk_score=score,
                risk_factors=json.dumps({
                    "amount_factor": round(score * 0.3, 1),
                    "timing_factor": round(score * 0.2, 1),
                    "pattern_factor": round(score * 0.25, 1),
                    "beneficiary_factor": round(score * 0.25, 1),
                }),
                status=status,
                created_at=utc(hours_ago=int(score % 24)),
            )
            db.add(ra)

        # ----------------------------------------------------------------
        # Payment Obligations — 6 upcoming
        # ----------------------------------------------------------------
        obligation_data = [
            (ben_ids[0], "250000.00", "USD", utc(days_ahead=3), "critical", "Q4 supplier contract payment — GlobalTech"),
            (ben_ids[8], "85000.00", "GBP", utc(days_ahead=5), "high", "Monthly freight settlement — Stellar Freight"),
            (ben_ids[2], "120000.00", "EUR", utc(days_ahead=7), "high", "Component delivery payment — Nordic Components"),
            (ben_ids[5], "60000.00", "EUR", utc(days_ahead=10), "normal", "Software license renewal — EuroTech GmbH"),
            (ben_ids[3], "45000.00", "SGD", utc(days_ahead=14), "normal", "APAC logistics monthly settlement"),
            (ben_ids[9], "15000.00", "USD", utc(days_ahead=30), "low", "Annual cloud service renewal — Atlas Cloud"),
        ]
        for b_id, amt, cur, due, priority, desc in obligation_data:
            ob = PaymentObligation(
                id=uid(), org_id=org_id, beneficiary_id=b_id,
                amount=amt, currency=cur, due_date=due, priority=priority,
                status="pending", description=desc,
            )
            db.add(ob)

        # ----------------------------------------------------------------
        # Audit Logs — 50+ entries
        # ----------------------------------------------------------------
        audit_events = [
            (admin_id, "admin@kaizen.dev", "admin", "user_created", "user", auditor_id, None, None, "Demo user created during initialization"),
            (admin_id, "admin@kaizen.dev", "admin", "seed_executed", "system", org_id, None, None, "Demo data seed executed"),
            (ops_id, "ops@kaizen.dev", "payment_ops", "payment_created", "payment", payment_ids[7], None, '{"status":"CREATED","amount":"156000","currency":"USD"}', None),
            (ops_id, "ops@kaizen.dev", "payment_ops", "payment_submitted", "payment", payment_ids[7], '{"status":"CREATED"}', '{"status":"SUBMITTED"}', None),
            (treasury_id, "treasury@kaizen.dev", "treasury_manager", "incident_assigned", "incident", incident_ids[0], None, f'{{"assigned_to":"{treasury_id}"}}', "Critical incident escalation"),
            (ops_id, "ops@kaizen.dev", "payment_ops", "payment_created", "payment", payment_ids[0], None, '{"status":"CREATED","amount":"125000","currency":"USD"}', None),
            (ops_id, "ops@kaizen.dev", "payment_ops", "payment_submitted", "payment", payment_ids[0], '{"status":"CREATED"}', '{"status":"SUBMITTED"}', None),
            (ops_id, "ops@kaizen.dev", "payment_ops", "payment_succeeded", "payment", payment_ids[0], '{"status":"SUBMITTED"}', '{"status":"SUCCEEDED"}', "Provider confirmed"),
            (treasury_id, "treasury@kaizen.dev", "treasury_manager", "risk_alert_reviewed", "risk_alert", None, '{"status":"open"}', '{"status":"reviewing"}', "Reviewing duplicate payment alert"),
            (admin_id, "admin@kaizen.dev", "admin", "user_role_updated", "user", ops_id, '{"role":"viewer"}', '{"role":"payment_ops"}', "Role upgrade approved"),
        ]

        for actor_id, actor_email, actor_role, action, entity_type, entity_id, before, after, reason in audit_events:
            al = AuditLog(
                id=uid(), org_id=org_id, actor_id=actor_id, actor_email=actor_email,
                actor_role=actor_role, action=action, entity_type=entity_type,
                entity_id=entity_id, before_state=before, after_state=after,
                reason=reason, created_at=utc(hours_ago=len(audit_events)),
            )
            db.add(al)

        # More audit logs for completeness
        for i, p_id in enumerate(payment_ids[:20]):
            al = AuditLog(
                id=uid(), org_id=org_id, actor_id=ops_id, actor_email="ops@kaizen.dev",
                actor_role="payment_ops", action="payment_created", entity_type="payment",
                entity_id=p_id, after_state=f'{{"status":"CREATED","amount":"{pay_data[i][0]}"}}',
                created_at=utc(days_ago=pay_data[i][5]),
            )
            db.add(al)

        for i, inc_id in enumerate(incident_ids):
            al = AuditLog(
                id=uid(), org_id=org_id, actor_id=ops_id, actor_email="ops@kaizen.dev",
                actor_role="payment_ops", action="incident_created", entity_type="incident",
                entity_id=inc_id, after_state=f'{{"status":"open","severity":"{inc_data[i][2]}"}}',
                created_at=inc_data[i][5],
            )
            db.add(al)

        # Notifications for admin
        notif_data = [
            (admin_id, "alert", "Critical Incident Detected", "Payment PAY-2024000014 shows UNKNOWN status — potential duplicate risk $95,000 USD", "incident", incident_ids[0]),
            (treasury_id, "alert", "SLA Breach Imminent", "Incident INC-2024000007 SLA deadline in 4 hours — urgent review required", "incident", incident_ids[6]),
            (ops_id, "info", "Reconciliation Run Complete", "October reconciliation: 22 matched, 2 unmatched, 1 exception", "reconciliation", recon_run_ids[0]),
            (admin_id, "warning", "Risk Alert: Duplicate Payment", "Potential duplicate detected — $125,000 USD to GlobalTech Supplies", "risk", None),
            (treasury_id, "info", "Treasury Position Update", "USD available balance updated: $487,500.00", "account", acc_usd_id),
        ]
        for user_id, ntype, title, msg, etype, eid in notif_data:
            n = Notification(
                id=uid(), user_id=user_id, type=ntype, title=title, message=msg,
                is_read=False, entity_type=etype, entity_id=eid,
            )
            db.add(n)

        await db.commit()
        print("[SUCCESS] KAIZEN FinTech demo data seeded successfully!")
        print(f"   Organization: Acme Corporation")
        print(f"   Users: admin@kaizen.dev, treasury@kaizen.dev, ops@kaizen.dev, auditor@kaizen.dev")
        print(f"   Password for all: Demo1234!")
        print(f"   Payments: {len(pay_data)} records")
        print(f"   Incidents: {len(inc_data)} records")
        print(f"   Risk Alerts: {len(risk_data)} records")


if __name__ == "__main__":
    asyncio.run(seed())
