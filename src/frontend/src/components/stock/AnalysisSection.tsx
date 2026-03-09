'use client'

// AnalysisSection — AI 분석 섹션 (4탭: 기술적/펀더멘털/숨겨진인사이트/뉴스센티먼트)
// 첫 번째 탭(기술적 분석)은 무료, 나머지는 AdGate로 잠금

import { useState, useEffect, useCallback } from 'react'
import { getAnalysis } from '@/lib/api'
import AdGate from '@/components/ui/AdGate'
import { AnalysisSkeleton } from '@/components/ui/LoadingSkeleton'
import { InlineError } from '@/components/ui/ErrorBoundary'
import type { AnalysisResult, AnalysisTab, Signal } from '@/types/stock'
import { clsx } from 'clsx'

const TABS: { id: AnalysisTab; label: string; icon: string; free: boolean }[] = [
  { id: 'technical', label: '기술적 분석', icon: '📊', free: true },
  { id: 'fundamental', label: '펀더멘털', icon: '💰', free: false },
  { id: 'insights', label: '숨겨진 인사이트', icon: '🔍', free: false },
  { id: 'sentiment', label: '뉴스 센티먼트', icon: '📰', free: false },
]

/** 신호 배지 */
function SignalBadge({ signal }: { signal: Signal }) {
  const colors: Record<Signal['type'], string> = {
    BUY: 'bg-rise/10 text-rise border-rise/20',
    SELL: 'bg-fall/10 text-fall border-fall/20',
    HOLD: 'bg-warning/10 text-warning border-warning/20',
    WATCH: 'bg-primary/10 text-primary border-primary/20',
  }
  const labels: Record<Signal['type'], string> = {
    BUY: '매수',
    SELL: '매도',
    HOLD: '보유',
    WATCH: '관찰',
  }

  return (
    <div className={clsx('flex items-start gap-2 p-3 rounded-lg border text-sm', colors[signal.type])}>
      <span className="font-bold shrink-0">[{labels[signal.type]}]</span>
      <div>
        <p className="text-text-primary">{signal.reason}</p>
        {signal.indicator && (
          <p className="text-xs opacity-70 mt-0.5">지표: {signal.indicator}</p>
        )}
      </div>
    </div>
  )
}

/** AI 점수 게이지 */
function ScoreGauge({ score }: { score: number }) {
  const getScoreColor = (s: number) => {
    if (s >= 70) return '#EF4444'  // 매수 신호
    if (s >= 50) return '#F59E0B'  // 중립
    return '#3B82F6'               // 매도 신호
  }
  const getScoreLabel = (s: number) => {
    if (s >= 70) return '강세'
    if (s >= 50) return '중립'
    return '약세'
  }

  const color = getScoreColor(score)
  const circumference = 2 * Math.PI * 30
  const dashOffset = circumference * (1 - score / 100)

  return (
    <div className="flex items-center gap-4 p-4 bg-surface rounded-xl">
      {/* 원형 게이지 */}
      <div className="relative w-20 h-20 shrink-0">
        <svg className="w-20 h-20 -rotate-90" viewBox="0 0 68 68">
          <circle cx="34" cy="34" r="30" fill="none" stroke="#1E293B" strokeWidth="5" />
          <circle
            cx="34"
            cy="34"
            r="30"
            fill="none"
            stroke={color}
            strokeWidth="5"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={dashOffset}
            style={{ transition: 'stroke-dashoffset 0.8s ease' }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-xl font-bold text-text-primary">{score}</span>
        </div>
      </div>

      <div>
        <p className="text-sm font-semibold" style={{ color }}>
          {getScoreLabel(score)} 신호
        </p>
        <p className="text-xs text-text-muted mt-1">
          AI 종합 점수 (0~100)<br />
          <span className="text-rise">70+</span> 강세 ·{' '}
          <span className="text-warning">50~70</span> 중립 ·{' '}
          <span className="text-fall">50-</span> 약세
        </p>
      </div>
    </div>
  )
}

/** 분석 콘텐츠 */
function AnalysisContent({ analysis }: { analysis: AnalysisResult }) {
  return (
    <div className="space-y-4 animate-fade-in">
      {/* AI 점수 */}
      {analysis.score !== undefined && <ScoreGauge score={analysis.score} />}

      {/* 요약 */}
      <div className="p-4 bg-surface rounded-xl">
        <h4 className="text-sm font-semibold text-text-primary mb-2">AI 분석 요약</h4>
        <p className="text-sm text-text-secondary leading-relaxed">{analysis.summary}</p>
      </div>

      {/* 시그널 */}
      {analysis.signals && analysis.signals.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-sm font-semibold text-text-primary">매매 시그널</h4>
          {analysis.signals.map((signal, i) => (
            <SignalBadge key={i} signal={signal} />
          ))}
        </div>
      )}

      {/* 상세 분석 (마크다운 → 단순 텍스트 표시) */}
      <div className="p-4 bg-surface rounded-xl">
        <h4 className="text-sm font-semibold text-text-primary mb-3">상세 분석</h4>
        <div className="text-sm text-text-secondary leading-relaxed whitespace-pre-line">
          {analysis.details
            .replace(/^#+\s/gm, '')         // 헤딩 제거
            .replace(/\*\*(.*?)\*\*/g, '$1') // 볼드 제거
            .replace(/^\s*[-*]\s/gm, '• ')  // 리스트 변환
            .replace(/^>\s/gm, '')           // 인용구 제거
            .trim()}
        </div>
      </div>

      {/* 법적 고지 */}
      <div className="p-3 bg-warning/5 border border-warning/20 rounded-lg">
        <p className="text-xs text-warning/80">
          ⚠️ {analysis.disclaimer}
        </p>
      </div>

      {/* 분석 시각 */}
      <p className="text-xs text-text-muted text-right">
        분석 생성: {new Date(analysis.generatedAt).toLocaleString('ko-KR')}
      </p>
    </div>
  )
}

interface AnalysisSectionProps {
  ticker: string
}

export default function AnalysisSection({ ticker }: AnalysisSectionProps) {
  const [activeTab, setActiveTab] = useState<AnalysisTab>('technical')
  const [analyses, setAnalyses] = useState<Partial<Record<AnalysisTab, AnalysisResult>>>({})
  const [loading, setLoading] = useState<Partial<Record<AnalysisTab, boolean>>>({})
  const [errors, setErrors] = useState<Partial<Record<AnalysisTab, string>>>({})

  const loadAnalysis = useCallback(
    async (tab: AnalysisTab) => {
      // 이미 로드된 경우 스킵
      if (analyses[tab]) return

      setLoading((prev) => ({ ...prev, [tab]: true }))
      setErrors((prev) => ({ ...prev, [tab]: undefined }))

      try {
        const result = await getAnalysis(ticker, tab)
        setAnalyses((prev) => ({ ...prev, [tab]: result }))
      } catch {
        setErrors((prev) => ({ ...prev, [tab]: '분석 데이터를 불러오는 중 오류가 발생했습니다.' }))
      } finally {
        setLoading((prev) => ({ ...prev, [tab]: false }))
      }
    },
    [ticker, analyses]
  )

  // 기술적 분석(무료 탭)은 마운트 시 자동 로드
  useEffect(() => {
    loadAnalysis('technical')
  }, [loadAnalysis])

  const handleTabChange = (tab: AnalysisTab) => {
    setActiveTab(tab)
    loadAnalysis(tab)
  }

  const currentTabInfo = TABS.find((t) => t.id === activeTab)!

  const TabContent = () => {
    if (loading[activeTab]) return <AnalysisSkeleton />
    if (errors[activeTab]) return (
      <InlineError
        message={errors[activeTab]}
        onRetry={() => {
          setAnalyses((prev) => ({ ...prev, [activeTab]: undefined }))
          loadAnalysis(activeTab)
        }}
      />
    )
    if (!analyses[activeTab]) return <AnalysisSkeleton />
    return <AnalysisContent analysis={analyses[activeTab]!} />
  }

  return (
    <div className="bg-card border border-border rounded-xl overflow-hidden">
      {/* 섹션 헤더 */}
      <div className="px-4 pt-4 pb-0">
        <h2 className="text-base font-bold text-text-primary flex items-center gap-2 mb-3">
          <span className="text-primary">✦</span>
          AI 심층 분석
          <span className="text-xs px-2 py-0.5 rounded-full bg-primary/10 text-primary font-normal">
            Claude AI
          </span>
        </h2>

        {/* 탭 */}
        <div className="flex gap-0 border-b border-border">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => handleTabChange(tab.id)}
              className={clsx(
                'flex items-center gap-1.5 px-3 py-2.5 text-sm font-medium border-b-2 transition-colors whitespace-nowrap',
                activeTab === tab.id
                  ? 'border-primary text-primary'
                  : 'border-transparent text-text-muted hover:text-text-secondary'
              )}
            >
              <span>{tab.icon}</span>
              <span className="hidden sm:block">{tab.label}</span>
              {!tab.free && (
                <svg
                  className="w-3 h-3 text-text-muted"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z"
                    clipRule="evenodd"
                  />
                </svg>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* 탭 콘텐츠 */}
      <div className="p-4">
        {currentTabInfo.free ? (
          <TabContent />
        ) : (
          <AdGate
            ticker={ticker}
            label={`${currentTabInfo.label} 잠금`}
          >
            <TabContent />
          </AdGate>
        )}
      </div>
    </div>
  )
}
