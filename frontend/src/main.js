import {createSessionStore, submitRegistration} from './api.js';

const form = document.getElementById('registration-form');
const input = document.getElementById('ma_sv');
const select = document.getElementById('ma_phien');
const button = document.getElementById('submit-button');
const status = document.getElementById('status');
const store = createSessionStore();
const baseLabels = new Map([...select.options].map((opt) => [opt.value, opt.textContent]));
let submitting = false;

function showStatus(state, message) {
  status.className = state ? `status status--${state}` : 'status';
  status.textContent = message;
}

function updateUI(isUserEdit = false) {
  const student = input.value.trim();
  for (const opt of select.options) {
    const base = baseLabels.get(opt.value);
    if (!opt.value || !base) continue;
    if (store.isFull(opt.value)) opt.textContent = `${base} (Hết chỗ)`;
    else if (store.isRegistered(student, opt.value)) opt.textContent = `${base} (Đã đăng ký)`;
    else opt.textContent = base;
  }
  const s = store.getSessionState(student, select.value);
  if (isUserEdit && !submitting) {
    if (s.status === 'registered') showStatus('duplicate', 'Bạn đã đăng ký phiên này.');
    else if (s.status === 'full') showStatus('error', 'Phiên này đã đủ 30 chỗ. Bạn hãy chọn phiên khác.');
    else showStatus('', 'Thông báo đăng ký sẽ xuất hiện tại đây.');
  }
  if (!submitting) {
    button.disabled = s.disabled;
    button.textContent = s.text;
  }
}

input.addEventListener('input', () => updateUI(true));
select.addEventListener('change', () => updateUI(true));

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  if (submitting) return;
  const payload = {ma_sv: input.value.trim(), ma_phien: select.value};
  if (!payload.ma_sv || !payload.ma_phien) {
    showStatus('error', 'Hãy nhập mã sinh viên và chọn một phiên.');
    if (!payload.ma_sv) input.focus();
    else select.focus();
    return;
  }
  const sessionState = store.getSessionState(payload.ma_sv, payload.ma_phien);
  if (sessionState.disabled) return;

  submitting = true;
  input.disabled = select.disabled = button.disabled = true;
  button.textContent = 'Đang gửi…';
  form.setAttribute('aria-busy', 'true');
  showStatus('pending', 'Đang gửi đăng ký…');
  try {
    const result = await submitRegistration(payload, fetch, () => store.markFull(payload.ma_phien));
    store.recordOutcome(payload.ma_sv, payload.ma_phien, result);
    showStatus(result.state, result.message);
  } catch {
    showStatus('error', 'Có lỗi khi gửi đăng ký. Vui lòng thử lại.');
  } finally {
    submitting = false;
    input.disabled = select.disabled = false;
    form.setAttribute('aria-busy', 'false');
    updateUI(false);
  }
});

updateUI();
