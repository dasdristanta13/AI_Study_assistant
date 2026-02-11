import { useState } from 'react';
import { Plus, Search, Link as LinkIcon, Upload, X } from 'lucide-react';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { SourceItem } from './SourceItem';
import type { Source } from './SourceItem';
import { useDropzone } from 'react-dropzone';
import { clsx } from 'clsx';

interface SidebarProps {
    sources: Source[];
    onAddSource: (type: 'file' | 'url' | 'search', data: string | File) => void;
    className?: string;
}

export function Sidebar({ sources, onAddSource, className }: SidebarProps) {
    const [isAdding, setIsAdding] = useState(false);
    const [addType, setAddType] = useState<'url' | 'search' | null>(null);
    const [inputValue, setInputValue] = useState('');

    const { getInputProps, open: openFileSelect } = useDropzone({
        onDrop: (acceptedFiles) => {
            if (acceptedFiles.length > 0) {
                onAddSource('file', acceptedFiles[0]);
                setIsAdding(false);
            }
        },
        maxFiles: 1,
        noClick: true,
        noKeyboard: true
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (inputValue.trim() && addType) {
            onAddSource(addType, inputValue);
            setInputValue('');
            setAddType(null);
            setIsAdding(false);
        }
    };

    return (
        <div className={clsx("flex flex-col h-full bg-gray-50 dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800", className)}>
            {/* Header */}
            <div className="p-4 border-b border-gray-200 dark:border-gray-800">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                    <span className="text-xl">📚</span> Notebook
                </h2>
            </div>

            {/* Sources List */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
                <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Sources</h3>

                {sources.length === 0 && (
                    <div className="text-center p-6 border-2 border-dashed border-gray-200 rounded-xl">
                        <p className="text-sm text-gray-500 mb-2">No sources yet</p>
                        <p className="text-xs text-gray-400">Add a topic, URL, or file to get started.</p>
                    </div>
                )}

                {sources.map(source => (
                    <SourceItem key={source.id} source={source} />
                ))}
            </div>

            {/* Add Source Area */}
            <div className="p-4 border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900">
                {!isAdding ? (
                    <Button
                        className="w-full justify-start gap-2"
                        variant="secondary"
                        onClick={() => setIsAdding(true)}
                    >
                        <Plus className="w-4 h-4" /> Add Source
                    </Button>
                ) : (
                    <div className="space-y-3 animate-slide-up">
                        <div className="flex items-center justify-between">
                            <span className="text-sm font-medium">Add to Notebook</span>
                            <button onClick={() => { setIsAdding(false); setAddType(null); }} className="text-gray-400 hover:text-gray-600">
                                <X className="w-4 h-4" />
                            </button>
                        </div>

                        {!addType ? (
                            <div className="grid grid-cols-3 gap-2">
                                <button
                                    onClick={() => setAddType('search')}
                                    className="flex flex-col items-center gap-2 p-3 rounded-lg border hover:bg-gray-50 text-xs font-medium"
                                >
                                    <Search className="w-5 h-5 text-orange-500" /> Topic
                                </button>
                                <button
                                    onClick={() => setAddType('url')}
                                    className="flex flex-col items-center gap-2 p-3 rounded-lg border hover:bg-gray-50 text-xs font-medium"
                                >
                                    <LinkIcon className="w-5 h-5 text-purple-500" /> URL
                                </button>
                                <button
                                    onClick={openFileSelect}
                                    className="flex flex-col items-center gap-2 p-3 rounded-lg border hover:bg-gray-50 text-xs font-medium"
                                >
                                    <Upload className="w-5 h-5 text-blue-500" /> File
                                </button>
                                <input {...getInputProps()} />
                            </div>
                        ) : (
                            <form onSubmit={handleSubmit} className="space-y-2">
                                <Input
                                    autoFocus
                                    placeholder={addType === 'search' ? "Enter topic (e.g. 'Photosynthesis')" : "Paste URL..."}
                                    value={inputValue}
                                    onChange={(e) => setInputValue(e.target.value)}
                                />
                                <Button type="submit" className="w-full" disabled={!inputValue.trim()}>
                                    Add Source
                                </Button>
                            </form>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
