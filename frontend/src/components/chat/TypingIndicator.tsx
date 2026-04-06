export default function TypingIndicator() {
  return (
    <div className="flex justify-start px-4 pb-2">
      <div className="bg-gray-100 rounded-lg px-4 py-2 flex space-x-1">
        <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
        <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
        <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
      </div>
    </div>
  );
}
