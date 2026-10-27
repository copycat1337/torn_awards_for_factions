let _myData = null;

async function toggleMyProfile() {
    const form = document.getElementById('my-profile-form');
    if (!form) return;

    if (form.style.display === 'none') {
        if (!_myData) await loadMyProfile();
        form.style.display = 'flex';
    } else {
        form.style.display = 'none';
    }
}

async function loadMyProfile() {
    const res = await fetch('/api/me');
    _myData = await res.json();

    document.getElementById('my-avatar-preview').src = _myData.profile_pic;
    document.getElementById('my-quote').value = _myData.quote || '';
}

async function saveMyProfile() {
    const quote = document.getElementById('my-quote').value;

    // 1. Update quote
    await fetch('/api/me', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ quote })
    });

    // 2. Upload new avatar if picked
    const file = document.getElementById('my-avatar-file').files[0];
    if (file) {
        const fd = new FormData();
        fd.append('avatar', file);
        const r = await fetch('/api/me/avatar', { method: 'POST', body: fd });
        const d = await r.json();
        if (d.error) return alert(d.error);
    }

    alert('Profile updated!');
    location.reload();
}

// Preview + wire once
document.addEventListener('DOMContentLoaded', () => {
    const file = document.getElementById('my-avatar-file');
    if (file) {
        file.addEventListener('change', e => {
            const f = e.target.files[0];
            if (!f) return;
            const reader = new FileReader();
            reader.onload = ev => document.getElementById('my-avatar-preview').src = ev.target.result;
            reader.readAsDataURL(f);
        });
    }
    loadMyProfile();
});