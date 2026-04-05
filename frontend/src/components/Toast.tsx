import { useStore } from '../store'
import { CheckCircle, XCircle, Info, X } from 'lucide-react'

export function Toast() {
  const { toast } = useStore()
  if (!toast) return null

  const icon = toast.type === 'success' ? <CheckCircle size={15} style={{ color: 'var(--success)' }} />
    : toast.type === 'error' ? <XCircle size={15} style={{ color: 'var(--danger)' }} />
    : <Info size={15} style={{ color: 'var(--primary)' }} />

  return (
    <div className="toast" style={{ background: 'var(--surface-elevated)', borderColor: 'var(--border)' }}>
      {icon}
      <span className="text-xs flex-1">{toast.message}</span>
      <button className="btn-ghost" onClick={() => useStore.setState({ toast: null })}><X size={12} /></button>
    </div>
  )
}
