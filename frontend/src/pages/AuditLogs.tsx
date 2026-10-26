import React, { useState, useEffect } from 'react';
import {
  History, Download, Filter, Search, FileJson, FileSpreadsheet,
  Clock, Shield, User as UserIcon
} from 'lucide-react';
import { auditService } from '../services/domainServices';
import { AuditLog } from '../types';
import { getErrorMessage } from '../services/api';

export const AuditLogs: React.FC = () => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [entityFilter, setEntityFilter] = useState('');
  const [loading, setLoading] = useState(true);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const res = await auditService.list({
        page,
        page_size: 25,
        entity_type: entityFilter || undefined,
      });
      setLogs(res.items);
      setTotal(res.total);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [page, entityFilter]);

  const handleExport = (format: 'csv' | 'json') => {
    window.open(auditService.getExportUrl(format), '_blank');
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h1 className="text-xl font-bold text-slate-100 tracking-tight flex items-center gap-2">
            <span>Immutable Audit Trail</span>
            <span className="text-xs bg-slate-800 text-slate-300 border border-slate-700 px-2 py-0.5 rounded font-mono">
              TAMPER-EVIDENT
            </span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Statutory log of all financial operations, agent decisions, state transitions, and operator interventions.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => handleExport('csv')}
            className="flex items-center gap-1.5 text-xs bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 px-3 py-1.5 rounded-lg transition-colors cursor-pointer"
          >
            <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-400" />
            <span>Export CSV</span>
          </button>
          <button
            onClick={() => handleExport('json')}
            className="flex items-center gap-1.5 text-xs bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 px-3 py-1.5 rounded-lg transition-colors cursor-pointer"
          >
            <FileJson className="w-3.5 h-3.5 text-amber-400" />
            <span>Export JSON</span>
          </button>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="flex items-center gap-3 bg-slate-900 p-3 rounded-xl border border-slate-800 text-xs">
        <span className="text-slate-500 flex items-center gap-1">
          <Filter className="w-3 h-3" /> Entity:
        </span>
        {['', 'payment', 'incident', 'user', 'risk_alert', 'system'].map((ent) => (
          <button
            key={ent}
            onClick={() => {
              setEntityFilter(ent);
              setPage(1);
            }}
            className={`px-2.5 py-1 rounded-md capitalize font-medium transition-colors cursor-pointer ${
              entityFilter === ent
                ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                : 'bg-slate-950 text-slate-400 hover:text-slate-200 border border-slate-800'
            }`}
          >
            {ent || 'All Entities'}
          </button>
        ))}
      </div>

      {/* Audit Log Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/80 border-b border-slate-800 text-slate-400 uppercase font-semibold text-[10px] tracking-wider">
              <tr>
                <th className="py-3 px-4">Timestamp (UTC)</th>
                <th className="py-3 px-4">Actor</th>
                <th className="py-3 px-4">Action</th>
                <th className="py-3 px-4">Entity Type</th>
                <th className="py-3 px-4">Target ID</th>
                <th className="py-3 px-4">Audit Justification</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono text-[11px]">
              {logs.map((log) => (
                <tr key={log.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3 px-4 text-slate-400">
                    {new Date(log.created_at).toISOString().replace('T', ' ').substring(0, 19)}
                  </td>
                  <td className="py-3 px-4 text-slate-200">
                    <div>
                      <span>{log.actor_email || 'system-orchestrator'}</span>
                      {log.actor_role && (
                        <span className="text-[10px] text-amber-400/80 block uppercase">
                          {log.actor_role}
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="py-3 px-4 font-bold text-slate-100">
                    {log.action}
                  </td>
                  <td className="py-3 px-4 text-slate-400 uppercase text-[10px]">
                    {log.entity_type}
                  </td>
                  <td className="py-3 px-4 text-slate-500">
                    {log.entity_id ? log.entity_id.substring(0, 8) + '...' : '—'}
                  </td>
                  <td className="py-3 px-4 text-slate-300 font-sans text-xs">
                    {log.reason || 'Standard automated state transition'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="p-3 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400 bg-slate-950/40">
          <span>Showing {logs.length} of {total} audit records</span>
          <div className="flex items-center gap-2">
            <button
              disabled={page <= 1}
              onClick={() => setPage(page - 1)}
              className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-slate-200 cursor-pointer"
            >
              Previous
            </button>
            <span className="px-2 font-mono">Page {page}</span>
            <button
              disabled={page * 25 >= total}
              onClick={() => setPage(page + 1)}
              className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-slate-200 cursor-pointer"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
