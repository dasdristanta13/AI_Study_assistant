import { useState } from 'react';
import axios from 'axios';
import { Loader2, AlertCircle, Sparkles } from 'lucide-react';
import { Quiz } from './components/Quiz.tsx';
import { Summary } from './components/Summary';
import { AppLayout } from './components/layout/AppLayout';
import type { Source } from './components/layout/SourceItem';

// Types (mirroring backend)
interface QuizQuestion {
  question: string;
  options: string[];
  correct_answer: string;
  explanation: string;
  difficulty: string;
}

interface SourceModel {
  title: string;
  type: string;
  content?: string;
}

interface StudyResponse {
  summary: string;
  key_points: string[];
  quiz: QuizQuestion[];
  sources: SourceModel[];
  messages: string[];
  error?: string;
}

function App() {
  const [sources, setSources] = useState<Source[]>([]);
  const [activeResult, setActiveResult] = useState<StudyResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAddSource = async (type: 'file' | 'url' | 'search', data: string | File) => {
    setIsLoading(true);
    setError(null);

    // Create a temporary source ID
    const tempId = Date.now().toString();
    const newSource: Source = {
      id: tempId,
      title: type === 'file' ? (data as File).name : (data as string),
      type,
      status: 'processing'
    };

    setSources(prev => [...prev, newSource]);

    try {
      let response;

      if (type === 'file' && data instanceof File) {
        const formData = new FormData();
        formData.append('file', data);
        formData.append('num_questions', '5');
        formData.append('difficulty', 'mixed');

        response = await axios.post<StudyResponse>('/api/process_file', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
      } else {
        response = await axios.post<StudyResponse>('/api/process', {
          input_type: type,
          input_data: data,
          num_questions: 5,
          difficulty: 'mixed'
        });
      }

      const result = response.data;

      // Update source status
      setSources(prev => prev.map(s =>
        s.id === tempId
          ? {
            ...s,
            status: 'completed',
            // Use title from backend if available (e.g. for search queries that return titles)
            // but for now keep input as title or update if sources list has info
          }
          : s
      ));

      setActiveResult(result);

      if (result.error) {
        setError(result.error);
        setSources(prev => prev.map(s => s.id === tempId ? { ...s, status: 'error', error: result.error } : s));
      }

    } catch (err: any) {
      console.error(err);
      const errorMsg = err.response?.data?.detail || 'An error occurred processing the source.';
      setError(errorMsg);
      setSources(prev => prev.map(s => s.id === tempId ? { ...s, status: 'error', error: errorMsg } : s));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AppLayout sources={sources} onAddSource={handleAddSource}>

      {/* Empty State */}
      {!activeResult && !isLoading && (
        <div className="flex flex-col items-center justify-center h-[50vh] text-center space-y-6">
          <div className="p-6 bg-primary-50 rounded-full animate-pulse">
            <Sparkles className="w-12 h-12 text-primary-500" />
          </div>
          <div className="max-w-md">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              Ready to study?
            </h2>
            <p className="text-gray-500 dark:text-gray-400">
              Add a topic (we'll search the web), paste a URL, or upload a document to generate a study guide.
            </p>
          </div>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="flex flex-col items-center justify-center py-12 space-y-4 animate-fade-in">
          <Loader2 className="w-8 h-8 text-primary-500 animate-spin" />
          <p className="text-gray-500 font-medium">Analyzing source and generating study material...</p>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="p-4 mb-6 rounded-lg bg-red-50 border border-red-200 text-red-700 flex items-center gap-3 animate-fade-in">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <p>{error}</p>
        </div>
      )}

      {/* Results View */}
      {activeResult && !isLoading && (
        <div className="space-y-8 animate-slide-up pb-20">
          <div className="grid md:grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="space-y-8">
              <Summary
                summary={activeResult.summary}
                keyPoints={activeResult.key_points}
              />
            </div>
            <div className="space-y-8">
              <Quiz questions={activeResult.quiz} />
            </div>
          </div>
        </div>
      )}

    </AppLayout>
  );
}

export default App;
