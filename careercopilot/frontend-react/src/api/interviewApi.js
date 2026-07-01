import client from './client';

export const getSessionQuestions = (sessionId) =>
  client.get(`/api/session/${sessionId}/questions`).then(r => r.data);

export const submitAudioAnswer = (sessionId, questionId, audioBlob) => {
  const form = new FormData();
  form.append('question_id', questionId);
  form.append('audio', audioBlob, 'answer.wav');
  return client.post(`/api/interview/${sessionId}/answer-audio`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 90000,
  }).then(r => r.data);
};

export const submitTextAnswer = (sessionId, questionId, answerText) => {
  const form = new FormData();
  form.append('question_id', questionId);
  form.append('answer_text', answerText);
  return client.post(`/api/interview/${sessionId}/answer-text`, form).then(r => r.data);
};
