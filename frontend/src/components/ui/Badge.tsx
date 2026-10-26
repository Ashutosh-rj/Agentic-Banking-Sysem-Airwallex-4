import React from 'react';
import clsx from 'clsx';

export interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info' | 'purple' | 'amber';
  size?: 'sm' | 'md';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'default',
  size = 'sm',
  className,
}) => {
  const variantStyles = {
    default: 'bg-slate-800 text-slate-300 border-slate-700',
    success: 'bg-emerald-950/80 text-emerald-400 border-emerald-800/60',
    warning: 'bg-amber-950/80 text-amber-400 border-amber-800/60',
    danger: 'bg-rose-950/80 text-rose-400 border-rose-800/60',
    info: 'bg-sky-950/80 text-sky-400 border-sky-800/60',
    purple: 'bg-purple-950/80 text-purple-400 border-purple-800/60',
    amber: 'bg-amber-500/10 text-amber-500 border-amber-500/30',
  };

  const sizeStyles = {
    sm: 'text-xs px-2.5 py-0.5',
    md: 'text-sm px-3 py-1',
  };

  return (
    <span
      className={clsx(
        'inline-flex items-center font-medium rounded-full border',
        variantStyles[variant],
        sizeStyles[size],
        className
      )}
    >
      {children}
    </span>
  );
};

export const StatusBadge: React.FC<{ status: string }> = ({ status }) => {
  const normalized = status?.toUpperCase() || 'UNKNOWN';

  let variant: BadgeProps['variant'] = 'default';
  if (['SUCCEEDED', 'RESOLVED', 'MATCHED', 'CONNECTED', 'HEALTHY'].includes(normalized)) {
    variant = 'success';
  } else if (['PENDING', 'SUBMITTED', 'VALIDATING', 'INVESTIGATING', 'REVIEWING', 'PROBABLE_MATCH'].includes(normalized)) {
    variant = 'warning';
  } else if (['FAILED', 'CRITICAL', 'CONFLICT', 'DISCONNECTED'].includes(normalized)) {
    variant = 'danger';
  } else if (['UNKNOWN', 'REQUIRES_REVIEW', 'DUPLICATE_CANDIDATE', 'HIGH'].includes(normalized)) {
    variant = 'purple';
  } else if (['OPEN', 'CREATED', 'INFO'].includes(normalized)) {
    variant = 'info';
  }

  return (
    <Badge variant={variant}>
      <span className="w-1.5 h-1.5 rounded-full mr-1.5 bg-current opacity-75" />
      {status}
    </Badge>
  );
};
