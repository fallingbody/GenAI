import { useState, useEffect } from 'react';
import axios from 'axios';
import { Clock, Code } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ProjectHistory = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const response = await axios.get(`${API}/projects`);
      setProjects(response.data);
    } catch (error) {
      console.error('Error fetching projects:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-black/60 backdrop-blur-2xl border border-white/10 rounded-2xl p-8 mt-8">
        <p className="text-[#A1A1AA] text-center">Loading history...</p>
      </div>
    );
  }

  if (projects.length === 0) {
    return null;
  }

  return (
    <div className="bg-black/60 backdrop-blur-2xl border border-white/10 rounded-2xl p-8 mt-8" data-testid="project-history">
      <h3 className="text-xl font-light text-white mb-6" style={{ fontFamily: 'Outfit' }}>
        Recent Generations
      </h3>
      <div className="space-y-3">
        {projects.slice(0, 5).map((project) => (
          <div
            key={project.id}
            className="flex items-center justify-between p-4 bg-black/40 border border-white/5 rounded-lg hover:border-[#00E5FF]/30 transition-all"
            data-testid="project-history-item"
          >
            <div className="flex items-center gap-3">
              <Code className="w-5 h-5 text-[#00E5FF]" />
              <div>
                <p className="text-white font-medium">{project.project_name}</p>
                <p className="text-xs text-[#A1A1AA]">{project.framework}</p>
              </div>
            </div>
            <div className="flex items-center gap-2 text-xs text-[#A1A1AA]">
              <Clock className="w-3 h-3" />
              {new Date(project.timestamp).toLocaleDateString()}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProjectHistory;