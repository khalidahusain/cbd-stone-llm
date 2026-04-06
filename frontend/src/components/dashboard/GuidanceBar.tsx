interface Props {
  probability: number;
}

const ZONES = [
  { start: 0, end: 10, label: "CCY \u00b1 IOC" },
  { start: 10, end: 44, label: "MRCP" },
  { start: 44, end: 90, label: "EUS" },
  { start: 90, end: 100, label: "ERCP" },
];

const TICKS = [0, 10, 44, 90, 100];

export default function GuidanceBar({ probability }: Props) {
  return (
    <div className="relative px-1">
      {/* Bar with gradient */}
      <div
        className="relative h-10 rounded overflow-hidden"
        style={{
          background: "linear-gradient(to right, rgb(198,239,1), rgb(0,100,0))",
        }}
      >
        {/* Zone labels */}
        {ZONES.map((zone) => (
          <div
            key={zone.label}
            className="absolute top-0 h-full flex items-center justify-center text-xs font-semibold text-black/80"
            style={{
              left: `${zone.start}%`,
              width: `${zone.end - zone.start}%`,
            }}
          >
            {zone.label}
          </div>
        ))}

        {/* Zone dividers */}
        {[10, 44, 90].map((boundary) => (
          <div
            key={boundary}
            className="absolute top-0 h-full w-px bg-black/40"
            style={{ left: `${boundary}%` }}
          />
        ))}

        {/* Pointer */}
        <div
          className="absolute -top-1 w-0 h-0 transition-all duration-500 ease-out"
          style={{
            left: `${probability}%`,
            transform: "translateX(-50%)",
            borderLeft: "8px solid transparent",
            borderRight: "8px solid transparent",
            borderTop: "10px solid #f97316",
          }}
        />
      </div>

      {/* Tick marks */}
      <div className="relative h-4 mt-0.5">
        {TICKS.map((tick) => (
          <span
            key={tick}
            className="absolute text-[10px] text-gray-500 -translate-x-1/2"
            style={{ left: `${tick}%` }}
          >
            {tick}%
          </span>
        ))}
      </div>
    </div>
  );
}
