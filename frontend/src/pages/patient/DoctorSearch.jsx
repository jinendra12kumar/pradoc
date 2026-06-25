import { useState, useEffect, useCallback } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { patientApi } from '../../api/doctorApi'
import { DoctorCard } from './PatientHome'

const SPECIALIZATIONS = [
  'Cardiology','Dermatology','Neurology','Orthopedics','Pediatrics',
  'Psychiatry','Gynecology','ENT','General Physician','Internal Medicine',
  'Diabetology','Ophthalmology','Urology','Gastroenterology','Pulmonology',
  'Oncology','Nephrology','Endocrinology','Rheumatology',
]

const EXP_OPTIONS = [
  { label: 'Any', min: null, max: null },
  { label: '0–5 yrs', min: 0, max: 5 },
  { label: '5–10 yrs', min: 5, max: 10 },
  { label: '10–20 yrs', min: 10, max: 20 },
  { label: '20+ yrs', min: 20, max: null },
]

const FEE_OPTIONS = [
  { label: 'Any', min: null, max: null },
  { label: '₹0–300', min: 0, max: 300 },
  { label: '₹300–500', min: 300, max: 500 },
  { label: '₹500–1000', min: 500, max: 1000 },
  { label: '₹1000+', min: 1000, max: null },
]

const DAYS = ['MON','TUE','WED','THU','FRI','SAT','SUN']

export default function DoctorSearch() {
  const [searchParams, setSearchParams] = useSearchParams()
  const navigate = useNavigate()

  // Filters state
  const [filters, setFilters] = useState({
    q: searchParams.get('q') || '',
    specialization: searchParams.get('specialization') || '',
    expIndex: 0,
    feeIndex: 0,
    gender: '',
    online_consultation: null,
    availability_day: '',
    sort_by: 'experience',
    page: 1,
  })

  const [results, setResults] = useState({ doctors: [], total: 0, total_pages: 1 })
  const [loading, setLoading] = useState(true)

  const fetchDoctors = useCallback(async () => {
    setLoading(true)
    const exp = EXP_OPTIONS[filters.expIndex]
    const fee = FEE_OPTIONS[filters.feeIndex]

    const params = {}
    if (filters.q) params.q = filters.q
    if (filters.specialization) params.specialization = filters.specialization
    if (exp.min != null) params.min_experience = exp.min
    if (exp.max != null) params.max_experience = exp.max
    if (fee.min != null) params.min_fee = fee.min
    if (fee.max != null) params.max_fee = fee.max
    if (filters.gender) params.gender = filters.gender
    if (filters.online_consultation != null) params.online_consultation = filters.online_consultation
    if (filters.availability_day) params.availability_day = filters.availability_day
    params.sort_by = filters.sort_by
    params.page = filters.page
    params.page_size = 12

    try {
      const res = await patientApi.searchDoctors(params)
      setResults(res.data)
    } catch (err) {
      console.error('Search failed:', err)
    } finally {
      setLoading(false)
    }
  }, [filters])

  useEffect(() => { fetchDoctors() }, [fetchDoctors])

  // Sync URL params on initial load
  useEffect(() => {
    const q = searchParams.get('q')
    const spec = searchParams.get('specialization')
    if (q || spec) {
      setFilters(f => ({
        ...f,
        q: q || f.q,
        specialization: spec || f.specialization,
      }))
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const updateFilter = (key, value) => {
    setFilters(f => ({ ...f, [key]: value, page: 1 }))
  }

  const clearFilters = () => {
    setFilters({
      q: '', specialization: '', expIndex: 0, feeIndex: 0,
      gender: '', online_consultation: null, availability_day: '',
      sort_by: 'experience', page: 1,
    })
  }

  return (
    <div className="search-layout">
      {/* ── Sidebar Filters ──────────────────────────────────────── */}
      <aside className="search-sidebar">
        <div className="sidebar-title">
          Filters
          <button className="clear-filters-btn" onClick={clearFilters}>
            Clear All
          </button>
        </div>

        {/* Specialization */}
        <div className="filter-group">
          <label className="filter-label">Specialization</label>
          <select
            className="filter-select"
            value={filters.specialization}
            onChange={(e) => updateFilter('specialization', e.target.value)}
          >
            <option value="">All Specializations</option>
            {SPECIALIZATIONS.map(s => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>

        {/* Experience */}
        <div className="filter-group">
          <label className="filter-label">Experience</label>
          <div className="filter-chips">
            {EXP_OPTIONS.map((opt, i) => (
              <button
                key={i}
                className={`filter-chip ${filters.expIndex === i ? 'active' : ''}`}
                onClick={() => updateFilter('expIndex', i)}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        {/* Fee Range */}
        <div className="filter-group">
          <label className="filter-label">Consultation Fee</label>
          <div className="filter-chips">
            {FEE_OPTIONS.map((opt, i) => (
              <button
                key={i}
                className={`filter-chip ${filters.feeIndex === i ? 'active' : ''}`}
                onClick={() => updateFilter('feeIndex', i)}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        {/* Gender */}
        <div className="filter-group">
          <label className="filter-label">Gender</label>
          <div className="filter-chips">
            {['', 'male', 'female'].map(g => (
              <button
                key={g}
                className={`filter-chip ${filters.gender === g ? 'active' : ''}`}
                onClick={() => updateFilter('gender', g)}
              >
                {g === '' ? 'Any' : g === 'male' ? 'Male' : 'Female'}
              </button>
            ))}
          </div>
        </div>

        {/* Online Consultation */}
        <div className="filter-group">
          <label className="filter-label">Consultation Mode</label>
          <div className="filter-chips">
            <button
              className={`filter-chip ${filters.online_consultation === null ? 'active' : ''}`}
              onClick={() => updateFilter('online_consultation', null)}
            >Any</button>
            <button
              className={`filter-chip ${filters.online_consultation === true ? 'active' : ''}`}
              onClick={() => updateFilter('online_consultation', true)}
            >Online</button>
            <button
              className={`filter-chip ${filters.online_consultation === false ? 'active' : ''}`}
              onClick={() => updateFilter('online_consultation', false)}
            >In-Clinic</button>
          </div>
        </div>

        {/* Availability */}
        <div className="filter-group">
          <label className="filter-label">Available On</label>
          <div className="filter-chips">
            <button
              className={`filter-chip ${filters.availability_day === '' ? 'active' : ''}`}
              onClick={() => updateFilter('availability_day', '')}
            >Any Day</button>
            {DAYS.map(d => (
              <button
                key={d}
                className={`filter-chip ${filters.availability_day === d ? 'active' : ''}`}
                onClick={() => updateFilter('availability_day', d)}
              >
                {d}
              </button>
            ))}
          </div>
        </div>
      </aside>

      {/* ── Results ──────────────────────────────────────────────── */}
      <div className="search-results">
        <div className="search-results-header">
          <span className="results-count">
            <strong>{results.total}</strong> doctor{results.total !== 1 ? 's' : ''} found
            {filters.q && <> for "<strong>{filters.q}</strong>"</>}
            {filters.specialization && <> in <strong>{filters.specialization}</strong></>}
          </span>
          <select
            className="sort-select"
            value={filters.sort_by}
            onChange={(e) => updateFilter('sort_by', e.target.value)}
          >
            <option value="experience">Sort by Experience</option>
            <option value="fee">Sort by Fee (Low to High)</option>
            <option value="name">Sort by Name</option>
          </select>
        </div>

        {loading ? (
          <div className="loading-state">
            <div className="loading-spinner" />
            <p className="loading-text">Searching doctors...</p>
          </div>
        ) : results.doctors.length === 0 ? (
          <div className="no-results">
            <div className="no-results-icon">🔍</div>
            <h3 className="no-results-title">No Doctors Found</h3>
            <p className="no-results-text">
              Try adjusting your filters or search terms
            </p>
          </div>
        ) : (
          <>
            <div className="doctors-grid">
              {results.doctors.map(doc => (
                <DoctorCard key={doc.id} doctor={doc} />
              ))}
            </div>

            {/* Pagination */}
            {results.total_pages > 1 && (
              <div className="pagination">
                <button
                  className="page-btn"
                  disabled={filters.page <= 1}
                  onClick={() => setFilters(f => ({ ...f, page: f.page - 1 }))}
                >
                  ← Prev
                </button>
                {Array.from({ length: Math.min(results.total_pages, 7) }, (_, i) => {
                  let pageNum
                  if (results.total_pages <= 7) {
                    pageNum = i + 1
                  } else if (filters.page <= 4) {
                    pageNum = i + 1
                  } else if (filters.page >= results.total_pages - 3) {
                    pageNum = results.total_pages - 6 + i
                  } else {
                    pageNum = filters.page - 3 + i
                  }
                  return (
                    <button
                      key={pageNum}
                      className={`page-btn ${filters.page === pageNum ? 'active' : ''}`}
                      onClick={() => setFilters(f => ({ ...f, page: pageNum }))}
                    >
                      {pageNum}
                    </button>
                  )
                })}
                <button
                  className="page-btn"
                  disabled={filters.page >= results.total_pages}
                  onClick={() => setFilters(f => ({ ...f, page: f.page + 1 }))}
                >
                  Next →
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
