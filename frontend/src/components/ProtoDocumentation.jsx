import { Code2, Zap, Layers, Sparkles } from 'lucide-react';

const ProtoDocumentation = () => {
  return (
    <div className="space-y-8" data-testid="proto-documentation">
      {/* Introduction */}
      <div className="bg-black/60 backdrop-blur-2xl border border-white/10 rounded-2xl p-8">
        <h2 className="text-3xl font-light text-white mb-4" style={{ fontFamily: 'Outfit' }}>
          About Project Proto
        </h2>
        <p className="text-[#A1A1AA] leading-relaxed mb-4" style={{ fontFamily: 'JetBrains Mono' }}>
          Proto bridges the gap between conceptual UI sketches and formal implementation. Using advanced AI technologies including Computer Vision, Graph Neural Networks, and Large Language Models, Proto automates the software prototyping process.
        </p>
        <p className="text-[#A1A1AA] leading-relaxed" style={{ fontFamily: 'JetBrains Mono' }}>
          Simply upload your UI mockup or sketch, describe your requirements, and let Proto generate production-ready frontend code tailored to your specifications.
        </p>
      </div>

      {/* Features Grid */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-black/60 backdrop-blur-2xl border border-white/10 rounded-2xl p-8">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-xl bg-[#00E5FF]/10 flex items-center justify-center">
              <Code2 className="w-6 h-6 text-[#00E5FF]" />
            </div>
            <h3 className="text-xl font-light text-white" style={{ fontFamily: 'Outfit' }}>Computer Vision</h3>
          </div>
          <p className="text-[#A1A1AA] text-sm leading-relaxed" style={{ fontFamily: 'JetBrains Mono' }}>
            YOLOv11-powered object detection analyzes UI components, layouts, and design elements from your sketches with high precision.
          </p>
        </div>

        <div className="bg-black/60 backdrop-blur-2xl border border-white/10 rounded-2xl p-8">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-xl bg-[#FF007F]/10 flex items-center justify-center">
              <Layers className="w-6 h-6 text-[#FF007F]" />
            </div>
            <h3 className="text-xl font-light text-white" style={{ fontFamily: 'Outfit' }}>Graph Neural Networks</h3>
          </div>
          <p className="text-[#A1A1AA] text-sm leading-relaxed" style={{ fontFamily: 'JetBrains Mono' }}>
            Extract topological relationships between UI elements to understand component hierarchy and structure.
          </p>
        </div>

        <div className="bg-black/60 backdrop-blur-2xl border border-white/10 rounded-2xl p-8">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-xl bg-[#D9F854]/10 flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-[#D9F854]" />
            </div>
            <h3 className="text-xl font-light text-white" style={{ fontFamily: 'Outfit' }}>LLM Integration</h3>
          </div>
          <p className="text-[#A1A1AA] text-sm leading-relaxed" style={{ fontFamily: 'JetBrains Mono' }}>
            Gemini 3 Flash processes your requirements and generates clean, production-ready code with proper structure and styling.
          </p>
        </div>

        <div className="bg-black/60 backdrop-blur-2xl border border-white/10 rounded-2xl p-8">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-xl bg-[#00E5FF]/10 flex items-center justify-center">
              <Zap className="w-6 h-6 text-[#00E5FF]" />
            </div>
            <h3 className="text-xl font-light text-white" style={{ fontFamily: 'Outfit' }}>Agentic Generation</h3>
          </div>
          <p className="text-[#A1A1AA] text-sm leading-relaxed" style={{ fontFamily: 'JetBrains Mono' }}>
            LangChain-powered agentic workflow optimizes code generation with chain-of-thought reasoning and iterative refinement.
          </p>
        </div>
      </div>

      {/* Technologies */}
      <div className="bg-black/60 backdrop-blur-2xl border border-white/10 rounded-2xl p-8">
        <h3 className="text-2xl font-light text-white mb-6" style={{ fontFamily: 'Outfit' }}>
          Technology Stack
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            'PyTorch',
            'YOLOv11',
            'OpenCV',
            'Gemini 3 Flash',
            'LangChain',
            'ChromaDB',
            'React',
            'FastAPI'
          ].map((tech) => (
            <div
              key={tech}
              className="px-4 py-3 bg-black/40 border border-white/5 rounded-lg text-center text-[#00E5FF] text-sm"
              style={{ fontFamily: 'JetBrains Mono' }}
            >
              {tech}
            </div>
          ))}
        </div>
      </div>

      {/* Team */}
      <div className="bg-black/60 backdrop-blur-2xl border border-white/10 rounded-2xl p-8">
        <h3 className="text-2xl font-light text-white mb-6" style={{ fontFamily: 'Outfit' }}>
          Project Team
        </h3>
        <div className="space-y-3">
          <div className="flex items-center gap-4 p-4 bg-black/40 border border-white/5 rounded-lg">
            <div>
              <p className="text-white font-medium">Ashirwad Singh</p>
              <p className="text-xs text-[#A1A1AA]" style={{ fontFamily: 'JetBrains Mono' }}>Enrollment: 9923103096 | Batch: F4</p>
            </div>
          </div>
          <div className="flex items-center gap-4 p-4 bg-black/40 border border-white/5 rounded-lg">
            <div>
              <p className="text-white font-medium">Samarth Gupta</p>
              <p className="text-xs text-[#A1A1AA]" style={{ fontFamily: 'JetBrains Mono' }}>Enrollment: 9923103101 | Batch: F4</p>
            </div>
          </div>
          <div className="mt-4 p-4 bg-black/40 border border-white/5 rounded-lg">
            <p className="text-sm text-[#A1A1AA]" style={{ fontFamily: 'JetBrains Mono' }}>
              <span className="text-white">Submitted to:</span> Mr. Keshan Srivastava
            </p>
            <p className="text-sm text-[#A1A1AA] mt-1" style={{ fontFamily: 'JetBrains Mono' }}>
              <span className="text-white">Institution:</span> Jaypee Institute Of Information Technology, Noida
            </p>
            <p className="text-sm text-[#A1A1AA] mt-1" style={{ fontFamily: 'JetBrains Mono' }}>
              <span className="text-white">Department:</span> CSE, GenAI Lab | 3rd Year, 6th Sem | 2026
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProtoDocumentation;