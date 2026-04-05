import { useEffect } from 'react'
import { useStore } from './store'
import { Sidebar } from './components/Sidebar'
import { PostBrowser } from './components/PostBrowser'
import { GeneratePanel } from './components/GeneratePanel'
import { AssetLibrary } from './components/AssetLibrary'
import { JobQueue } from './components/JobQueue'
import { SettingsModal } from './components/SettingsModal'
import { VideoPreview } from './components/VideoPreview'
import { StatusBar } from './components/StatusBar'
import { Toast } from './components/Toast'
import { Zap } from 'lucide-react'

export default function App() {
  const { activeTab, fetchConfig, fetchAssets, fetchJobHistory } = useStore()

  useEffect(() => { fetchConfig(); fetchAssets(); fetchJobHistory() }, [fetchConfig, fetchAssets, fetchJobHistory])

  return (
    <div className="h-screen flex flex-col overflow-hidden" style={{ background: 'var(--background)' }}>
      {/* Top Bar */}
      <header className="flex items-center justify-between px-5 border-b"
        style={{ background: 'var(--surface)', borderColor: 'var(--border)', height: 44, minHeight: 44 }}>
        <div className="flex items-center gap-2.5">
          <div className="flex items-center justify-center w-7 h-7 rounded" style={{ background: 'var(--primary-muted)' }}>
            <Zap size={13} style={{ color: 'var(--primary)' }} strokeWidth={2.5} />
          </div>
          <span className="text-sm font-bold tracking-tight gradient-text">Slop Factory</span>
          <span className="text-[9px] font-mono px-1.5 py-0.5 rounded"
            style={{ background: 'var(--surface-elevated)', color: 'var(--text-muted)', border: '1px solid var(--border)' }}>v1.0</span>
        </div>
        <div className="flex items-center gap-2">
          <button className="btn-ghost text-xs" onClick={() => useStore.getState().setSettingsOpen(true)}
            style={{ color: 'var(--text-secondary)' }}>
            <span>Settings</span>
            <span className="kbd">,</span>
          </button>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-hidden flex">
          <Content />
          <VideoPreview />
        </main>
      </div>

      <StatusBar />
      <SettingsModal />
      <Toast />
    </div>
  )
}

function Content() {
  const t = useStore(s => s.activeTab)
  if (t === 'fetch') return <PostBrowser />
  if (t === 'generate') return <GeneratePanel />
  if (t === 'assets') return <AssetLibrary />
  if (t === 'queue') return <JobQueue />
  return null
}
