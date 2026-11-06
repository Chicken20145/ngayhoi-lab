export async function submitRegistration(payload, fetchImpl = fetch, onFull = null) {
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
  if (response.status === 409 && data?.detail === 'HET_CHO') {
    onFull?.(payload?.ma_phien);
    return {state: 'error', message: 'Phiên này đã đủ 30 chỗ. Bạn hãy chọn phiên khác.'};
  }
  if (response.status === 422) {
    return {state: 'error', message: 'Dữ liệu chưa hợp lệ. Hãy kiểm tra mã sinh viên và mã phiên.'};
  }
  if (response.status >= 500) {
    return {state: 'error', message: 'Máy chủ gặp lỗi. Vui lòng thử lại sau.'};
  }
  return {state: 'error', message: 'Phản hồi từ máy chủ không hợp lệ. Vui lòng thử lại.'};
}

export function normalizeStudent(id) {
  return typeof id === 'string' ? id.trim() : '';
}

export function createSessionStore(initialFull = []) {
  const registered = new Map();
  const full = new Set(initialFull);

  return {
    normalizeStudent,
    isRegistered(student, session) {
      const s = normalizeStudent(student);
      return Boolean(s && session && registered.get(s)?.has(session));
    },
    isFull(session) {
      return Boolean(session && full.has(session));
    },
    markRegistered(student, session) {
      const s = normalizeStudent(student);
      if (!s || !session) return;
      if (!registered.has(s)) registered.set(s, new Set());
      registered.get(s).add(session);
    },
    markFull(session) {
      if (session) full.add(session);
    },
    recordOutcome(student, session, result) {
      if (!result) return;
      if (result.state === 'success' || result.state === 'duplicate') {
        this.markRegistered(student, session);
      }
    },
    getSessionState(student, session) {
      if (!session) return {disabled: false, text: 'Đăng ký tham gia', status: 'idle'};
      if (this.isRegistered(student, session)) return {disabled: true, text: 'Đã đăng ký', status: 'registered'};
      if (this.isFull(session)) return {disabled: true, text: 'Hết chỗ', status: 'full'};
      return {disabled: false, text: 'Đăng ký tham gia', status: 'available'};
    },
  };
}
