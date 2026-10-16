export async function submitRegistration(payload, fetchImpl = fetch) {
  let response;
  try {
    response = await fetchImpl('http://localhost:8000/api/dang-ky', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(15000),
    });
  } catch {
    return {state: 'error', message: 'Không kết nối được máy chủ. Kiểm tra backend ở cổng 8000.'};
  }
  const data = await response.json().catch(() => null);
  if (response.status === 201 && data?.ok === true) {
    return {state: 'success', message: 'Đăng ký thành công.'};
  }
  if (response.status === 409 && data?.detail === 'DA_DANG_KY') {
    return {state: 'duplicate', message: 'Bạn đã đăng ký phiên này.'};
  }
  if (response.status === 422) {
    return {state: 'error', message: 'Dữ liệu chưa hợp lệ. Hãy kiểm tra mã sinh viên và mã phiên.'};
  }
  if (response.status >= 500) {
    return {state: 'error', message: 'Máy chủ gặp lỗi. Vui lòng thử lại sau.'};
  }
  return {state: 'error', message: 'Phản hồi từ máy chủ không hợp lệ. Vui lòng thử lại.'};
}
