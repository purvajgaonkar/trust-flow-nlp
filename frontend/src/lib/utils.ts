import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import type { AttackType, RiskLevel } from '../types';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function getRiskColor(level: RiskLevel): string {
  const colors: Record<RiskLevel, string> = {
    SAFE: '#22c55e',
    LOW: '#84cc16',
    MEDIUM: '#f59e0b',
    HIGH: '#f97316',
    CRITICAL: '#ef4444',
  };
  return colors[level] || '#94a3b8';
}

export function getRiskClass(level: RiskLevel): string {
  const classes: Record<RiskLevel, string> = {
    SAFE: 'risk-safe',
    LOW: 'risk-low',
    MEDIUM: 'risk-medium',
    HIGH: 'risk-high',
    CRITICAL: 'risk-critical',
  };
  return classes[level] || 'risk-safe';
}

export function getAttackLabel(type: AttackType): string {
  const labels: Record<AttackType, string> = {
    SAFE: 'Safe',
    DIRECT_INJECTION: 'Direct Injection',
    INDIRECT_INJECTION: 'Indirect Injection',
    JAILBREAK: 'Jailbreak',
    SYSTEM_PROMPT_EXTRACTION: 'System Prompt Extraction',
    DATA_EXFILTRATION: 'Data Exfiltration',
    ROLE_MANIPULATION: 'Role Manipulation',
    OBFUSCATION: 'Obfuscation Attack',
    MULTILINGUAL_ATTACK: 'Multilingual Attack',
    UNKNOWN_ATTACK: 'Unknown Attack',
  };
  return labels[type] || type;
}

export function formatPercent(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

export function formatScore(value: number): string {
  return value.toFixed(3);
}

export function formatMs(ms: number): string {
  if (ms < 1000) return `${ms.toFixed(0)}ms`;
  return `${(ms / 1000).toFixed(2)}s`;
}

export function getNLIColor(label: string): string {
  const colors: Record<string, string> = {
    ENTAILMENT: '#22c55e',
    CONTRADICTION: '#ef4444',
    NEUTRAL: '#f59e0b',
  };
  return colors[label] || '#94a3b8';
}

export function truncate(text: string, maxLen = 100): string {
  if (text.length <= maxLen) return text;
  return text.slice(0, maxLen) + '…';
}
