import { useEffect } from 'react'
import { useStore } from '../store'
import { Search, Wand2, Film, ListVideo, Settings, Loader2, CheckCircle2, Zap } from 'lucide-react'

const TABS = [
  { id: 'fetch', label: 'Reddit Browser', icon: Search, kbd: '1' },
  { id: 'generate', label: 'Generate', icon: Wand2, kbd: '2' },
  { id: 'assets', label: 'Asset Library', icon: Film, kbd: '3' },
  { id: 'queue', label: 'Job Queue', icon: ListVideo, kbd: '4' },
]

export function Sidebar() {
  const { activeTab, setActiveTab, currentJob, config, setSettingsOpen } = useStore()
  const ready = config?.has_reddit && config?.has_mistral

  // Keyboard shortcuts
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLSelectElement) return
      const num = parseInt(e.key)
      if (num >= 1 && num <= 4) {
        setActiveTab(TABS[num - 1].id)
        return
      }
      if (e.key === ',') {
        setSettingsOpen(true)
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [setActiveTab, setSettingsOpen])

  return (
    <nav className="flex flex-col py-3 border-r" style={{ width: 200, minWidth: 200, background: 'var(--surface)', borderColor: 'var(--border)' }}>
      <div className="px-3 mb-3">
        <span className="text-[10px] font-semibold uppercase tracking-[0.12em]" style={{ color: 'var(--text-muted)' }}>Workspace</span>
      </div>

      {TABS.map(t => (
        <button key={t.id} onClick={() => setActiveTab(t.id)}
          className="flex items-center justify-between mx-1.5 px-3 py-2 rounded text-[0.85rem] transition-all duration-100 cursor-pointer"
          style={{
            background: activeTab === t.id ? 'var(--primary-muted)' : 'transparent',
            color: activeTab === t.id ? 'var(--primary)' : 'var(--text-secondary)',
            fontWeight: activeTab === t.id ? 600 : 400,
          }}>
          <div className="flex items-center gap-2.5">
            <t.icon size={15} />
            {t.label}
          </div>
          <span className="flex items-center gap-1">
            {t.id === 'queue' && currentJob && <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse" />}
            <span className="kbd">{t.kbd}</span>
          </span>
        </button>
      ))}

      <div className="flex-1" />

      {/* Connection status */}
      <div className="px-3 py-2 border-t" style={{ borderColor: 'var(--border)' }}>
        <div className="flex items-center gap-2 mb-1">
          <div className="w-1.5 h-1.5 rounded-full" style={{ background: ready ? 'var(--success)' : 'var(--warning)' }} />
          <span className="text-[10px] font-semibold uppercase tracking-[0.1em]" style={{ color: 'var(--text-muted)' }}>
            {ready ? 'Ready' : 'Setup needed'}
          </span>
        </div>
        {!ready && !config && (
          <div className="flex items-center gap-1" style={{ color: 'var(--text-muted)' }}>
            <Loader2 size={9} className="animate-spin" />
            <span className="text-[10px]">Checking...</span>
          </div>
        )}
        {!ready && config && (
          <button className="text-[10px] mt-0.5 hover:underline" style={{ color: 'var(--primary)' }}
            onClick={() => setSettingsOpen(true)}>
            Configure keys &rarr;
          </button>
        )}
      </div>
    </nav>
  )
}
