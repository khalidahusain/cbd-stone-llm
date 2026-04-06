interface Props {
  onConfirm: () => void;
}

export default function ConfirmButton({ onConfirm }: Props) {
  return (
    <div className="flex items-center gap-3 px-4 pb-2">
      <button
        onClick={onConfirm}
        className="bg-green-600 hover:bg-green-700 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
      >
        Confirm & Run Prediction
      </button>
      <span className="text-xs text-gray-400">
        or type corrections in the chat
      </span>
    </div>
  );
}
