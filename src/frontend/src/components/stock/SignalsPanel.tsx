'use client'

// SignalsPanel — 숨겨진 인사이트 & 주요 시그널 패널
// AdGate 잠금 내부에서 사용 (AnalysisSection의 insights 탭에서 호출)

import { clsx } from 'clsx'
import type { Signal } from '@/types/stock'

interface SignalsPanelProps {
  ticker: string
  signals?: Signal[]
  insightSummary?: string
}

/** 시그널 강도 표시 */
function StrengthBar({ strength }: { strength: Signal['strength'] }) {
  const bars = { STRONG: 3, MODERATE: 2, WEAK: 1 }
  const count = bars[strength]
  const labels = { STRONG: '강', MODERATE: '중', WEAK: '약' }

  return (
    <div className="flex items-center gap-1">
      {[1, 2, 3].map((i) => (
        <div
          key={i}
          className={clsx(
            'w-1.5 h-4 rounded-full',
            i <= count ? 'bg-primary' : 'bg-border'
          )}
        />
      ))}
      <span className="text-xs text-text-muted ml-1">{labels[strength]}</span>
    </div>
  )
}

export default function SignalsPanel({ ticker, signals, insightSummary }: SignalsPanelProps) {
  const displaySignals = signals && signals.length > 0 ? signals : []

  const signalColors: Record<Signal['type'], { bg: string; text: string; border: string; label: string }> = {
    BUY: { bg: 'bg-rise/10', text: 'text-rise', border: 'border-rise/20', label: '매수' },
    SELL: { bg: 'bg-fall/10', text: 'text-fall', border: 'border-fall/20', label: '매도' },
    HOLD: { bg: 'bg-warning/10', text: 'text-warning', border: 'border-warning/20', label: '보유' },
    WATCH: { bg: 'bg-primary/10', text: 'text-primary', border: 'border-primary/20', label: '관찰' },
  }

  return (
    <div className="space-y-4">
      {/* 헤더 */}
      <div className="flex items-center gap-2">
        <span className="text-lg">🔍</span>
        <div>
          <h3 className="font-bold text-text-primary">숨겨진 인사이트</h3>
          <p className="text-xs text-text-muted">일반 투자자들이 놓치기 쉬운 핵심 신호</p>
        </div>
      </div>

      {/* AI 요약 */}
      <div className="p-4 bg-surface rounded-xl border border-primary/20">
        <div className="flex items-start gap-2">
          <span className="text-primary text-lg shrink-0">✦</span>
          <p className="text-sm text-text-secondary leading-relaxed">
            {insightSummary ||
              `${ticker} 종목에 대한 숨겨진 인사이트를 분석 중입니다.`}
          </p>
        </div>
      </div>

      {/* 시그널 목록 */}
      {displaySignals.length > 0 ? (
        <div className="space-y-3">
          <h4 className="text-sm font-semibold text-text-primary">주요 시그널</h4>
          {displaySignals.map((signal, i) => {
            const style = signalColors[signal.type]
            return (
              <div
                key={i}
                className={clsx(
                  'flex items-start gap-3 p-3 rounded-xl border',
                  style.bg,
                  style.border
                )}
              >
                {/* 시그널 타입 배지 */}
                <span
                  className={clsx(
                    'text-xs font-bold px-2 py-0.5 rounded-md shrink-0',
                    style.bg,
                    style.text,
                    'border',
                    style.border
                  )}
                >
                  {style.label}
                </span>

                <div className="flex-1 min-w-0">
                  <p className="text-sm text-text-primary">{signal.reason}</p>
                  {signal.indicator && (
                    <p className="text-xs text-text-muted mt-1">📌 {signal.indicator}</p>
                  )}
                </div>

                {/* 강도 */}
                <StrengthBar strength={signal.strength} />
              </div>
            )
          })}
        </div>
      ) : (
        <div className="p-4 bg-surface rounded-xl border border-border text-center">
          <p className="text-sm text-text-muted">시그널 데이터를 분석 중입니다.</p>
        </div>
      )}

      {/* 정보 출처 */}
      <div className="p-3 bg-surface rounded-lg border border-border">
        <p className="text-xs text-text-muted">
          📊 데이터 출처: OpenDART 공시, pykrx 수급 데이터, 내부자 거래 신고 데이터
        </p>
      </div>
    </div>
  )
}
