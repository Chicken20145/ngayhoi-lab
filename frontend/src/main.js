import {submitRegistration} from './api.js';

const form = document.getElementById('registration-form');
const input = document.getElementById('ma_sv');
const select = document.getElementById('ma_phien');
const button = document.getElementById('submit-button');
const status = document.getElementById('status');
let submitting = false;

function showStatus(state, message) {
  status.className = `status status--${state}`;
  status.textContent = message;
}

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
  submitting = true;
  input.disabled = select.disabled = button.disabled = true;
  button.textContent = 'Đang gửi…';
  form.setAttribute('aria-busy', 'true');
  showStatus('pending', 'Đang gửi đăng ký…');
  try {
    const result = await submitRegistration(payload);
    showStatus(result.state, result.message);
  } catch {
    showStatus('error', 'Có lỗi khi gửi đăng ký. Vui lòng thử lại.');
  } finally {
    submitting = false;
    input.disabled = select.disabled = button.disabled = false;
    button.textContent = 'Đăng ký tham gia';
    form.setAttribute('aria-busy', 'false');
  }
});
