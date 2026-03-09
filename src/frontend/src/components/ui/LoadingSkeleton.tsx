// LoadingSkeleton — 로딩 중 스켈레톤 UI 컴포넌트

import { clsx } from 'clsx'

interface SkeletonProps {
  className?: string
}

/** 기본 스켈레톤 박스 */
function Skeleton({ className }: SkeletonProps) {
  return (
    <div
      className={clsx(
        'animate-pulse bg-gradient-to-r from-card via-surface to-card bg-[length:200%_100%] rounded',
        className
      )}
      style={{
        animation: 'shimmer 1.5s infinite',
      }}
    />
  )
}

/** 종목 카드 스켈레톤 */
export function StockCardSkeleton() {
  return (
    <div className="bg-card border border-border rounded-xl p-4 space-y-3">
      <div className="flex items-center gap-3">
        <Skeleton className="w-10 h-10 rounded-lg" />
        <div className="space-y-1.5 flex-1">
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-3 w-16" />
        </div>
      </div>
      <div className="flex items-end justify-between">
        <Skeleton className="h-6 w-20" />
        <Skeleton className="h-5 w-16" />
      </div>
      <Skeleton className="h-10 w-full rounded-lg" />
    </div>
  )
}

/** 차트 스켈레톤 */
export function ChartSkeleton() {
  return (
    <div className="bg-card border border-border rounded-xl p-4 space-y-3">
      {/* 가격 정보 */}
      <div className="flex items-center gap-4">
        <Skeleton className="h-8 w-32" />
        <Skeleton className="h-6 w-20" />
      </div>
      {/* 차트 영역 */}
      <Skeleton className="h-64 w-full rounded-lg" />
      {/* 기간 선택 버튼 */}
      <div className="flex gap-2">
        {['1D', '1W', '1M', '3M', '1Y'].map((p) => (
          <Skeleton key={p} className="h-8 w-12 rounded-lg" />
        ))}
      </div>
    </div>
  )
}

/** 분석 섹션 스켈레톤 */
export function AnalysisSkeleton() {
  return (
    <div className="bg-card border border-border rounded-xl p-4 space-y-4">
      {/* 탭 */}
      <div className="flex gap-2 border-b border-border pb-3">
        {[1, 2, 3, 4].map((i) => (
          <Skeleton key={i} className="h-8 w-24 rounded-lg" />
        ))}
      </div>
      {/* 요약 */}
      <div className="space-y-2">
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-4/5" />
        <Skeleton className="h-4 w-3/4" />
      </div>
      {/* 점수 */}
      <div className="flex items-center gap-4">
        <Skeleton className="w-16 h-16 rounded-full" />
        <div className="space-y-2 flex-1">
          <Skeleton className="h-3 w-full rounded-full" />
          <Skeleton className="h-3 w-3/4 rounded-full" />
        </div>
      </div>
    </div>
  )
}

/** 뉴스 패널 스켈레톤 */
export function NewsPanelSkeleton() {
  return (
    <div className="bg-card border border-border rounded-xl p-4 space-y-3">
      <Skeleton className="h-5 w-24" />
      {[1, 2, 3].map((i) => (
        <div key={i} className="space-y-2 py-3 border-b border-border last:border-0">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-4/5" />
          <div className="flex gap-2">
            <Skeleton className="h-3 w-16" />
            <Skeleton className="h-3 w-12" />
          </div>
        </div>
      ))}
    </div>
  )
}

/** 홈 페이지 인기 종목 그리드 스켈레톤 */
export function PopularStocksSkeleton() {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
      {Array.from({ length: 6 }).map((_, i) => (
        <StockCardSkeleton key={i} />
      ))}
    </div>
  )
}

// shimmer 애니메이션 CSS를 globals.css에 추가해야 함
export default Skeleton
