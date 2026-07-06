// src/pages/admin/ManageArticles.jsx
import { useState, useEffect } from 'react'
import { fetchAdminArticles, createArticle, updateArticle, deleteArticle, fetchArticleById } from '../../api/admin'

const CATEGORIES = ['General Health', 'Cardiology', 'Dermatology', 'Neurology', 'Pediatrics',
  'Orthopedics', 'Mental Health', 'Nutrition', 'Women\'s Health', 'Other']

const EMPTY_FORM = {
  title: '', excerpt: '', content: '', category: '', author_name: 'PraDoc Team',
  cover_image_url: '', is_published: false,
}

export default function ManageArticles() {
  const [data, setData]         = useState(null)
  const [loading, setLoading]   = useState(true)
  const [page, setPage]         = useState(1)
  const [modal, setModal]       = useState(null) // null | 'create' | 'edit'
  const [form, setForm]         = useState(EMPTY_FORM)
  const [editId, setEditId]     = useState(null)
  const [saving, setSaving]     = useState(false)
  const [busy, setBusy]         = useState(null)

  const load = (p = page) => {
    setLoading(true)
    fetchAdminArticles(p).then(setData).finally(() => setLoading(false))
  }

  useEffect(() => { load(page) }, [page])

  const openCreate = () => { setForm(EMPTY_FORM); setEditId(null); setModal('create') }

  const openEdit = async (id) => {
    const article = await fetchArticleById(id)
    setForm({
      title: article.title || '', excerpt: article.excerpt || '',
      content: article.content || '', category: article.category || '',
      author_name: article.author_name || 'PraDoc Team',
      cover_image_url: article.cover_image_url || '',
      is_published: article.is_published || false,
    })
    setEditId(id); setModal('edit')
  }

  const handleSave = async () => {
    if (!form.title.trim() || !form.content.trim()) return alert('Title and Content are required.')
    setSaving(true)
    if (modal === 'create') await createArticle(form)
    else await updateArticle(editId, form)
    setSaving(false); setModal(null); load()
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this article permanently?')) return
    setBusy(id); await deleteArticle(id); setBusy(null); load()
  }

  const totalPages = data ? Math.ceil(data.total / 20) : 1
  const f = (k) => e => setForm(p => ({ ...p, [k]: e.target.value }))

  return (
    <>
      <div className="adm-table-wrap">
        <div className="adm-table-header">
          <div className="adm-section-title" style={{ margin: 0 }}>📝 Health Articles</div>
          <button className="btn-adm-primary" onClick={openCreate}>＋ New Article</button>
        </div>

        {loading ? <div className="adm-loading">Loading…</div>
        : !data?.items?.length ? (
          <div className="adm-empty">
            <div className="icon">📝</div>
            <div className="msg">No articles yet. Create your first one!</div>
          </div>
        ) : (
          <table className="adm-table">
            <thead>
              <tr><th>Title</th><th>Category</th><th>Author</th><th>Status</th><th>Date</th><th>Actions</th></tr>
            </thead>
            <tbody>
              {data.items.map(a => (
                <tr key={a.id}>
                  <td>
                    <div style={{ fontWeight: 600, color: '#e2e8f0', maxWidth: 260 }}>{a.title}</div>
                    {a.excerpt && <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: 2 }}>{a.excerpt.slice(0,80)}…</div>}
                  </td>
                  <td><span className="adm-badge adm-badge-purple">{a.category || 'General'}</span></td>
                  <td style={{ color: '#94a3b8' }}>{a.author_name}</td>
                  <td>
                    <span className={`adm-badge ${a.is_published ? 'adm-badge-success' : 'adm-badge-muted'}`}>
                      {a.is_published ? '🟢 Published' : '⚫ Draft'}
                    </span>
                  </td>
                  <td style={{ color: '#64748b', fontSize: '0.78rem' }}>
                    {a.created_at ? new Date(a.created_at).toLocaleDateString('en-IN') : '—'}
                  </td>
                  <td>
                    <div className="adm-action-group">
                      <button className="btn-adm-ghost" onClick={() => openEdit(a.id)}>✏️ Edit</button>
                      <button className="btn-adm-danger" disabled={busy===a.id} onClick={() => handleDelete(a.id)}>🗑️ Delete</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {totalPages > 1 && (
          <div className="adm-pagination">
            <button className="btn-adm-ghost" onClick={() => setPage(p => Math.max(1,p-1))} disabled={page===1}>← Prev</button>
            <span>Page {page} of {totalPages}</span>
            <button className="btn-adm-ghost" onClick={() => setPage(p => Math.min(totalPages,p+1))} disabled={page===totalPages}>Next →</button>
          </div>
        )}
      </div>

      {/* Create / Edit Modal */}
      {modal && (
        <div className="adm-modal-overlay" onClick={() => setModal(null)}>
          <div className="adm-modal" onClick={e => e.stopPropagation()}>
            <h2>{modal === 'create' ? '✏️ New Article' : '✏️ Edit Article'}</h2>

            <div className="adm-form-group">
              <label>Title *</label>
              <input placeholder="Article title…" value={form.title} onChange={f('title')} />
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
              <div className="adm-form-group">
                <label>Category</label>
                <select value={form.category} onChange={f('category')}>
                  <option value="">Select…</option>
                  {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>
              <div className="adm-form-group">
                <label>Author Name</label>
                <input value={form.author_name} onChange={f('author_name')} />
              </div>
            </div>
            <div className="adm-form-group">
              <label>Cover Image URL</label>
              <input placeholder="https://…" value={form.cover_image_url} onChange={f('cover_image_url')} />
            </div>
            <div className="adm-form-group">
              <label>Excerpt (short summary)</label>
              <input placeholder="Short description shown in article cards…" value={form.excerpt} onChange={f('excerpt')} />
            </div>
            <div className="adm-form-group">
              <label>Content *</label>
              <textarea placeholder="Full article content…" rows={8} value={form.content} onChange={f('content')} />
            </div>
            <div className="adm-toggle-row">
              <span className="adm-toggle-label">Publish immediately</span>
              <button
                className={`adm-toggle ${form.is_published ? 'on' : 'off'}`}
                onClick={() => setForm(p => ({ ...p, is_published: !p.is_published }))}
              />
            </div>

            <div className="adm-modal-actions">
              <button className="btn-adm-ghost" onClick={() => setModal(null)}>Cancel</button>
              <button className="btn-adm-primary" disabled={saving} onClick={handleSave}>
                {saving ? 'Saving…' : modal === 'create' ? '＋ Create Article' : '💾 Save Changes'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
