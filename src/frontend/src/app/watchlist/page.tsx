'use client'

// 관심 종목 페이지 — localStorage 기반 (서버리스)

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { getWatchlist, removeFromWatchlist } from '@/lib/api'
import { getStockPrice } from '@/lib/api'
import type { WatchlistItem, StockPrice } from '@/types/stock'
import { StockCardSkeleton } from '@/components/ui/LoadingSkeleton'

/** 관심 종목 아이템 (가격 포함) */
function WatchlistItemCard({
  item,
  price,
  onRemove,
}: {
  item: WatchlistItem
  price: StockPrice | null
  onRemove: (ticker: string) => void
}) {
  const isPositive = (price?.changePercent ?? 0) >= 0

  return (
    <div className="bg-card border border-border rounded-xl p-4 hover:border-primary/30 transition-colors">
      <div className="flex items-center justify-between">
        <Link href={`/stock/${item.ticker}`} className="flex items-center gap-3 flex-1 min-w-0">
          {/* 아이콘 */}
          <div className="w-10 h-10 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center font-bold text-primary text-sm shrink-0">
            {item.name.charAt(0)}
          </div>

          {/* 종목 정보 */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <p className="font-semibold text-text-primary text-sm truncate">{item.name}</p>
              <span className="text-xs px-1.5 py-0.5 rounded bg-surface border border-border text-text-muted shrink-0">
                {item.market}
              </span>
            </div>
            <p className="text-xs text-text-muted mt-0.5">{item.ticker}</p>
          </div>
        </Link>

        <div className="flex items-center gap-4 ml-4">
          {/* 가격 정보 */}
          {price ? (
            <div className="text-right">
              <p className="text-sm font-bold text-text-primary tabular-nums">
                {price.currentPrice.toLocaleString('ko-KR')}원
              </p>
              <p className={`text-xs font-medium ${isPositive ? 'text-rise' : 'text-fall'}`}>
                {isPositive ? '+' : ''}{price.changePercent.toFixed(2)}%
              </p>
            </div>
          ) : (
            <div className="text-right">
              <div className="h-4 w-16 bg-surface animate-pulse rounded mb-1" />
              <div className="h-3 w-12 bg-surface animate-pulse rounded" />
            </div>
          )}

          {/* 삭제 버튼 */}
          <button
            onClick={() => onRemove(item.ticker)}
            className="p-1.5 rounded-lg text-text-muted hover:text-error hover:bg-error/10 transition-colors"
            title="관심 종목에서 제거"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      {/* 사용자 메모 */}
      {item.note && (
        <p className="mt-2 text-xs text-text-muted bg-surface rounded-lg px-3 py-2 border border-border">
          📝 {item.note}
        </p>
      )}

      {/* 추가 날짜 */}
      <p className="text-xs text-text-muted mt-2 text-right">
        추가: {new Date(item.addedAt).toLocaleDateString('ko-KR')}
      </p>
    </div>
  )
}

/** 빈 상태 UI */
function EmptyWatchlist() {
  return (
    <div className="flex flex-col items-center justify-center py-24 text-center">
      {/* 하트 아이콘 */}
      <div className="w-20 h-20 rounded-full bg-card border border-border flex items-center justify-center mb-6">
        <svg
          className="w-10 h-10 text-text-muted"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
          />
        </svg>
      </div>

      <h3 className="text-lg font-bold text-text-primary mb-2">관심 종목이 없습니다</h3>
      <p className="text-text-muted text-sm max-w-xs mb-8">
        분석 페이지에서 하트 버튼을 눌러 관심 종목을 추가해보세요.
      </p>

      <Link
        href="/"
        className="px-6 py-3 bg-primary hover:bg-primary-hover rounded-xl font-semibold text-white text-sm transition-colors"
      >
        종목 검색하기
      </Link>
    </div>
  )
}

export default function WatchlistPage() {
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([])
  const [prices, setPrices] = useState<Record<string, StockPrice>>({})
  const [isLoading, setIsLoading] = useState(true)

  // 관심 종목 로드
  useEffect(() => {
    const load = async () => {
      const items = await getWatchlist()
      setWatchlist(items)
      setIsLoading(false)

      // 각 종목의 가격 병렬 로드
      if (items.length > 0) {
        const pricePromises = items.map(async (item) => {
          try {
            const price = await getStockPrice(item.ticker)
            return [item.ticker, price] as const
          } catch {
            return null
          }
        })

        const results = await Promise.all(pricePromises)
        const priceMap: Record<string, StockPrice> = {}
        results.forEach((r) => {
          if (r) priceMap[r[0]] = r[1]
        })
        setPrices(priceMap)
      }
    }

    load()
  }, [])

  // 관심 종목 제거
  const handleRemove = async (ticker: string) => {
    await removeFromWatchlist(ticker)
    setWatchlist((prev) => prev.filter((item) => item.ticker !== ticker))
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      {/* 페이지 헤더 */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold text-text-primary">관심 종목</h1>
          <p className="text-sm text-text-muted mt-0.5">
            {isLoading ? '로딩 중...' : `${watchlist.length}개 종목`}
          </p>
        </div>

        {watchlist.length > 0 && (
          <Link
            href="/"
            className="flex items-center gap-1.5 text-sm text-primary hover:text-primary-light transition-colors"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            종목 추가
          </Link>
        )}
      </div>

      {/* 로딩 상태 */}
      {isLoading && (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <StockCardSkeleton key={i} />
          ))}
        </div>
      )}

      {/* 빈 상태 */}
      {!isLoading && watchlist.length === 0 && <EmptyWatchlist />}

      {/* 관심 종목 목록 */}
      {!isLoading && watchlist.length > 0 && (
        <div className="space-y-3">
          {watchlist.map((item) => (
            <WatchlistItemCard
              key={item.ticker}
              item={item}
              price={prices[item.ticker] ?? null}
              onRemove={handleRemove}
            />
          ))}
        </div>
      )}
    </div>
  )
}
