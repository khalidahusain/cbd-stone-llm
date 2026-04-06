const ABBREVS = [
  ["ERCP", "Endoscopic retrograde cholangiopancreatography"],
  ["EUS", "Endoscopic ultrasound"],
  ["MRCP", "Magnetic resonance cholangiopancreatography"],
  ["IOC", "Intraoperative cholangiography"],
  ["CCY", "Cholecystectomy"],
  ["CBD", "Common bile duct"],
  ["ALP", "Alkaline phosphatase"],
  ["AST", "Aspartate aminotransferase"],
  ["ALT", "Alanine aminotransferase"],
  ["CCI", "Charlson Comorbidity Index"],
];

export default function Abbreviations() {
  return (
    <div>
      <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
        Abbreviations
      </h3>
      <div className="grid grid-cols-2 gap-x-2 gap-y-0.5 text-[10px] text-gray-500">
        {ABBREVS.map(([abbr, full]) => (
          <div key={abbr}>
            <span className="font-semibold text-gray-600">{abbr}</span> — {full}
          </div>
        ))}
      </div>
    </div>
  );
}
