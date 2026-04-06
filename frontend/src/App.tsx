import { ChatProvider } from "./context/ChatContext";
import ChatPanel from "./components/ChatPanel";
import DashboardPanel from "./components/DashboardPanel";
import MobileDashboard from "./components/MobileDashboard";

function App() {
  return (
    <ChatProvider>
      <div className="flex flex-col h-screen bg-gray-50">
        <header className="h-10 bg-slate-800 flex items-center px-4 shrink-0">
          <h1 className="text-white text-sm font-semibold">
            CBD Stone LLM — Clinical Decision Support
          </h1>
        </header>
        <div className="flex flex-col md:flex-row flex-1 min-h-0">
          {/* Mobile dashboard: above chat, hidden on desktop */}
          <div className="md:hidden shrink-0">
            <MobileDashboard />
          </div>
          {/* Chat panel */}
          <div className="w-full md:w-2/3 flex-1 md:flex-none md:border-r border-gray-200 min-h-0">
            <ChatPanel />
          </div>
          {/* Desktop dashboard: hidden on mobile */}
          <div className="hidden md:block w-1/3 bg-white">
            <DashboardPanel />
          </div>
        </div>
      </div>
    </ChatProvider>
  );
}

export default App;
