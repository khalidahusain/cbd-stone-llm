interface Props {
  message: string;
}

export default function CholangitisOverlay({ message }: Props) {
  return (
    <div className="relative">
      {/* Blur the content behind */}
      <div className="absolute inset-0 backdrop-blur-sm bg-white/30 z-10 rounded flex items-center justify-center p-3">
        <div className="bg-white/90 rounded-lg px-4 py-3 shadow-md text-center">
          <p className="text-red-700 font-bold text-sm">{message}</p>
        </div>
      </div>
    </div>
  );
}
