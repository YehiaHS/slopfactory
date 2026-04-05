import { useStore } from '../store'
import { CheckCircle2, Zap, Loader2 } from 'lucide-react'

export function StatusBar() {
  const { config, currentJob } = useStore()
  const ready = config?.has_reddit && config?.has_mistral

  return (
    <footer className="flex items-center justify-between px-4 select-none"
      style={{ height: 24, minHeight: 24, background: 'var(--surface)', borderTop: '1px solid var(--border)', fontSize: 10 }}>
      <div className="flex items-center gap-3">
        {ready ? (
          <span className="flex items-center gap-1" style={{ color: 'var(--success)' }}>
            <CheckCircle2 size={9} /> Ready
          </span>
        ) : (
          <span className="flex items-center gap-1" style={{ color: 'var(--warning)' }}>
            <Zap size={9} /> Configure API keys
          </span>
        )}
        {currentJob && currentJob.status !== 'completed' && currentJob.status !== 'failed' && (
          <span className="flex items-center gap-1" style={{ color: 'var(--primary)' }}>
            <Loader2 size={9} className="animate-spin" />
            {currentJob.stage} &mdash; {currentJob.progress}%
          </span>
        )}
      </div>
      <div className="flex items-center gap-3">
        <span className="font-mono" style={{ color: 'var(--text-muted)' }}>9:16 &middot; 1080x1920</span>
        <span className="font-mono" style={{ color: 'var(--text-muted)' }}>Slop Factory v1.0</span>
      </div>
    </footer>
  )
}
