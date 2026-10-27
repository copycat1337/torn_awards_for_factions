// ================== AWARD DETAIL POPUP ==================
function showAwardDetail(award) {
    const modal = document.getElementById('award-detail-modal');
    if (!modal) return;

    const icon        = document.getElementById('award-detail-icon');
    const name        = document.getElementById('award-detail-name');
    const description = document.getElementById('award-detail-description');
    const iconWrap    = modal.querySelector('.award-detail-icon-wrap');
    const howBlock    = document.getElementById('award-detail-how');
    const howText     = document.getElementById('award-detail-how-text');

    if (icon) {
        icon.src = award.icon_url || '';
        icon.alt = award.name || '';
    }

    if (iconWrap) {
        iconWrap.style.borderColor = award.color || '#00e0ff';
        iconWrap.style.boxShadow = `0 0 60px ${award.color || '#00e0ff'}44`;
    }

    if (name)        name.textContent = award.name || '';
    if (description) description.textContent = award.description || 'No description available.';

    // How to earn block
    if (howBlock && howText) {
        if (award.how_to_earn && award.how_to_earn.trim() !== '') {
            howText.textContent = award.how_to_earn;
            howBlock.style.display = 'block';
            howBlock.style.borderLeftColor = award.color || '#00e0ff';
        } else {
            howBlock.style.display = 'none';
        }
    }

    modal.classList.add('show');
}

// ================== MODAL HELPERS ==================
function closeModal(target) {
    const el = typeof target === 'string' ? document.getElementById(target) : target;
    if (el) el.classList.remove('show');
}

// ================== EVENT WIRING ==================
document.addEventListener('DOMContentLoaded', () => {

    // Wire up award cards
    document.querySelectorAll('.awards-library-card').forEach(card => {
        card.addEventListener('click', function () {
            const awardData = {
                name:        this.dataset.name        || '',
                description: this.dataset.description || '',
                how_to_earn: this.dataset.howToEarn   || '',
                icon_url:    this.dataset.icon        || '',
                color:       this.dataset.color       || '#00e0ff'
            };
            showAwardDetail(awardData);
        });
    });

    // Close modal on backdrop click
    document.querySelectorAll('.modal').forEach(m => {
        m.addEventListener('click', e => {
            if (e.target === m) m.classList.remove('show');
        });
    });

    // Close modal on Escape key
    document.addEventListener('keydown', e => {
        if (e.key !== 'Escape') return;
        document.querySelectorAll('.modal.show').forEach(m => m.classList.remove('show'));
    });
});