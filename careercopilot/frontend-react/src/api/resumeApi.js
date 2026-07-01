import client from './client';

export const uploadResume = (file, jobDescription, studentId) => {
  const form = new FormData();
  form.append('resume', file);
  form.append('job_description', jobDescription);
  if (studentId) form.append('student_id', studentId);
  return client.post('/api/resume/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 90000,
  }).then(r => r.data);
};
