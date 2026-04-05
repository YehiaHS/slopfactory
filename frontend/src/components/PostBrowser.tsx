import { useState } from 'react'
import { useStore } from '../store'
import { Search, ArrowUp, MessageSquare, RefreshCw } from 'lucide-react'

export function PostBrowser() {
  const { fetchPosts, posts, selectedPost, selectPost, postsLoading } = useStore()
  const [subs, setSubs] = useState('AskReddit,stories,confession,nosleep')
  const [sort, setSort] = useState('hot')
  const [tf, setTf] = useState('week')
  const [limit, setLimit] = useState(15)

  const go = () => {
    const s = subs.split(',').map(x => x.trim()).filter(Boolean)
    fetchPosts(s, sort, tf, limit)
  }

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <div className="px-5 py-3.5 border-b" style={{ borderColor: 'var(--border)' }}>
        <h2 className="text-base font-bold">Fetch Reddit Posts</h2>
        <p className="text-xs mt-0.5" style={{ color: 'var(--text-secondary)' }}>
          Find the best stories to turn into videos
        </p>
      </div>
      <div className="flex gap-2 items-center px-4 py-2 border-b text-[0.8rem]" style={{ borderColor: 'var(--border)', background: 'var(--surface)' }}>
        <div className="flex-1 min-w-0">
          <input value={subs} onChange={e => setSubs(e.target.value)} onKeyDown={e => e.key === 'Enter' && go()}
            placeholder="subreddit1,subreddit2..." className="h-7 text-xs" />
        </div>
        <select value={sort} onChange={e => setSort(e.target.value)} className="h-7 text-xs w-16">
          {['hot','top','new','rising'].map(s => <option key={s} value={s}>{s}</option>)}
        </select>
        <select value={tf} onChange={e => setTf(e.target.value)} className="h-7 text-xs w-16">
          {[['hour','1h'],['day','24h'],['week','1w'],['month','1m'],['year','1y']].map(([v,l]) =>
            <option key={v} value={v}>{l}</option>)}
        </select>
        <input type="number" value={limit} onChange={e => setLimit(+e.target.value)} min={1} max={50} className="h-7 text-xs w-12" title="Limit" />
        <button className="btn-primary h-7 text-xs px-3 disabled:opacity-40" onClick={go} disabled={postsLoading}>
          <RefreshCw size={12} className={postsLoading ? 'animate-spin' : ''} />
          {postsLoading ? '...' : ''} Fetch
        </button>
      </div>
      <div className="flex-1 overflow-y-auto px-5 py-3">
        {!postsLoading && posts.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full" style={{ color: 'var(--text-muted)' }}>
            <Search size={32} className="mb-3 opacity-15" />
            <p className="text-sm font-medium mb-0.5">No posts loaded</p>
            <p className="text-xs">Configure subreddits above and hit Fetch</p>
          </div>
        )}
        {postsLoading && (
          <div className="flex flex-col items-center justify-center h-full" style={{ color: 'var(--text-muted)' }}>
            <RefreshCw size={18} className="animate-spin mb-2" />
            <p className="text-sm">Fetching top posts...</p>
          </div>
        )}
        <div className="space-y-1 pb-4">
          {posts.map(p => (
            <div key={p.id}
              className="rounded border cursor-pointer transition-all px-4 py-2.5"
              onClick={() => selectPost(p)}
              style={{
                borderColor: selectedPost?.id === p.id ? 'var(--primary)' : 'var(--border)',
                background: selectedPost?.id === p.id ? 'var(--primary-muted)' : 'var(--surface)',
              }}>
              <div className="flex gap-3">
                <div className="flex flex-col items-center pt-0.5" style={{ minWidth: 32, gap: 1 }}>
                  <ArrowUp size={12} style={{ color: 'var(--primary)' }} />
                  <span className="text-[10px] font-bold" style={{ color: 'var(--primary)' }}>{p.score >= 1000 ? `${(p.score/1000).toFixed(1)}k` : p.score}</span>
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-[0.85rem] font-semibold leading-tight mb-0.5 line-clamp-2">{p.title}</h3>
                  <div className="flex items-center gap-1.5 text-[10px]" style={{ color: 'var(--text-muted)' }}>
                    <span className="font-semibold" style={{ color: 'var(--primary)' }}>r/{p.subreddit}</span>
                    {p.num_comments > 0 && <><span>·</span><span className="flex items-center gap-0.5"><MessageSquare size={9} />{p.num_comments}</span></>}
                  </div>
                  {p.body && <p className="text-[10px] mt-1 leading-relaxed" style={{ color: 'var(--text-secondary)' }}>{p.body.substring(0, 200)}{p.body.length > 200 ? '...' : ''}</p>}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
