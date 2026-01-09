/**
 * Media Renamer Web App - Frontend JavaScript
 */

// State
const state = {
    files: [],
    currentFile: null,
    selectedFiles: new Set(),
    browserPath: '/',
    searchType: null
};

// DOM Elements
const elements = {
    tmdbApiKey: document.getElementById('tmdb-api-key'),
    toggleApiKey: document.getElementById('toggle-api-key'),
    mediaDir: document.getElementById('media-dir'),
    browseDir: document.getElementById('browse-dir'),
    modeSelect: document.getElementById('mode-select'),
    dryRun: document.getElementById('dry-run'),
    saveSettings: document.getElementById('save-settings'),
    scanFiles: document.getElementById('scan-files'),
    filesPanel: document.getElementById('files-panel'),
    filesList: document.getElementById('files-list'),
    fileCount: document.getElementById('file-count'),
    selectAll: document.getElementById('select-all'),
    renameSelected: document.getElementById('rename-selected'),
    browserModal: document.getElementById('browser-modal'),
    browserUp: document.getElementById('browser-up'),
    browserCurrentPath: document.getElementById('browser-current-path'),
    browserList: document.getElementById('browser-list'),
    browserSelect: document.getElementById('browser-select'),
    searchModal: document.getElementById('search-modal'),
    searchModalTitle: document.getElementById('search-modal-title'),
    searchQuery: document.getElementById('search-query'),
    searchBtn: document.getElementById('search-btn'),
    searchResults: document.getElementById('search-results'),
    toastContainer: document.getElementById('toast-container')
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initEventListeners();
    loadConfig();
});

function initEventListeners() {
    // Settings
    elements.toggleApiKey.addEventListener('click', toggleApiKeyVisibility);
    elements.saveSettings.addEventListener('click', saveSettings);
    elements.scanFiles.addEventListener('click', scanFiles);

    // Directory Browser
    elements.browseDir.addEventListener('click', openBrowser);
    elements.browserUp.addEventListener('click', browserGoUp);
    elements.browserSelect.addEventListener('click', selectBrowserPath);

    // Modal close buttons
    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', () => {
            btn.closest('.modal').classList.remove('active');
        });
    });

    // Click outside modal to close
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('active');
            }
        });
    });

    // File selection
    elements.selectAll.addEventListener('click', toggleSelectAll);
    elements.renameSelected.addEventListener('click', renameSelected);

    // Search
    elements.searchBtn.addEventListener('click', performSearch);
    elements.searchQuery.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') performSearch();
    });
}

// Toast notifications
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    elements.toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Toggle API key visibility
function toggleApiKeyVisibility() {
    const input = elements.tmdbApiKey;
    input.type = input.type === 'password' ? 'text' : 'password';
}

// Load config from server
async function loadConfig() {
    try {
        const response = await fetch('/api/config');
        const config = await response.json();
        elements.mediaDir.value = config.media_dir || '/media';
    } catch (error) {
        console.error('Failed to load config:', error);
    }
}

// Save settings
async function saveSettings() {
    const settings = {
        tmdb_api_key: elements.tmdbApiKey.value,
        media_dir: elements.mediaDir.value
    };

    try {
        const response = await fetch('/api/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(settings)
        });

        if (response.ok) {
            showToast('Settings saved', 'success');
        } else {
            const data = await response.json();
            showToast(data.error || 'Failed to save settings', 'error');
        }
    } catch (error) {
        showToast('Failed to save settings', 'error');
    }
}

// Scan files
async function scanFiles() {
    const directory = elements.mediaDir.value;
    const mode = elements.modeSelect.value;

    elements.filesList.innerHTML = '<div class="loading"><div class="spinner"></div>Scanning...</div>';
    elements.filesPanel.style.display = 'block';

    try {
        const response = await fetch('/api/scan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ directory, mode })
        });

        const data = await response.json();

        if (response.ok) {
            state.files = data.files;
            state.selectedFiles.clear();
            renderFiles();
            elements.fileCount.textContent = data.count;
            showToast(`Found ${data.count} files`, 'success');
        } else {
            elements.filesList.innerHTML = `<div class="empty-state"><h3>Error</h3><p>${data.error}</p></div>`;
            showToast(data.error, 'error');
        }
    } catch (error) {
        elements.filesList.innerHTML = '<div class="empty-state"><h3>Error</h3><p>Failed to scan directory</p></div>';
        showToast('Failed to scan directory', 'error');
    }
}

// Render files list
function renderFiles() {
    if (state.files.length === 0) {
        elements.filesList.innerHTML = '<div class="empty-state"><h3>No files found</h3><p>Try changing the mode or directory</p></div>';
        return;
    }

    elements.filesList.innerHTML = state.files.map((file, index) => {
        const isSelected = state.selectedFiles.has(index);
        const detectedInfo = getDetectedInfo(file);

        return `
            <div class="file-item ${isSelected ? 'selected' : ''} ${file.renamed ? 'renamed' : ''}" data-index="${index}">
                <input type="checkbox" class="file-checkbox" ${isSelected ? 'checked' : ''}>
                <div class="file-info">
                    <div class="file-name">${escapeHtml(file.filename)}</div>
                    <span class="file-type ${file.type}">${file.type}</span>
                    <div class="file-detected">${detectedInfo}</div>
                    ${file.newName ? `<div class="file-new-name">${escapeHtml(file.newName)}</div>` : ''}
                </div>
                <div class="file-actions">
                    <button class="btn btn-sm btn-primary" onclick="openSearch(${index})">Search</button>
                    ${file.newName ? `<button class="btn btn-sm btn-success" onclick="renameFile(${index})">Rename</button>` : ''}
                </div>
            </div>
        `;
    }).join('');

    // Add checkbox event listeners
    elements.filesList.querySelectorAll('.file-checkbox').forEach((checkbox, index) => {
        checkbox.addEventListener('change', () => toggleFileSelection(index));
    });
}

function getDetectedInfo(file) {
    if (!file.detected_info) return '';

    if (file.type === 'movie') {
        const year = file.detected_info.year ? ` (${file.detected_info.year})` : '';
        return `Detected: ${file.detected_info.name}${year}`;
    } else if (file.type === 'tv') {
        return `Detected: ${file.detected_info.show_name} S${file.detected_info.season}E${file.detected_info.episode}`;
    } else if (file.type === 'music') {
        return `Search: ${file.detected_info.query}`;
    }
    return '';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// File selection
function toggleFileSelection(index) {
    if (state.selectedFiles.has(index)) {
        state.selectedFiles.delete(index);
    } else {
        state.selectedFiles.add(index);
    }
    renderFiles();
}

function toggleSelectAll() {
    if (state.selectedFiles.size === state.files.length) {
        state.selectedFiles.clear();
    } else {
        state.files.forEach((_, index) => state.selectedFiles.add(index));
    }
    renderFiles();
}

// Directory Browser
function openBrowser() {
    state.browserPath = elements.mediaDir.value || '/';
    loadBrowserDirectory(state.browserPath);
    elements.browserModal.classList.add('active');
}

async function loadBrowserDirectory(path) {
    try {
        const response = await fetch(`/api/browse?path=${encodeURIComponent(path)}`);
        const data = await response.json();

        if (response.ok) {
            state.browserPath = data.current;
            elements.browserCurrentPath.textContent = data.current;
            elements.browserUp.disabled = !data.parent;

            elements.browserList.innerHTML = data.items.map(item => `
                <li data-path="${escapeHtml(item.path)}">
                    <span class="folder-icon"></span>
                    ${escapeHtml(item.name)}
                </li>
            `).join('');

            // Add click listeners
            elements.browserList.querySelectorAll('li').forEach(li => {
                li.addEventListener('click', () => {
                    elements.browserList.querySelectorAll('li').forEach(el => el.classList.remove('selected'));
                    li.classList.add('selected');
                });
                li.addEventListener('dblclick', () => {
                    loadBrowserDirectory(li.dataset.path);
                });
            });
        } else {
            showToast(data.error, 'error');
        }
    } catch (error) {
        showToast('Failed to browse directory', 'error');
    }
}

function browserGoUp() {
    const parent = state.browserPath.split('/').slice(0, -1).join('/') || '/';
    loadBrowserDirectory(parent);
}

function selectBrowserPath() {
    const selected = elements.browserList.querySelector('li.selected');
    if (selected) {
        elements.mediaDir.value = selected.dataset.path;
    } else {
        elements.mediaDir.value = state.browserPath;
    }
    elements.browserModal.classList.remove('active');
}

// Search functionality
function openSearch(index) {
    state.currentFile = index;
    const file = state.files[index];
    state.searchType = file.type;

    let title, query;
    if (file.type === 'movie') {
        title = 'Search Movies';
        query = file.detected_info?.name || '';
    } else if (file.type === 'tv') {
        title = 'Search TV Shows';
        query = file.detected_info?.show_name || '';
    } else {
        title = 'Search Music';
        query = file.detected_info?.query || '';
    }

    elements.searchModalTitle.textContent = title;
    elements.searchQuery.value = query;
    elements.searchResults.innerHTML = '';
    elements.searchModal.classList.add('active');
    elements.searchQuery.focus();
}

async function performSearch() {
    const query = elements.searchQuery.value.trim();
    if (!query) return;

    const file = state.files[state.currentFile];
    let endpoint;

    if (file.type === 'movie') {
        endpoint = '/api/search/movie';
    } else if (file.type === 'tv') {
        endpoint = '/api/search/tv';
    } else {
        endpoint = '/api/search/music';
    }

    elements.searchResults.innerHTML = '<div class="loading"><div class="spinner"></div>Searching...</div>';

    try {
        const body = { query };
        if (file.type === 'movie' && file.detected_info?.year) {
            body.year = file.detected_info.year;
        }

        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });

        const data = await response.json();

        if (response.ok) {
            renderSearchResults(data.results, file.type);
        } else {
            elements.searchResults.innerHTML = `<div class="empty-state">${data.error}</div>`;
            showToast(data.error, 'error');
        }
    } catch (error) {
        elements.searchResults.innerHTML = '<div class="empty-state">Search failed</div>';
        showToast('Search failed', 'error');
    }
}

function renderSearchResults(results, type) {
    if (results.length === 0) {
        elements.searchResults.innerHTML = '<div class="empty-state">No results found</div>';
        return;
    }

    elements.searchResults.innerHTML = results.map((result, index) => {
        let title, meta, overview;

        if (type === 'movie') {
            title = result.title;
            meta = `${result.year || 'Unknown year'} | Rating: ${result.vote_average}/10`;
            overview = result.overview;
        } else if (type === 'tv') {
            title = result.name;
            meta = `${result.year || 'Unknown year'} | Rating: ${result.vote_average}/10`;
            overview = result.overview;
        } else {
            title = result.title;
            meta = `${result.artist} | ${result.album} ${result.year ? `(${result.year})` : ''}`;
            overview = `Match score: ${result.score}%`;
        }

        return `
            <div class="search-result" data-index="${index}" onclick="selectSearchResult(${index}, ${JSON.stringify(result).replace(/"/g, '&quot;')})">
                <div class="search-result-title">${escapeHtml(title)}</div>
                <div class="search-result-meta">${escapeHtml(meta)}</div>
                <div class="search-result-overview">${escapeHtml(overview || '')}</div>
            </div>
        `;
    }).join('');
}

async function selectSearchResult(index, result) {
    const file = state.files[state.currentFile];

    // Highlight selection
    elements.searchResults.querySelectorAll('.search-result').forEach((el, i) => {
        el.classList.toggle('selected', i === index);
    });

    // Generate new filename
    let newName;
    let renameData = {
        type: file.type,
        filepath: file.filepath
    };

    if (file.type === 'movie') {
        renameData.title = result.title;
        renameData.year = result.year;
        newName = `${result.title} (${result.year}).${file.extension}`;
    } else if (file.type === 'tv') {
        // Get episode title
        try {
            const epResponse = await fetch('/api/search/tv/episode', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    show_id: result.id,
                    season: file.detected_info.season,
                    episode: file.detected_info.episode
                })
            });
            const epData = await epResponse.json();

            renameData.show_name = result.name;
            renameData.season = file.detected_info.season;
            renameData.episode = file.detected_info.episode;
            renameData.episode_title = epData.title || '';

            const season = String(parseInt(file.detected_info.season)).padStart(2, '0');
            const episode = String(parseInt(file.detected_info.episode)).padStart(2, '0');
            newName = epData.title
                ? `${result.name} - S${season}E${episode} - ${epData.title}.${file.extension}`
                : `${result.name} - S${season}E${episode}.${file.extension}`;
        } catch (error) {
            renameData.show_name = result.name;
            renameData.season = file.detected_info.season;
            renameData.episode = file.detected_info.episode;
            const season = String(parseInt(file.detected_info.season)).padStart(2, '0');
            const episode = String(parseInt(file.detected_info.episode)).padStart(2, '0');
            newName = `${result.name} - S${season}E${episode}.${file.extension}`;
        }
    } else {
        renameData.artist = result.artist;
        renameData.title = result.title;
        newName = `${result.artist} - ${result.title}.${file.extension}`;
    }

    // Update state
    state.files[state.currentFile].newName = newName;
    state.files[state.currentFile].renameData = renameData;
    state.selectedFiles.add(state.currentFile);

    // Close modal and re-render
    elements.searchModal.classList.remove('active');
    renderFiles();
    showToast('Selection applied. Click "Rename" to apply changes.', 'info');
}

// Rename files
async function renameFile(index) {
    const file = state.files[index];
    if (!file.renameData) {
        showToast('Please search and select a match first', 'warning');
        return;
    }

    const dryRun = elements.dryRun.checked;
    const data = { ...file.renameData, dry_run: dryRun };

    try {
        const response = await fetch('/api/rename', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (result.success) {
            file.renamed = true;
            file.filename = file.newName;
            file.filepath = result.new_path;
            renderFiles();
            showToast(dryRun ? `[Dry Run] Would rename to: ${result.new_filename}` : `Renamed successfully!`, 'success');
        } else {
            showToast(result.message || 'Rename failed', 'error');
        }
    } catch (error) {
        showToast('Rename failed', 'error');
    }
}

async function renameSelected() {
    if (state.selectedFiles.size === 0) {
        showToast('No files selected', 'warning');
        return;
    }

    const filesToRename = Array.from(state.selectedFiles)
        .map(index => state.files[index])
        .filter(file => file.renameData);

    if (filesToRename.length === 0) {
        showToast('Selected files have no matches. Search and select matches first.', 'warning');
        return;
    }

    const dryRun = elements.dryRun.checked;
    const files = filesToRename.map(file => ({
        ...file.renameData,
        filepath: file.filepath
    }));

    try {
        const response = await fetch('/api/batch/rename', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ files, dry_run: dryRun })
        });

        const result = await response.json();

        if (response.ok) {
            // Update state for successful renames
            result.results.forEach((res, idx) => {
                if (res.success) {
                    const file = filesToRename[idx];
                    file.renamed = true;
                    file.filename = res.new_filename;
                    if (res.new_path) file.filepath = res.new_path;
                }
            });

            renderFiles();
            const msg = dryRun
                ? `[Dry Run] Would rename ${result.success_count}/${result.total} files`
                : `Renamed ${result.success_count}/${result.total} files`;
            showToast(msg, result.success_count > 0 ? 'success' : 'warning');
        } else {
            showToast('Batch rename failed', 'error');
        }
    } catch (error) {
        showToast('Batch rename failed', 'error');
    }
}
