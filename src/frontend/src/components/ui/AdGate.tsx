'use client'

// AdGate — StockMind AI 핵심 수익 모델
// 잠긴 콘텐츠를 광고 시청 후 당일 무제한 열람 가능하게 하는 컴포넌트

import { useState, useEffect, useCallback, useRef } from 'react'
import { isUnlocked, unlockTicker } from '@/lib/adGate'

interface AdGateProps {
  ticker: string           // 종목 코드
  children: React.ReactNode  // 잠긴 콘텐츠
  label?: string           // 잠금 설명 문구
}

/** 광고 카운트다운 모달 */
function AdCountdownModal({
  onComplete,
  onClose,
}: {
  onComplete: () => void
  onClose: () => void
}) {
  const [count, setCount] = useState(5)
  const [adPhase, setAdPhase] = useState<'loading' | 'playing' | 'done'>('loading')
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    // 1초 후 광고 로드 완료 → 재생 시작
    const loadTimer = setTimeout(() => {
      setAdPhase('playing')

      // 5초 카운트다운
      intervalRef.current = setInterval(() => {
        setCount((prev) => {
          if (prev <= 1) {
            if (intervalRef.current) clearInterval(intervalRef.current)
            setAdPhase('done')
            return 0
          }
          return prev - 1
        })
      }, 1000)
    }, 1000)

    return () => {
      clearTimeout(loadTimer)
      if (intervalRef.current) clearInterval(intervalRef.current)
    }
  }, [])

  const circumference = 2 * Math.PI * 22  // SVG 원 둘레
  const dashOffset = adPhase === 'playing'
    ? circumference * (1 - count / 5)
    : adPhase === 'done' ? circumference : 0

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/70 backdrop-blur-sm animate-fade-in">
      <div className="bg-card border border-border rounded-2xl p-8 max-w-sm w-full mx-4 shadow-2xl animate-slide-up">
        {/* 헤더 */}
        <div className="text-center mb-6">
          <h3 className="text-lg font-bold text-text-primary">광고 시청 중</h3>
          <p className="text-sm text-text-secondary mt-1">
            광고 시청 후 오늘 하루 전체 분석을 무제한으로 확인하세요
          </p>
        </div>

        {/* 광고 영역 (시뮬레이션) */}
        <div className="bg-surface rounded-xl h-32 flex items-center justify-center mb-6 border border-border overflow-hidden relative">
          {adPhase === 'loading' && (
            <div className="flex flex-col items-center gap-2">
              <div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin" />
              <span className="text-xs text-text-muted">광고 로딩 중...</span>
            </div>
          )}
          {(adPhase === 'playing' || adPhase === 'done') && (
            <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-primary/10 to-surface">
              <div className="text-center">
                <div className="text-4xl mb-1">📈</div>
                <p className="text-xs text-text-muted">광고 영역</p>
                <p className="text-xs text-text-muted">(실제 광고가 표시됩니다)</p>
              </div>
            </div>
          )}
        </div>

        {/* 카운트다운 원형 타이머 */}
        <div className="flex flex-col items-center gap-4">
          {adPhase !== 'done' ? (
            <div className="relative w-16 h-16">
              <svg className="w-16 h-16 -rotate-90" viewBox="0 0 48 48">
                {/* 배경 원 */}
                <circle
                  cx="24"
                  cy="24"
                  r="22"
                  fill="none"
                  stroke="#1E293B"
                  strokeWidth="3"
                />
                {/* 진행 원 */}
                <circle
                  cx="24"
                  cy="24"
                  r="22"
                  fill="none"
                  stroke="#3B82F6"
                  strokeWidth="3"
                  strokeLinecap="round"
                  strokeDasharray={circumference}
                  strokeDashoffset={dashOffset}
                  style={{ transition: 'stroke-dashoffset 1s linear' }}
                />
              </svg>
              <span className="absolute inset-0 flex items-center justify-center text-xl font-bold text-text-primary">
                {adPhase === 'loading' ? '...' : count}
              </span>
            </div>
          ) : (
            /* 완료 버튼 */
            <button
              onClick={onComplete}
              className="w-full py-3 bg-primary hover:bg-primary-hover rounded-xl font-semibold text-white transition-colors animate-fade-in"
            >
              전체 분석 확인하기 ✓
            </button>
          )}

          {adPhase !== 'done' && (
            <p className="text-xs text-text-muted">
              {adPhase === 'loading' ? '잠시만 기다려주세요...' : `${count}초 후 건너뛸 수 있습니다`}
            </p>
          )}

          {/* 닫기 */}
          <button
            onClick={onClose}
            className="text-xs text-text-muted hover:text-text-secondary underline transition-colors"
          >
            취소
          </button>
        </div>
      </div>
    </div>
  )
}

/** AdGate 메인 컴포넌트 */
export default function AdGate({ ticker, children, label }: AdGateProps) {
  const [unlocked, setUnlocked] = useState(false)
  const [showModal, setShowModal] = useState(false)

  // 클라이언트 마운트 후 잠금 상태 확인
  useEffect(() => {
    setUnlocked(isUnlocked(ticker))
  }, [ticker])

  const handleAdComplete = useCallback(() => {
    unlockTicker(ticker)
    setUnlocked(true)
    setShowModal(false)
  }, [ticker])

  // 이미 잠금 해제된 경우 바로 콘텐츠 표시
  if (unlocked) {
    return <>{children}</>
  }

  return (
    <>
      {/* 광고 모달 */}
      {showModal && (
        <AdCountdownModal
          onComplete={handleAdComplete}
          onClose={() => setShowModal(false)}
        />
      )}

      {/* 잠긴 콘텐츠 (블러 오버레이) */}
      <div className="relative rounded-xl overflow-hidden">
        {/* 블러 처리된 콘텐츠 미리보기 */}
        <div className="blur-sm pointer-events-none select-none opacity-60">
          {children}
        </div>

        {/* 잠금 오버레이 */}
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-background/80 backdrop-blur-sm">
          <div className="text-center px-6 py-8 max-w-xs">
            {/* 자물쇠 아이콘 */}
            <div className="w-14 h-14 rounded-full bg-card border border-border flex items-center justify-center mx-auto mb-4">
              <svg
                className="w-7 h-7 text-primary"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                />
              </svg>
            </div>

            <h4 className="font-bold text-text-primary mb-1">
              {label || '전체 분석 잠금'}
            </h4>
            <p className="text-sm text-text-secondary mb-5">
              광고를 보고 오늘 하루{' '}
              <span className="text-primary font-medium">전체 AI 분석</span>을
              무제한으로 확인하세요
            </p>

            {/* 혜택 목록 */}
            <ul className="text-xs text-text-muted space-y-1 mb-5 text-left">
              {['기술적 분석 (보조지표 포함)', '펀더멘털 심층 분석', '숨겨진 인사이트', '뉴스 센티먼트 분석'].map(
                (item) => (
                  <li key={item} className="flex items-center gap-2">
                    <svg className="w-3 h-3 text-primary shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    {item}
                  </li>
                )
              )}
            </ul>

            <button
              onClick={() => setShowModal(true)}
              className="w-full py-3 bg-primary hover:bg-primary-hover rounded-xl font-semibold text-white text-sm transition-colors"
            >
              광고 보기 (5초)
            </button>
            <p className="text-xs text-text-muted mt-2">
              하루 한 번만 보면 오늘 전체 무제한 이용
            </p>
          </div>
        </div>
      </div>
    </>
  )
}
