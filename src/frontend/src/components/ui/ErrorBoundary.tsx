'use client'

// ErrorBoundary — React 에러 경계 컴포넌트
// 하위 컴포넌트에서 발생한 에러를 잡아 대체 UI를 표시

import { Component, type ReactNode } from 'react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
  onError?: (error: Error, info: { componentStack: string }) => void
}

interface State {
  hasError: boolean
  error: Error | null
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, info: { componentStack: string }) {
    // 에러 로깅 (향후 Sentry 등 연동)
    console.error('[StockMind ErrorBoundary]', error, info)
    this.props.onError?.(error, info)
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <DefaultErrorUI
          error={this.state.error}
          onRetry={() => this.setState({ hasError: false, error: null })}
        />
      )
    }

    return this.props.children
  }
}

/** 기본 에러 UI */
function DefaultErrorUI({
  error,
  onRetry,
}: {
  error: Error | null
  onRetry: () => void
}) {
  return (
    <div className="flex flex-col items-center justify-center p-8 bg-card border border-border rounded-xl text-center">
      {/* 에러 아이콘 */}
      <div className="w-14 h-14 rounded-full bg-error/10 flex items-center justify-center mb-4">
        <svg
          className="w-7 h-7 text-error"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          />
        </svg>
      </div>

      <h3 className="font-semibold text-text-primary mb-1">오류가 발생했습니다</h3>
      <p className="text-sm text-text-secondary mb-4">
        일시적인 문제가 발생했습니다. 잠시 후 다시 시도해주세요.
      </p>

      {/* 개발 환경에서 에러 메시지 표시 */}
      {process.env.NODE_ENV === 'development' && error && (
        <pre className="text-xs text-error/70 bg-error/5 rounded-lg p-3 mb-4 text-left overflow-auto max-w-full">
          {error.message}
        </pre>
      )}

      <button
        onClick={onRetry}
        className="px-4 py-2 bg-primary hover:bg-primary-hover rounded-lg text-sm font-medium text-white transition-colors"
      >
        다시 시도
      </button>
    </div>
  )
}

/** API 에러 인라인 표시 컴포넌트 */
export function InlineError({
  message,
  onRetry,
}: {
  message?: string
  onRetry?: () => void
}) {
  return (
    <div className="flex items-center justify-between p-4 bg-error/5 border border-error/20 rounded-lg">
      <div className="flex items-center gap-3">
        <svg
          className="w-5 h-5 text-error shrink-0"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <p className="text-sm text-error">
          {message || '데이터를 불러오는 중 오류가 발생했습니다.'}
        </p>
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="text-xs text-primary hover:underline ml-3 shrink-0"
        >
          재시도
        </button>
      )}
    </div>
  )
}

export default ErrorBoundary
