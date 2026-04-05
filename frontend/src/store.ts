import { create } from 'zustand'

const API = '/api'

export interface RedditPost {
  id: string; title: string; body: string; author: string;
  subreddit: string; score: number; num_comments: number;
  url: string; top_comment: string;
  comments: Array<{ author: string; body: string }>;
}

export interface VideoAsset {
  id: string; category: string; title: string; local_path: string;
  url: string; duration: number; is_downloaded: boolean; source: string;
}

export interface VideoJob {
  id: string; status: string; progress: number; stage: string;
  error: string | null; output_path: string | null;
  request: Record<string, any>; created_at: number;
}

export interface Config {
  has_reddit: boolean; has_mistral: boolean;
  max_concurrent_jobs: number; default_subreddits: string; output_dir: string;
}

export interface GenerateOptions {
  voice: string; background: string; secondary_background: string;
  subtitle_style: string; fps: number;
}

export function redditPostTTS(r: RedditPost): string {
  const body = (r.body || '').trim()
  const tc = (r.top_comment || '').trim()
  if (body.length > 10) return `${r.title}\n${body}`
  if (tc.length > 10) return `${r.title}\n${tc}`
  return r.title
}

let _pollTimer: ReturnType<typeof setTimeout> | null = null

function startPoll(jobId: string) {
  if (_pollTimer) clearTimeout(_pollTimer)
  const tick = async () => {
    try {
      const r = await fetch(`${API}/jobs/${jobId}`)
      const j = await r.json()
      useStore.setState({ currentJob: j })
      if (j.status === 'completed' || j.status === 'failed') {
        useStore.setState({ generating: false, currentJob: null })
        useStore.getState().showToast(
          j.status === 'completed' ? 'Video generated!' : `Failed: ${j.error}`,
          j.status === 'completed' ? 'success' : 'error'
        )
        return
      }
      _pollTimer = setTimeout(tick, 1500)
    } catch { _pollTimer = setTimeout(tick, 3000) }
  }
  _pollTimer = setTimeout(tick, 1500)
}

interface S {
  posts: RedditPost[]; selectedPost: RedditPost | null; postsLoading: boolean;
  fetchPosts: (subs: string[], sort: string, tf: string, limit: number) => Promise<void>;
  selectPost: (p: RedditPost) => void;

  assets: Record<string, VideoAsset[]>; categories: string[]; assetsLoading: boolean;
  fetchAssets: () => Promise<void>;

  currentJob: VideoJob | null; generating: boolean;
  jobHistory: VideoJob[];
  generateOptions: GenerateOptions;
  setGen: (o: Partial<GenerateOptions>) => void;
  generateVideo: () => Promise<void>;
  fetchJobHistory: () => Promise<void>;
  deleteJob: (id: string) => Promise<void>;
  downloadAsset: (id: string) => Promise<void>;

  config: Config | null;
  fetchConfig: () => Promise<void>;
  updateSettings: (s: { reddit_client_id?: string; reddit_client_secret?: string; mistral_api_key?: string }) => Promise<void>;

  activeTab: string; setActiveTab: (t: string) => void;
  settingsOpen: boolean; setSettingsOpen: (v: boolean) => void;

  toast: { message: string; type: 'success' | 'error' | 'info' } | null;
  showToast: (m: string, t: 'success' | 'error' | 'info') => void;
}

export const useStore = create<S>()((set, get) => ({
  posts: [], selectedPost: null, postsLoading: false,
  fetchPosts: async (subs, sort, tf, limit) => {
    set({ postsLoading: true })
    try {
      const r = await fetch(`${API}/reddit/fetch`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ subreddits: subs, sort, time_filter: tf, limit }),
      })
      const d = await r.json()
      set({ posts: d.posts ?? [], postsLoading: false })
      if (d.posts?.length > 0) set({ selectedPost: d.posts[0] })
    } catch { set({ postsLoading: false }); get().showToast('Failed to fetch posts', 'error') }
  },
  selectPost: (post) => set({ selectedPost: post }),

  assets: {}, categories: [], assetsLoading: false,
  fetchAssets: async () => {
    set({ assetsLoading: true })
    try {
      const r = await fetch(`${API}/assets`)
      const d = await r.json()
      const map: Record<string, VideoAsset[]> = {}
      const cats: string[] = d.categories ?? []
      for (const a of d.assets ?? []) {
        if (!map[a.category]) map[a.category] = []
        map[a.category].push(a)
      }
      set({ assets: map, categories: cats, assetsLoading: false })
    } catch { set({ assetsLoading: false }) }
  },

  currentJob: null, generating: false, jobHistory: [],
  generateOptions: {
    voice: 'voice_troll', background: 'subway_surfers',
    secondary_background: 'minecraft_parkour', subtitle_style: 'classic',
    fps: 30,
  },
  setGen: (o) => set((s) => ({ generateOptions: { ...s.generateOptions, ...o } })),
  generateVideo: async () => {
    const { selectedPost, generateOptions } = get()
    if (!selectedPost) { get().showToast('Select a post first', 'error'); return }
    set({ generating: true })
    try {
      const r = await fetch(`${API}/generate`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          post_id: selectedPost.id,
          post_title: selectedPost.title,
          post_text: redditPostTTS(selectedPost),
          post_subreddit: selectedPost.subreddit,
          ...generateOptions,
        }),
      })
      const d = await r.json()
      startPoll(d.job_id)
      set({ currentJob: { id: d.job_id, status: 'queued', progress: 0, stage: 'Starting...', error: null, output_path: null, request: {}, created_at: Math.floor(Date.now() / 1000) } })
    } catch { set({ generating: false }); get().showToast('Failed to start generation', 'error') }
  },

  config: null,
  fetchConfig: async () => {
    try { const r = await fetch(`${API}/config`); set({ config: await r.json() }) } catch {}
  },
  updateSettings: async (s) => {
    try {
      await fetch(`${API}/config/settings`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(s),
      })
      get().fetchConfig()
      get().showToast('Settings saved', 'success')
    } catch { get().showToast('Failed to save settings', 'error') }
  },

  fetchJobHistory: async () => {
    try {
      const r = await fetch(`${API}/jobs`)
      const d = await r.json()
      set({ jobHistory: (d.jobs ?? []).sort((a: VideoJob, b: VideoJob) => (b.created_at || 0) - (a.created_at || 0)) })
    } catch {}
  },
  deleteJob: async (id: string) => {
    try {
      await fetch(`${API}/jobs/${id}`, { method: 'DELETE' })
      set((s) => ({ jobHistory: s.jobHistory.filter(j => j.id !== id) }))
      get().showToast('Job deleted', 'info')
    } catch { get().showToast('Failed to delete job', 'error') }
  },
  downloadAsset: async (id: string) => {
    try {
      await fetch(`${API}/assets/${id}/download`, { method: 'POST' })
      get().showToast('Asset download started', 'info')
      setTimeout(() => get().fetchAssets(), 5000)
    } catch { get().showToast('Failed to download asset', 'error') }
  },

  activeTab: 'fetch', setActiveTab: (t) => set({ activeTab: t }),
  settingsOpen: false, setSettingsOpen: (v) => set({ settingsOpen: v }),

  toast: null,
  showToast: (message, type) => {
    set({ toast: { message, type } })
    setTimeout(() => set({ toast: null }), 3500)
  },
}))
