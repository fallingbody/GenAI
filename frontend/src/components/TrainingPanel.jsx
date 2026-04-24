import { useState, useEffect } from 'react';
import axios from 'axios';
import { Database, Loader2, RefreshCw, CheckCircle, AlertCircle, BarChart3, Layers, GitBranch, ExternalLink } from 'lucide-react';
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
      await axios.post(`${API}/train`, {}, { timeout: 10000 });
      toast.info('Training started! Downloading pix2code dataset...');
      
      // Poll for completion
      const pollInterval = setInterval(async () => {
        try {
          const res = await axios.get(`${API}/training-status`);
          const status = res.data;
          
          if (!status.is_training && status.is_trained) {
            clearInterval(pollInterval);
            setTraining(false);
            toast.success(`Training complete! ${status.total_entries} pix2code samples loaded`);
            onTrainingComplete();
          } else if (status.training_error) {
            clearInterval(pollInterval);
            setTraining(false);
            toast.error(`Training failed: ${status.training_error}`);
          }
        } catch (err) {
          // Ignore poll errors
        }
      }, 5000);
      
    } catch (error) {
      console.error('Training error:', error);
      toast.error(error.response?.data?.detail || 'Training failed');
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
              Train on the public <span className="text-[#00E5FF]">pix2code</span> dataset (1748 real UI-to-code pairs) from HuggingFace
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

        {/* Pipeline Workflow */}
        <div className="grid grid-cols-4 gap-4 mb-8">
          {[
            { step: '1', label: 'Fetch Dataset', desc: 'HuggingFace pix2code', icon: Database, done: !!datasetInfo },
            { step: '2', label: 'Parse DSL + HTML', desc: '1748 real pairs', icon: Layers, done: !!datasetInfo },
            { step: '3', label: 'Create Embeddings', desc: 'Text embeddings', icon: GitBranch, done: trainingStatus?.is_trained },
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
              Downloading & Training on pix2code dataset...
            </>
          ) : trainingStatus?.is_trained ? (
            <>
              <RefreshCw className="w-5 h-5 mr-2" />
              Retrain Model
            </>
          ) : (
            <>
              <Database className="w-5 h-5 mr-2" />
              Start Training on pix2code
            </>
          )}
        </Button>
      </div>

      {/* Dataset Info + Vector DB */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Public Dataset Source */}
        <div className="bg-black/60 backdrop-blur-2xl border border-white/10 rounded-2xl p-8">
          <h3 className="text-xl font-light text-white mb-4" style={{ fontFamily: 'Outfit' }}>
            Public Dataset
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
                <p className="text-xs text-[#A1A1AA] mt-2 leading-relaxed">{datasetInfo.description}</p>
              </div>

              {/* Links */}
              <div className="space-y-2">
                {[
                  { label: 'HuggingFace', url: datasetInfo.reference_huggingface },
                  { label: 'GitHub', url: datasetInfo.reference_github },
                  { label: 'Paper', url: datasetInfo.reference_paper }
                ].map((link) => (
                  <a 
                    key={link.label}
                    href={link.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="flex items-center justify-between p-3 bg-black/20 rounded-lg hover:bg-black/40 transition-all group"
                  >
                    <span className="text-sm text-[#A1A1AA] group-hover:text-white">{link.label}</span>
                    <ExternalLink className="w-3 h-3 text-[#FF007F]" />
                  </a>
                ))}
              </div>
              
              {/* Stats */}
              <div className="grid grid-cols-3 gap-3">
                <div className="p-3 bg-black/40 border border-white/5 rounded-lg text-center">
                  <p className="text-2xl font-light text-[#00E5FF]">{datasetInfo.total_train}</p>
                  <p className="text-[10px] text-[#A1A1AA] uppercase tracking-wider mt-1">Train</p>
                </div>
                <div className="p-3 bg-black/40 border border-white/5 rounded-lg text-center">
                  <p className="text-2xl font-light text-[#FF007F]">{datasetInfo.total_test}</p>
                  <p className="text-[10px] text-[#A1A1AA] uppercase tracking-wider mt-1">Test</p>
                </div>
                <div className="p-3 bg-black/40 border border-white/5 rounded-lg text-center">
                  <p className="text-2xl font-light text-[#D9F854]">{datasetInfo.total_samples}</p>
                  <p className="text-[10px] text-[#A1A1AA] uppercase tracking-wider mt-1">Total</p>
                </div>
              </div>
            </div>
          ) : (
            <p className="text-[#A1A1AA]">Failed to load dataset info</p>
          )}
        </div>

        {/* Vector Database */}
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
                  {trainingStatus.total_entries} vectors indexed with cosine similarity
                </p>
              </div>
              
              {/* Workflow */}
              <div className="p-3 bg-black/40 border border-white/5 rounded-lg">
                <p className="text-xs uppercase tracking-[0.2em] text-[#A1A1AA] mb-3">RAG Generation Flow</p>
                <div className="space-y-2">
                  {[
                    'Upload UI sketch image',
                    'Gemini analyzes design components',
                    'Query ChromaDB for similar pix2code layouts',
                    'Retrieve top matching HTML patterns',
                    'Generate final code with RAG context'
                  ].map((step, i) => (
                    <div key={i} className="flex items-center gap-2">
                      <span className="w-5 h-5 rounded-full bg-[#00E5FF]/10 flex items-center justify-center text-[10px] text-[#00E5FF] shrink-0">{i + 1}</span>
                      <span className="text-xs text-[#A1A1AA]">{step}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Categories */}
              {trainingStatus.stats?.categories && (
                <div className="space-y-2">
                  <p className="text-xs uppercase tracking-[0.2em] text-[#A1A1AA]">Layout Categories</p>
                  <div className="space-y-1">
                    {Object.entries(trainingStatus.stats.categories).map(([cat, count]) => (
                      <div key={cat} className="flex items-center justify-between p-2 bg-black/20 rounded-lg">
                        <span className="text-xs text-white">{cat.replace(/_/g, ' ')}</span>
                        <span className="text-xs text-[#00E5FF]" style={{ fontFamily: 'JetBrains Mono' }}>{count}</span>
                      </div>
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
                Click "Start Training on pix2code" to download and index the public dataset
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TrainingPanel;
