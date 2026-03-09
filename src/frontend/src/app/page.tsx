// 홈 페이지 — 검색창 + 인기 종목 카드 그리드

import type { Metadata } from 'next'
import { Suspense } from 'react'
import StockCard from '@/components/stock/StockCard'
import { PopularStocksSkeleton } from '@/components/ui/LoadingSkeleton'
import HomeSearchClient from '@/components/ui/HomeSearchClient'
import { getPopularStocks } from '@/lib/api'

// 백엔드 API를 사용하므로 정적 생성 비활성화
export const dynamic = 'force-dynamic'

export const metadata: Metadata = {
  title: 'StockMind AI — AI 기반 주식 심층 분석',
  description: 'AI가 분석하는 한국 주식 심층 리포트. 실시간 분석으로 투자 인사이트를 얻으세요.',
}

// 인기 종목 섹션 (서버 컴포넌트)
async function PopularStocks() {
  const stocks = await getPopularStocks()

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
      {stocks.map((stock) => (
        <StockCard key={stock.ticker} stock={stock} />
      ))}
    </div>
  )
}

export default function HomePage() {
  return (
    <div className="min-h-[calc(100vh-4rem)]">
      {/* 히어로 섹션 */}
      <section className="relative overflow-hidden bg-gradient-to-b from-surface to-background">
        {/* 배경 그라데이션 효과 */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-32 -left-32 w-96 h-96 bg-primary/5 rounded-full blur-3xl" />
          <div className="absolute -top-16 -right-16 w-64 h-64 bg-primary/3 rounded-full blur-3xl" />
        </div>

        <div className="relative max-w-4xl mx-auto px-4 py-16 md:py-24 text-center">
          {/* 태그라인 */}
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/20 text-xs text-primary font-medium mb-6">
            <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
            Claude AI 기반 실시간 분석
          </div>

          {/* 메인 헤딩 */}
          <h1 className="text-3xl md:text-5xl font-bold text-text-primary mb-4 leading-tight">
            AI가 분석하는<br />
            <span className="text-primary">주식 심층 인사이트</span>
          </h1>

          <p className="text-text-secondary text-base md:text-lg mb-8 max-w-xl mx-auto">
            기술적 분석부터 숨겨진 수급 신호까지.<br className="hidden sm:block" />
            일반 투자자가 놓치기 쉬운 핵심 정보를 한 눈에.
          </p>

          {/* 검색창 (클라이언트 사이드 — Header와 별개로 홈에 큰 검색창) */}
          <HomeSearchClient />

          {/* 특징 배지 */}
          <div className="flex flex-wrap justify-center gap-3 mt-8">
            {[
              '📊 기술적 분석',
              '💰 펀더멘털 분석',
              '🔍 숨겨진 인사이트',
              '📰 뉴스 센티먼트',
            ].map((item) => (
              <span
                key={item}
                className="text-xs px-3 py-1.5 rounded-full bg-card border border-border text-text-secondary"
              >
                {item}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* 인기 종목 섹션 */}
      <section className="max-w-7xl mx-auto px-4 py-12">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-lg font-bold text-text-primary">인기 종목</h2>
            <p className="text-sm text-text-muted mt-0.5">오늘 많이 조회된 종목</p>
          </div>
          <div className="flex items-center gap-1.5 text-xs text-text-muted">
            <span className="w-1.5 h-1.5 rounded-full bg-success animate-pulse" />
            실시간 업데이트
          </div>
        </div>

        <Suspense fallback={<PopularStocksSkeleton />}>
          <PopularStocks />
        </Suspense>
      </section>

      {/* 서비스 소개 섹션 */}
      <section className="max-w-7xl mx-auto px-4 pb-16">
        <div className="grid md:grid-cols-3 gap-6">
          {[
            {
              icon: '⚡',
              title: '빠른 AI 분석',
              desc: 'Claude AI가 수백 개의 지표를 실시간으로 분석하여 핵심 인사이트만 제공합니다.',
            },
            {
              icon: '🎯',
              title: '숨겨진 신호 탐지',
              desc: '수급 데이터, 내부자 거래, 기관 동향 등 일반 투자자가 놓치기 쉬운 신호를 포착합니다.',
            },
            {
              icon: '📱',
              title: '모바일 최적화',
              desc: '언제 어디서나 편리하게 확인할 수 있는 모바일 퍼스트 디자인으로 설계되었습니다.',
            },
          ].map((feature) => (
            <div key={feature.title} className="bg-card border border-border rounded-xl p-6">
              <div className="text-3xl mb-3">{feature.icon}</div>
              <h3 className="font-bold text-text-primary mb-2">{feature.title}</h3>
              <p className="text-sm text-text-secondary leading-relaxed">{feature.desc}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
