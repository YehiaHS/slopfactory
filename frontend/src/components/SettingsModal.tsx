import { useState } from 'react'
import { useStore } from '../store'
import { X, Key, Save, CheckCircle, AlertCircle, Check } from 'lucide-react'

export function SettingsModal() {
  const { settingsOpen, setSettingsOpen, config, updateSettings } = useStore()
  const [clientId, setClientId] = useState('')
  const [clientSecret, setClientSecret] = useState('')
  const [apiKey, setApiKey] = useState('')
  const [showS, setShowS] = useState(false)
  const [showK, setShowK] = useState(false)
  const [saving, setSaving] = useState(false)

  if (!settingsOpen) return null

  const save = () => {
    setSaving(true)
    const u: Record<string, string> = {}
    if (clientId.trim()) u.reddit_client_id = clientId.trim()
    if (clientSecret.trim()) u.reddit_client_secret = clientSecret.trim()
    if (apiKey.trim()) u.mistral_api_key = apiKey.trim()
    if (Object.keys(u).length === 0) {
      useStore.getState().showToast('Enter at least one API key to save', 'error')
      setSaving(false)
      return
    }
    updateSettings(u).finally(() => {
      setSaving(false)
      setSettingsOpen(false)
    })
  }

  return (
    <div className="modal-overlay" onClick={() => setSettingsOpen(false)}>
      <div className="modal-content w-full mx-4" style={{ maxWidth: 420 }} onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between px-5 py-3 border-b" style={{ borderColor: 'var(--border)' }}>
          <h2 className="text-sm font-bold">Settings</h2>
          <button className="btn-ghost" onClick={() => setSettingsOpen(false)}><X size={14} /></button>
        </div>

        <div className="p-5 space-y-5">
          {/* Reddit */}
          <div>
            <label className="text-[10px] font-semibold uppercase tracking-wider mb-2 block flex items-center gap-1.5" style={{ color: 'var(--text-muted)' }}>
              <Key size={12} /> Reddit API
            </label>
            <div className="space-y-2">
              <div>
                <label className="text-xs mb-1 block" style={{ color: 'var(--text-secondary)' }}>Client ID</label>
                <input value={clientId} onChange={e => setClientId(e.target.value)} placeholder="Your Reddit client ID" />
              </div>
              <div>
                <label className="text-xs mb-1 block" style={{ color: 'var(--text-secondary)' }}>Client Secret</label>
                <div className="relative">
                  <input type={showS ? 'text' : 'password'} value={clientSecret} onChange={e => setClientSecret(e.target.value)} placeholder="Your Reddit client secret" />
                  <button className="absolute right-2 top-1/2 -translate-y-1/2 btn-ghost p-0.5" type="button" onClick={() => setShowS(!showS)}>
                    {showS ? <Key size={13} /> : <Key size={13} />}
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Mistral */}
          <div>
            <label className="text-[10px] font-semibold uppercase tracking-wider mb-2 block flex items-center gap-1.5" style={{ color: 'var(--text-muted)' }}>
              <Key size={12} /> Mistral AI
            </label>
            <div>
              <label className="text-xs mb-1 block" style={{ color: 'var(--text-secondary)' }}>API Key</label>
              <input type={showK ? 'text' : 'password'} value={apiKey} onChange={e => setApiKey(e.target.value)} placeholder="Your Mistral API key" />
            </div>
          </div>

          {/* Status */}
          {config && (
            <div className="p-3 rounded-lg" style={{ background: 'var(--background)', border: '1px solid var(--border)' }}>
              <p className="text-[10px] font-semibold uppercase tracking-wider mb-2" style={{ color: 'var(--text-muted)' }}>Connection Status</p>
              <div className="space-y-1.5">
                {[
                  ['Reddit', config.has_reddit],
                  ['Mistral', config.has_mistral],
                ].map(([name, ok]) => (
                  <div key={name as string} className="flex items-center justify-between">
                    <span className="text-xs" style={{ color: 'var(--text-secondary)' }}>{name as string}</span>
                    {ok
                      ? <span className="badge badge-success flex items-center gap-1"><CheckCircle size={10} />Connected</span>
                      : <span className="badge badge-warning flex items-center gap-1"><AlertCircle size={10} />Not configured</span>
                    }
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="flex items-center justify-end gap-2 px-5 py-3 border-t" style={{ borderColor: 'var(--border)' }}>
          <button className="btn-secondary" onClick={() => setSettingsOpen(false)}>Cancel</button>
          <button className="btn-primary" onClick={save} disabled={saving}>
            <Save size={13} /> {saving ? 'Saving...' : 'Save'}
          </button>
        </div>
      </div>
    </div>
  )
}
