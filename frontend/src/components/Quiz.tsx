import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card';
import { CheckCircle2, XCircle } from 'lucide-react';
import { clsx } from 'clsx';

interface QuizQuestion {
    question: string;
    options: string[];
    correct_answer: string;
    explanation: string;
    difficulty: string;
}

interface QuizProps {
    questions: QuizQuestion[];
}

export function Quiz({ questions }: QuizProps) {
    const [userAnswers, setUserAnswers] = useState<Record<number, string>>({});
    const [showExplanation, setShowExplanation] = useState<Record<number, boolean>>({});

    if (!questions || questions.length === 0) {
        return null;
    }

    const handleOptionSelect = (questionIndex: number, optionLabel: string) => {
        if (userAnswers[questionIndex]) return; // Prevent changing answer

        setUserAnswers(prev => ({
            ...prev,
            [questionIndex]: optionLabel
        }));
        setShowExplanation(prev => ({
            ...prev,
            [questionIndex]: true
        }));
    };

    const getOptionLabel = (index: number) => String.fromCharCode(65 + index); // A, B, C, D

    return (
        <div className="space-y-6">
            <h2 className="text-2xl font-bold">📚 Quiz</h2>

            {questions.map((q, qIndex) => (
                <Card key={qIndex} className="overflow-hidden">
                    <CardHeader className="bg-gray-50 dark:bg-gray-900/50">
                        <div className="flex justify-between items-start gap-4">
                            <CardTitle className="text-lg font-medium">
                                {qIndex + 1}. {q.question}
                            </CardTitle>
                            <span className={clsx(
                                "px-2 py-1 text-xs rounded-full font-medium capitalize",
                                {
                                    'bg-green-100 text-green-700': q.difficulty === 'easy',
                                    'bg-yellow-100 text-yellow-700': q.difficulty === 'medium',
                                    'bg-red-100 text-red-700': q.difficulty === 'hard',
                                }
                            )}>
                                {q.difficulty}
                            </span>
                        </div>
                    </CardHeader>
                    <CardContent className="pt-6 grid gap-3">
                        {q.options.map((option, oIndex) => {
                            const label = getOptionLabel(oIndex);
                            const isSelected = userAnswers[qIndex] === label;
                            const isCorrect = q.correct_answer === label;
                            const isWrong = isSelected && !isCorrect;
                            const showResult = !!userAnswers[qIndex];

                            return (
                                <button
                                    key={oIndex}
                                    onClick={() => handleOptionSelect(qIndex, label)}
                                    disabled={showResult}
                                    className={clsx(
                                        "w-full text-left p-3 rounded-lg border transition-all flex items-center justify-between",
                                        {
                                            'hover:bg-gray-50 border-gray-200': !showResult,
                                            'bg-green-50 border-green-200 text-green-800': showResult && isCorrect,
                                            'bg-red-50 border-red-200 text-red-800': showResult && isWrong,
                                            'opacity-50 border-gray-100': showResult && !isCorrect && !isWrong
                                        }
                                    )}
                                >
                                    <div className="flex items-center gap-3">
                                        <span className={clsx(
                                            "flex items-center justify-center w-6 h-6 rounded-full text-xs font-bold border",
                                            {
                                                'bg-white border-gray-300 text-gray-500': !showResult,
                                                'bg-green-100 border-green-300 text-green-700': showResult && isCorrect,
                                                'bg-red-100 border-red-300 text-red-700': showResult && isWrong,
                                            }
                                        )}>
                                            {label}
                                        </span>
                                        <span>{option}</span>
                                    </div>

                                    {showResult && isCorrect && <CheckCircle2 className="w-5 h-5 text-green-600" />}
                                    {showResult && isWrong && <XCircle className="w-5 h-5 text-red-600" />}
                                </button>
                            );
                        })}

                        {showExplanation[qIndex] && (
                            <div className="mt-4 p-4 bg-blue-50 text-blue-900 rounded-lg text-sm animate-fade-in">
                                <p className="font-semibold mb-1">Explanation:</p>
                                {q.explanation}
                            </div>
                        )}
                    </CardContent>
                </Card>
            ))}
        </div>
    );
}
