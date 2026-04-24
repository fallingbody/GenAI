import { useState, useEffect } from 'react';
import axios from 'axios';
import { Database, Loader2, RefreshCw, CheckCircle, AlertCircle, BarChart3, Layers, GitBranch } from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const TrainingPanel = ({ trainingStatus, onTrainingComplete }) => {
  const [training, setTraining] = useState(false);
  const [datasetInfo, setDatasetInfo] = useState(null);
  const [loadingInfo, setLoadingInfo] = useState(true);

  useEffect(() => {
    fetchDatasetInfo();
  }, []);

  const fetchDatasetInfo = async () => {
    try {
      const response = await axios.get(`${API}/dataset-info`);
      setDatasetInfo(response.data);
    } catch (error) {
      console.error('Error fetching dataset info:', error);
    } finally {
      setLoadingInfo(false);
    }
  };

  const handleTrain = async () => {
    setTraining(true);
    try {
      const response = await axios.post(`${API}/train`, {}, { timeout: 60000 });
      toast.success(`Training complete! ${response.data.stats.total_samples} samples loaded into vector DB`);
      onTrainingComplete();
    } catch (error) {
      console.error('Training error:', error);
      toast.error(error.response?.data?.detail || 'Training failed');
    } finally {
      setTraining(false);
    }
  };

  return (
    <div className="space-y-6" data-testid="training-panel">
      {/* Training Status Header */}
      <div className="bg-black/60 backdrop-blur-2xl border border-white/10 rounded-2xl p-8">
        <div className="flex items-start justify-between mb-6">
          <div>
            <h2 className="text-3xl font-light text-white mb-2" style={{ fontFamily: 'Outfit' }}>
              RAG Training Pipeline
            </h2>
            <p className="text-[#A1A1AA] text-sm" style={{ fontFamily: 'JetBrains Mono' }}>
              Train the vector database with pix2code + curated UI templates for enhanced code generation
            </p>
          </div>
          <div className={`px-4 py-2 rounded-full border flex items-center gap-2 ${
            trainingStatus?.is_trained 
              ? 'border-[#00E5FF]/30 bg-[#00E5FF]/5' 
              : 'border-[#FF007F]/30 bg-[#FF007F]/5'
          }`}>
            {trainingStatus?.is_trained 
              ? <CheckCircle className="w-4 h-4 text-[#00E5FF]" />
              : <AlertCircle className="w-4 h-4 text-[#FF007F]" />
            }
            <span className={`text-xs ${trainingStatus?.is_trained ? 'text-[#00E5FF]' : 'text-[#FF007F]'}`} style={{ fontFamily: 'JetBrains Mono' }}>
              {trainingStatus?.is_trained ? 'TRAINED' : 'NOT TRAINED'}
            </span>
          </div>
        </div>

        {/* Pipeline Workflow Visual */}
        <div className="grid grid-cols-4 gap-4 mb-8">
          {[
            { step: '1', label: 'Load Dataset', desc: 'pix2code + curated', icon: Database, done: !!datasetInfo },
            { step: '2', label: 'Process Data', desc: 'Extract descriptions', icon: Layers, done: !!datasetInfo },
            { step: '3', label: 'Create Embeddings', desc: 'Vector embeddings', icon: GitBranch, done: trainingStatus?.is_trained },
            { step: '4', label: 'Store in ChromaDB', desc: 'Vector database', icon: BarChart3, done: trainingStatus?.is_trained }
          ].map((item, i) => (
            <div key={i} className={`p-4 rounded-xl border transition-all ${
              item.done 
                ? 'border-[#00E5FF]/30 bg-[#00E5FF]/5' 
                : 'border-white/5 bg-black/40'
            }`}>
              <div className="flex items-center gap-2 mb-2">
                <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                  item.done ? 'bg-[#00E5FF] text-black' : 'bg-white/10 text-[#A1A1AA]'
                }`}>{item.step}</span>
                <item.icon className={`w-4 h-4 ${item.done ? 'text-[#00E5FF]' : 'text-[#A1A1AA]'}`} />
              </div>
              <p className={`text-sm font-medium ${item.done ? 'text-white' : 'text-[#A1A1AA]'}`}>{item.label}</p>
              <p className="text-xs text-[#A1A1AA] mt-1" style={{ fontFamily: 'JetBrains Mono' }}>{item.desc}</p>
            </div>
          ))}
        </div>

        {/* Train Button */}
        <Button
          onClick={handleTrain}
          disabled={training}
          className="w-full bg-[#FF007F] text-white hover:bg-[#FF007F]/90 hover:shadow-[0_0_20px_rgba(255,0,127,0.5)] transition-all font-medium py-6"
          data-testid="train-button"
        >
          {training ? (
            <>
              <Loader2 className="w-5 h-5 mr-2 animate-spin" />
              Training RAG Model...
            </>
          ) : trainingStatus?.is_trained ? (
            <>
              <RefreshCw className="w-5 h-5 mr-2" />
              Retrain Model
            </>
          ) : (
            <>
              <Database className="w-5 h-5 mr-2" />
              Start Training
            </>
          )}
        </Button>
      </div>

      {/* Dataset Info */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Dataset Source */}
        <div className="bg-black/60 backdrop-blur-2xl border border-white/10 rounded-2xl p-8">
          <h3 className="text-xl font-light text-white mb-4" style={{ fontFamily: 'Outfit' }}>
            Dataset Source
          </h3>
          
          {loadingInfo ? (
            <div className="text-center py-8">
              <Loader2 className="w-8 h-8 mx-auto text-[#A1A1AA] animate-spin" />
            </div>
          ) : datasetInfo ? (
            <div className="space-y-4">
              <div className="p-4 bg-black/40 border border-white/5 rounded-lg">
                <p className="text-sm text-[#00E5FF] font-medium" style={{ fontFamily: 'JetBrains Mono' }}>
                  {datasetInfo.dataset_name}
                </p>
                <p className="text-xs text-[#A1A1AA] mt-1">{datasetInfo.description}</p>
                <a 
                  href={datasetInfo.reference} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-xs text-[#FF007F] mt-2 inline-block hover:underline"
                >
                  {datasetInfo.reference}
                </a>
              </div>
              
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 bg-black/40 border border-white/5 rounded-lg text-center">
                  <p className="text-2xl font-light text-[#00E5FF]">{datasetInfo.total_samples}</p>
                  <p className="text-xs text-[#A1A1AA] uppercase tracking-wider mt-1">Total Samples</p>
                </div>
                <div className="p-3 bg-black/40 border border-white/5 rounded-lg text-center">
                  <p className="text-2xl font-light text-[#FF007F]">{Object.keys(datasetInfo.categories).length}</p>
                  <p className="text-xs text-[#A1A1AA] uppercase tracking-wider mt-1">Categories</p>
                </div>
              </div>

              {/* Sources Breakdown */}
              <div className="space-y-2">
                <p className="text-xs uppercase tracking-[0.2em] text-[#A1A1AA]">Sources</p>
                {Object.entries(datasetInfo.sources).map(([source, count]) => (
                  <div key={source} className="flex items-center justify-between p-2 bg-black/20 rounded-lg">
                    <span className="text-sm text-white capitalize">{source}</span>
                    <span className="text-sm text-[#00E5FF]" style={{ fontFamily: 'JetBrains Mono' }}>{count} samples</span>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <p className="text-[#A1A1AA]">Failed to load dataset info</p>
          )}
        </div>

        {/* Training Stats */}
        <div className="bg-black/60 backdrop-blur-2xl border border-white/10 rounded-2xl p-8">
          <h3 className="text-xl font-light text-white mb-4" style={{ fontFamily: 'Outfit' }}>
            Vector Database
          </h3>
          
          {trainingStatus?.is_trained ? (
            <div className="space-y-4">
              <div className="p-4 bg-[#00E5FF]/5 border border-[#00E5FF]/20 rounded-lg">
                <p className="text-sm text-[#00E5FF] font-medium" style={{ fontFamily: 'JetBrains Mono' }}>
                  ChromaDB Active
                </p>
                <p className="text-xs text-[#A1A1AA] mt-1">
                  {trainingStatus.total_entries} vectors stored with cosine similarity indexing
                </p>
              </div>
              
              <div className="p-3 bg-black/40 border border-white/5 rounded-lg">
                <p className="text-xs uppercase tracking-[0.2em] text-[#A1A1AA] mb-3">How It Works</p>
                <div className="space-y-2">
                  {[
                    'Upload UI sketch image',
                    'AI analyzes design components',
                    'RAG retrieves similar examples',
                    'Generates code with context'
                  ].map((step, i) => (
                    <div key={i} className="flex items-center gap-2">
                      <span className="w-5 h-5 rounded-full bg-[#00E5FF]/10 flex items-center justify-center text-[10px] text-[#00E5FF]">{i + 1}</span>
                      <span className="text-sm text-[#A1A1AA]">{step}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Categories in DB */}
              {trainingStatus.stats?.categories && (
                <div className="space-y-2">
                  <p className="text-xs uppercase tracking-[0.2em] text-[#A1A1AA]">Categories</p>
                  <div className="flex flex-wrap gap-2">
                    {Object.keys(trainingStatus.stats.categories).slice(0, 10).map((cat) => (
                      <span key={cat} className="px-3 py-1 bg-black/40 border border-white/5 rounded-full text-xs text-[#00E5FF]">
                        {cat}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-12">
              <Database className="w-12 h-12 mx-auto text-[#A1A1AA] mb-4" />
              <p className="text-[#A1A1AA] mb-2" style={{ fontFamily: 'JetBrains Mono' }}>
                Vector DB empty
              </p>
              <p className="text-xs text-[#A1A1AA]">
                Click "Start Training" to populate the vector database with UI patterns
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TrainingPanel;
