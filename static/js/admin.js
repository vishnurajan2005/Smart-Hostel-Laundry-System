let adminMachines = [];


/* =========================================================
   PAGE INITIALIZATION
   ========================================================= */

document.addEventListener('DOMContentLoaded', function () {

    const addButton =
        document.getElementById('add-machine-button');

    const closeButton =
        document.getElementById('close-machine-modal');

    const cancelButton =
        document.getElementById('cancel-machine-modal');

    const machineForm =
        document.getElementById('machine-form');

    const filterButton =
        document.getElementById('filter-bookings-button');

    const machineModal =
        document.getElementById('machine-modal');


    /* Add machine */

    if (addButton) {

        addButton.addEventListener('click', function () {

            openMachineModal();

        });

    }


    /* Close button */

    if (closeButton) {

        closeButton.addEventListener('click', function () {

            closeMachineModal();

        });

    }


    /* Cancel button */

    if (cancelButton) {

        cancelButton.addEventListener('click', function () {

            closeMachineModal();

        });

    }


    /* Machine form */

    if (machineForm) {

        machineForm.addEventListener('submit', function (event) {

            saveMachine(event);

        });

    }


    /* Booking filter */

    if (filterButton) {

        filterButton.addEventListener('click', function () {

            loadAdminBookings();

        });

    }


    /* Escape key */

    if (machineModal) {

        machineModal.addEventListener('cancel', function (event) {

            event.preventDefault();

            closeMachineModal();

        });

    }


    /* Backdrop */

    if (machineModal) {

        machineModal.addEventListener('click', function (event) {

            if (event.target === machineModal) {

                closeMachineModal();

            }

        });

    }


    /* Load admin dashboard */

    loadAdmin();

});


/* =========================================================
   LOAD ADMIN
   ========================================================= */

async function loadAdmin() {

    await Promise.all([

        loadAdminMachines(),

        loadAdminBookings()

    ]);

}


/* =========================================================
   LOAD MACHINES
   ========================================================= */

async function loadAdminMachines() {

    const result =
        await api('/api/machines');


    if (!result || !result.success) {

        console.error('Failed to load machines:', result);

        return;

    }


    adminMachines =
        result.machines || [];


    renderMachines();

}


/* =========================================================
   RENDER MACHINES
   ========================================================= */

function renderMachines() {

    const container =
        document.getElementById('admin-machines');


    if (!container) {

        return;

    }


    /* Empty state */

    if (adminMachines.length === 0) {

        container.innerHTML =

            '<div class="empty-state">' +

                '<p>No machines configured.</p>' +

                '<button type="button" ' +
                    'class="btn btn-primary" ' +
                    'id="empty-add-machine">' +
                    'Add your first machine' +
                '</button>' +

            '</div>';


        const emptyButton =
            document.getElementById('empty-add-machine');


        if (emptyButton) {

            emptyButton.addEventListener(
                'click',
                function () {

                    openMachineModal();

                }
            );

        }

        return;

    }


    let rows = '';


    adminMachines.forEach(function (machine) {

        const name =
            escapeHtml(machine.name || '');


        const status =
            escapeHtml(machine.status || '');


        const toggleText =
            machine.status === 'active'
                ? 'Disable'
                : 'Enable';


        rows +=

            '<tr>' +

                '<td>' +
                    name +
                '</td>' +

                '<td>' +

                    '<span class="status status-' +
                        status +
                    '">' +

                        status +

                    '</span>' +

                '</td>' +

                '<td class="machine-actions">' +

                    '<button type="button" ' +
                        'class="btn btn-outline machine-toggle" ' +
                        'data-id="' +
                            machine.id +
                        '">' +

                        toggleText +

                    '</button>' +

                    '<button type="button" ' +
                        'class="btn btn-outline machine-edit" ' +
                        'data-id="' +
                            machine.id +
                        '">' +

                        'Edit' +

                    '</button>' +

                    '<button type="button" ' +
                        'class="btn btn-danger machine-delete" ' +
                        'data-id="' +
                            machine.id +
                        '">' +

                        'Delete' +

                    '</button>' +

                '</td>' +

            '</tr>';

    });


    container.innerHTML =

        '<table class="data-table">' +

            '<thead>' +

                '<tr>' +

                    '<th>Machine</th>' +

                    '<th>Status</th>' +

                    '<th>Actions</th>' +

                '</tr>' +

            '</thead>' +

            '<tbody>' +

                rows +

            '</tbody>' +

        '</table>';


    /* Toggle */

    container
        .querySelectorAll('.machine-toggle')
        .forEach(function (button) {

            button.addEventListener(
                'click',
                function () {

                    const id =
                        Number(button.dataset.id);

                    toggleMachine(id);

                }
            );

        });


    /* Edit */

    container
        .querySelectorAll('.machine-edit')
        .forEach(function (button) {

            button.addEventListener(
                'click',
                function () {

                    const id =
                        Number(button.dataset.id);

                    editMachine(id);

                }
            );

        });


    /* Delete */

    container
        .querySelectorAll('.machine-delete')
        .forEach(function (button) {

            button.addEventListener(
                'click',
                function () {

                    const id =
                        Number(button.dataset.id);

                    deleteMachine(id);

                }
            );

        });

}


/* =========================================================
   OPEN MACHINE MODAL
   ========================================================= */

function openMachineModal(machine) {

    const modal =
        document.getElementById('machine-modal');

    const title =
        document.getElementById('machine-modal-title');

    const idInput =
        document.getElementById('machine-id');

    const nameInput =
        document.getElementById('machine-name');

    const statusInput =
        document.getElementById('machine-status');


    if (!modal || !title || !idInput ||
        !nameInput || !statusInput) {

        console.error(
            'Machine modal elements are missing.'
        );

        return;

    }


    if (machine) {

        title.textContent =
            'Edit machine';

        idInput.value =
            machine.id;

        nameInput.value =
            machine.name;

        statusInput.value =
            machine.status;

    }

    else {

        title.textContent =
            'Add machine';

        idInput.value =
            '';

        nameInput.value =
            '';

        statusInput.value =
            'active';

    }


    if (typeof modal.showModal === 'function') {

        modal.showModal();

    }

    else {

        modal.setAttribute('open', '');

    }


    setTimeout(function () {

        nameInput.focus();

    }, 100);

}


/* =========================================================
   CLOSE MACHINE MODAL
   ========================================================= */

function closeMachineModal() {

    const modal =
        document.getElementById('machine-modal');

    const form =
        document.getElementById('machine-form');

    const idInput =
        document.getElementById('machine-id');


    if (!modal) {

        return;

    }


    if (typeof modal.close === 'function') {

        if (modal.open) {

            modal.close();

        }

    }

    else {

        modal.removeAttribute('open');

    }


    if (form) {

        form.reset();

    }


    if (idInput) {

        idInput.value = '';

    }

}


/* =========================================================
   SAVE MACHINE
   ========================================================= */

async function saveMachine(event) {

    event.preventDefault();


    const idInput =
        document.getElementById('machine-id');

    const nameInput =
        document.getElementById('machine-name');

    const statusInput =
        document.getElementById('machine-status');


    if (!idInput || !nameInput || !statusInput) {

        showToast(
            'Machine form could not be loaded.',
            'error'
        );

        return;

    }


    const id =
        idInput.value.trim();

    const name =
        nameInput.value.trim();

    const status =
        statusInput.value;


    if (name.length < 2) {

        showToast(
            'Machine name must contain at least 2 characters.',
            'error'
        );

        nameInput.focus();

        return;

    }


    if (name.length > 120) {

        showToast(
            'Machine name cannot exceed 120 characters.',
            'error'
        );

        nameInput.focus();

        return;

    }


    if (
        status !== 'active' &&
        status !== 'inactive'
    ) {

        showToast(
            'Invalid machine status.',
            'error'
        );

        return;

    }


    const payload = {

        name: name,

        status: status

    };


    let result;


    if (id) {

        result =
            await api(
                '/api/admin/machines/' + id,
                {
                    method: 'PUT',

                    headers: {
                        'Content-Type':
                            'application/json'
                    },

                    body:
                        JSON.stringify(payload)
                }
            );

    }

    else {

        result =
            await api(
                '/api/admin/machines',
                {
                    method: 'POST',

                    headers: {
                        'Content-Type':
                            'application/json'
                    },

                    body:
                        JSON.stringify(payload)
                }
            );

    }


    if (!result || !result.success) {

        console.error(
            'Machine API failed:',
            result
        );

        return;

    }


    closeMachineModal();

    await loadAdmin();

}


/* =========================================================
   EDIT MACHINE
   ========================================================= */

function editMachine(id) {

    const machine =
        adminMachines.find(function (item) {

            return item.id === id;

        });


    if (!machine) {

        showToast(
            'Machine not found.',
            'error'
        );

        return;

    }


    openMachineModal(machine);

}


/* =========================================================
   TOGGLE MACHINE
   ========================================================= */

async function toggleMachine(id) {

    const machine =
        adminMachines.find(function (item) {

            return item.id === id;

        });


    if (!machine) {

        return;

    }


    const newStatus =
        machine.status === 'active'
            ? 'inactive'
            : 'active';


    const result =
        await api(
            '/api/admin/machines/' +
            id +
            '/status',
            {
                method: 'PATCH',

                headers: {
                    'Content-Type':
                        'application/json'
                },

                body:
                    JSON.stringify({
                        status: newStatus
                    })
            }
        );


    if (result && result.success) {

        await loadAdmin();

    }

}


/* =========================================================
   DELETE MACHINE
   ========================================================= */

async function deleteMachine(id) {

    const machine =
        adminMachines.find(function (item) {

            return item.id === id;

        });


    if (!machine) {

        return;

    }


    const confirmed =
        confirm(
            'Delete "' +
            machine.name +
            '"? This action cannot be undone.'
        );


    if (!confirmed) {

        return;

    }


    const result =
        await api(
            '/api/admin/machines/' + id,
            {
                method: 'DELETE'
            }
        );


    if (result && result.success) {

        await loadAdmin();

    }

}


/* =========================================================
   LOAD ADMIN BOOKINGS
   ========================================================= */

async function loadAdminBookings() {

    const searchInput =
        document.getElementById('booking-search');

    const statusInput =
        document.getElementById('booking-status');

    const dateInput =
        document.getElementById('booking-date');


    const search =
        searchInput
            ? searchInput.value.trim()
            : '';


    const status =
        statusInput
            ? statusInput.value
            : '';


    const bookingDate =
        dateInput
            ? dateInput.value
            : '';


    const params =
        new URLSearchParams();


    if (search) {

        params.set(
            'search',
            search
        );

    }


    if (status) {

        params.set(
            'status',
            status
        );

    }


    if (bookingDate) {

        params.set(
            'date',
            bookingDate
        );

    }


    const queryString =
        params.toString();


    const url =
        queryString
            ? '/api/admin/bookings?' + queryString
            : '/api/admin/bookings';


    const result =
        await api(url);


    if (!result || !result.success) {

        console.error(
            'Failed to load bookings:',
            result
        );

        return;

    }


    renderAdminBookings(
        result.bookings || []
    );

}


/* =========================================================
   RENDER ADMIN BOOKINGS
   ========================================================= */

function renderAdminBookings(bookings) {

    const container =
        document.getElementById('admin-bookings');


    if (!container) {

        return;

    }


    if (!bookings || bookings.length === 0) {

        container.innerHTML =

            '<div class="empty-state">' +

                '<p>No bookings match your filters.</p>' +

            '</div>';

        return;

    }


    let rows = '';


    bookings.forEach(function (booking) {

        const studentName =
            escapeHtml(
                booking.student_name || ''
            );


        const studentEmail =
            escapeHtml(
                booking.student_email || ''
            );


        const machineName =
            escapeHtml(
                booking.machine_name || ''
            );


        const slot =
            escapeHtml(
                booking.slot || ''
            );


        const status =
            escapeHtml(
                booking.status || ''
            );


        rows +=

            '<tr>' +

                '<td>' +

                    studentName +

                    '<br>' +

                    '<small>' +

                        studentEmail +

                    '</small>' +

                '</td>' +

                '<td>' +

                    machineName +

                '</td>' +

                '<td>' +

                    formatDate(
                        booking.booking_date
                    ) +

                '</td>' +

                '<td>' +

                    slot +

                '</td>' +

                '<td>' +

                    '<span class="status status-' +

                        status +

                    '">' +

                        status +

                    '</span>' +

                '</td>' +

            '</tr>';

    });


    container.innerHTML =

        '<table class="data-table">' +

            '<thead>' +

                '<tr>' +

                    '<th>Student</th>' +

                    '<th>Machine</th>' +

                    '<th>Date</th>' +

                    '<th>Slot</th>' +

                    '<th>Status</th>' +

                '</tr>' +

            '</thead>' +

            '<tbody>' +

                rows +

            '</tbody>' +

        '</table>';

}