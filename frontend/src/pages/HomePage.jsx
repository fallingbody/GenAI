import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Upload, Code, Sparkles, Download, Database, Loader2, RefreshCw, Search, Layers, Zap } from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import CodeDisplay from '@/components/CodeDisplay';
import ProjectHistory from '@/components/ProjectHistory';
import ProtoDocumentation from '@/components/ProtoDocumentation';
import TrainingPanel from '@/components/TrainingPanel';
import RAGResults from '@/components/RAGResults';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const HomePage = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [projectName, setProjectName] = useState('');
  const [description, setDescription] = useState('');
  const [framework, setFramework] = useState('React');
  const [loading, setLoading] = useState(false);
  const [generatedCode, setGeneratedCode] = useState(null);
  const [activeTab, setActiveTab] = useState('training');
  const [trainingStatus, setTrainingStatus] = useState(null);
  const [ragContext, setRagContext] = useState([]);

  const fetchTrainingStatus = useCallback(async () => {
    try {
      const response = await axios.get(`${API}/training-status`);
      setTrainingStatus(response.data);
    } catch (error) {
      console.error('Error fetching training status:', error);
    }
  }, []);

  useEffect(() => {
    fetchTrainingStatus();
  }, [fetchTrainingStatus]);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
        toast.error('Please upload a JPEG, PNG, or WEBP image');
        return;
      }
      setSelectedImage(file);
      const reader = new FileReader();
      reader.onloadend = () => setImagePreview(reader.result);
      reader.readAsDataURL(file);
    }
  };

  const handleGenerate = async () => {
    if (!selectedImage || !projectName || !description) {
      toast.error('Please fill all fields and upload an image');
      return;
    }

    if (!trainingStatus?.is_trained) {
      toast.error('Please train the RAG model first in the Training tab');
      return;
    }

    setLoading(true);
    try {
      const reader = new FileReader();
      reader.onloadend = async () => {
        try {
          const base64String = reader.result.split(',')[1];
          const response = await axios.post(`${API}/generate`, {
            image_base64: base64String,
            project_name: projectName,
            description: description,
            framework: framework
          }, { timeout: 120000 });

          setGeneratedCode(response.data);
          setRagContext(response.data.rag_context || []);
          toast.success('Code generated with RAG-enhanced AI!');
          setActiveTab('code');
        } catch (error) {
          console.error('Error generating code:', error);
          toast.error(error.response?.data?.detail || 'Failed to generate code');
        } finally {
          setLoading(false);
        }
      };
      reader.readAsDataURL(selectedImage);
    } catch (error) {
      console.error('Error:', error);
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!generatedCode) return;
    const blob = new Blob([generatedCode.generated_code], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    const ext = generatedCode.framework === 'HTML/CSS/JS' ? '.html' : '.jsx';
    a.download = `${generatedCode.project_name.replace(/\s+/g, '_')}${ext}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success('Code downloaded!');
  };

  return (
    <div className="min-h-screen" style={{ background: '#05050A' }}>
      {/* Hero */}
      <div className="relative overflow-hidden">
        <div 
          className="absolute inset-0 opacity-10"
          style={{
            backgroundImage: 'url(https://images.pexels.com/photos/28583190/pexels-photo-28583190.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940)',
            backgroundSize: 'cover',
            backgroundPosition: 'center'
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent to-[#05050A]" />
        
        <div className="relative container mx-auto px-6 py-12">
          <div className="text-center mb-10">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-[#00E5FF]/20 bg-[#00E5FF]/5 mb-6">
              <Sparkles className="w-4 h-4 text-[#00E5FF]" />
              <span className="text-xs text-[#00E5FF] uppercase tracking-[0.2em]" style={{ fontFamily: 'JetBrains Mono' }}>
                RAG-Powered Proto
              </span>
            </div>
            
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-light tracking-tight mb-4 text-white" style={{ fontFamily: 'Outfit, sans-serif' }}>
              Idea into <span className="text-[#00E5FF]">Project</span>
            </h1>
            <p className="text-base md:text-lg text-[#A1A1AA] max-w-2xl mx-auto leading-relaxed" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
              Train on the pix2code dataset, then generate production-ready frontend code from your UI sketches using RAG-enhanced AI.
            </p>

            {/* Status Badge */}
            <div className="mt-4 inline-flex items-center gap-2 px-4 py-2 rounded-full border bg-black/40" style={{
              borderColor: trainingStatus?.is_trained ? '#00E5FF' : '#FF007F'
            }}>
              <div className={`w-2 h-2 rounded-full ${trainingStatus?.is_trained ? 'bg-[#00E5FF] animate-pulse' : 'bg-[#FF007F]'}`} />
              <span className="text-xs" style={{ 
                fontFamily: 'JetBrains Mono',
                color: trainingStatus?.is_trained ? '#00E5FF' : '#FF007F'
              }}>
                {trainingStatus?.is_trained 
                  ? `Model Trained (${trainingStatus.total_entries} vectors)` 
                  : 'Model Not Trained'}
              </span>
            </div>
          </div>

          {/* Main Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList 
              className="grid w-full max-w-lg mx-auto grid-cols-4 mb-8 bg-black/60 backdrop-blur-2xl border border-white/10 p-1"
              data-testid="main-tabs"
            >
              <TabsTrigger 
                value="training" 
                className="data-[state=active]:bg-[#FF007F] data-[state=active]:text-white text-xs"
                data-testid="training-tab"
              >
                <Database className="w-4 h-4 mr-1" />
                Train
              </TabsTrigger>
              <TabsTrigger 
                value="generator" 
                className="data-[state=active]:bg-[#00E5FF] data-[state=active]:text-black text-xs"
                data-testid="generator-tab"
              >
                <Upload className="w-4 h-4 mr-1" />
                Generate
              </TabsTrigger>
              <TabsTrigger 
                value="code"
                className="data-[state=active]:bg-[#00E5FF] data-[state=active]:text-black text-xs"
                data-testid="code-tab"
              >
                <Code className="w-4 h-4 mr-1" />
                Code
              </TabsTrigger>
              <TabsTrigger 
                value="docs"
                className="data-[state=active]:bg-[#00E5FF] data-[state=active]:text-black text-xs"
                data-testid="docs-tab"
              >
                <Layers className="w-4 h-4 mr-1" />
                Docs
              </TabsTrigger>
            </TabsList>

            {/* Training Tab */}
            <TabsContent value="training">
              <div className="max-w-6xl mx-auto">
                <TrainingPanel 
                  trainingStatus={trainingStatus} 
                  onTrainingComplete={fetchTrainingStatus} 
                />
              </div>
            </TabsContent>

            {/* Generator Tab */}
            <TabsContent value="generator" className="space-y-8">
              <div className="grid lg:grid-cols-2 gap-8 max-w-6xl mx-auto">
                {/* Upload */}
                <div className="bg-black/60 backdrop-blur-2xl border border-white/10 rounded-2xl p-8">
                  <h3 className="text-2xl font-light text-white mb-6" style={{ fontFamily: 'Outfit' }}>
                    Upload Design
                  </h3>
                  <div 
                    className="border-2 border-dashed border-white/20 rounded-xl p-8 text-center cursor-pointer hover:border-[#00E5FF]/50 transition-all"
                    onClick={() => document.getElementById('image-upload').click()}
                    data-testid="image-upload-area"
                  >
                    {imagePreview ? (
                      <img src={imagePreview} alt="Preview" className="max-h-64 mx-auto rounded-lg" />
                    ) : (
                      <div className="space-y-4">
                        <Upload className="w-16 h-16 mx-auto text-[#00E5FF]" />
                        <p className="text-[#A1A1AA]" style={{ fontFamily: 'JetBrains Mono' }}>Click to upload your UI sketch</p>
                        <p className="text-sm text-[#A1A1AA]">JPEG, PNG, or WEBP</p>
                      </div>
                    )}
                  </div>
                  <input
                    id="image-upload"
                    type="file"
                    accept="image/jpeg,image/png,image/webp"
                    onChange={handleImageChange}
                    className="hidden"
                    data-testid="image-upload-input"
                  />
                </div>

                {/* Details */}
                <div className="bg-black/60 backdrop-blur-2xl border border-white/10 rounded-2xl p-8 space-y-6">
                  <h3 className="text-2xl font-light text-white mb-6" style={{ fontFamily: 'Outfit' }}>
                    Project Details
                  </h3>
                  
                  <div className="space-y-2">
                    <label className="text-xs uppercase tracking-[0.2em] text-[#A1A1AA]">Project Name</label>
                    <Input
                      value={projectName}
                      onChange={(e) => setProjectName(e.target.value)}
                      placeholder="My Awesome Project"
                      className="bg-black/40 border-white/10 text-white focus:border-[#00E5FF]"
                      data-testid="project-name-input"
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="text-xs uppercase tracking-[0.2em] text-[#A1A1AA]">Framework</label>
                    <select
                      value={framework}
                      onChange={(e) => setFramework(e.target.value)}
                      className="w-full px-4 py-3 bg-black/40 border border-white/10 rounded-lg text-white focus:border-[#00E5FF] outline-none"
                      data-testid="framework-select"
                    >
                      <option value="React">React</option>
                      <option value="Vue">Vue</option>
                      <option value="Angular">Angular</option>
                      <option value="HTML/CSS/JS">HTML/CSS/JS</option>
                    </select>
                  </div>

                  <div className="space-y-2">
                    <label className="text-xs uppercase tracking-[0.2em] text-[#A1A1AA]">Description</label>
                    <Textarea
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                      placeholder="Describe your project: layout, components, colors, features..."
                      rows={5}
                      className="bg-black/40 border-white/10 text-white focus:border-[#00E5FF] resize-none"
                      data-testid="description-textarea"
                    />
                  </div>

                  <Button
                    onClick={handleGenerate}
                    disabled={loading || !trainingStatus?.is_trained}
                    className="w-full bg-[#00E5FF] text-black hover:bg-[#00E5FF]/90 hover:shadow-[0_0_20px_rgba(0,229,255,0.5)] transition-all font-medium py-6 disabled:opacity-50"
                    data-testid="generate-button"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                        Analyzing & Generating...
                      </>
                    ) : !trainingStatus?.is_trained ? (
                      <>
                        <Database className="w-5 h-5 mr-2" />
                        Train Model First
                      </>
                    ) : (
                      <>
                        <Zap className="w-5 h-5 mr-2" />
                        Generate with RAG
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </TabsContent>

            {/* Code Tab */}
            <TabsContent value="code">
              <div className="max-w-6xl mx-auto">
                {generatedCode ? (
                  <div className="space-y-6">
                    <div className="flex justify-between items-center">
                      <h3 className="text-2xl font-light text-white" style={{ fontFamily: 'Outfit' }}>
                        Generated: {generatedCode.project_name}
                      </h3>
                      <Button
                        onClick={handleDownload}
                        className="bg-[#FF007F] text-white hover:bg-[#FF007F]/90 hover:shadow-[0_0_20px_rgba(255,0,127,0.5)]"
                        data-testid="download-button"
                      >
                        <Download className="w-4 h-4 mr-2" />
                        Download
                      </Button>
                    </div>
                    
                    {/* RAG Context */}
                    {ragContext.length > 0 && <RAGResults results={ragContext} />}
                    
                    <CodeDisplay code={generatedCode.generated_code} />
                    <ProjectHistory />
                  </div>
                ) : (
                  <div className="bg-black/60 backdrop-blur-2xl border border-white/10 rounded-2xl p-16 text-center">
                    <Code className="w-16 h-16 mx-auto text-[#A1A1AA] mb-4" />
                    <p className="text-[#A1A1AA]" style={{ fontFamily: 'JetBrains Mono' }}>
                      No code generated yet. Train the model, then upload a design to generate code.
                    </p>
                  </div>
                )}
              </div>
            </TabsContent>

            {/* Docs Tab */}
            <TabsContent value="docs">
              <div className="max-w-6xl mx-auto">
                <ProtoDocumentation />
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
