// 종목 상세 분석 페이지 — [ticker] 동적 라우트

import type { Metadata } from 'next'
import dynamic from 'next/dynamic'
import { notFound } from 'next/navigation'
import { getStockPrice, getStockInfo } from '@/lib/api'
import AnalysisSection from '@/components/stock/AnalysisSection'
import NewsPanel from '@/components/stock/NewsPanel'
import AdGate from '@/components/ui/AdGate'
import { ChartSkeleton, AnalysisSkeleton } from '@/components/ui/LoadingSkeleton'

// PriceChart: TradingView는 브라우저 전용 — dynamic import로 SSR 우회
const PriceChart = dynamic(
  () => import('@/components/stock/PriceChart'),
  {
    ssr: false,
    loading: () => <ChartSkeleton />,
  }
)

interface PageProps {
  params: Promise<{ ticker: string }>
}

/** 메타데이터 동적 생성 */
export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { ticker } = await params

  try {
    const [price, stockInfo] = await Promise.all([getStockPrice(ticker), getStockInfo(ticker)])
    const changeSign = price.changePercent >= 0 ? '+' : ''
    return {
      title: `${stockInfo.name} (${ticker}) 주가 분석 — AI 인사이트`,
      description: `${stockInfo.name} 현재가 ${price.currentPrice.toLocaleString('ko-KR')}원 (${changeSign}${price.changePercent.toFixed(2)}%). AI 기반 기술적 분석, 펀더멘털, 숨겨진 인사이트 제공.`,
    }
  } catch {
    return {
      title: `${ticker} 주가 분석 | StockMind AI`,
    }
  }
}

/** 등락률 컬러 클래스 */
function getChangeStyle(changePercent: number) {
  if (changePercent > 0) return 'text-rise'
  if (changePercent < 0) return 'text-fall'
  return 'text-text-secondary'
}

export default async function StockDetailPage({ params }: PageProps) {
  const { ticker } = await params

  // 종목 코드 유효성 검사 (기본)
  if (!ticker || ticker.length > 10) {
    notFound()
  }

  // 가격 데이터 + 종목 기본 정보 로드 (서버 사이드, 병렬)
  let priceData
  let stockInfo: { name: string; market: string; ticker: string }
  try {
    ;[priceData, stockInfo] = await Promise.all([getStockPrice(ticker), getStockInfo(ticker)])
  } catch {
    notFound()
  }

  const isPositive = priceData.changePercent >= 0
  const changeStyle = getChangeStyle(priceData.changePercent)

  return (
    <div className="max-w-4xl mx-auto px-4 py-6 space-y-6">
      {/* 종목 헤더 */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          {/* 종목 코드 + 시장 */}
          <div className="flex items-center gap-2 mb-1">
            <span className="text-sm text-text-muted">{ticker}</span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-card border border-border text-text-muted">
              {stockInfo.market}
            </span>
          </div>

          {/* 종목명 */}
          <h1 className="text-2xl font-bold text-text-primary">{stockInfo.name}</h1>
        </div>

        {/* 현재가 + 등락률 */}
        <div className="sm:text-right">
          <div className="text-3xl font-bold text-text-primary tabular-nums">
            {priceData.currentPrice.toLocaleString('ko-KR')}
            <span className="text-base font-normal text-text-muted ml-1">원</span>
          </div>
          <div className={`flex sm:justify-end items-center gap-2 mt-1 ${changeStyle}`}>
            {priceData.changePercent !== 0 && (
              <svg
                className={`w-4 h-4 ${isPositive ? '' : 'rotate-180'}`}
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path fillRule="evenodd" d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
              </svg>
            )}
            <span className="font-semibold text-lg">
              {isPositive ? '+' : ''}{priceData.changePercent.toFixed(2)}%
            </span>
            <span className="text-sm opacity-70">
              ({isPositive ? '+' : ''}{priceData.change.toLocaleString('ko-KR')}원)
            </span>
          </div>
        </div>
      </div>

      {/* 주요 지표 바 */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: '시가', value: priceData.openPrice.toLocaleString('ko-KR') + '원' },
          { label: '고가', value: priceData.highPrice.toLocaleString('ko-KR') + '원', color: 'text-rise' },
          { label: '저가', value: priceData.lowPrice.toLocaleString('ko-KR') + '원', color: 'text-fall' },
          {
            label: '거래량',
            value:
              priceData.volume >= 10000
                ? `${(priceData.volume / 10000).toFixed(0)}만주`
                : `${priceData.volume.toLocaleString('ko-KR')}주`,
          },
        ].map((item) => (
          <div key={item.label} className="bg-card border border-border rounded-lg px-3 py-2.5">
            <p className="text-xs text-text-muted">{item.label}</p>
            <p className={`text-sm font-semibold mt-0.5 ${item.color || 'text-text-primary'}`}>
              {item.value}
            </p>
          </div>
        ))}
      </div>

      {/* 주가 차트 (Client Component, dynamic import) */}
      <PriceChart
        ticker={ticker}
        currentPrice={priceData.currentPrice}
        changePercent={priceData.changePercent}
      />

      {/* AI 분석 섹션 — 탭 기반 */}
      <AnalysisSection ticker={ticker} />

      {/* 뉴스/공시 패널 — AdGate 잠금 */}
      <div className="bg-card border border-border rounded-xl p-4">
        <AdGate ticker={ticker} label="뉴스 센티먼트 분석 잠금">
          <NewsPanel ticker={ticker} />
        </AdGate>
      </div>

      {/* 법적 고지 */}
      <div className="p-4 bg-warning/5 border border-warning/20 rounded-xl">
        <p className="text-xs text-warning/70 leading-relaxed">
          <strong className="text-warning">투자 유의사항:</strong>{' '}
          본 페이지의 모든 AI 분석 결과는 참고 목적으로만 제공되며, 투자 권유 또는 투자 조언이 아닙니다.
          과거의 수익률이 미래의 수익률을 보장하지 않으며, 투자 결과에 대한 책임은 전적으로 투자자 본인에게 있습니다.
        </p>
      </div>
    </div>
  )
}
