import { useStore } from '../store'
import { Play, Film, ArrowUp, MessageSquare, Sparkles } from 'lucide-react'

export function VideoPreview() {
  const { selectedPost, currentJob, activeTab } = useStore()

  return (
    <div className="flex flex-col border-l select-none" style={{ width: 280, minWidth: 280, background: 'var(--surface)', borderColor: 'var(--border)' }}>
      <div className="px-4 py-2.5 border-b flex items-center justify-between" style={{ borderColor: 'var(--border)' }}>
        <div className="flex items-center gap-1.5">
          <Play size={11} style={{ color: 'var(--text-muted)' }} />
          <span className="text-[0.8rem] font-bold uppercase tracking-wider">Preview</span>
        </div>
        <span className="text-[10px] font-mono" style={{ color: 'var(--text-muted)' }}>9:16</span>
      </div>

      <div className="flex-1 flex items-center justify-center p-3 overflow-hidden">
        <div className="w-full rounded-lg overflow-hidden relative" style={{ aspectRatio: '9/16', maxHeight: 'calc(100vh - 140px)', border: '1px solid var(--border)' }}>
          {/* Background gradient simulating gameplay footage */}
          <div className="absolute inset-0 flex flex-col" style={{ background: 'linear-gradient(180deg, #0a0f14 0%, #111827 50%, #0a0f14 100%)' }}>
            {/* Animated subtle effect */}
            <div className="absolute inset-0 opacity-5" style={{
              backgroundImage: 'radial-gradient(circle at 30% 70%, #22c55e 0%, transparent 50%), radial-gradient(circle at 70% 30%, #38bdf8 0%, transparent 50%)',
            }} />

            <div className="relative z-10 flex flex-col h-full">
              {/* Reddit card overlay */}
              <div className="mx-2 mt-2 px-3 pt-2.5 pb-2 rounded-lg" style={{ background: 'rgba(18,18,18,0.88)', backdropFilter: 'blur(8px)' }}>
                {selectedPost ? (
                  <>
                    <div className="flex items-center gap-1.5 mb-1">
                      <div className="w-4 h-4 rounded-full" style={{ background: '#FF4500' }} />
                      <span className="text-[11px] font-semibold">r/{selectedPost.subreddit}</span>
                    </div>
                    <p className="text-[0.8rem] font-semibold leading-tight">{selectedPost.title}</p>
                    <div className="flex items-center gap-3 mt-1.5 text-[10px]" style={{ color: 'var(--text-muted)' }}>
                      <span className="flex items-center gap-0.5"><ArrowUp size={10} color="var(--primary)" />{selectedPost.score >= 1000 ? `${(selectedPost.score/1000).toFixed(1)}k` : selectedPost.score}</span>
                      <span className="flex items-center gap-0.5"><MessageSquare size={10} />{selectedPost.num_comments}</span>
                    </div>
                  </>
                ) : (
                  <div className="py-4 text-center" style={{ color: 'var(--text-muted)' }}>
                    <Film size={16} className="mx-auto mb-1 opacity-20" />
                    <p className="text-[10px]">No post selected</p>
                  </div>
                )}
              </div>

              {/* Gameplay area */}
              <div className="flex-1 flex items-center justify-center">
                {currentJob?.status === 'processing' && (
                  <div className="text-center animate-fade-in">
                    <Sparkles size={20} className="mx-auto mb-2 animate-pulse" style={{ color: 'var(--primary)' }} />
                    <p className="text-[10px]" style={{ color: 'var(--text-secondary)' }}>{currentJob.stage}</p>
                    <p className="text-xs font-mono font-bold mt-1" style={{ color: 'var(--primary)' }}>{currentJob.progress}%</p>
                  </div>
                )}
                {!currentJob && !selectedPost && (
                  <div className="text-center" style={{ color: 'var(--text-muted)' }}>
                    <Film size={24} className="mx-auto mb-1 opacity-10" />
                    <p className="text-[10px]">Select a post to preview layout</p>
                  </div>
                )}
                {!currentJob && selectedPost && (
                  <div className="text-center" style={{ color: 'var(--text-muted)' }}>
                    <Play size={24} className="mx-auto mb-1 opacity-10" />
                    <p className="text-[10px]">Generate to see the video</p>
                  </div>
                )}
              </div>

              {/* Subtitle bar */}
              <div className="px-2.5 pb-2.5">
                {selectedPost ? (
                  <div className="rounded-lg px-3 py-2 text-center" style={{ background: 'rgba(0,0,0,0.85)', backdropFilter: 'blur(4px)' }}>
                    <p className="text-[0.85rem] font-bold" style={{ color: '#FFD700' }}>
                      {selectedPost.title.substring(0, 45)}
                      {selectedPost.title.length > 45 && '...'}
                    </p>
                  </div>
                ) : (
                  <div className="rounded-lg px-3 py-2 text-center" style={{ background: 'rgba(0,0,0,0.5)' }}>
                    <p className="text-[10px]" style={{ color: 'var(--text-muted)' }}>Subtitles appear here</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
