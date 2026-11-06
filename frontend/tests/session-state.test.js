import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createSessionStore, normalizeStudent, submitRegistration} from '../src/api.js';

test('normalizeStudent trims whitespace and handles empty', () => {
  assert.equal(normalizeStudent('  SV001  '), 'SV001');
  assert.equal(normalizeStudent(''), '');
  assert.equal(normalizeStudent(null), '');
});

test('state differs per student and per session', () => {
  const store = createSessionStore();
  store.recordOutcome('SV001', 'P01', {state: 'success'});
  assert.equal(store.isRegistered('SV001', 'P01'), true);
  assert.equal(store.isRegistered('  SV001  ', 'P01'), true);
  assert.equal(store.isRegistered('SV002', 'P01'), false);
  assert.equal(store.isRegistered('SV001', 'P02'), false);
});

test('success and duplicate disable submission with Đã đăng ký', () => {
  const store = createSessionStore();
  store.recordOutcome('SV001', 'P01', {state: 'success'});
  store.recordOutcome('SV002', 'P02', {state: 'duplicate'});
  const s1 = store.getSessionState('SV001', 'P01');
  assert.equal(s1.disabled, true);
  assert.equal(s1.text, 'Đã đăng ký');
  const s2 = store.getSessionState('SV002', 'P02');
  assert.equal(s2.disabled, true);
  assert.equal(s2.text, 'Đã đăng ký');
});

test('full session disables submission with Hết chỗ across all students', () => {
  const store = createSessionStore();
  store.markFull('P03');
  assert.equal(store.isFull('P03'), true);
  const forSv1 = store.getSessionState('SV001', 'P03');
  assert.equal(forSv1.disabled, true);
  assert.equal(forSv1.text, 'Hết chỗ');
  const forSv2 = store.getSessionState('SV002', 'P03');
  assert.equal(forSv2.disabled, true);
  assert.equal(forSv2.text, 'Hết chỗ');
});

test('unknown and error responses remain retryable', () => {
  const store = createSessionStore();
  store.recordOutcome('SV001', 'P04', {state: 'error', message: 'Lỗi'});
  assert.equal(store.isRegistered('SV001', 'P04'), false);
  assert.equal(store.isFull('P04'), false);
  const s = store.getSessionState('SV001', 'P04');
  assert.equal(s.disabled, false);
  assert.equal(s.text, 'Đăng ký tham gia');
});

test('full outcome reaches store via callback even if message text changes', async () => {
  const store = createSessionStore();
  let fullCalled = false;
  const customFetch = async () => new Response('{"detail":"HET_CHO"}', {status: 409});
  await submitRegistration({ma_sv: 'SV001', ma_phien: 'P03'}, customFetch, (session) => {
    fullCalled = true;
    store.markFull(session);
  });
  assert.equal(fullCalled, true);
  assert.equal(store.isFull('P03'), true);
  const s = store.getSessionState('SV001', 'P03');
  assert.equal(s.disabled, true);
  assert.equal(s.text, 'Hết chỗ');
});
