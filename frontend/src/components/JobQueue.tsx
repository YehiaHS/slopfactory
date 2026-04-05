import { useStore } from '../store'
import { ListVideo, CheckCircle2, XCircle, Loader2, Download, Trash2, Clock, RotateCcw, ExternalLink } from 'lucide-react'

export function JobQueue() {
  const { currentJob, jobHistory, fetchJobHistory, deleteJob } = useStore()

  const allJobs = currentJob
    ? [currentJob, ...jobHistory.filter(j => j.id !== currentJob.id)]
    : jobHistory

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <div className="px-5 py-3.5 border-b flex items-center justify-between" style={{ borderColor: 'var(--border)' }}>
        <div>
          <h2 className="text-base font-bold">Job Queue</h2>
          <p className="text-xs mt-0.5" style={{ color: 'var(--text-secondary)' }}>Monitor generation progress and download videos</p>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="text-[11px]" style={{ color: 'var(--text-muted)' }}>{allJobs.length} job{allJobs.length !== 1 ? 's' : ''}</span>
          <button className="btn-ghost text-xs" onClick={fetchJobHistory} style={{ color: 'var(--text-secondary)' }}>
            <Clock size={13} /> Refresh
          </button>
        </div>
      </div>
      <div className="flex-1 overflow-y-auto px-5 py-4">
        {allJobs.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full" style={{ color: 'var(--text-muted)' }}>
            <ListVideo size={36} className="mb-3 opacity-15" />
            <p className="text-sm font-medium mb-1">No active jobs</p>
            <p className="text-xs">Generate a video to see it here</p>
          </div>
        ) : (
          <div className="space-y-2.5">
            {allJobs.map(j => <JobCard key={j.id} job={j} onDelete={() => deleteJob(j.id)} />)}
          </div>
        )}
      </div>
    </div>
  )
}

function JobCard({ job, onDelete }: { job: { id: string; status: string; progress: number; stage: string; error: string | null; output_path: string | null; request?: Record<string, any>; created_at?: number }; onDelete: () => void }) {
  const icon = job.status === 'completed'
    ? <CheckCircle2 size={15} style={{ color: 'var(--success)' }} />
    : job.status === 'failed'
    ? <XCircle size={15} style={{ color: 'var(--danger)' }} />
    : <Loader2 size={15} className="animate-spin" style={{ color: 'var(--primary)' }} />

  const label = job.status === 'completed' ? 'Video Generated' : job.status === 'failed' ? 'Generation Failed' : 'Generating Video'
  const time = job.created_at ? new Date(job.created_at * 1000).toLocaleString() : ''
  const subtitle = job.request?.post_title || job.stage

  return (
    <div className="rounded-lg border p-3.5" style={{ background: 'var(--surface-elevated)', borderColor: 'var(--border)' }}>
      <div className="flex items-start gap-3 mb-2.5">
        <div className="mt-0.5">{icon}</div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between">
            <p className="text-[0.85rem] font-semibold">{label}</p>
            <div className="flex items-center gap-1.5">
              {job.status === 'completed' && (
                <button className="btn-secondary text-xs px-2 py-1" onClick={() => window.open(`/api/jobs/${job.id}/download`, '_blank')}>
                  <Download size={12} /> Download
                </button>
              )}
              <button className="btn-ghost p-1" onClick={onDelete} title="Delete job">
                <Trash2 size={13} />
              </button>
            </div>
          </div>
          {subtitle && <p className="text-[11px] line-clamp-1" style={{ color: 'var(--text-secondary)' }}>{subtitle}</p>}
          {time && <p className="text-[10px] font-mono" style={{ color: 'var(--text-muted)' }}>{time}</p>}
        </div>
      </div>
      {(job.status === 'processing' || job.status === 'queued') && (
        <>
          <div className="flex items-center justify-between mb-1">
            <span className="text-[11px]" style={{ color: 'var(--text-secondary)' }}>{job.stage}</span>
            <span className="text-[11px] font-mono font-semibold" style={{ color: 'var(--primary)' }}>{job.progress}%</span>
          </div>
          <div className="progress-bar-track">
            <div className="progress-bar-fill" style={{ width: `${job.progress}%` }} />
          </div>
        </>
      )}
      {job.status === 'failed' && job.error && (
        <div className="mt-2 p-2 rounded" style={{ background: 'var(--danger-muted)', border: '1px solid var(--danger)' }}>
          <p className="text-xs" style={{ color: 'var(--danger)' }}>{job.error}</p>
        </div>
      )}
    </div>
  )
}
