import { useState } from 'react'
import { useStore, type VideoAsset } from '../store'
import { Film, Download, CheckCircle, Play, HardDrive, Loader2 } from 'lucide-react'

const CAT_META: Record<string, { name: string; emoji: string; desc: string }> = {
  subway_surfers: { name: 'Subway Surfers', emoji: '🏃', desc: 'Endless runner gameplay' },
  minecraft_parkour: { name: 'Minecraft Parkour', emoji: '⛏️', desc: 'Parkour challenge maps' },
  csgo: { name: 'CS2 Gameplay', emoji: '🔫', desc: 'Counter-Strike 2 action' },
  satisfying: { name: 'Satisfying', emoji: '✨', desc: 'Oddly satisfying visuals' },
}

export function AssetLibrary() {
  const { assets, categories, assetsLoading, downloadAsset } = useStore()
  const totalReady = Object.values(assets).reduce((s, arr) => s + arr.filter(a => a.is_downloaded).length, 0)
  const total = Object.values(assets).reduce((s, arr) => s + arr.length, 0)

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <div className="px-5 py-3.5 border-b flex items-center justify-between" style={{ borderColor: 'var(--border)' }}>
        <div>
          <h2 className="text-base font-bold">Asset Library</h2>
          <p className="text-xs mt-0.5" style={{ color: 'var(--text-secondary)' }}>Background footage to accompany your narration</p>
        </div>
        {total > 0 && (
          <span className={`badge ${totalReady === total ? 'badge-success' : 'badge-warning'}`}>
            {totalReady}/{total} Ready
          </span>
        )}
      </div>

      <div className="flex-1 overflow-y-auto px-5 py-4">
        {assetsLoading ? (
          <div className="flex items-center justify-center h-full" style={{ color: 'var(--text-muted)' }}>
            <Loader2 size={20} className="animate-spin mr-2" /> Loading assets...
          </div>
        ) : categories.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full" style={{ color: 'var(--text-muted)' }}>
            <HardDrive size={40} className="mb-3 opacity-20" />
            <p className="text-sm font-medium mb-1">No assets available</p>
            <p className="text-xs">Background video references are loaded from the catalog</p>
          </div>
        ) : (
          <div className="space-y-5">
            {categories.map(cat => {
              const meta = CAT_META[cat] || { name: cat, emoji: '🎬', desc: '' }
              const items = assets[cat] || []
              const ready = items.filter(a => a.is_downloaded).length
              return (
                <div key={cat}>
                  <div className="flex items-center justify-between mb-2.5">
                    <div className="flex items-center gap-2">
                      <span className="text-lg">{meta.emoji}</span>
                      <div>
                        <h3 className="text-sm font-bold">{meta.name}</h3>
                        <p className="text-[11px]" style={{ color: 'var(--text-muted)' }}>{meta.desc}</p>
                      </div>
                    </div>
                    <span className="text-[11px] font-mono" style={{ color: 'var(--text-muted)' }}>{ready}/{items.length}</span>
                  </div>
                  <div className="grid grid-cols-3 gap-2">
                    {items.map(a => (
                      <div key={a.id} className="rounded-lg overflow-hidden transition-all duration-100 hover:scale-[1.02]"
                        style={{ background: 'var(--surface-elevated)', border: '1px solid var(--border)', opacity: a.is_downloaded ? 1 : 0.6 }}>
                        <div className="aspect-video flex items-center justify-center" style={{ background: 'var(--background)' }}>
                          {a.is_downloaded
                            ? <Play size={20} style={{ color: 'var(--primary)', opacity: 0.5 }} />
                            : <Download size={18} style={{ color: 'var(--text-muted)', opacity: 0.3 }} />
                          }
                        </div>
                        <div className="px-2.5 py-2">
                          <p className="text-xs font-semibold truncate">{a.title}</p>
                          <div className="flex items-center justify-between mt-1">
                            <span className="text-[10px]" style={{ color: 'var(--text-muted)' }}>{a.duration}s · {a.source}</span>
                            {a.is_downloaded
                              ? <CheckCircle size={12} style={{ color: 'var(--success)' }} />
                              : <button className="btn-ghost p-0.5"
                                  onClick={() => downloadAsset(a.id)}>
                                <Download size={12} style={{ color: 'var(--primary)' }} />
                              </button>
                            }
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
