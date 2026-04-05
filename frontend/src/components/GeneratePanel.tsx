import { useState } from 'react'
import { useStore } from '../store'
import { Sparkles, Mic, Type, Settings2, Check, Loader2, ChevronDown, ChevronUp } from 'lucide-react'

const VOICES = [
  { id: 'voice_troll', name: 'Troll', desc: 'Mistral signature voice', icon: '🎭' },
  { id: 'coral', name: 'Coral', desc: 'Warm and engaging', icon: '🪸' },
  { id: 'lena', name: 'Lena', desc: 'Professional and clear', icon: '🎙️' },
  { id: 'mike', name: 'Mike', desc: 'Deep and authoritative', icon: '🎤' },
  { id: 'thomas', name: 'Thomas', desc: 'Friendly and conversational', icon: '💬' },
]

const SUB_STYLES = [
  { id: 'classic', name: 'Classic', c: '#FFD700' },
  { id: 'modern', name: 'Modern', c: '#4DEEEA' },
  { id: 'minimal', name: 'Minimal', c: '#FF6B6B' },
  { id: 'youtube', name: 'YouTube', c: '#FFD700' },
]

const BACKGROUNDS = [
  { id: 'subway_surfers', name: 'Subway Surfers', e: '🏃' },
  { id: 'minecraft_parkour', name: 'Minecraft PK', e: '⛏️' },
  { id: 'csgo', name: 'CS2', e: '🔫' },
  { id: 'satisfying', name: 'Satisfying', e: '✨' },
]

export function GeneratePanel() {
  const { selectedPost, generateOptions, setGen, generateVideo, currentJob } = useStore()
  const [showAdv, setShowAdv] = useState(false)

  const ttsText = selectedPost
    ? ((selectedPost.body?.trim().length ?? 0) > 10
      ? `${selectedPost.title}\n${selectedPost.body}`
      : (selectedPost.top_comment?.trim().length ?? 0) > 10
        ? `${selectedPost.title}\n${selectedPost.top_comment}`
        : selectedPost.title)
    : ''

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <div className="px-5 py-3.5 border-b" style={{ borderColor: 'var(--border)' }}>
        <h2 className="text-base font-bold">Generate Video</h2>
        <p className="text-xs mt-0.5" style={{ color: 'var(--text-secondary)' }}>Configure narration and rendering options</p>
      </div>

      <div className="flex-1 overflow-y-auto px-5 py-3 space-y-3">
        {/* Selected post */}
        {selectedPost ? (
          <div className="rounded-lg border p-3" style={{ background: 'var(--primary-muted)', borderColor: 'var(--primary)' }}>
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-semibold uppercase tracking-wider" style={{ color: 'var(--primary)' }}>Selected Post</span>
              <span className="text-[10px] font-mono" style={{ color: 'var(--text-muted)' }}>~{ttsText.split(/\s+/).length} words</span>
            </div>
            <p className="text-sm font-semibold mt-1 line-clamp-2">{selectedPost.title}</p>
            <span className="text-[11px]" style={{ color: 'var(--text-muted)' }}>r/{selectedPost.subreddit} · {typeof selectedPost.score === 'number' ? selectedPost.score.toLocaleString() : selectedPost.score} upvotes</span>
            <details className="mt-2">
              <summary className="text-[11px] cursor-pointer" style={{ color: 'var(--text-secondary)' }}>Narration preview</summary>
              <p className="text-[11px] mt-1 leading-relaxed" style={{ color: 'var(--text-secondary)' }}>{ttsText.substring(0, 300)}{ttsText.length > 300 ? '...' : ''}</p>
            </details>
          </div>
        ) : (
          <div className="rounded-lg border border-dashed p-4 text-center" style={{ borderColor: 'var(--border)', color: 'var(--text-muted)' }}>
            <p className="text-sm font-medium mb-0.5">No post selected</p>
            <p className="text-xs">Go to Reddit Browser to pick a post first</p>
          </div>
        )}

        {/* Voice */}
        <Section title="Voice" icon={Mic}>
          <div className="grid grid-cols-1 gap-1">
            {VOICES.map(v => (
              <button key={v.id} onClick={() => setGen({ voice: v.id })}
                className="flex items-center gap-2.5 px-2.5 py-2 rounded text-left transition-all"
                style={{
                  background: generateOptions.voice === v.id ? 'var(--primary-muted)' : 'var(--surface-elevated)',
                  border: `1px solid ${generateOptions.voice === v.id ? 'var(--primary)' : 'var(--border)'}`,
                }}>
                <span className="text-base">{v.icon}</span>
                <div className="flex-1 min-w-0">
                  <span className="text-[0.85rem] font-medium">{v.name}</span>
                  <span className="text-[10px] block" style={{ color: 'var(--text-muted)' }}>{v.desc}</span>
                </div>
                {generateOptions.voice === v.id && <Check size={14} style={{ color: 'var(--primary)' }} />}
              </button>
            ))}
          </div>
        </Section>

        {/* Backgrounds */}
        <Section title="Backgrounds" icon={Sparkles}>
          <div className="space-y-2">
            <div>
              <label className="text-[10px] font-semibold uppercase tracking-wider mb-1 block" style={{ color: 'var(--text-muted)' }}>Primary</label>
              <div className="grid grid-cols-4 gap-1">
                {BACKGROUNDS.map(b => (
                  <button key={b.id} onClick={() => setGen({ background: b.id })}
                    className="flex flex-col items-center gap-0.5 p-2 rounded text-center transition-all"
                    style={{
                      background: generateOptions.background === b.id ? 'var(--primary-muted)' : 'var(--surface-elevated)',
                      border: `1px solid ${generateOptions.background === b.id ? 'var(--primary)' : 'var(--border)'}`,
                    }}>
                    <span className="text-lg">{b.e}</span>
                    <span className="text-[10px] font-medium">{b.name}</span>
                  </button>
                ))}
              </div>
            </div>
            <div>
              <label className="text-[10px] font-semibold uppercase tracking-wider mb-1 block" style={{ color: 'var(--text-muted)' }}>Secondary (alternates)</label>
              <div className="grid grid-cols-4 gap-1">
                {BACKGROUNDS.map(b => (
                  <button key={`s-${b.id}`} onClick={() => setGen({ secondary_background: b.id })}
                    className="flex flex-col items-center gap-0.5 p-2 rounded text-center transition-all"
                    style={{
                      background: generateOptions.secondary_background === b.id ? 'var(--primary-muted)' : 'var(--surface-elevated)',
                      border: `1px solid ${generateOptions.secondary_background === b.id ? 'var(--primary)' : 'var(--border)'}`,
                    }}>
                    <span className="text-lg">{b.e}</span>
                    <span className="text-[10px] font-medium">{b.name}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </Section>

        {/* Subtitles */}
        <Section title="Subtitle Style" icon={Type}>
          <div className="grid grid-cols-4 gap-1">
            {SUB_STYLES.map(s => (
              <button key={s.id} onClick={() => setGen({ subtitle_style: s.id })}
                className="flex flex-col items-center gap-1.5 px-2 py-2.5 rounded text-center transition-all"
                style={{
                  background: generateOptions.subtitle_style === s.id ? 'var(--primary-muted)' : 'var(--surface-elevated)',
                  border: `1px solid ${generateOptions.subtitle_style === s.id ? 'var(--primary)' : 'var(--border)'}`,
                }}>
                <span className="w-3.5 h-3.5 rounded-full" style={{ background: s.c }} />
                <span className="text-[0.8rem] font-medium">{s.name}</span>
              </button>
            ))}
          </div>
        </Section>

        {/* Advanced */}
        <Section title="Advanced" icon={Settings2}>
          <button className="flex items-center gap-1.5 text-[0.8rem]"
            style={{ color: 'var(--text-secondary)' }}
            onClick={() => setShowAdv(!showAdv)}>
            {showAdv ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
            {showAdv ? 'Hide advanced' : 'Show advanced'}
          </button>
          {showAdv && (
            <div className="animate-slide-down mt-2 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[0.85rem]">Frame rate</span>
                <div className="flex gap-1">
                  {[24, 30, 60].map(f => (
                    <button key={f} onClick={() => setGen({ fps: f })}
                      className="px-3 py-1 rounded-[3px] text-[0.8rem] font-medium transition-all border"
                      style={{
                        background: generateOptions.fps === f ? 'var(--primary-muted)' : 'var(--surface-elevated)',
                        borderColor: generateOptions.fps === f ? 'var(--primary)' : 'var(--border)',
                        color: generateOptions.fps === f ? 'var(--primary)' : 'var(--text-secondary)',
                      }}>{f} fps</button>
                  ))}
                </div>
              </div>
            </div>
          )}
        </Section>
      </div>

      {/* Generate button / progress */}
      <div className="px-5 py-3 border-t" style={{ borderColor: 'var(--border)' }}>
        {currentJob ? (
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-[0.8rem]">
              <span style={{ color: 'var(--text-secondary)' }}>
                <Loader2 size={11} className="animate-spin inline mr-1" />{currentJob.stage}
              </span>
              <span className="font-mono font-semibold" style={{ color: 'var(--primary)' }}>{currentJob.progress}%</span>
            </div>
            <div className="progress-bar-track">
              <div className="progress-bar-fill" style={{ width: `${currentJob.progress}%` }} />
            </div>
          </div>
        ) : (
          <button className="btn-primary w-full justify-center py-2 text-[0.85rem]" onClick={generateVideo} disabled={!selectedPost}>
            <Sparkles size={14} />
            Generate Video
          </button>
        )}
      </div>
    </div>
  )
}

function Section({ title, icon: Icon, children }: { title: string; icon: any; children: React.ReactNode }) {
  return (
    <div className="animate-slide-up">
      <div className="flex items-center gap-1.5 mb-2">
        <Icon size={13} style={{ color: 'var(--primary)' }} />
        <h3 className="text-[0.85rem] font-bold">{title}</h3>
      </div>
      {children}
    </div>
  )
}
