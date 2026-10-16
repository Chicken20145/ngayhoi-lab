import {test} from 'node:test';
import assert from 'node:assert/strict';
import {submitRegistration} from '../src/api.js';

const payload = {ma_sv:'SV_TEST_001',ma_phien:'P01'};

test('201 maps to success and request sends exact field names', async () => {
  const result = await submitRegistration(payload, async (url, options) => {
    assert.equal(url, 'http://localhost:8000/api/dang-ky');
    assert.equal(options.method, 'POST');
    assert.equal(options.headers['Content-Type'], 'application/json');
    assert.deepEqual(JSON.parse(options.body), {ma_sv:'SV_TEST_001',ma_phien:'P01'});
    return new Response('{"ok":true}', {status:201});
  });
  assert.deepEqual(result, {state:'success',message:'Đăng ký thành công.'});
});
test('409 DA_DANG_KY maps to duplicate', async () => {
  assert.deepEqual(await submitRegistration(payload, async () =>
    new Response('{"detail":"DA_DANG_KY"}', {status:409})),
    {state:'duplicate',message:'Bạn đã đăng ký phiên này.'});
});
test('422 maps to validation error not duplicate', async () => {
  const r = await submitRegistration(payload, async () => new Response('{"detail":[]}', {status:422}));
  assert.equal(r.state, 'error');
  assert.equal(r.message, 'Dữ liệu chưa hợp lệ. Hãy kiểm tra mã sinh viên và mã phiên.');
});
test('500 maps to server error not duplicate', async () => {
  const r = await submitRegistration(payload, async () => new Response('Internal Server Error', {status:500}));
  assert.deepEqual(r, {state:'error',message:'Máy chủ gặp lỗi. Vui lòng thử lại sau.'});
});
test('network failure maps to connection error', async () => {
  const r = await submitRegistration(payload, async () => {throw new TypeError('Failed to fetch');});
  assert.deepEqual(r, {state:'error',message:'Không kết nối được máy chủ. Kiểm tra backend ở cổng 8000.'});
});
test('malformed success payload cannot be reported as success', async () => {
  const r = await submitRegistration(payload, async () => new Response('{"ok":false}', {status:201}));
  assert.equal(r.state, 'error');
});
