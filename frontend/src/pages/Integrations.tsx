import React, { useState, useEffect } from 'react';
import {
  Plug, CheckCircle2, AlertTriangle, RefreshCw, Zap,
  ShieldCheck, Lock, ExternalLink, Activity
} from 'lucide-react';
import { integrationService } from '../services/domainServices';
import { IntegrationStatus } from '../types';
import { StatusBadge, Badge } from '../components/ui/Badge';
import { Modal } from '../components/ui/Modal';
import { getErrorMessage } from '../services/api';

export const Integrations: React.FC = () => {
  const [integrations, setIntegrations] = useState<IntegrationStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [testingId, setTestingId] = useState<string | null>(null);
  const [testResult, setTestResult] = useState<any>(null);

  const fetchIntegrations = async () => {
    setLoading(true);
    try {
      const res = await integrationService.list();
      setIntegrations(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIntegrations();
  }, []);

  const handleTestConnection = async (id: string) => {
    setTestingId(id);
    try {
      const res = await integrationService.test(id);
      setTestResult(res);
    } catch (err) {
      alert(getErrorMessage(err));
    } finally {
      setTestingId(null);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h1 className="text-xl font-bold text-slate-100 tracking-tight flex items-center gap-2">
            <span>Payment Rails & Integrations</span>
            <span className="text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded font-mono">
              GATEWAY STATUS
            </span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Real-time health status, latency metrics, and diagnostic probes for external clearing networks.
          </p>
        </div>
      </div>

      {/* Integration Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {integrations.map((item) => (
          <div key={item.id} className="p-5 rounded-xl bg-slate-900 border border-slate-800 flex flex-col justify-between space-y-4">
            <div>
              <div className="flex items-start justify-between">
                <div>
                  <span className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold block">{item.category}</span>
                  <h3 className="text-base font-bold text-slate-100 mt-0.5">{item.name}</h3>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant={item.mode === 'sandbox' ? 'amber' : 'purple'}>
                    {item.mode.toUpperCase()}
                  </Badge>
                  <StatusBadge status={item.status} />
                </div>
              </div>

              <div className="mt-4 p-3 bg-slate-950 rounded-lg border border-slate-800/80 space-y-2 text-xs">
                <div className="flex justify-between text-slate-400">
                  <span>Endpoint URL:</span>
                  <span className="font-mono text-slate-200 truncate max-w-[200px]">{item.endpoint_url}</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Roundtrip Latency:</span>
                  <span className="font-mono text-emerald-400">{item.latency_ms || 120} ms</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Credential Status:</span>
                  <span className="text-slate-200 flex items-center gap-1">
                    <Lock className="w-3 h-3 text-emerald-400" />
                    <span>Server-Side Stored (Protected)</span>
                  </span>
                </div>
              </div>

              {/* Supported Features */}
              <div className="mt-3">
                <span className="text-[11px] text-slate-500 block mb-1.5 font-medium">Supported Capabilities:</span>
                <div className="flex flex-wrap gap-1.5">
                  {item.features.map((f, i) => (
                    <span key={i} className="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded border border-slate-700/60">
                      {f}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Test Connection Button */}
            <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between">
              <span className="text-[10px] text-slate-500">
                Pings health probe endpoint
              </span>
              <button
                onClick={() => handleTestConnection(item.id)}
                disabled={testingId === item.id}
                className="px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-lg text-xs font-semibold transition-colors flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
              >
                <Activity className={`w-3.5 h-3.5 text-amber-400 ${testingId === item.id ? 'animate-spin' : ''}`} />
                <span>{testingId === item.id ? 'Testing...' : 'Test Connection'}</span>
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Test Diagnostic Result Modal */}
      {testResult && (
        <Modal
          isOpen={!!testResult}
          onClose={() => setTestResult(null)}
          title="Integration Connection Diagnostic"
          description={`Tested at ${new Date(testResult.tested_at).toLocaleTimeString()}`}
          maxWidth="md"
        >
          <div className="space-y-4 text-xs">
            <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 rounded-lg flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
              <span>{testResult.message}</span>
            </div>

            <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg space-y-1.5 font-mono text-[11px]">
              <div className="flex justify-between text-slate-400">
                <span>Latency:</span>
                <span className="text-emerald-400 font-bold">{testResult.latency_ms} ms</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>HTTP Response:</span>
                <span className="text-slate-200">{testResult.diagnostics.http_status} OK</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Security / TLS:</span>
                <span className="text-slate-200">{testResult.diagnostics.tls_version}</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Rate Limit Headroom:</span>
                <span className="text-slate-200">{testResult.diagnostics.rate_limit_remaining} requests remaining</span>
              </div>
            </div>

            <button
              onClick={() => setTestResult(null)}
              className="w-full bg-slate-800 hover:bg-slate-700 text-slate-200 py-2 rounded-lg font-medium text-xs transition-colors"
            >
              Close Diagnostic
            </button>
          </div>
        </Modal>
      )}
    </div>
  );
};
