import React, { useState } from 'react';
import {
  Settings as SettingsIcon, Shield, Bell, Globe, Check,
  Save, AlertCircle, Building, Key
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const Settings: React.FC = () => {
  const { user } = useAuth();
  const [baseCurrency, setBaseCurrency] = useState('USD');
  const [timezone, setTimezone] = useState('UTC');
  const [singleApprovalLimit, setSingleApprovalLimit] = useState('100000');
  const [requireDualApproval, setRequireDualApproval] = useState(true);
  const [emailAlerts, setEmailAlerts] = useState(true);
  const [slaAlertHours, setSlaAlertHours] = useState('4');
  const [saved, setSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h1 className="text-xl font-bold text-slate-100 tracking-tight flex items-center gap-2">
            <span>Workspace Settings & Governance</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Configure internal financial approval limits, SLA escalation thresholds, and organizational parameters.
          </p>
        </div>
      </div>

      {saved && (
        <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs rounded-xl flex items-center gap-2">
          <Check className="w-4 h-4 flex-shrink-0" />
          <span>Governance and workspace settings updated successfully.</span>
        </div>
      )}

      <form onSubmit={handleSave} className="space-y-6">
        {/* User Identity & Workspace Card */}
        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-4 text-xs">
          <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
            <Building className="w-4 h-4 text-amber-400" />
            <span>Organization Profile</span>
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-slate-400 mb-1">Company Workspace</label>
              <input
                type="text"
                disabled
                value="Acme Corporation (Demo Tenant)"
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-300 opacity-80"
              />
            </div>
            <div>
              <label className="block text-slate-400 mb-1">Current Active Persona</label>
              <input
                type="text"
                disabled
                value={`${user?.full_name} (${user?.role})`}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-300 opacity-80"
              />
            </div>
          </div>
        </div>

        {/* Financial Approval Thresholds */}
        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-4 text-xs">
          <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
            <Shield className="w-4 h-4 text-amber-400" />
            <span>Internal Controls & Approval Policies</span>
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-slate-400 mb-1">Single-Transaction Soft Limit (USD)</label>
              <input
                type="number"
                value={singleApprovalLimit}
                onChange={(e) => setSingleApprovalLimit(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-100 font-mono"
              />
              <span className="text-[10px] text-slate-500 mt-1 block">Wires exceeding this amount trigger a Risk Alert</span>
            </div>

            <div>
              <label className="block text-slate-400 mb-1">SLA Urgent Escalation Buffer</label>
              <select
                value={slaAlertHours}
                onChange={(e) => setSlaAlertHours(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-100"
              >
                <option value="2">2 Hours before breach</option>
                <option value="4">4 Hours before breach</option>
                <option value="8">8 Hours before breach</option>
              </select>
            </div>
          </div>

          <div className="flex items-center justify-between p-3 rounded-lg bg-slate-950 border border-slate-800/80">
            <div>
              <p className="font-semibold text-slate-200">Enforce 4-Eyes Principle for Ambiguous Retries</p>
              <p className="text-[11px] text-slate-400 mt-0.5">
                Prohibits the same operator who initiated a failed wire from authorizing its retry.
              </p>
            </div>
            <input
              type="checkbox"
              checked={requireDualApproval}
              onChange={(e) => setRequireDualApproval(e.target.checked)}
              className="accent-amber-500 w-4 h-4 cursor-pointer"
            />
          </div>
        </div>

        {/* Currency & Localization */}
        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-4 text-xs">
          <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
            <Globe className="w-4 h-4 text-amber-400" />
            <span>Localization & Base Currency</span>
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-slate-400 mb-1">Primary Reporting Currency</label>
              <select
                value={baseCurrency}
                onChange={(e) => setBaseCurrency(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-100"
              >
                <option value="USD">USD ($) - United States Dollar</option>
                <option value="EUR">EUR (€) - Euro</option>
                <option value="GBP">GBP (£) - British Pound</option>
                <option value="SGD">SGD (S$) - Singapore Dollar</option>
              </select>
            </div>

            <div>
              <label className="block text-slate-400 mb-1">Treasury Working Timezone</label>
              <select
                value={timezone}
                onChange={(e) => setTimezone(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-100"
              >
                <option value="UTC">UTC (Coordinated Universal Time)</option>
                <option value="America/New_York">America/New York (EST/EDT)</option>
                <option value="Europe/London">Europe/London (GMT/BST)</option>
                <option value="Asia/Singapore">Asia/Singapore (SGT)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Submit */}
        <div className="flex items-center justify-end">
          <button
            type="submit"
            className="px-5 py-2.5 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold rounded-lg text-xs transition-colors flex items-center gap-2 cursor-pointer shadow-md"
          >
            <Save className="w-4 h-4" />
            <span>Save Governance Policies</span>
          </button>
        </div>
      </form>
    </div>
  );
};
