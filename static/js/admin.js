// ================== GLOBAL STATE ==================
let allUsers = [];
let allAwards = [];
let selectedUserId = null;

// ================== INIT ==================
document.addEventListener('DOMContentLoaded', () => {
    setupTabs();
    loadUsers();
    loadAwards();
    loadAssignPanel();

    const search = document.getElementById('assign-user-search');
    if (search) search.addEventListener('input', filterAssignUsers);

    const fileInput = document.getElementById('user-avatar-file');
    if (fileInput) {
        fileInput.addEventListener('change', e => {
            const f = e.target.files[0];
            if (!f) return;
            const reader = new FileReader();
            reader.onload = ev => {
                document.getElementById('user-avatar-preview').src = ev.target.result;
            };
            reader.readAsDataURL(f);
        });
    }

    const awardFileInput = document.getElementById('award-icon-file');
    if (awardFileInput) {
        awardFileInput.addEventListener('change', e => {
            const f = e.target.files[0];
            if (!f) return;
            const reader = new FileReader();
            reader.onload = ev => {
                document.getElementById('award-icon-preview').src = ev.target.result;
            };
            reader.readAsDataURL(f);
        });
    }

    // ================== EVENT DELEGATION ==================
    document.addEventListener('click', e => {
        // Edit user
        const editUserBtn = e.target.closest('.edit-user-btn');
        if (editUserBtn) {
            const id = parseInt(editUserBtn.dataset.userId);
            const user = allUsers.find(u => u.id === id);
            if (user) openUserModal(user);
            return;
        }

        // Delete user
        const delUserBtn = e.target.closest('.delete-user-btn');
        if (delUserBtn) {
            const id = parseInt(delUserBtn.dataset.userId);
            const user = allUsers.find(u => u.id === id);
            if (user) deleteUser(id, user.username);
            return;
        }

        // Edit award
        const editAwardBtn = e.target.closest('.edit-award-btn');
        if (editAwardBtn) {
            const id = parseInt(editAwardBtn.dataset.awardId);
            const award = allAwards.find(a => a.id === id);
            if (award) openAwardModal(award);
            return;
        }

        // Delete award
        const delAwardBtn = e.target.closest('.delete-award-btn');
        if (delAwardBtn) {
            const id = parseInt(delAwardBtn.dataset.awardId);
            const award = allAwards.find(a => a.id === id);
            if (award) deleteAward(id, award.name);
            return;
        }

        // Award icon preview (mini-icon in awards table)
        const previewImg = e.target.closest('[data-award-preview]');
        if (previewImg) {
            const id = parseInt(previewImg.dataset.awardPreview);
            const award = allAwards.find(a => a.id === id);
            if (award) {
                showAwardDetail({
                    name: award.name,
                    description: award.description || '',
                    how_to_earn: award.how_to_earn || '',
                    icon_url: award.icon_url,
                    color: award.color,
                    count: 1,
                    username: '(award preview)'
                });
            }
        }
    });
});

// ================== TABS ==================
function setupTabs() {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            const target = document.getElementById('tab-' + btn.dataset.tab);
            if (target) target.classList.add('active');

            document.querySelectorAll('.sidebar-link[data-nav-tab]').forEach(l => {
                l.classList.toggle('active', l.dataset.navTab === btn.dataset.tab);
            });
        });
    });
}

// ================== USERS ==================
async function loadUsers() {
    const res = await fetch('/api/users');
    allUsers = await res.json();
    renderUsersTable();
    renderAssignUserList();
}

function renderUsersTable() {
    const tbody = document.querySelector('#users-table tbody');
    if (!tbody) return;

    const catLabels = { fame: 'Fame', shame: 'Shame', friend: 'Friend' };

    tbody.innerHTML = allUsers.map(u => {
        const statusClass = (u.status || '').toLowerCase();
        const cat = u.category || 'fame';
        return `
        <tr>
            <td>${u.id}</td>
            <td>
                <div class="user-cell">
                    <img src="${u.profile_pic}" class="table-avatar" alt="">
                    <strong>${u.username}</strong>
                </div>
            </td>
            <td><span class="badge ${u.role}">${u.role}</span></td>
            <td>${u.user_role || '—'}</td>
            <td><span class="cat-pill cat-${cat}">${catLabels[cat] || cat}</span></td>
            <td><span class="status-pill status-${statusClass}">${u.status || '—'}</span></td>
            <td>
                <button class="btn-sm edit-user-btn" data-user-id="${u.id}">Edit</button>
                <button class="btn-sm danger delete-user-btn" data-user-id="${u.id}">Delete</button>
            </td>
        </tr>
        `;
    }).join('');
}

function openUserModal(user = null) {
    document.getElementById('user-modal-title').textContent = user ? 'Edit User' : 'Add User';
    document.getElementById('user-id').value = user ? user.id : '';
    document.getElementById('user-username').value = user ? user.username : '';
    document.getElementById('user-password').value = '';
    document.getElementById('user-role').value = user ? user.role : 'member';
    document.getElementById('user-category').value = user ? (user.category || 'fame') : 'fame';
    document.getElementById('user-user-role').value = user ? (user.user_role || 'Member') : 'Member';
    document.getElementById('user-torn-id').value = user ? (user.torn_id || 0) : 0;
    document.getElementById('user-status').value = user ? (user.status || 'Active') : 'Active';
    document.getElementById('user-description').value = user ? (user.description || '') : '';
    document.getElementById('user-quote').value = user
        ? user.quote
        : 'Silent moves. Loud results.';

    const pic = user ? user.profile_pic : '/static/img/default_avatar.png';
    document.getElementById('user-profile-pic').value = pic;
    document.getElementById('user-avatar-preview').src = pic;
    document.getElementById('user-avatar-file').value = '';

    document.getElementById('user-modal').classList.add('show');
}

async function submitUserForm(e) {
    e.preventDefault();
    const id = document.getElementById('user-id').value;
    const payload = {
        username: document.getElementById('user-username').value.trim(),
        role: document.getElementById('user-role').value,
        category: document.getElementById('user-category').value,
        user_role: document.getElementById('user-user-role').value,
        torn_id: parseInt(document.getElementById('user-torn-id').value) || 0,
        status: document.getElementById('user-status').value,
        description: document.getElementById('user-description').value,
        quote: document.getElementById('user-quote').value,
    };
    const pw = document.getElementById('user-password').value;
    if (pw) payload.password = pw;
    if (!id && !pw) return alert('Password required for new user');

    const url = id ? `/api/users/${id}` : '/api/users';
    const method = id ? 'PUT' : 'POST';
    const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.error) return alert(data.error);

    const savedId = id || data.id;
    const file = document.getElementById('user-avatar-file').files[0];
    if (file && savedId) {
        const fd = new FormData();
        fd.append('avatar', file);
        const uploadRes = await fetch(`/api/users/${savedId}/avatar`, {
            method: 'POST',
            body: fd
        });
        const upData = await uploadRes.json();
        if (upData.error) alert('Avatar upload failed: ' + upData.error);
    }

    closeModal('user-modal');
    loadUsers();
}

async function deleteUser(id, name) {
    if (!confirm(`Delete user "${name}"? This will remove all their awards.`)) return;
    const res = await fetch(`/api/users/${id}`, { method: 'DELETE' });
    const data = await res.json();
    if (data.error) return alert(data.error);
    loadUsers();
    if (selectedUserId === id) resetAssignPanel();
}

// ================== AWARDS ==================
async function loadAwards() {
    const res = await fetch('/api/awards');
    allAwards = await res.json();
    renderAwardsTable();
}

function renderAwardsTable() {
    const tbody = document.querySelector('#awards-table tbody');
    if (!tbody) return;

    tbody.innerHTML = allAwards.map(a => {
        return `
        <tr>
            <td>${a.id}</td>
            <td>
                <img src="${a.icon_url}"
                     class="mini-icon"
                     style="border-color:${a.color}; cursor:pointer;"
                     title="Click to preview"
                     onerror="this.src='/static/img/default_award.png'"
                     data-award-preview="${a.id}">
            </td>
            <td><strong>${a.name}</strong></td>
            <td>${a.description || ''}</td>
            <td><span class="color-swatch" style="background:${a.color}"></span> ${a.color}</td>
            <td>
                <button class="btn-sm edit-award-btn" data-award-id="${a.id}">Edit</button>
                <button class="btn-sm danger delete-award-btn" data-award-id="${a.id}">Delete</button>
            </td>
        </tr>
        `;
    }).join('');
}

function openAwardModal(award = null) {
    document.getElementById('award-modal-title').textContent = award ? 'Edit Award' : 'Add Award';
    document.getElementById('award-id').value = award ? award.id : '';
    document.getElementById('award-name').value = award ? award.name : '';
    document.getElementById('award-description').value = award ? award.description : '';
    document.getElementById('award-how-to-earn').value = award ? (award.how_to_earn || '') : '';
    document.getElementById('award-icon').value = award ? award.icon_url : '';
    document.getElementById('award-color').value = award ? award.color : '#00ffcc';

    const iconPreview = document.getElementById('award-icon-preview');
    if (iconPreview) {
        iconPreview.src = award ? award.icon_url : '/static/img/default_award.png';
        iconPreview.onerror = () => { iconPreview.src = '/static/img/default_award.png'; };
    }
    const awardFileInput = document.getElementById('award-icon-file');
    if (awardFileInput) awardFileInput.value = '';

    document.getElementById('award-modal').classList.add('show');
}

async function submitAwardForm(e) {
    e.preventDefault();
    const id = document.getElementById('award-id').value;
    const payload = {
        name: document.getElementById('award-name').value.trim(),
        description: document.getElementById('award-description').value,
        how_to_earn: document.getElementById('award-how-to-earn').value,
        icon_url: document.getElementById('award-icon').value || '/static/icons/default.png',
        color: document.getElementById('award-color').value,
    };
    const url = id ? `/api/awards/${id}` : '/api/awards';
    const method = id ? 'PUT' : 'POST';
    const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.error) return alert(data.error);

    const savedId = id || data.id;
    const file = document.getElementById('award-icon-file').files[0];
    if (file && savedId) {
        const fd = new FormData();
        fd.append('icon', file);
        try {
            const uploadRes = await fetch(`/api/awards/${savedId}/icon`, {
                method: 'POST',
                body: fd
            });
            if (!uploadRes.ok) {
                const errText = await uploadRes.text();
                console.error('Icon upload failed:', uploadRes.status, errText);
                alert('Award icon upload failed: ' + uploadRes.status);
            } else {
                const upData = await uploadRes.json();
                if (upData.error) alert('Award icon upload failed: ' + upData.error);
            }
        } catch (err) {
            console.error('Icon upload exception:', err);
            alert('Award icon upload exception: ' + err.message);
        }
    }

    closeModal('award-modal');
    loadAwards();
    if (selectedUserId) loadUserAwardPanel(selectedUserId);
}

async function deleteAward(id, name) {
    if (!confirm(`Delete award "${name}"? Removes it from all users.`)) return;
    const res = await fetch(`/api/awards/${id}`, { method: 'DELETE' });
    const data = await res.json();
    if (data.error) return alert(data.error);
    loadAwards();
    if (selectedUserId) loadUserAwardPanel(selectedUserId);
}

// ================== ASSIGN PANEL ==================
function loadAssignPanel() {
    renderAssignUserList();
}

function renderAssignUserList() {
    const list = document.getElementById('assign-user-list');
    if (!list) return;

    const fameUsers = allUsers.filter(u => (u.category || 'fame') === 'fame');

    list.innerHTML = fameUsers.map(u => `
        <li data-user-id="${u.id}" class="${selectedUserId === u.id ? 'selected' : ''}">
            <span class="dot ${u.status === 'Active' ? 'online' : ''}"></span>
            <strong>${u.username}</strong>
            <small>${u.user_role || u.role}</small>
        </li>
    `).join('');

    list.querySelectorAll('li').forEach(li => {
        li.addEventListener('click', () => {
            selectedUserId = parseInt(li.dataset.userId);
            renderAssignUserList();
            loadUserAwardPanel(selectedUserId);
        });
    });
}

function filterAssignUsers(e) {
    const q = e.target.value.toLowerCase();
    document.querySelectorAll('#assign-user-list li').forEach(li => {
        li.style.display = li.textContent.toLowerCase().includes(q) ? '' : 'none';
    });
}

async function loadUserAwardPanel(userId) {
    const user = allUsers.find(u => u.id === userId);
    if (!user) return;

    document.querySelector('#assign-title .highlight').textContent = user.username;

    const res = await fetch(`/api/users/${userId}/awards`);
    const userAwards = await res.json();

    const grid = document.getElementById('assign-award-grid');
    grid.innerHTML = allAwards.map(a => {
        const owned = userAwards.find(ua => ua.id === a.id);
        const count = owned ? owned.count : 0;
        return `
            <div class="award-assign-card ${count > 0 ? 'owned' : ''}">
                <div class="award-icon-wrap"
                     style="border-color:${a.color}; cursor:pointer;"
                     title="Click to preview"
                     onclick='showAwardDetail({
                         "name": ${JSON.stringify(a.name)},
                         "description": ${JSON.stringify(a.description || "")},
                         "how_to_earn": ${JSON.stringify(a.how_to_earn || "")},
                         "icon_url": ${JSON.stringify(a.icon_url)},
                         "color": ${JSON.stringify(a.color)},
                         "count": ${count || 1},
                         "username": ${JSON.stringify(user.username)}
                     })'>
                    <img src="${a.icon_url}" alt="${a.name}"
                         onerror="this.src='/static/img/default_award.png'">
                    ${count > 0 ? `<span class="stack-count">x${count}</span>` : ''}
                </div>
                <div class="award-assign-name">${a.name}</div>
                <div class="award-assign-actions">
                    <button class="btn-sm danger"
                            onclick="event.stopPropagation(); changeAward(${userId}, ${a.id}, -1)">−</button>
                    <button class="btn-sm"
                            onclick="event.stopPropagation(); changeAward(${userId}, ${a.id}, 1)">+</button>
                </div>
            </div>
        `;
    }).join('');
}

async function changeAward(userId, awardId, delta) {
    const url = delta > 0 ? '/api/add_award' : '/api/remove_award';
    const body = delta > 0
        ? { user_id: userId, award_id: awardId, amount: 1 }
        : { user_id: userId, award_id: awardId };

    const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });
    const data = await res.json();
    if (data.error) return alert(data.error);
    loadUserAwardPanel(userId);
}

function resetAssignPanel() {
    selectedUserId = null;
    const highlight = document.querySelector('#assign-title .highlight');
    if (highlight) highlight.textContent = '—';
    const grid = document.getElementById('assign-award-grid');
    if (grid) grid.innerHTML = '<p class="empty-msg">Select a member to assign awards.</p>';
    renderAssignUserList();
}