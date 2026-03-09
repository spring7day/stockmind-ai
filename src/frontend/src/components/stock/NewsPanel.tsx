'use client'

// NewsPanel — 뉴스/공시 패널
// 최신 뉴스와 AI 감성 분석 결과 표시

import { useState, useEffect, useCallback } from 'react'
import { getNews } from '@/lib/api'
import type { NewsItem } from '@/types/stock'
import { NewsPanelSkeleton } from '@/components/ui/LoadingSkeleton'
import { InlineError } from '@/components/ui/ErrorBoundary'
import { clsx } from 'clsx'

interface NewsPanelProps {
  ticker: string
}

/** 감성 배지 */
function SentimentBadge({ sentiment, score }: { sentiment: NewsItem['sentiment']; score: number }) {
  const config = {
    POSITIVE: { label: '긍정', className: 'bg-rise/10 text-rise border-rise/20' },
    NEGATIVE: { label: '부정', className: 'bg-fall/10 text-fall border-fall/20' },
    NEUTRAL: { label: '중립', className: 'bg-text-muted/10 text-text-muted border-text-muted/20' },
  }[sentiment]

  const absScore = Math.abs(score)
  const intensity = absScore >= 0.7 ? '강' : absScore >= 0.4 ? '중' : '약'

  return (
    <span className={clsx('text-xs px-2 py-0.5 rounded-full border font-medium', config.className)}>
      {config.label} ({intensity})
    </span>
  )
}

/** 다양한 형식의 날짜 문자열 파싱 */
function parseDate(dateStr: string): Date | null {
  if (!dateStr) return null

  // ISO 8601 (표준 - 우선 시도)
  let date = new Date(dateStr)
  if (!isNaN(date.getTime())) return date

  // 네이버 금융 형식: "2024.03.15 14:30" 또는 "2024.03.15 14:30:45" (초 포함)
  const naverMatch = dateStr.match(/^(\d{4})\.(\d{2})\.(\d{2})\s+(\d{2}):(\d{2})(?::\d{2})?$/)
  if (naverMatch) {
    const [, y, m, d, h, min] = naverMatch
    date = new Date(parseInt(y), parseInt(m) - 1, parseInt(d), parseInt(h), parseInt(min))
    if (!isNaN(date.getTime())) return date
  }

  // DART 형식: "20240315"
  const dartMatch = dateStr.match(/^(\d{4})(\d{2})(\d{2})$/)
  if (dartMatch) {
    const [, y, m, d] = dartMatch
    date = new Date(parseInt(y), parseInt(m) - 1, parseInt(d))
    if (!isNaN(date.getTime())) return date
  }

  return null
}

/** 상대 시간 포맷 */
function formatRelativeTime(dateStr: string): string {
  const date = parseDate(dateStr)
  if (!date) return dateStr || '날짜 없음'

  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  if (diffMs < 0) return '방금 전'
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMins / 60)
  const diffDays = Math.floor(diffHours / 24)

  if (diffMins < 60) return `${diffMins}분 전`
  if (diffHours < 24) return `${diffHours}시간 전`
  return `${diffDays}일 전`
}

/** 전체 감성 분포 계산 */
function calcSentimentDistribution(news: NewsItem[]) {
  const counts = { POSITIVE: 0, NEGATIVE: 0, NEUTRAL: 0 }
  news.forEach((n) => counts[n.sentiment]++)
  const total = news.length || 1
  return {
    positive: Math.round((counts.POSITIVE / total) * 100),
    negative: Math.round((counts.NEGATIVE / total) * 100),
    neutral: Math.round((counts.NEUTRAL / total) * 100),
  }
}

export default function NewsPanel({ ticker }: NewsPanelProps) {
  const [news, setNews] = useState<NewsItem[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadNews = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const data = await getNews(ticker)
      setNews(data)
    } catch {
      setError('뉴스를 불러오는 중 오류가 발생했습니다.')
    } finally {
      setIsLoading(false)
    }
  }, [ticker])

  useEffect(() => {
    loadNews()
  }, [loadNews])

  if (isLoading) return <NewsPanelSkeleton />
  if (error) return <InlineError message={error} onRetry={loadNews} />

  const distribution = calcSentimentDistribution(news)

  return (
    <div className="space-y-4">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-lg">📰</span>
          <h3 className="font-bold text-text-primary">뉴스 센티먼트</h3>
        </div>
        <button
          onClick={loadNews}
          className="text-xs text-text-muted hover:text-primary transition-colors flex items-center gap-1"
        >
          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          새로고침
        </button>
      </div>

      {/* 감성 분포 바 */}
      <div className="p-4 bg-surface rounded-xl space-y-2">
        <p className="text-xs font-medium text-text-secondary mb-3">
          최근 뉴스 감성 분포 ({news.length}건)
        </p>
        <div className="flex h-2 rounded-full overflow-hidden gap-0.5">
          {distribution.positive > 0 && (
            <div
              className="bg-rise rounded-full transition-all duration-500"
              style={{ width: `${distribution.positive}%` }}
            />
          )}
          {distribution.neutral > 0 && (
            <div
              className="bg-text-muted/40 rounded-full transition-all duration-500"
              style={{ width: `${distribution.neutral}%` }}
            />
          )}
          {distribution.negative > 0 && (
            <div
              className="bg-fall rounded-full transition-all duration-500"
              style={{ width: `${distribution.negative}%` }}
            />
          )}
        </div>
        <div className="flex justify-between text-xs text-text-muted">
          <span className="text-rise">긍정 {distribution.positive}%</span>
          <span>중립 {distribution.neutral}%</span>
          <span className="text-fall">부정 {distribution.negative}%</span>
        </div>
      </div>

      {/* 뉴스 목록 */}
      <div className="space-y-0 divide-y divide-border">
        {news.length === 0 ? (
          <p className="text-sm text-text-muted text-center py-8">
            관련 뉴스가 없습니다.
          </p>
        ) : (
          news.map((item) => (
            <a
              key={item.id}
              href={item.url}
              target="_blank"
              rel="noopener noreferrer"
              className="block py-4 hover:bg-surface/50 transition-colors px-1 -mx-1 rounded-lg"
            >
              <div className="space-y-2">
                {/* 제목 */}
                <p className="text-sm font-medium text-text-primary leading-snug hover:text-primary transition-colors">
                  {item.title}
                </p>

                {/* AI 요약 */}
                {item.summary && (
                  <p className="text-xs text-text-muted leading-relaxed">
                    {item.summary}
                  </p>
                )}

                {/* 메타 정보 */}
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-xs text-text-muted">{item.source}</span>
                  <span className="text-text-muted">·</span>
                  <span className="text-xs text-text-muted">{formatRelativeTime(item.publishedAt)}</span>
                  <SentimentBadge sentiment={item.sentiment} score={item.sentimentScore} />
                </div>
              </div>
            </a>
          ))
        )}
      </div>

      {/* 데이터 출처 */}
      <p className="text-xs text-text-muted text-right">
        AI 감성 분석: Claude API · 뉴스 출처: 각 언론사
      </p>
    </div>
  )
}
