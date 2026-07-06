// src/pages/consultation/VideoConsultation.jsx
import { useState, useEffect, useRef, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { createMeeting, getJoinInfo, endMeeting } from '../../api/video'
import '../../consultation.css'

const JITSI_DOMAIN = 'meet.jit.si'

function loadJitsiScript() {
  return new Promise((resolve, reject) => {
    if (window.JitsiMeetExternalAPI) return resolve()
    const script = document.createElement('script')
    script.src = `https://${JITSI_DOMAIN}/external_api.js`
    script.async = true
    script.onload = resolve
    script.onerror = () => reject(new Error('Failed to load Jitsi SDK'))
    document.head.appendChild(script)
  })
}

export default function VideoConsultation() {
  const { appointmentId } = useParams()
  const navigate = useNavigate()
  const jitsiDivRef = useRef(null)
  const apiRef = useRef(null)

  const [joinInfo, setJoinInfo] = useState(null)
  const [phase, setPhase] = useState('loading') // loading | premeet | waiting | in-meeting | ended | error
  const [errorMsg, setErrorMsg] = useState('')
  const [ending, setEnding] = useState(false)
  const user = JSON.parse(localStorage.getItem('user') || '{}')
  const isDoctor = user.role === 'doctor'

  // Load join info
  const loadInfo = useCallback(async () => {
    try {
      const info = await getJoinInfo(appointmentId)
      if (info.detail) throw new Error(info.detail)
      setJoinInfo(info)
      if (isDoctor) {
        setPhase(info.meeting_started ? 'in-meeting' : 'premeet')
      } else {
        setPhase(info.meeting_started ? 'in-meeting' : 'waiting')
      }
    } catch (e) {
      setErrorMsg(e.message || 'Could not load appointment info.')
      setPhase('error')
    }
  }, [appointmentId, isDoctor])

  useEffect(() => { loadInfo() }, [loadInfo])

  // Patient polls every 5s while in waiting room
  useEffect(() => {
    if (phase !== 'waiting') return
    const timer = setInterval(async () => {
      try {
        const info = await getJoinInfo(appointmentId)
        if (info.meeting_started) { setJoinInfo(info); setPhase('in-meeting') }
      } catch (_) {}
    }, 5000)
    return () => clearInterval(timer)
  }, [phase, appointmentId])

  // Initialize Jitsi once phase = in-meeting
  useEffect(() => {
    if (phase !== 'in-meeting' || !joinInfo) return
    let mounted = true

    loadJitsiScript().then(() => {
      if (!mounted || !jitsiDivRef.current) return
      if (apiRef.current) { apiRef.current.dispose(); apiRef.current = null }

      apiRef.current = new window.JitsiMeetExternalAPI(JITSI_DOMAIN, {
        roomName: joinInfo.room_name,
        parentNode: jitsiDivRef.current,
        width: '100%',
        height: '100%',
        userInfo: { displayName: joinInfo.display_name },
        configOverwrite: {
          startWithAudioMuted: false,
          startWithVideoMuted: false,
          enableWelcomePage: false,
          prejoinPageEnabled: false,
          disableDeepLinking: true,
        },
        interfaceConfigOverwrite: {
          TOOLBAR_BUTTONS: [
            'microphone', 'camera', 'desktop', 'chat',
            'raisehand', 'tileview', 'hangup',
          ],
          SHOW_JITSI_WATERMARK: false,
          SHOW_BRAND_WATERMARK: false,
          SHOW_CHROME_EXTENSION_BANNER: false,
          MOBILE_APP_PROMO: false,
          HIDE_INVITE_MORE_HEADER: true,
        },
      })

      apiRef.current.addEventListener('videoConferenceLeft', () => {
        if (isDoctor) handleEndMeeting()
        else setPhase('ended')
      })
    }).catch(e => { setErrorMsg(e.message); setPhase('error') })

    return () => {
      mounted = false
      if (apiRef.current) { apiRef.current.dispose(); apiRef.current = null }
    }
  }, [phase, joinInfo])

  // Doctor starts the meeting
  const handleStartMeeting = async () => {
    setPhase('loading')
    try {
      const data = await createMeeting(appointmentId)
      if (data.detail) throw new Error(data.detail)
      setJoinInfo(prev => ({ ...prev, ...data, meeting_started: true }))
      setPhase('in-meeting')
    } catch (e) {
      setErrorMsg(e.message || 'Could not start meeting.')
      setPhase('error')
    }
  }

  // Doctor ends the meeting
  const handleEndMeeting = async () => {
    if (ending) return
    setEnding(true)
    if (apiRef.current) { apiRef.current.dispose(); apiRef.current = null }
    try { await endMeeting(appointmentId) } catch (_) {}
    setPhase('ended')
    setEnding(false)
  }

  const dashPath = isDoctor ? '/doctor/dashboard' : '/patient/my-appointments'

  return (
    <div className="consultation-page">
      {/* Top Bar */}
      <div className="consult-topbar">
        <div className="brand">🩺 PraDoc Health</div>
        <div className="appt-info">
          {joinInfo && (
            <div className="appt-badge">
              📅 {joinInfo.appointment_date} · {joinInfo.slot_start_time?.slice(0,5)}
            </div>
          )}
          {phase === 'in-meeting' && (
            <div className="live-badge"><span className="live-dot" />LIVE</div>
          )}
          {isDoctor && phase === 'in-meeting' && (
            <button className="btn-end-meeting" onClick={handleEndMeeting} disabled={ending}>
              📴 {ending ? 'Ending…' : 'End Meeting'}
            </button>
          )}
          <button className="btn-back-consult" onClick={() => navigate(dashPath)}>
            ← Dashboard
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="consult-main">
        {phase === 'loading' && (
          <div className="consult-loading">
            <div className="spin-ring" />
            <span>Setting up your consultation…</span>
          </div>
        )}

        {phase === 'error' && (
          <div className="consult-error">
            <div className="err-icon">⚠️</div>
            <div className="err-title">Unable to Join</div>
            <div className="err-msg">{errorMsg}</div>
            <button className="btn-back-consult" onClick={() => navigate(dashPath)}>← Go Back</button>
          </div>
        )}

        {/* Doctor — Pre-meeting panel */}
        {phase === 'premeet' && joinInfo && (
          <div className="premeet-panel">
            <div className="premeet-card">
              <div className="premeet-icon">🎥</div>
              <div className="premeet-title">Start Video Consultation</div>
              <div className="premeet-sub">
                Your patient is waiting. Click below to open the meeting room and begin the session.
              </div>
              <div className="premeet-info-grid">
                <div className="premeet-info-item">
                  <div className="premeet-info-label">Date</div>
                  <div className="premeet-info-value">{joinInfo.appointment_date}</div>
                </div>
                <div className="premeet-info-item">
                  <div className="premeet-info-label">Time</div>
                  <div className="premeet-info-value">{joinInfo.slot_start_time?.slice(0,5)}</div>
                </div>
              </div>
              <button className="btn-start-meeting" onClick={handleStartMeeting}>
                🚀 Create &amp; Start Meeting
              </button>
            </div>
          </div>
        )}

        {/* Patient — Waiting Room */}
        {phase === 'waiting' && joinInfo && (
          <div className="waiting-room">
            <div className="waiting-card">
              <div className="waiting-pulse-ring">⏳</div>
              <div className="waiting-title">Waiting for Doctor</div>
              <div className="waiting-sub">
                The doctor hasn't started the session yet. You'll be automatically connected once the meeting begins.
              </div>
              <div className="waiting-dots">
                <span /><span /><span />
              </div>
              <div className="waiting-appt-detail">
                <span>📅 {joinInfo.appointment_date}</span>
                <span>🕐 {joinInfo.slot_start_time?.slice(0,5)}</span>
                <span>🔄 Checking every 5 seconds…</span>
              </div>
            </div>
          </div>
        )}

        {/* In Meeting — Jitsi Embed */}
        {phase === 'in-meeting' && (
          <div className="jitsi-container" ref={jitsiDivRef} />
        )}

        {/* Ended */}
        {phase === 'ended' && (
          <div className="meeting-ended">
            <div className="ended-card">
              <div className="ended-icon">✅</div>
              <div className="ended-title">Consultation Complete</div>
              <div className="ended-sub">
                {isDoctor
                  ? 'The meeting has ended and the appointment has been marked as completed.'
                  : 'Your video consultation has ended. Thank you for using PraDoc.'}
              </div>
              <button className="btn-go-dash" onClick={() => navigate(dashPath)}>
                🏠 Go to Dashboard
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
