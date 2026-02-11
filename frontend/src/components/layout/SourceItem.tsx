import { FileText, Link as LinkIcon, Search, CheckCircle2, Loader2, XCircle } from 'lucide-react';
import { clsx } from 'clsx';

export interface Source {
    id: string;
    title: string;
    type: 'file' | 'url' | 'search';
    content?: string;
    status: 'pending' | 'processing' | 'completed' | 'error';
    error?: string;
}

interface SourceItemProps {
    source: Source;
    onClick?: () => void;
}

export function SourceItem({ source, onClick }: SourceItemProps) {
    const Icon = source.type === 'file' ? FileText : source.type === 'url' ? LinkIcon : Search;

    return (
        <div
            onClick={onClick}
            className={clsx(
                "flex items-center gap-3 p-3 rounded-lg border transition-all cursor-pointer group",
                "bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700",
                "hover:border-primary-400 dark:hover:border-primary-500",
                source.status === 'processing' && "opacity-80"
            )}
        >
            <div className={clsx(
                "p-2 rounded-md",
                source.type === 'file' && "bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400",
                source.type === 'url' && "bg-purple-100 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400",
                source.type === 'search' && "bg-orange-100 text-orange-600 dark:bg-orange-900/30 dark:text-orange-400",
            )}>
                <Icon className="w-4 h-4" />
            </div>

            <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                    {source.title}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400 truncate capitalize">
                    {source.type} • {source.status}
                </p>
            </div>

            {source.status === 'completed' && <CheckCircle2 className="w-4 h-4 text-green-500" />}
            {source.status === 'processing' && <Loader2 className="w-4 h-4 text-primary-500 animate-spin" />}
            {source.status === 'error' && <XCircle className="w-4 h-4 text-red-500" />}
        </div>
    );
}
