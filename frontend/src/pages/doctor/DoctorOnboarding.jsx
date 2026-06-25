import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { doctorApi } from '../../api/doctorApi'
import PersonalInfoStep from './steps/PersonalInfoStep'
import ProfessionalInfoStep from './steps/ProfessionalInfoStep'
import QualificationsStep from './steps/QualificationsStep'
import SpecializationsStep from './steps/SpecializationsStep'
import PracticeInfoStep from './steps/PracticeInfoStep'
import DocumentsStep from './steps/DocumentsStep'
import './doctor-onboarding.css'

const STEPS = [
  { num: 1, label: 'Personal' },
  { num: 2, label: 'Professional' },
  { num: 3, label: 'Qualifications' },
  { num: 4, label: 'Specializations' },
  { num: 5, label: 'Practice' },
  { num: 6, label: 'Documents' },
]

export default function DoctorOnboarding() {
  const navigate = useNavigate()
  const [step, setStep] = useState(1)
  const [showGuide, setShowGuide] = useState(true)
  const [profile, setProfile] = useState(null)
  const [refData, setRefData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const loadProfile = useCallback(async (isInitial = false) => {
    try {
      const [profRes, refRes] = await Promise.all([
        doctorApi.getProfile(),
        doctorApi.getReferenceData(),
      ])
      setProfile(profRes.data)
      setRefData(refRes.data)
      if (isInitial && profRes.data.current_step) {
        setStep(profRes.data.current_step)
      }
    } catch (e) {
      console.error('Load profile error:', e)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { loadProfile(true) }, [loadProfile])

  const goStep = (n) => {
    const maxUnlockedStep = profile?.current_step || 1
    if (n > maxUnlockedStep) {
      setError(`Please complete step ${maxUnlockedStep} first before proceeding.`)
      return
    }
    setError('')
    setStep(n)
  }
  const nextStep = () => goStep(Math.min(step + 1, 6))
  const prevStep = () => goStep(Math.max(step - 1, 1))

  const handleSubmit = async () => {
    setSaving(true)
    setError('')
    try {
      await doctorApi.submitForVerification()
      navigate('/doctor/dashboard')
    } catch (e) {
      setError(e.response?.data?.detail || 'Submission failed.')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return <div className="loading-page"><div className="loading-spinner" /></div>
  }

  const renderStep = () => {
    const common = { profile, refData, setSaving, setError, onReload: loadProfile }
    switch (step) {
      case 1: return <PersonalInfoStep {...common} onNext={nextStep} />
      case 2: return <ProfessionalInfoStep {...common} onNext={nextStep} onBack={prevStep} />
      case 3: return <QualificationsStep {...common} onNext={nextStep} onBack={prevStep} />
      case 4: return <SpecializationsStep {...common} onNext={nextStep} onBack={prevStep} />
      case 5: return <PracticeInfoStep {...common} onNext={nextStep} onBack={prevStep} />
      case 6: return <DocumentsStep {...common} onBack={prevStep} onSubmit={handleSubmit} saving={saving} />
      default: return null
    }
  }

  return (
    <div className="onboarding-page">
      <div className="onboarding-container">
        <div className="onboarding-header">
          <h1>Complete Your Profile</h1>
          <p>Fill in your details to get verified and start receiving patients</p>
        </div>

        {showGuide && (
          <div className="step-card" style={{ marginBottom: 24, background: '#f0fdfa', borderColor: '#b2f5ea', padding: '20px 24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
              <h3 style={{ margin: 0, color: '#0f766e', fontSize: 16, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
                ℹ️ Onboarding & Verification Guidelines
              </h3>
              <button 
                onClick={() => setShowGuide(false)}
                style={{ background: 'none', border: 'none', color: '#0f766e', cursor: 'pointer', fontSize: 18, fontWeight: 'bold' }}
              >
                ×
              </button>
            </div>
            <p style={{ fontSize: 13, color: '#115e59', lineHeight: 1.5, marginBottom: 14 }}>
              To protect patient trust and security, PraDoc verifies all registration credentials. Follow these instructions to complete the process smoothly:
            </p>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16 }}>
              <div style={{ background: '#ffffff', padding: 12, borderRadius: 8, border: '1px solid #e2e8f0' }}>
                <strong style={{ fontSize: 13, color: '#134e4a', display: 'block', marginBottom: 4 }}>1. Public Presentation</strong>
                <span style={{ fontSize: 12, color: '#475569', lineHeight: 1.4, display: 'block' }}>Your Bio, Languages, and Specializations display on the doctor listing for patient selection.</span>
              </div>
              <div style={{ background: '#ffffff', padding: 12, borderRadius: 8, border: '1px solid #e2e8f0' }}>
                <strong style={{ fontSize: 13, color: '#134e4a', display: 'block', marginBottom: 4 }}>2. Consultations & Slots</strong>
                <span style={{ fontSize: 12, color: '#475569', lineHeight: 1.4, display: 'block' }}>Your Clinic address and availability schedule directly define your patient booking options.</span>
              </div>
              <div style={{ background: '#ffffff', padding: 12, borderRadius: 8, border: '1px solid #e2e8f0' }}>
                <strong style={{ fontSize: 13, color: '#134e4a', display: 'block', marginBottom: 4 }}>3. Automated Approval</strong>
                <span style={{ fontSize: 12, color: '#475569', lineHeight: 1.4, display: 'block' }}>Complete all steps and upload mandatory certificates to reach a score of 80+ for instant activation.</span>
              </div>
            </div>
          </div>
        )}
        {!showGuide && (
          <div style={{ textAlign: 'right', marginBottom: 16 }}>
            <button 
              onClick={() => setShowGuide(true)} 
              style={{ background: 'none', border: 'none', color: '#0f766e', fontSize: 12, fontWeight: 600, cursor: 'pointer', textDecoration: 'underline' }}
            >
              Show Onboarding Instructions
            </button>
          </div>
        )}

        <div className="step-indicator">
          {STEPS.map((s, i) => (
            <div className="step-item" key={s.num}>
              <div
                className={`step-circle ${step === s.num ? 'active' : ''} ${step > s.num ? 'completed' : ''}`}
                onClick={() => goStep(s.num)}
                title={s.label}
              >
                {step > s.num ? '✓' : s.num}
              </div>
              {i < STEPS.length - 1 && (
                <div className={`step-line ${step > s.num ? 'completed' : ''}`} />
              )}
            </div>
          ))}
        </div>

        {error && <div className="alert alert-error" style={{marginBottom: 16}}>{error}</div>}

        {renderStep()}
      </div>
    </div>
  )
}
