const RANGES = [
  { range: "0-10%", risk: "Low", action: "CCY \u00b1 IOC", desc: "Cholecystectomy with optional intraoperative cholangiography" },
  { range: "10-44%", risk: "Intermediate", action: "MRCP", desc: "Magnetic resonance cholangiopancreatography" },
  { range: "44-90%", risk: "High", action: "EUS", desc: "Endoscopic ultrasound" },
  { range: "90-100%", risk: "Very High", action: "ERCP", desc: "Endoscopic retrograde cholangiopancreatography" },
];

export default function InterpretationGuide() {
  return (
    <div>
      <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
        Interpretation Guide
      </h3>
      <div className="space-y-1">
        {RANGES.map((r) => (
          <div key={r.range} className="text-[11px] text-gray-600">
            <span className="font-semibold">{r.range}</span>{" "}
            <span className="text-gray-500">({r.risk})</span>{" "}
            &rarr; {r.action}
          </div>
        ))}
      </div>
    </div>
  );
}
