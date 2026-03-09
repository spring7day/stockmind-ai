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

/** 기본 목 시그널 데이터 */
const DEFAULT_SIGNALS: Signal[] = [
  {
    type: 'BUY',
    strength: 'MODERATE',
    reason: '외국인 수급 5일 연속 순매수 전환 — 기관 수급 개선 중',
    indicator: '수급분석',
  },
  {
    type: 'WATCH',
    strength: 'STRONG',
    reason: '52주 신저가 근접 구간에서 대량 거래 발생 — 저점 매집 가능성',
    indicator: '거래량분석',
  },
  {
    type: 'HOLD',
    strength: 'MODERATE',
    reason: '글로벌 경쟁사 대비 밸류에이션 20% 할인 거래 중',
    indicator: '상대가치분석',
  },
  {
    type: 'BUY',
    strength: 'WEAK',
    reason: '내부자 매수 신고 3건 확인 — 경영진 자사주 매입',
    indicator: '내부자거래',
  },
]

export default function SignalsPanel({ ticker, signals, insightSummary }: SignalsPanelProps) {
  const displaySignals = signals || DEFAULT_SIGNALS

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
              `${ticker} 종목에서 일반적으로 알려지지 않은 3가지 핵심 신호가 감지되었습니다.
              수급 데이터, 내부자 거래, 기술적 패턴을 종합 분석한 결과입니다.`}
          </p>
        </div>
      </div>

      {/* 시그널 목록 */}
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

      {/* 정보 출처 */}
      <div className="p-3 bg-surface rounded-lg border border-border">
        <p className="text-xs text-text-muted">
          📊 데이터 출처: OpenDART 공시, pykrx 수급 데이터, 내부자 거래 신고 데이터
        </p>
      </div>
    </div>
  )
}
