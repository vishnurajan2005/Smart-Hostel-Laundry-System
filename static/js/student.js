async function loadStudentData() {
    try {
        const [machinesResult, bookingsResult] = await Promise.all([
            api('/api/machines'),
            api('/api/bookings')
        ]);

        if (!machinesResult.success || !bookingsResult.success) {
            return;
        }

        const machines = machinesResult.machines || [];
        const bookings = bookingsResult.bookings || [];

        const activeMachines = machines.filter(function (machine) {
            return machine.status === 'active';
        });

        const availableMachines =
            document.getElementById('available-machines');

        const activeBookings =
            document.getElementById('active-bookings');

        const machineList =
            document.getElementById('machine-list');

        if (availableMachines) {
            availableMachines.textContent = activeMachines.length;
        }

        if (activeBookings) {
            activeBookings.textContent = bookings.filter(function (booking) {
                return booking.status === 'confirmed';
            }).length;
        }

        if (machineList) {
            if (machines.length === 0) {
                machineList.innerHTML =
                    '<div class="empty-state">' +
                    '<p>No machines found.</p>' +
                    '</div>';
            } else {
                machineList.innerHTML = machines.map(function (machine) {
                    const machineName = escapeHtml(machine.name);
                    const machineStatus = escapeHtml(machine.status);

                    return (
                        '<div class="machine-card">' +
                            '<h3>' + machineName + '</h3>' +
                            '<span class="status status-' +
                                machineStatus +
                            '">' +
                                machineStatus +
                            '</span>' +
                        '</div>'
                    );
                }).join('');
            }
        }

        renderBookings(bookings);

    } catch (error) {
        console.error('Failed to load student data:', error);
        showToast('Unable to load dashboard data.', 'error');
    }
}


function renderBookings(bookings) {
    const element = document.getElementById('booking-list');

    if (!element) {
        return;
    }

    if (!bookings || bookings.length === 0) {
        element.innerHTML =
            '<div class="empty-state">' +
                '<p>No bookings yet.</p>' +
                '<a class="btn btn-primary" href="/book">' +
                    'Book your first slot' +
                '</a>' +
            '</div>';

        return;
    }

    element.innerHTML = bookings.map(function (booking) {
        const machineName = escapeHtml(booking.machine_name);
        const bookingSlot = escapeHtml(booking.slot);
        const bookingStatus = escapeHtml(booking.status);
        const bookingDate = formatDate(booking.booking_date);

        let cancelButton = '';

        if (booking.status === 'confirmed') {
            cancelButton =
                '<button ' +
                    'class="btn btn-danger" ' +
                    'data-testid="cancel-booking" ' +
                    'data-booking-id="' + booking.id + '">' +
                    'Cancel' +
                '</button>';
        }

        return (
            '<div class="booking-card">' +
                '<div class="booking-main">' +
                    '<strong>' + machineName + '</strong>' +
                    '<div class="booking-meta">' +
                        bookingDate +
                        ' · ' +
                        bookingSlot +
                    '</div>' +
                '</div>' +

                '<div class="booking-actions">' +
                    '<span class="status status-' +
                        bookingStatus +
                    '">' +
                        bookingStatus +
                    '</span>' +
                    cancelButton +
                '</div>' +
            '</div>'
        );
    }).join('');

    element
        .querySelectorAll('[data-testid="cancel-booking"]')
        .forEach(function (button) {
            button.addEventListener('click', function () {
                const bookingId =
                    Number(button.dataset.bookingId);

                cancelBooking(bookingId);
            });
        });
}


async function cancelBooking(id) {
    const confirmed = confirm(
        'Cancel this upcoming laundry booking? The slot will be released.'
    );

    if (!confirmed) {
        return;
    }

    const result = await api(
        '/api/bookings/' + id,
        {
            method: 'DELETE'
        }
    );

    if (result.success) {
        await loadStudentData();
    }
}


document.addEventListener('DOMContentLoaded', async function () {
    await loadStudentData();
});