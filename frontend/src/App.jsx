import { useState } from 'react';
import {
  Moon,
  Sun,
  Copy,
  AlertCircle,
  CheckCircle,
  RefreshCw,
  Sparkles,
  PenLine,
  Zap,
  Globe2,
  Clock3,
} from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const CONTENT_TYPES = ['blog post', 'article', 'essay', 'social media post', 'product description', 'marketing copy'];
const TONES = ['Professional', 'Friendly', 'Informative', 'Persuasive', 'Creative', 'Casual'];
const LENGTHS = ['Short', 'Medium', 'Long'];

const FEATURES = [
  { icon: PenLine, label: '6 Content Types', desc: 'Blogs, articles, essays, social posts, product descriptions, and marketing copy' },
  { icon: Zap, label: 'AI Powered', desc: 'Powered by Qwen2.5-0.5B-Instruct for fast, high-quality generation' },
  { icon: Globe2, label: 'Global Ready', desc: 'Works on any device with a responsive, themeable interface' },
  { icon: Clock3, label: 'Fast Generation', desc: 'Get your content in seconds with optimized model loading' },
];

function App() {
  const [theme, setTheme] = useState('light');
  const [topic, setTopic] = useState('');
  const [contentType, setContentType] = useState('blog post');
  const [tone, setTone] = useState('Professional');
  const [length, setLength] = useState('Medium');
  const [temperature, setTemperature] = useState(0.7);
  const [generatedContent, setGeneratedContent] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const toggleTheme = () => {
    setTheme(theme === 'light' ? 'dark' : 'light');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!topic.trim()) {
      setError('Please enter a topic');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic,
          content_type: contentType,
          tone,
          length,
          temperature,
        }),
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();
      setGeneratedContent(data.content);
    } catch (err) {
      setError(err.message || 'Failed to generate content');
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = async () => {
    if (!generatedContent) return;
    await navigator.clipboard.writeText(generatedContent);
  };

  const resetForm = () => {
    setGeneratedContent('');
    setError(null);
    setTopic('');
    setContentType('blog post');
    setTone('Professional');
    setLength('Medium');
    setTemperature(0.7);
  };

  if (theme === 'dark') {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50/50 to-gray-50 dark:from-gray-900 dark:via-gray-900 dark:to-gray-900">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <header className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">AI Content Writer</h1>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Create engaging content with the power of Qwen AI</p>
          </div>
          <button
            onClick={toggleTheme}
            className="p-3 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors shadow-soft"
            aria-label="Toggle theme"
          >
            {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
          </button>
        </header>

        <div className="mb-10">
          <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-blue-600 via-blue-500 to-indigo-500 p-8 text-white shadow-soft-lg">
            <div className="absolute -right-16 -top-16 h-48 w-48 rounded-full bg-white/10 blur-2xl"></div>
            <div className="absolute -bottom-24 -left-8 h-56 w-56 rounded-full bg-white/10 blur-2xl"></div>
            <div className="relative">
              <div className="mb-3 inline-flex items-center gap-2 rounded-full bg-white/20 px-4 py-1.5 text-sm font-medium">
                <Sparkles size={16} />
                Powered by Qwen2.5-0.5B-Instruct
              </div>
              <h2 className="text-2xl font-bold mb-2">Write Better Content, Faster</h2>
              <p className="text-blue-100 text-sm max-w-lg">
                Generate professional-quality content in seconds. Customize tone, length, and creativity to match your exact needs.
              </p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {FEATURES.map(({ icon: FeatureIcon, label, desc }) => (
            <div key={label} className="card p-4">
              <FeatureIcon size={22} className="text-blue-600 dark:text-blue-400 mb-3" />
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-1">{label}</h3>
              <p className="text-xs text-gray-500 dark:text-gray-400 leading-relaxed">{desc}</p>
            </div>
          ))}
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="card-gradient">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-3 rounded-lg bg-blue-600/10 text-blue-600 dark:text-blue-400">
                <Sparkles size={20} />
              </div>
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Content Settings</h2>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Topic *
                </label>
                <textarea
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  placeholder="Enter your topic..."
                  rows={3}
                  className="input-field"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Content Type
                  </label>
                  <select
                    value={contentType}
                    onChange={(e) => setContentType(e.target.value)}
                    className="select-field"
                  >
                    {CONTENT_TYPES.map((type) => (
                      <option key={type} value={type}>
                        {type}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Tone
                  </label>
                  <select
                    value={tone}
                    onChange={(e) => setTone(e.target.value)}
                    className="select-field"
                  >
                    {TONES.map((t) => (
                      <option key={t} value={t}>
                        {t}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Length
                </label>
                <select
                  value={length}
                  onChange={(e) => setLength(e.target.value)}
                  className="select-field"
                >
                  {LENGTHS.map((len) => (
                    <option key={len} value={len}>
                      {len} ({len === 'Short' ? 150 : len === 'Medium' ? 300 : 500} tokens)
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Temperature: {temperature.toFixed(1)}
                </label>
                <input
                  type="range"
                  min="0.1"
                  max="1.2"
                  step="0.1"
                  value={temperature}
                  onChange={(e) => setTemperature(parseFloat(e.target.value))}
                  className="w-full accent-blue-600"
                />
                <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                  <span>More Deterministic</span>
                  <span>More Creative</span>
                </div>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="btn-primary w-full flex items-center justify-center gap-2"
              >
                {isLoading ? (
                  <>
                    <RefreshCw size={20} className="animate-spin" />
                    Generating...
                  </>
                ) : (
                  'Generate Content'
                )}
              </button>
            </div>
          </div>
        </form>

        {error && (
          <div className="error-banner">
            <AlertCircle size={20} className="text-red-600 dark:text-red-400" />
            <p className="text-red-700 dark:text-red-300 text-sm">{error}</p>
          </div>
        )}

        {generatedContent && (
          <div className="mt-6">
            <div className="flex justify-between items-center mb-4">
              <div className="flex items-center gap-3">
                <div className="p-3 rounded-lg bg-green-600/10 text-green-600 dark:text-green-400">
                  <CheckCircle size={20} />
                </div>
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Generated Content</h2>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={copyToClipboard}
                  className="btn-copy"
                >
                  <Copy size={16} />
                  Copy
                </button>
                <button
                  onClick={resetForm}
                  className="btn-reset"
                >
                  <RefreshCw size={16} />
                  New
                </button>
              </div>
            </div>

            <div className="card-glow">
              <div className="flex items-start gap-3">
                <CheckCircle size={20} className="text-green-600 dark:text-green-400 mt-1 flex-shrink-0" />
                <div className="flex-1">
                  <pre className="whitespace-pre-wrap text-gray-800 dark:text-gray-200 font-mono leading-relaxed overflow-y-auto max-h-80">
                    {generatedContent}
                  </pre>
                </div>
              </div>
            </div>
          </div>
        )}

        {isLoading && (
          <div className="loading-overlay">
            <div className="loading-card">
              <RefreshCw size={32} className="animate-spin text-blue-600 dark:text-blue-400" />
              <p className="text-gray-700 dark:text-gray-300">Generating content...</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
