// src/api/video.js — Video Consultation API helpers

const BASE = '/api/v1/video'

const authHeader = () => ({
  Authorization: `Bearer ${localStorage.getItem('access_token')}`,
  'Content-Type': 'application/json',
})

/** Doctor: create/start a Jitsi meeting room for an appointment */
export const createMeeting = (appointmentId) =>
  fetch(`${BASE}/create-meeting/${appointmentId}`, {
    method: 'POST',
    headers: authHeader(),
  }).then(r => r.json())

/** Doctor or Patient: get room name + join info */
export const getJoinInfo = (appointmentId) =>
  fetch(`${BASE}/join/${appointmentId}`, {
    headers: authHeader(),
  }).then(r => r.json())

/** Doctor: end the meeting and mark appointment completed */
export const endMeeting = (appointmentId) =>
  fetch(`${BASE}/end-meeting/${appointmentId}`, {
    method: 'POST',
    headers: authHeader(),
  }).then(r => r.json())
