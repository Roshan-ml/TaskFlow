// Modal helpers
function openEditModal(taskId, title, description, priority, dueDate, assignedToId) {
    document.getElementById('editTaskForm').action = `/tasks/${taskId}/edit`;
    document.getElementById('editTitle').value = title;
    document.getElementById('editDescription').value = description;
    document.getElementById('editPriority').value = priority;
    document.getElementById('editDueDate').value = dueDate;
    document.getElementById('editAssignee').value = assignedToId;
    document.getElementById('editTaskModal').classList.remove('hidden');
}

// Close modals on backdrop click
document.addEventListener('click', function(e) {
    ['createModal', 'createTaskModal', 'editTaskModal'].forEach(id => {
        const modal = document.getElementById(id);
        if (modal && e.target === modal) {
            modal.classList.add('hidden');
        }
    });
});

// Close modals on Escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        ['createModal', 'createTaskModal', 'editTaskModal'].forEach(id => {
            const modal = document.getElementById(id);
            if (modal) modal.classList.add('hidden');
        });
    }
});

// Auto-dismiss flash messages after 4 seconds
setTimeout(() => {
    document.querySelectorAll('[class*="bg-green-50"], [class*="bg-red-50"]').forEach(el => {
        el.style.transition = 'opacity 0.5s';
        el.style.opacity = '0';
        setTimeout(() => el.remove(), 500);
    });
}, 4000);
