/**
 * PCM Asset - Global JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Sidebar Toggle Logic
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('mobile-overlay');

    window.toggleSidebar = function () {
        if (!sidebar || !overlay) return;

        const isClosed = sidebar.classList.contains('-translate-x-full');
        if (isClosed) {
            // Open
            sidebar.classList.remove('-translate-x-full');
            overlay.classList.remove('hidden');
            setTimeout(() => {
                overlay.classList.remove('opacity-0');
            }, 10);
        } else {
            // Close
            sidebar.classList.add('-translate-x-full');
            overlay.classList.add('opacity-0');
            setTimeout(() => {
                overlay.classList.add('hidden');
            }, 300);
        }
    };

    // 2. Keyboard shortcut for Search (/)
    document.addEventListener('keydown', (e) => {
        if (e.key === '/' && !['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) {
            e.preventDefault();
            document.querySelector('input[name="search"]')?.focus();
        }
    });

    // 3. Auto dismiss flash messages
    const toasts = document.querySelectorAll('.flash-message');
    toasts.forEach(toast => {
        setTimeout(() => {
            toast.classList.add('opacity-0', 'translate-x-[100%]');
            setTimeout(() => {
                toast.remove();
            }, 500);
        }, 5000);
    });

    // 4. Global Event Delegation for Delete Buttons
    document.addEventListener('click', (e) => {
        const btn = e.target.closest('.delete-item-btn');
        if (btn) {
            const id = btn.getAttribute('data-id');
            const name = btn.getAttribute('data-name');
            const url = btn.getAttribute('data-url');
            if (id && name && url) {
                window.confirmDeleteItem(id, name, url);
            }
        }
    });
});

/**
 * Shared Item Deletion Logic
 * @param {number} id - Item ID
 * @param {string} name - Item Name
 * @param {string} deleteUrlPattern - URL pattern with placeholder
 */
window.confirmDeleteItem = function (id, name, deleteUrlPattern) {
    Swal.fire({
        title: 'Perhatian!',
        text: `Apakah Anda yakin ingin menghapus "${name}"? Tindakan ini tidak dapat dibatalkan.`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#ef4444',
        cancelButtonColor: '#1f2937',
        confirmButtonText: 'Ya, Hapus',
        cancelButtonText: 'Batal',
        customClass: {
            confirmButton: 'order-2',
            cancelButton: 'order-1'
        }
    }).then((result) => {
        if (result.isConfirmed) {
            const form = document.getElementById('delete-form');
            if (form) {
                form.action = deleteUrlPattern.replace('0', id);
                form.submit();
            }
        }
    });
};
