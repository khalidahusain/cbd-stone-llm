import { ChatProvider } from "./context/ChatContext";
import ChatPanel from "./components/ChatPanel";
import DashboardPanel from "./components/DashboardPanel";

function App() {
  return (
    <ChatProvider>
      <div className="flex flex-col h-screen bg-gray-50">
        {/* Header */}
        <header className="h-10 bg-slate-800 flex items-center px-4 shrink-0">
          <h1 className="text-white text-sm font-semibold">
            CBD Stone LLM — Clinical Decision Support
          </h1>
        </header>

        {/* Main content */}
        <div className="flex flex-1 min-h-0">
          {/* Chat panel: left ~2/3 */}
          <div className="w-2/3 border-r border-gray-200">
            <ChatPanel />
          </div>

          {/* Dashboard panel: right ~1/3 */}
          <div className="w-1/3 bg-white">
            <DashboardPanel />
          </div>
        </div>
      </div>
    </ChatProvider>
  );
}

export default App;
