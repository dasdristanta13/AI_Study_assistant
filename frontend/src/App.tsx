import { useState } from 'react';
import axios from 'axios';
import { BookOpen, Search, Upload, Link as LinkIcon, FileText, Loader2, AlertCircle } from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import { clsx } from 'clsx';
import { Button } from './components/ui/Button';
import { Input } from './components/ui/Input';
import { Card } from './components/ui/Card';
import { Quiz } from './components/Quiz.tsx'; // Explicit extensions for clarity if needed, mostly .tsx implied
import { Summary } from './components/Summary';

// Types (mirroring backend)
interface QuizQuestion {
  question: string;
  options: string[];
  correct_answer: string;
  explanation: string;
  difficulty: string;
}

interface StudyResponse {
  summary: string;
  key_points: string[];
  quiz: QuizQuestion[];
  messages: string[];
  error?: string;
}

type InputType = 'text' | 'url' | 'search' | 'file';

function App() {
  const [activeTab, setActiveTab] = useState<InputType>('text');
  const [inputText, setInputText] = useState('');
  const [numQuestions, setNumQuestions] = useState(5);
  const [difficulty, setDifficulty] = useState('mixed');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<StudyResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // File Upload Logic
  const onDrop = async (acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      handleProcess('file', acceptedFiles[0]);
    }
  };
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    maxFiles: 1,
    accept: {
      'text/plain': ['.txt', '.md'],
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    }
  });

  const handleProcess = async (type: InputType, data: string | File) => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      let response;

      if (type === 'file' && data instanceof File) {
        const formData = new FormData();
        formData.append('file', data);
        formData.append('num_questions', numQuestions.toString());
        formData.append('difficulty', difficulty);

        response = await axios.post<StudyResponse>('/api/process_file', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
      } else {
        response = await axios.post<StudyResponse>('/api/process', {
          input_type: type,
          input_data: data,
          num_questions: numQuestions,
          difficulty: difficulty
        });
      }

      setResult(response.data);
      if (response.data.error) {
        setError(response.data.error);
      }
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || 'An error occurred while processing your request.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 font-sans pb-20">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2 text-primary-600">
            <BookOpen className="w-6 h-6" />
            <span className="text-xl font-bold tracking-tight">AI Study Assistant</span>
          </div>
          <a
            href="https://github.com/yourusername/ai-study-assistant"
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm font-medium text-gray-500 hover:text-gray-900 transition-colors"
          >
            GitHub
          </a>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-8 space-y-8">
        {/* Intro */}
        <section className="text-center space-y-4 max-w-2xl mx-auto">
          <h1 className="text-4xl font-extrabold tracking-tight text-gray-900 sm:text-5xl">
            Master any topic with AI
          </h1>
          <p className="text-lg text-gray-600">
            Turn your study materials into concise summaries, key points, and interactive quizzes in seconds.
          </p>
        </section>

        {/* Input Card */}
        <Card className="max-w-3xl mx-auto shadow-lg border-0 ring-1 ring-gray-200">
          {/* Tabs */}
          <div className="flex border-b border-gray-100">
            {[
              { id: 'text', label: 'Paste Text', icon: FileText },
              { id: 'file', label: 'Upload File', icon: Upload },
              { id: 'url', label: 'URL', icon: LinkIcon },
              { id: 'search', label: 'Web Search', icon: Search },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as InputType)}
                className={clsx(
                  "flex-1 flex items-center justify-center gap-2 py-4 text-sm font-medium transition-all relative",
                  activeTab === tab.id
                    ? "text-primary-600 bg-primary-50/50"
                    : "text-gray-500 hover:text-gray-700 hover:bg-gray-50"
                )}
              >
                <tab.icon className="w-4 h-4" />
                {tab.label}
                {activeTab === tab.id && (
                  <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-600" />
                )}
              </button>
            ))}
          </div>

          <div className="p-6 space-y-6">
            {/* Tab Content */}
            <div className="min-h-[150px]">
              {activeTab === 'text' && (
                <textarea
                  className="w-full h-40 p-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
                  placeholder="Paste your study notes, article, or text here..."
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                />
              )}

              {activeTab === 'file' && (
                <div
                  {...getRootProps()}
                  className={clsx(
                    "h-40 border-2 border-dashed rounded-xl flex flex-col items-center justify-center text-center cursor-pointer transition-colors",
                    isDragActive ? "border-primary-500 bg-primary-50" : "border-gray-300 hover:border-primary-400 hover:bg-gray-50"
                  )}
                >
                  <input {...getInputProps()} />
                  <Upload className="w-8 h-8 text-gray-400 mb-3" />
                  <p className="text-sm font-medium text-gray-700">
                    {isDragActive ? "Drop the file here" : "Click or drag file to upload"}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">PDF, DOCX, TXT, MD (Max 10MB)</p>
                </div>
              )}

              {activeTab === 'url' && (
                <div className="flex flex-col justify-center h-40">
                  <Input
                    placeholder="https://example.com/article"
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    className="h-12"
                  />
                  <p className="text-sm text-gray-500 mt-2 text-center">
                    Enter a URL to extract content and generate a study guide.
                  </p>
                </div>
              )}

              {activeTab === 'search' && (
                <div className="flex flex-col justify-center h-40">
                  <Input
                    placeholder="e.g., Photosynthesis process"
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    className="h-12"
                  />
                  <p className="text-sm text-gray-500 mt-2 text-center">
                    We'll search the web and create a study guide from the top results.
                  </p>
                </div>
              )}
            </div>

            {/* Settings & Action */}
            <div className="flex flex-col sm:flex-row gap-4 items-center justify-between pt-4 border-t border-gray-100">
              <div className="flex gap-4 w-full sm:w-auto">
                <div className="flex-1 sm:w-32">
                  <label className="block text-xs font-semibold text-gray-500 uppercase mb-1">Questions</label>
                  <select
                    value={numQuestions}
                    onChange={(e) => setNumQuestions(Number(e.target.value))}
                    className="w-full text-sm rounded-md border-gray-300 focus:border-primary-500 focus:ring-primary-500"
                  >
                    {[3, 5, 10, 15].map(n => <option key={n} value={n}>{n}</option>)}
                  </select>
                </div>
                <div className="flex-1 sm:w-32">
                  <label className="block text-xs font-semibold text-gray-500 uppercase mb-1">Difficulty</label>
                  <select
                    value={difficulty}
                    onChange={(e) => setDifficulty(e.target.value)}
                    className="w-full text-sm rounded-md border-gray-300 focus:border-primary-500 focus:ring-primary-500 capitalize"
                  >
                    {['easy', 'medium', 'hard', 'mixed'].map(d => <option key={d} value={d}>{d}</option>)}
                  </select>
                </div>
              </div>

              <div className="w-full sm:w-auto">
                {/* Spacer or empty label to align button */}
                <label className="block text-xs font-semibold text-transparent uppercase mb-1 hidden sm:block">Action</label>
                <Button
                  onClick={() => handleProcess(activeTab, inputText)}
                  disabled={isLoading || (activeTab !== 'file' && !inputText.trim())}
                  className="w-full sm:w-auto min-w-[120px]"
                  size="lg"
                >
                  {isLoading ? 'Processing...' : 'Generate Study Guide'}
                </Button>
              </div>
            </div>
          </div>
        </Card>

        {/* Error Message */}
        {error && (
          <div className="p-4 rounded-lg bg-red-50 border border-red-200 text-red-700 flex items-center gap-3 animate-fade-in">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <p>{error}</p>
          </div>
        )}

        {/* Results */}
        {result && (
          <div className="grid md:grid-cols-2 gap-8 animate-slide-up">
            <div className="space-y-8">
              <Summary summary={result.summary} keyPoints={result.key_points} />
            </div>
            <div>
              <Quiz questions={result.quiz} />
            </div>
          </div>
        )}

        {/* Loading State Skeleton (Optional Improvement) */}
        {isLoading && !result && (
          <div className="max-w-3xl mx-auto text-center py-12 text-gray-500 animate-pulse">
            <Loader2 className="w-8 h-8 mx-auto mb-4 animate-spin text-primary-500" />
            <p>Analyzing content and generating your study plan...</p>
            <p className="text-xs mt-2">This usually takes 10-20 seconds.</p>
          </div>
        )}

      </main>
    </div>
  );
}

export default App;
