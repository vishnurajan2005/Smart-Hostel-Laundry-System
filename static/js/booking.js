let machines = [], bookings = [];
const dateInput = document.getElementById('date-input'), machineSelect = document.getElementById('machine-select'), slotSelect = document.getElementById('slot-select'), summary = document.getElementById('summary'), note = document.getElementById('availability-note');
async function initBooking() {
  const [m, s, b] = await Promise.all([api('/api/machines'), api('/api/slots'), api('/api/bookings')]);
  if (!m.success || !s.success || !b.success) return;
  machines = m.machines; bookings = b.bookings;
  machineSelect.innerHTML = '<option value="">Select machine</option>' + machines.map(x => `<option value="${x.id}" ${x.status!=='active'?'disabled':''}>${escapeHtml(x.name)}${x.status!=='active'?' (Inactive)':''}</option>`).join('');
  slotSelect.innerHTML = '<option value="">Select time slot</option>' + s.slots.map(x => `<option value="${escapeHtml(x)}">${escapeHtml(x)}</option>`).join('');
  dateInput.addEventListener('change', refreshAvailability); machineSelect.addEventListener('change', refreshAvailability); slotSelect.addEventListener('change', updateSummary);
  refreshAvailability();
}
function refreshAvailability() {
  const selectedDate = dateInput.value, machineId = Number(machineSelect.value);
  [...slotSelect.options].forEach(o => { if (!o.value) return; const taken = bookings.some(b => b.machine_id === machineId && b.booking_date === selectedDate && b.slot === o.value && b.status === 'confirmed'); o.disabled = taken; o.textContent = o.value + (taken ? ' — Booked' : ' — Available'); });
  const selectedMachine = machines.find(m => m.id === machineId);
  if (!selectedDate || !machineId) note.textContent = 'Select a date and machine to see availability.';
  else if (!selectedMachine || selectedMachine.status !== 'active') note.textContent = 'This machine is inactive.';
  else note.textContent = 'Booked slots are disabled. Choose any available slot.';
  updateSummary();
}
function updateSummary() { const machine=machines.find(m=>m.id===Number(machineSelect.value)); summary.innerHTML = machine && dateInput.value && slotSelect.value ? `<p><strong>${escapeHtml(machine.name)}</strong></p><p>${formatDate(dateInput.value)}</p><p>${escapeHtml(slotSelect.value)}</p>` : '<p class="muted">Your selection will appear here.</p>'; }
document.getElementById('booking-form').addEventListener('submit', async (e) => { e.preventDefault(); if (!dateInput.value || !machineSelect.value || !slotSelect.value) return showToast('Select date, machine and time slot.', 'error'); const result = await api('/api/bookings',{method:'POST',body:JSON.stringify({booking_date:dateInput.value,machine_id:Number(machineSelect.value),slot:slotSelect.value})}); if(result.success){ bookings.push(result.booking); showToast('Booking confirmed.','success'); setTimeout(()=>location.href='/dashboard',700); } });
initBooking();
