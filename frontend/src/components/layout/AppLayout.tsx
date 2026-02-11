import type { ReactNode } from 'react';
import { Sidebar } from './Sidebar';
import type { Source } from './SourceItem';

interface AppLayoutProps {
    children: ReactNode;
    sources: Source[];
    onAddSource: (type: 'file' | 'url' | 'search', data: string | File) => void;
}

export function AppLayout({ children, sources, onAddSource }: AppLayoutProps) {
    return (
        <div className="flex h-screen overflow-hidden bg-white dark:bg-gray-950">
            {/* Sidebar - Fixed width */}
            <div className="w-80 flex-shrink-0 h-full">
                <Sidebar sources={sources} onAddSource={onAddSource} />
            </div>

            {/* Main Content - Flexible */}
            <div className="flex-1 h-full overflow-hidden flex flex-col">
                <header className="h-16 border-b border-gray-200 dark:border-gray-800 flex items-center px-8 bg-white/50 backdrop-blur-sm z-10">
                    <h1 className="text-xl font-bold bg-gradient-to-r from-primary-600 to-purple-600 bg-clip-text text-transparent">
                        Studio
                    </h1>
                </header>

                <main className="flex-1 overflow-y-auto p-8">
                    <div className="max-w-4xl mx-auto">
                        {children}
                    </div>
                </main>
            </div>
        </div>
    );
}
