'use client'

// StockCard — 종목 기본 정보 카드 컴포넌트

import Link from 'next/link'
import { clsx } from 'clsx'
import type { StockSummary } from '@/types/stock'

interface StockCardProps {
  stock: StockSummary
  variant?: 'default' | 'compact'
}

/** 가격 포맷 (한국 원화) */
function formatPrice(price: number, currency: 'KRW' | 'USD'): string {
  if (currency === 'USD') {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(price)
  }
  return new Intl.NumberFormat('ko-KR').format(price) + '원'
}

/** 등락률 색상 (한국: 상승=빨강, 하락=파랑) */
function getChangeColor(change: number): string {
  if (change > 0) return 'text-rise'
  if (change < 0) return 'text-fall'
  return 'text-text-secondary'
}

/** 등락률 배경 색상 */
function getChangeBgColor(change: number): string {
  if (change > 0) return 'bg-rise/10 border-rise/20'
  if (change < 0) return 'bg-fall/10 border-fall/20'
  return 'bg-card border-border'
}

/** 거래량 포맷 (억, 만 단위) */
function formatVolume(volume: number): string {
  if (volume >= 100_000_000) return `${(volume / 100_000_000).toFixed(1)}억주`
  if (volume >= 10_000) return `${(volume / 10_000).toFixed(0)}만주`
  return `${volume.toLocaleString('ko-KR')}주`
}

/** 미니 스파크라인 (6개 더미 포인트) */
function MiniSparkline({ isPositive }: { isPositive: boolean }) {
  const points = isPositive
    ? '0,20 12,18 24,15 36,17 48,12 60,8'
    : '0,8 12,10 24,14 36,12 48,16 60,20'

  return (
    <svg width="60" height="28" viewBox="0 0 60 28" className="opacity-70">
      <polyline
        points={points}
        fill="none"
        stroke={isPositive ? '#EF4444' : '#3B82F6'}
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}

export default function StockCard({ stock, variant = 'default' }: StockCardProps) {
  const isPositive = stock.changePercent >= 0
  const changeColor = getChangeColor(stock.changePercent)
  const changeBg = getChangeBgColor(stock.changePercent)

  if (variant === 'compact') {
    return (
      <Link href={`/stock/${stock.ticker}`}>
        <div className="flex items-center justify-between p-3 bg-card border border-border rounded-lg hover:border-primary/40 transition-colors cursor-pointer">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center text-xs font-bold text-primary">
              {stock.name.charAt(0)}
            </div>
            <div>
              <p className="text-sm font-medium text-text-primary">{stock.name}</p>
              <p className="text-xs text-text-muted">{stock.ticker}</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm font-semibold text-text-primary">
              {formatPrice(stock.currentPrice, stock.currency)}
            </p>
            <p className={clsx('text-xs font-medium', changeColor)}>
              {isPositive ? '+' : ''}{stock.changePercent.toFixed(2)}%
            </p>
          </div>
        </div>
      </Link>
    )
  }

  return (
    <Link href={`/stock/${stock.ticker}`}>
      <div className="group bg-card border border-border rounded-xl p-4 hover:border-primary/40 hover:shadow-lg hover:shadow-primary/5 transition-all cursor-pointer">
        {/* 상단: 종목 정보 + 스파크라인 */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-2.5">
            {/* 종목 아이콘 (이니셜) */}
            <div className="w-10 h-10 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center font-bold text-primary text-sm group-hover:bg-primary/20 transition-colors">
              {stock.name.charAt(0)}
            </div>
            <div>
              <p className="font-semibold text-text-primary text-sm">{stock.name}</p>
              <div className="flex items-center gap-1.5 mt-0.5">
                <span className="text-xs text-text-muted">{stock.ticker}</span>
                <span className="text-text-muted">·</span>
                <span className="text-xs text-text-muted">{stock.market}</span>
              </div>
            </div>
          </div>
          {/* 스파크라인 */}
          <MiniSparkline isPositive={isPositive} />
        </div>

        {/* 가격 */}
        <div className="mb-3">
          <p className="text-xl font-bold text-text-primary">
            {formatPrice(stock.currentPrice, stock.currency)}
          </p>
        </div>

        {/* 등락률 + 거래량 */}
        <div className="flex items-center justify-between">
          <div className={clsx('flex items-center gap-1 px-2 py-1 rounded-lg border text-xs font-medium', changeBg, changeColor)}>
            {/* 화살표 */}
            {stock.changePercent !== 0 && (
              <svg
                className={clsx('w-3 h-3', isPositive ? 'rotate-0' : 'rotate-180')}
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path fillRule="evenodd" d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
              </svg>
            )}
            <span>
              {isPositive ? '+' : ''}{stock.changePercent.toFixed(2)}%
            </span>
            <span className="opacity-60">
              ({isPositive ? '+' : ''}{stock.change.toLocaleString('ko-KR')})
            </span>
          </div>

          {/* 거래량 */}
          <span className="text-xs text-text-muted">
            {formatVolume(stock.volume)}
          </span>
        </div>

        {/* AI 분석 보기 CTA */}
        <div className="mt-3 pt-3 border-t border-border">
          <div className="flex items-center justify-between">
            <span className="text-xs text-text-muted">AI 분석</span>
            <span className="text-xs text-primary flex items-center gap-1 group-hover:gap-1.5 transition-all">
              상세 보기
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </span>
          </div>
        </div>
      </div>
    </Link>
  )
}
