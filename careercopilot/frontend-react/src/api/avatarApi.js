import client from './client';

export const createAvatarStream = () =>
  client.post('/api/avatar/stream/create').then(r => r.data);

export const submitSdp = (streamId, sessionId, sdp) =>
  client.post(`/api/avatar/stream/${streamId}/sdp`, { session_id: sessionId, sdp }).then(r => r.data);

export const submitIce = (streamId, sessionId, candidate) =>
  client.post(`/api/avatar/stream/${streamId}/ice`, { session_id: sessionId, candidate }).then(r => r.data);

export const triggerSpeak = (streamId, sessionId, text) =>
  client.post(`/api/avatar/stream/${streamId}/speak`, { session_id: sessionId, text }).then(r => r.data);
