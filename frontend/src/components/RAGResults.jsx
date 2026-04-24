import { Search } from 'lucide-react';

const RAGResults = ({ results }) => {
  if (!results || results.length === 0) return null;

  return (
    <div className="bg-black/60 backdrop-blur-2xl border border-[#FF007F]/20 rounded-2xl p-6" data-testid="rag-results">
      <div className="flex items-center gap-2 mb-4">
        <Search className="w-5 h-5 text-[#FF007F]" />
        <h4 className="text-lg font-light text-white" style={{ fontFamily: 'Outfit' }}>
          RAG Retrieved Context
        </h4>
        <span className="px-2 py-0.5 bg-[#FF007F]/10 border border-[#FF007F]/20 rounded-full text-xs text-[#FF007F]" style={{ fontFamily: 'JetBrains Mono' }}>
          {results.length} matches
        </span>
      </div>
      
      <div className="grid grid-cols-3 gap-3">
        {results.map((result, i) => (
          <div 
            key={i} 
            className="p-4 bg-black/40 border border-white/5 rounded-lg hover:border-[#FF007F]/20 transition-all"
            data-testid="rag-result-item"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-[#FF007F] font-medium uppercase tracking-wider">
                {result.category}
              </span>
              <span className="text-xs text-[#A1A1AA]" style={{ fontFamily: 'JetBrains Mono' }}>
                {(result.similarity * 100).toFixed(0)}% match
              </span>
            </div>
            <p className="text-xs text-[#A1A1AA]" style={{ fontFamily: 'JetBrains Mono' }}>
              ID: {result.id}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RAGResults;
