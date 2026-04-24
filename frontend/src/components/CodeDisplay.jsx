import { useState } from 'react';
import { Copy, Check } from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';

const CodeDisplay = ({ code }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    toast.success('Code copied to clipboard!');
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-[#0A0A0F] border border-white/5 rounded-xl overflow-hidden" data-testid="code-display">
      <div className="flex justify-between items-center px-6 py-4 border-b border-white/5 bg-black/40">
        <span className="text-sm text-[#A1A1AA] uppercase tracking-[0.2em]" style={{ fontFamily: 'JetBrains Mono' }}>
          Generated Code
        </span>
        <Button
          onClick={handleCopy}
          variant="ghost"
          size="sm"
          className="text-[#00E5FF] hover:text-[#00E5FF]/80 hover:bg-[#00E5FF]/10"
          data-testid="copy-code-button"
        >
          {copied ? <Check className="w-4 h-4 mr-2" /> : <Copy className="w-4 h-4 mr-2" />}
          {copied ? 'Copied!' : 'Copy'}
        </Button>
      </div>
      <div className="p-6 overflow-x-auto">
        <pre className="text-sm text-[#E5E5E7] leading-relaxed" style={{ fontFamily: 'JetBrains Mono' }}>
          <code>{code}</code>
        </pre>
      </div>
    </div>
  );
};

export default CodeDisplay;