'use client'

// PriceChart — TradingView Lightweight Charts 주가 차트
// dynamic import로 SSR 우회 (lightweight-charts는 브라우저 전용)

import { useEffect, useRef, useState, useCallback } from 'react'
import { getStockChart } from '@/lib/api'
import type { CandleData } from '@/types/stock'
import { ChartSkeleton } from '@/components/ui/LoadingSkeleton'
import { InlineError } from '@/components/ui/ErrorBoundary'

type Period = '1D' | '1W' | '1M' | '3M' | '1Y'

const PERIODS: { label: string; value: Period }[] = [
  { label: '1일', value: '1D' },
  { label: '1주', value: '1W' },
  { label: '1개월', value: '1M' },
  { label: '3개월', value: '3M' },
  { label: '1년', value: '1Y' },
]

interface PriceChartProps {
  ticker: string
  currentPrice: number
  changePercent: number
}

export default function PriceChart({ ticker, currentPrice, changePercent }: PriceChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null)
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const chartRef = useRef<any>(null)
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const seriesRef = useRef<any>(null)

  const [period, setPeriod] = useState<Period>('3M')
  const [candles, setCandles] = useState<CandleData[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const isPositive = changePercent >= 0

  // 차트 데이터 로드
  const loadChartData = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const data = await getStockChart(ticker, period)
      setCandles(data)
    } catch {
      setError('차트 데이터를 불러오는 중 오류가 발생했습니다.')
    } finally {
      setIsLoading(false)
    }
  }, [ticker, period])

  useEffect(() => {
    loadChartData()
  }, [loadChartData])

  // Lightweight Charts 초기화 및 업데이트
  useEffect(() => {
    if (!chartContainerRef.current || candles.length === 0) return

    // 동적 임포트
    import('lightweight-charts').then(({ createChart, ColorType }) => {
      const container = chartContainerRef.current!

      // 기존 차트 제거
      if (chartRef.current) {
        chartRef.current.remove()
        chartRef.current = null
      }

      // 차트 생성
      const chart = createChart(container, {
        layout: {
          background: { type: ColorType.Solid, color: '#1A2235' },
          textColor: '#94A3B8',
        },
        grid: {
          vertLines: { color: '#1E293B' },
          horzLines: { color: '#1E293B' },
        },
        crosshair: {
          mode: 1,
        },
        rightPriceScale: {
          borderColor: '#1E293B',
          textColor: '#94A3B8',
        },
        timeScale: {
          borderColor: '#1E293B',
          timeVisible: true,
        },
        width: container.clientWidth,
        height: 280,
      })

      // 캔들스틱 시리즈 추가 (v4 API)
      const candleSeries = chart.addCandlestickSeries({
        upColor: '#EF4444',        // 상승: 빨강 (한국 시장)
        downColor: '#3B82F6',      // 하락: 파랑 (한국 시장)
        borderUpColor: '#EF4444',
        borderDownColor: '#3B82F6',
        wickUpColor: '#EF4444',
        wickDownColor: '#3B82F6',
      })

      // 데이터 설정
      candleSeries.setData(
        candles.map((c) => ({
          time: c.time as `${number}-${number}-${number}`,
          open: c.open,
          high: c.high,
          low: c.low,
          close: c.close,
        }))
      )

      // 차트 fit
      chart.timeScale().fitContent()

      chartRef.current = chart
      seriesRef.current = candleSeries

      // 반응형 리사이즈
      const resizeObserver = new ResizeObserver((entries) => {
        if (entries[0]) {
          chart.applyOptions({ width: entries[0].contentRect.width })
        }
      })
      resizeObserver.observe(container)

      return () => {
        resizeObserver.disconnect()
      }
    })

    return () => {
      if (chartRef.current) {
        chartRef.current.remove()
        chartRef.current = null
      }
    }
  }, [candles])

  if (isLoading) return <ChartSkeleton />

  return (
    <div className="bg-card border border-border rounded-xl p-4">
      {/* 가격 헤더 */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-baseline gap-3">
          <span className="text-2xl font-bold text-text-primary">
            {currentPrice.toLocaleString('ko-KR')}원
          </span>
          <span className={`text-sm font-medium ${isPositive ? 'text-rise' : 'text-fall'}`}>
            {isPositive ? '+' : ''}{changePercent.toFixed(2)}%
          </span>
        </div>

        {/* 기간 선택 */}
        <div className="flex items-center gap-1">
          {PERIODS.map((p) => (
            <button
              key={p.value}
              onClick={() => setPeriod(p.value)}
              className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-colors ${
                period === p.value
                  ? 'bg-primary text-white'
                  : 'text-text-muted hover:text-text-secondary hover:bg-surface'
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {/* 에러 표시 */}
      {error && (
        <InlineError message={error} onRetry={loadChartData} />
      )}

      {/* 차트 컨테이너 */}
      <div ref={chartContainerRef} className="w-full rounded-lg overflow-hidden" />

      {/* 데이터 출처 */}
      <p className="text-xs text-text-muted mt-2 text-right">
        데이터 출처: pykrx
      </p>
    </div>
  )
}
