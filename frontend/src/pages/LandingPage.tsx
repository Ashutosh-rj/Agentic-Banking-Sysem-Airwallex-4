import React, { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  Shield, Bot, ArrowRight, CheckCircle2, AlertTriangle, Wallet,
  BarChart3, RefreshCw, ChevronDown, ChevronUp, Lock, Zap,
  Layers, FileText, Check, Sparkles, Building2, Terminal
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated, quickDemoLogin } = useAuth();
  const [openFaq, setOpenFaq] = useState<number | null>(0);

  // Demo calculation state for Section 5 example
  const [demoAmount, setDemoAmount] = useState<number>(125000);
  const [riskAssessment, setRiskAssessment] = useState<{
    preventedDuplicationCost: number;
    hoursSaved: number;
    recommendedAction: string;
  }>({
    preventedDuplicationCost: 125000,
    hoursSaved: 4.5,
    recommendedAction: 'HOLD & VERIFY: Ambiguous provider status with identical $125k reference within 15 days.',
  });

  const handleLaunchDemo = async (role: 'admin' | 'treasury_manager' | 'payment_ops' | 'auditor' = 'treasury_manager') => {
    await quickDemoLogin(role);
    navigate('/app');
  };

  const faqs = [
    {
      q: 'How does KAIZEN prevent duplicate payments during provider timeouts?',
      a: 'When an API timeout occurs, KAIZEN preserves the original payment ID and idempotency key, marking the transaction UNKNOWN rather than failed. A database-level lock prevents subsequent retries until an automated investigation queries the provider status or an authorized treasury operator reviews verified evidence.',
    },
    {
      q: 'Does KAIZEN require an active LLM provider API key to operate?',
      a: 'No. KAIZEN is architected with a deterministic financial state machine and a rules-based agentic pipeline that operates reliably in zero-dependency sandbox and production modes. When an LLM key is configured, it enriches root-cause narratives without affecting deterministic financial safety boundaries.',
    },
    {
      q: 'How are multi-currency treasury positions calculated?',
      a: 'KAIZEN uses precise decimal arithmetic (not floating point). Available liquidity = confirmed provider balance minus reserved obligations not yet settled. Currencies are segregated across USD, EUR, GBP, and SGD accounts.',
    },
    {
      q: 'What role-based access controls are enforced?',
      a: 'KAIZEN enforces four distinct roles at the backend API layer: Admin, Treasury Manager (approvals & liquidity), Payment Operations Analyst (investigation & retry execution), and Auditor (immutable read-only log access).',
    },
    {
      q: 'How are reconciliation discrepancies flagged?',
      a: 'Our matching engine evaluates provider statement references, exact timestamps, amounts, and currency. Records are classified into Exact Matches (99%+), Probable Matches (60-98%), and Unmatched Exceptions requiring operator sign-off.',
    },
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-amber-600/20 via-amber-500/10 to-amber-600/20 border-b border-amber-500/20 py-2 px-4 text-center text-xs text-amber-300 flex items-center justify-center gap-2">
        <Sparkles className="w-3.5 h-3.5 text-amber-400" />
        <span>KAIZEN FinTech is live in <strong>Demonstration Simulation Mode</strong> — All financial flows backed by persistent SQLite ledger.</span>
      </div>

      {/* Navigation */}
      <header className="border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-amber-600 to-amber-400 flex items-center justify-center font-bold text-slate-950 text-lg shadow-lg shadow-amber-500/20">
            K
          </div>
          <div>
            <span className="font-extrabold tracking-tight text-slate-100 text-lg flex items-center gap-1.5">
              KAIZEN <span className="text-xs font-semibold bg-amber-500/10 text-amber-400 px-2 py-0.5 rounded border border-amber-500/20">FINTECH</span>
            </span>
          </div>
        </div>

        <nav className="hidden md:flex items-center gap-8 text-sm text-slate-400 font-medium">
          <a href="#capabilities" className="hover:text-amber-400 transition-colors">Capabilities</a>
          <a href="#workflow" className="hover:text-amber-400 transition-colors">Workflow</a>
          <a href="#calculator" className="hover:text-amber-400 transition-colors">Live Incident</a>
          <a href="#security" className="hover:text-amber-400 transition-colors">Controls & Security</a>
          <a href="#faq" className="hover:text-amber-400 transition-colors">FAQ</a>
        </nav>

        <div className="flex items-center gap-3">
          {isAuthenticated ? (
            <button
              onClick={() => navigate('/app')}
              className="bg-amber-500 hover:bg-amber-400 text-slate-950 font-semibold px-4 py-2 rounded-lg text-sm transition-all shadow-md flex items-center gap-2"
            >
              <span>Command Center</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          ) : (
            <>
              <NavLink
                to="/login"
                className="text-slate-300 hover:text-white px-3 py-2 text-sm font-medium transition-colors"
              >
                Sign In
              </NavLink>
              <button
                onClick={() => handleLaunchDemo('treasury_manager')}
                className="bg-amber-500 hover:bg-amber-400 text-slate-950 font-semibold px-4 py-2 rounded-lg text-sm transition-all shadow-md shadow-amber-500/10 flex items-center gap-1.5 cursor-pointer"
              >
                <span>Launch Command Center</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </>
          )}
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative pt-20 pb-16 px-6 max-w-6xl mx-auto text-center overflow-hidden">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900 border border-slate-800 text-amber-400 text-xs font-medium mb-6">
          <Bot className="w-3.5 h-3.5" />
          <span>Autonomous Treasury Command & Payment Operations</span>
        </div>

        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-slate-100 max-w-4xl mx-auto leading-tight">
          Your Treasury Operations. <br />
          <span className="bg-gradient-to-r from-amber-400 via-amber-300 to-yellow-500 bg-clip-text text-transparent">
            Under Intelligent Command.
          </span>
        </h1>

        <p className="mt-6 text-lg sm:text-xl text-slate-400 max-w-2xl mx-auto font-normal leading-relaxed">
          Investigate payment incidents, reconcile transactions, protect liquidity, and resolve operational exceptions through explainable AI and deterministic financial workflows.
        </p>

        <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
          <button
            onClick={() => handleLaunchDemo('treasury_manager')}
            className="w-full sm:w-auto bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold px-7 py-3 rounded-xl text-base shadow-xl shadow-amber-500/20 flex items-center justify-center gap-2 transition-transform hover:-translate-y-0.5 cursor-pointer"
          >
            <span>Launch Command Center</span>
            <ArrowRight className="w-5 h-5" />
          </button>
          <button
            onClick={() => handleLaunchDemo('auditor')}
            className="w-full sm:w-auto bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 font-semibold px-6 py-3 rounded-xl text-base transition-colors flex items-center justify-center gap-2 cursor-pointer"
          >
            <Shield className="w-4 h-4 text-slate-400" />
            <span>Explore Auditor View</span>
          </button>
        </div>

        {/* Live-looking Command Center Preview */}
        <div className="mt-14 p-2 rounded-2xl bg-gradient-to-b from-slate-800 to-slate-900 border border-slate-800 shadow-2xl">
          <div className="bg-slate-950 rounded-xl p-4 sm:p-6 border border-slate-800/80 text-left">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-6">
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-rose-500/80" />
                <span className="w-3 h-3 rounded-full bg-amber-500/80" />
                <span className="w-3 h-3 rounded-full bg-emerald-500/80" />
                <span className="ml-2 font-mono text-xs text-slate-500">kaizen://command-center.treasury/live</span>
              </div>
              <div className="flex items-center gap-2 text-xs text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-md border border-emerald-500/20">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                <span>Live Autonomous Engine Active</span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-xl">
                <p className="text-xs text-slate-400 font-medium">Available Liquidity</p>
                <p className="text-2xl font-bold text-slate-100 mt-1 font-mono">$941,500.00</p>
                <span className="text-[10px] text-emerald-400 mt-1 inline-block">4 Currencies Segregated</span>
              </div>
              <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-xl">
                <p className="text-xs text-slate-400 font-medium">Committed / Pending</p>
                <p className="text-2xl font-bold text-amber-400 mt-1 font-mono">$488,000.00</p>
                <span className="text-[10px] text-slate-400 mt-1 inline-block">6 Pending Obligations</span>
              </div>
              <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-xl">
                <p className="text-xs text-slate-400 font-medium">Open Incidents</p>
                <p className="text-2xl font-bold text-rose-400 mt-1 font-mono">10 Active</p>
                <span className="text-[10px] text-rose-400 mt-1 inline-block">2 Critical (Duplicate / UNKNOWN)</span>
              </div>
              <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-xl">
                <p className="text-xs text-slate-400 font-medium">Prevented Loss Exposure</p>
                <p className="text-2xl font-bold text-emerald-400 mt-1 font-mono">$125,000.00</p>
                <span className="text-[10px] text-slate-400 mt-1 inline-block">1 Duplicate Intercepted</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Business Problem Section */}
      <section className="py-16 px-6 border-t border-slate-800/80 bg-slate-900/20">
        <div className="max-w-6xl mx-auto">
          <div className="text-center max-w-3xl mx-auto mb-12">
            <h2 className="text-xs font-semibold text-amber-400 tracking-wider uppercase">The Problem We Solve</h2>
            <p className="text-3xl font-bold text-slate-100 mt-2">The Cost of Financial Uncertainty in Global Treasury</p>
            <p className="text-slate-400 mt-3 text-sm">
              Organizations lose millions in operational efficiency, duplicated wire transfers, and delayed supplier relations when payment outcomes remain ambiguous.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-6 rounded-xl bg-slate-900/60 border border-slate-800">
              <div className="w-10 h-10 rounded-lg bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-400 mb-4">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-semibold text-slate-200">Timeout Ambiguity & Duplicate Risk</h3>
              <p className="text-sm text-slate-400 mt-2">
                A provider gateway times out. Does the analyst press retry? An ordinary second submission risks triggering an unauthorized duplicate payment.
              </p>
            </div>

            <div className="p-6 rounded-xl bg-slate-900/60 border border-slate-800">
              <div className="w-10 h-10 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400 mb-4">
                <RefreshCw className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-semibold text-slate-200">Manual Reconciliation Latency</h3>
              <p className="text-sm text-slate-400 mt-2">
                Finance teams spend days matching bank statement lines against internal ledgers, resulting in delayed vendor releases and SLA breaches.
              </p>
            </div>

            <div className="p-6 rounded-xl bg-slate-900/60 border border-slate-800">
              <div className="w-10 h-10 rounded-lg bg-sky-500/10 border border-sky-500/20 flex items-center justify-center text-sky-400 mb-4">
                <Wallet className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-semibold text-slate-200">Fragmented Multi-Currency Liquidity</h3>
              <p className="text-sm text-slate-400 mt-2">
                Balances scattered across accounts without real-time reservation accounting cause false insufficient-funds errors and missed working capital discounts.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Capabilities Section */}
      <section id="capabilities" className="py-20 px-6 border-t border-slate-800/80">
        <div className="max-w-6xl mx-auto">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-xs font-semibold text-amber-400 tracking-wider uppercase">Engineered for Reliability</h2>
            <p className="text-3xl font-bold text-slate-100 mt-2">Six Enterprise Treasury Principles</p>
            <p className="text-slate-400 mt-3 text-sm">
              Implemented as functional business logic, calculations, and auditable workflows.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                title: 'Treasury & Cash Management',
                desc: 'Available liquidity formula: confirmed balance minus active commitments. Decimal-precision multi-currency balance ledgers.',
                icon: Wallet,
              },
              {
                title: 'Payment Reconciliation',
                desc: 'Multi-parameter matching algorithm matching UETR, provider refs, dates, and amounts with confidence ratings.',
                icon: CheckCircle2,
              },
              {
                title: 'Risk & Internal Controls',
                desc: 'Deterministic rules blocking ambiguous retries, detecting 24-hour duplicate amounts, and requiring 4-eyes approval.',
                icon: Shield,
              },
              {
                title: 'Working Capital Management',
                desc: 'SLA-based priority ranking factoring vendor criticality, contractual due date, and cash-flow obligations.',
                icon: Layers,
              },
              {
                title: 'Operations & SLA Prioritization',
                desc: 'Automatic countdown clocks with tiered escalation rules before deadlines cause penalties or supply disruptions.',
                icon: Zap,
              },
              {
                title: 'Cost-Benefit & Operational ROI',
                desc: 'Auditable calculations of prevented duplicate exposure, operator hours saved, and SLA compliance metrics.',
                icon: BarChart3,
              },
            ].map((cap, idx) => {
              const Icon = cap.icon;
              return (
                <div key={idx} className="p-6 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 transition-colors">
                  <div className="w-10 h-10 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400 mb-4">
                    <Icon className="w-5 h-5" />
                  </div>
                  <h4 className="text-base font-semibold text-slate-200">{cap.title}</h4>
                  <p className="text-sm text-slate-400 mt-2 leading-relaxed">{cap.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* 7-Agent Pipeline Workflow */}
      <section id="workflow" className="py-20 px-6 border-t border-slate-800/80 bg-slate-900/30">
        <div className="max-w-6xl mx-auto">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-xs font-semibold text-amber-400 tracking-wider uppercase">Deterministic Intelligence</h2>
            <p className="text-3xl font-bold text-slate-100 mt-2">The 7-Step Agentic Investigation Pipeline</p>
            <p className="text-slate-400 mt-3 text-sm">
              Every payment incident undergoes specialized diagnostic stages. Transparent, verifiable, and explainable.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-7 gap-3 text-center">
            {[
              { num: '01', name: 'Intake Agent', role: 'Severity & Category' },
              { num: '02', name: 'Payment Inv.', role: 'State Machine & Logs' },
              { num: '03', name: 'Reconciliation', role: 'Provider Discrepancies' },
              { num: '04', name: 'Root Cause', role: 'Deterministic Diagnostics' },
              { num: '05', name: 'Treasury Dec.', role: 'Liquidity Impact' },
              { num: '06', name: 'Action Plan', role: 'Approval Policy' },
              { num: '07', name: 'Business Imp.', role: 'ROI & Saved Exposure' },
            ].map((agent, i) => (
              <div key={i} className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 flex flex-col justify-between">
                <div>
                  <span className="font-mono text-xs text-amber-400 font-bold">{agent.num}</span>
                  <h5 className="text-sm font-semibold text-slate-200 mt-2">{agent.name}</h5>
                </div>
                <p className="text-[11px] text-slate-400 mt-3">{agent.role}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Live Calculator Section */}
      <section id="calculator" className="py-20 px-6 border-t border-slate-800/80">
        <div className="max-w-4xl mx-auto bg-slate-900 border border-slate-800 rounded-2xl p-8">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 pb-6 border-b border-slate-800">
            <div>
              <span className="text-xs font-semibold text-amber-400 uppercase tracking-wider">Interactive Diagnostic Model</span>
              <h3 className="text-2xl font-bold text-slate-100 mt-1">Simulate Incident Evaluation</h3>
              <p className="text-sm text-slate-400 mt-1">Adjust payment value to observe KAIZEN duplicate protection & decision rules.</p>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm text-slate-400">Payment Amount:</span>
              <input
                type="number"
                value={demoAmount}
                onChange={(e) => {
                  const val = Number(e.target.value);
                  setDemoAmount(val);
                  setRiskAssessment({
                    preventedDuplicationCost: val,
                    hoursSaved: Math.round((val / 25000) * 10) / 10 + 2,
                    recommendedAction: val > 100000
                      ? 'REQUIRE 4-EYES APPROVAL: Amount exceeds $100k threshold. Automatic lock active.'
                      : 'STANDARD RETRY PROTOCOL: Awaiting webhook signature verification.',
                  });
                }}
                className="bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-sm font-mono text-amber-400 w-36"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-6">
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
              <p className="text-xs text-slate-400">Potential Duplicate Exposure Prevented</p>
              <p className="text-2xl font-bold text-emerald-400 mt-2 font-mono">
                ${riskAssessment.preventedDuplicationCost.toLocaleString()}.00
              </p>
              <p className="text-[10px] text-slate-500 mt-1">Protected from double debiting</p>
            </div>
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
              <p className="text-xs text-slate-400">Estimated Operator Time Saved</p>
              <p className="text-2xl font-bold text-amber-400 mt-2 font-mono">{riskAssessment.hoursSaved} Hours</p>
              <p className="text-[10px] text-slate-500 mt-1">Automated evidence collation</p>
            </div>
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
              <p className="text-xs text-slate-400">Rule Trigger</p>
              <p className="text-sm font-semibold text-rose-400 mt-2">{riskAssessment.recommendedAction}</p>
            </div>
          </div>
        </div>
      </section>

      {/* Security & Oversight */}
      <section id="security" className="py-20 px-6 border-t border-slate-800/80 bg-slate-900/20">
        <div className="max-w-6xl mx-auto">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-xs font-semibold text-amber-400 tracking-wider uppercase">Zero Trust Architecture</h2>
            <p className="text-3xl font-bold text-slate-100 mt-2">Internal Controls & Human Oversight</p>
            <p className="text-slate-400 mt-3 text-sm">
              AI agents advise, human treasury officers execute. No unverified autonomous movement of capital.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="p-6 rounded-xl bg-slate-900/60 border border-slate-800">
              <Lock className="w-6 h-6 text-amber-400 mb-4" />
              <h4 className="text-base font-semibold text-slate-200">Enforced Idempotency</h4>
              <p className="text-sm text-slate-400 mt-2 leading-relaxed">
                Unique idempotency keys per transaction prevent double-submission even when networks experience jitter or concurrent requests.
              </p>
            </div>
            <div className="p-6 rounded-xl bg-slate-900/60 border border-slate-800">
              <Building2 className="w-6 h-6 text-amber-400 mb-4" />
              <h4 className="text-base font-semibold text-slate-200">Strict Role Separation</h4>
              <p className="text-sm text-slate-400 mt-2 leading-relaxed">
                Separation of duties ensures that payment creators cannot approve threshold exceptions or modify audit records.
              </p>
            </div>
            <div className="p-6 rounded-xl bg-slate-900/60 border border-slate-800">
              <Terminal className="w-6 h-6 text-amber-400 mb-4" />
              <h4 className="text-base font-semibold text-slate-200">Immutable Audit Trail</h4>
              <p className="text-sm text-slate-400 mt-2 leading-relaxed">
                Every state transition, actor ID, timestamp, and diff is cryptographically logged and exportable for statutory audits.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ Accordion */}
      <section id="faq" className="py-20 px-6 border-t border-slate-800/80">
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-xs font-semibold text-amber-400 tracking-wider uppercase">Answers</h2>
            <p className="text-3xl font-bold text-slate-100 mt-2">Frequently Asked Questions</p>
          </div>

          <div className="space-y-4">
            {faqs.map((faq, idx) => (
              <div key={idx} className="border border-slate-800 rounded-xl bg-slate-900/50 overflow-hidden">
                <button
                  onClick={() => setOpenFaq(openFaq === idx ? null : idx)}
                  className="w-full p-5 text-left flex items-center justify-between font-semibold text-slate-200 text-sm hover:text-amber-400 transition-colors"
                >
                  <span>{faq.q}</span>
                  {openFaq === idx ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
                </button>
                {openFaq === idx && (
                  <div className="px-5 pb-5 text-sm text-slate-400 leading-relaxed border-t border-slate-800/50 pt-3">
                    {faq.a}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Final Call to Action */}
      <section className="py-20 px-6 border-t border-slate-800/80 bg-gradient-to-b from-slate-900/40 to-slate-950 text-center">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-100">
            Ready to Take Command of Your Treasury?
          </h2>
          <p className="text-slate-400 mt-4 text-base">
            Eliminate payment uncertainty today. Test with pre-seeded enterprise scenarios in demo mode.
          </p>
          <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
            <button
              onClick={() => handleLaunchDemo('treasury_manager')}
              className="bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold px-8 py-3.5 rounded-xl text-base shadow-xl shadow-amber-500/20 flex items-center gap-2 cursor-pointer transition-transform hover:-translate-y-0.5"
            >
              <span>Launch Live Command Center</span>
              <ArrowRight className="w-5 h-5" />
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-800 py-10 px-6 bg-slate-950 text-xs text-slate-500">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-2.5">
            <div className="w-6 h-6 rounded bg-amber-500 flex items-center justify-center font-bold text-slate-950 text-xs">
              K
            </div>
            <span className="font-semibold text-slate-300">KAIZEN FinTech</span>
            <span>— "Every Payment Accounted For. Every Decision Explained."</span>
          </div>

          <div className="flex items-center gap-6">
            <NavLink to="/app" className="hover:text-slate-300">App</NavLink>
            <NavLink to="/login" className="hover:text-slate-300">Sign In</NavLink>
            <a href="/docs" target="_blank" rel="noreferrer" className="hover:text-slate-300">FastAPI Docs</a>
            <a href="/health/ready" target="_blank" rel="noreferrer" className="hover:text-slate-300">Health Probe</a>
          </div>
        </div>
      </footer>
    </div>
  );
};
