export default function Footer() {
  return (
    <footer className="border-t border-border bg-surface mt-auto">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          {/* 브랜드 */}
          <div className="flex items-center gap-2">
            <span className="font-bold text-text-primary">
              StockMind <span className="text-primary">AI</span>
            </span>
            <span className="text-text-muted text-sm">|</span>
            <span className="text-text-muted text-sm">AI 기반 주식 분석 서비스</span>
          </div>

          {/* 법적 고지 */}
          <p className="text-xs text-text-muted text-center md:text-right max-w-lg">
            본 서비스의 모든 분석 결과는 참고 목적으로만 제공되며, 투자 권유 또는 투자 조언이 아닙니다.
            투자 결과에 대한 책임은 전적으로 투자자 본인에게 있습니다.
          </p>
        </div>

        <div className="mt-4 pt-4 border-t border-border flex flex-col sm:flex-row items-center justify-between gap-2">
          <p className="text-xs text-text-muted">
            © 2026 StockMind AI. All rights reserved.
          </p>
          <div className="flex items-center gap-4 text-xs text-text-muted">
            <span>데이터 출처: pykrx, Alpha Vantage, OpenDART</span>
          </div>
        </div>
      </div>
    </footer>
  )
}
