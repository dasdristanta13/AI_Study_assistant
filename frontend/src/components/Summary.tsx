
import ReactMarkdown from 'react-markdown';
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card';

interface SummaryProps {
    summary: string;
    keyPoints: string[];
}

export function Summary({ summary, keyPoints }: SummaryProps) {
    return (
        <div className="space-y-6">
            <Card>
                <CardHeader>
                    <CardTitle className="text-xl">📝 Summary</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="prose dark:prose-invert max-w-none text-gray-700 dark:text-gray-300">
                        <ReactMarkdown>{summary}</ReactMarkdown>
                    </div>
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle className="text-xl">🎯 Key Points</CardTitle>
                </CardHeader>
                <CardContent>
                    <ul className="space-y-2">
                        {keyPoints.map((point, index) => (
                            <li key={index} className="flex items-start gap-3">
                                <span className="flex-shrink-0 flex items-center justify-center w-6 h-6 rounded-full bg-primary-100 text-primary-700 text-xs font-bold mt-0.5">
                                    {index + 1}
                                </span>
                                <span className="text-gray-700 dark:text-gray-300">{point}</span>
                            </li>
                        ))}
                    </ul>
                </CardContent>
            </Card>
        </div>
    );
}
