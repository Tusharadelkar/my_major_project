import client from './client';
export const createOrGetStudent = (name, email) =>
  client.post('/api/student', { name, email }).then(r => r.data);
