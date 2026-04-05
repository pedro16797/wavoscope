import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useStore } from '../store/useStore';
import { X, Plus, Trash2, Edit2, Music, Check, ChevronRight, FileAudio } from 'lucide-react';

interface PlaylistDialogProps {
    onClose: () => void;
}

export const PlaylistDialog: React.FC<PlaylistDialogProps> = ({ onClose }) => {
    const { t } = useTranslation();
    const {
        playlists, activePlaylistId, activeItemId, fetchPlaylists,
        createPlaylist, updatePlaylist, deletePlaylist,
        addItemToPlaylist, removeItemFromPlaylist, selectPlaylistItem, loadPlaylistItem,
        currentTheme, themes, ui_scale
    } = useStore();

    const theme = themes[currentTheme] || {};
    const [newPlaylistName, setNewPlaylistName] = useState('');
    const [editingPlaylistId, setEditingPlaylistId] = useState<string | null>(null);
    const [editName, setEditName] = useState('');
    const [selectedId, setSelectedId] = useState<string | null>(activePlaylistId);

    useEffect(() => {
        fetchPlaylists();
    }, []);

    const handleCreate = () => {
        if (newPlaylistName.trim()) {
            createPlaylist(newPlaylistName.trim());
            setNewPlaylistName('');
        }
    };

    const handleEditSave = (id: string) => {
        if (editName.trim()) {
            updatePlaylist(id, editName.trim());
            setEditingPlaylistId(null);
        }
    };

    const handleAddItem = async (plId: string) => {
        const pywindow = window as any;
        if (pywindow.pywebview?.api?.browse) {
            // This is a bit tricky since browse() doesn't return the path directly to JS
            // but opens it in the project. We might need a separate 'browse_file' that returns the path.
            // For now, let's assume browse_file_path exists or we add it to the API.
            if (pywindow.pywebview.api.browse_file_path) {
                const path = await pywindow.pywebview.api.browse_file_path();
                if (path) {
                    addItemToPlaylist(plId, path);
                }
            } else {
                alert("File browsing for playlists is only supported in the desktop app.");
            }
        }
    };

    const currentPlaylist = playlists.find(p => p.id === selectedId);

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
            <div className="bg-surface rounded-[var(--ui-radius)] border-[width:var(--ui-border)] border-white/10 shadow-2xl flex flex-col max-h-[80vh] w-full max-w-4xl overflow-hidden"
                 style={{ color: theme.text }}>

                {/* Header */}
                <div className="p-4 border-b border-white/5 flex items-center justify-between bg-white/5">
                    <div className="flex items-center gap-2">
                        <Music size={20 * ui_scale} className="text-accent" />
                        <h2 className="text-lg font-bold">{t('playlist.title')}</h2>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-full transition-colors">
                        <X size={20 * ui_scale} />
                    </button>
                </div>

                <div className="flex-1 flex min-h-0">
                    {/* Left Sidebar: Playlist List */}
                    <div className="w-1/3 border-r border-white/5 flex flex-col bg-white/5">
                        <div className="p-3 border-b border-white/5">
                            <div className="flex gap-2">
                                <input
                                    type="text"
                                    value={newPlaylistName}
                                    onChange={(e) => setNewPlaylistName(e.target.value)}
                                    placeholder={t('playlist.new_placeholder')}
                                    className="flex-1 bg-black/20 border border-white/10 rounded px-2 py-1 text-xs outline-none focus:border-accent"
                                    onKeyDown={(e) => e.key === 'Enter' && handleCreate()}
                                />
                                <button
                                    onClick={handleCreate}
                                    disabled={!newPlaylistName.trim()}
                                    className={`p-1 bg-accent text-surface rounded transition-opacity ${!newPlaylistName.trim() ? 'opacity-30 cursor-not-allowed' : 'hover:opacity-80'}`}>
                                    <Plus size={16 * ui_scale} />
                                </button>
                            </div>
                        </div>
                        <div className="flex-1 overflow-y-auto p-2 space-y-1">
                            {playlists.map(pl => (
                                <div key={pl.id}
                                     onClick={() => setSelectedId(pl.id)}
                                     className={`group flex items-center justify-between p-2 rounded cursor-pointer transition-colors ${selectedId === pl.id ? 'bg-accent/20 text-accent' : 'hover:bg-white/5'}`}>

                                    <div className="flex-1 min-w-0">
                                        {editingPlaylistId === pl.id ? (
                                            <input
                                                autoFocus
                                                value={editName}
                                                onChange={(e) => setEditName(e.target.value)}
                                                onBlur={() => handleEditSave(pl.id)}
                                                onKeyDown={(e) => e.key === 'Enter' && handleEditSave(pl.id)}
                                                className="bg-black/40 text-xs px-1 rounded w-full outline-none border border-accent"
                                            />
                                        ) : (
                                            <div className="text-xs font-medium truncate">{pl.name}</div>
                                        )}
                                    </div>

                                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0">
                                        <button onClick={(e) => { e.stopPropagation(); setEditingPlaylistId(pl.id); setEditName(pl.name); }} className="p-1 hover:text-white">
                                            <Edit2 size={12 * ui_scale} />
                                        </button>
                                        <button onClick={(e) => { e.stopPropagation(); deletePlaylist(pl.id); }} className="p-1 hover:text-red-400">
                                            <Trash2 size={12 * ui_scale} />
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Right Content: Playlist Items */}
                    <div className="flex-1 flex flex-col bg-black/10 min-w-0">
                        {currentPlaylist ? (
                            <>
                                <div className="p-4 border-b border-white/5 flex items-center justify-between gap-4">
                                    <h3 className="font-bold text-sm truncate min-w-0">{currentPlaylist.name}</h3>
                                    <button onClick={() => handleAddItem(currentPlaylist.id)} className="flex items-center gap-1 px-3 py-1 bg-accent/10 text-accent rounded hover:bg-accent/20 transition-colors text-xs flex-shrink-0">
                                        <Plus size={14 * ui_scale} />
                                        {t('playlist.add_song')}
                                    </button>
                                </div>
                                <div className="flex-1 overflow-y-auto p-2 space-y-1">
                                    {currentPlaylist.items.length === 0 ? (
                                        <div className="h-full flex flex-col items-center justify-center opacity-30 text-xs gap-2">
                                            <FileAudio size={48 * ui_scale} />
                                            {t('playlist.empty')}
                                        </div>
                                    ) : (
                                        currentPlaylist.items.map((item, idx) => (
                                            <div key={item.id}
                                                 className={`group flex items-center gap-3 p-2 rounded hover:bg-white/5 transition-colors ${activeItemId === item.id ? 'border-l-2 border-accent bg-accent/5' : ''}`}>
                                                <div className="text-[10px] opacity-40 w-4 text-right">{idx + 1}</div>
                                                <div className="flex-1 min-w-0">
                                                    <div className={`text-xs font-medium truncate ${!item.exists ? 'text-red-400 line-through opacity-60' : ''}`}>
                                                        {item.name}
                                                    </div>
                                                    <div className="text-[10px] opacity-40 truncate">{item.path}</div>
                                                </div>
                                                <div className="flex items-center gap-2 flex-shrink-0">
                                                    {item.exists ? (
                                                        <button
                                                            onClick={() => {
                                                                selectPlaylistItem(currentPlaylist.id, item.id);
                                                                loadPlaylistItem(item);
                                                            }}
                                                            className={`p-1.5 rounded transition-colors ${activeItemId === item.id ? 'bg-accent text-surface' : 'bg-white/5 hover:bg-accent/20 hover:text-accent'}`}>
                                                            {activeItemId === item.id ? <Check size={14 * ui_scale} /> : <ChevronRight size={14 * ui_scale} />}
                                                        </button>
                                                    ) : (
                                                        <span className="text-[10px] text-red-400 font-bold px-2 uppercase">{t('playlist.not_found')}</span>
                                                    )}
                                                    <button onClick={() => removeItemFromPlaylist(currentPlaylist.id, item.id)} className="p-1.5 bg-white/5 hover:bg-red-500/20 hover:text-red-400 rounded transition-colors opacity-0 group-hover:opacity-100">
                                                        <Trash2 size={14 * ui_scale} />
                                                    </button>
                                                </div>
                                            </div>
                                        ))
                                    )}
                                </div>
                            </>
                        ) : (
                            <div className="flex-1 flex flex-col items-center justify-center opacity-30 text-xs gap-3">
                                <Music size={64 * ui_scale} />
                                {t('playlist.select_prompt')}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};
