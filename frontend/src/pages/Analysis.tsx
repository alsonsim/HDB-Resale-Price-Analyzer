import { useState, useEffect } from "react";
import InsightCard from "../components/InsightCard";
import { analyzeListing, getTowns, getFlatTypes } from "../api/client";
import type { AnalysisResult } from "../api/client";

export default function Analysis() {
  const [towns, setTowns] = useState<string[]>([]);
  const [flatTypes, setFlatTypes] = useState<string[]>([]);
  const [town, setTown] = useState("");
  const [flatType, setFlatType] = useState("");
  const [askingPrice, setAskingPrice] = useState("");
  const [floorArea, setFloorArea] = useState("");
  const [storey, setStorey] = useState("");
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    getTowns().then(setTowns);
    getFlatTypes().then(setFlatTypes);
  }, []);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!town || !flatType || !askingPrice) return;

    setLoading(true);
    setError("");
    setAnalysis(null);

    try {
      const result = await analyzeListing({
        town,
        flat_type: flatType,
        asking_price: parseFloat(askingPrice),
        floor_area_sqm: floorArea ? parseFloat(floorArea) : undefined,
        storey_range: storey || undefined,
      });
      setAnalysis(result);
    } catch (err) {
      setError("Analysis failed. Make sure data is synced for this town.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Price Analysis</h1>
        <p className="text-gray-500">
          Check if an HDB flat is fairly priced using AI
        </p>
      </div>

      <form onSubmit={handleAnalyze} className="card space-y-4">
        <h3 className="font-semibold">Listing Details</h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Town *
            </label>
            <select
              value={town}
              onChange={(e) => setTown(e.target.value)}
              className="input-field"
              required
            >
              <option value="">Select town...</option>
              {towns.map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Flat Type *
            </label>
            <select
              value={flatType}
              onChange={(e) => setFlatType(e.target.value)}
              className="input-field"
              required
            >
              <option value="">Select type...</option>
              {flatTypes.map((ft) => (
                <option key={ft} value={ft}>{ft}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Asking Price (SGD) *
            </label>
            <input
              type="number"
              value={askingPrice}
              onChange={(e) => setAskingPrice(e.target.value)}
              placeholder="e.g. 550000"
              className="input-field"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Floor Area (sqm)
            </label>
            <input
              type="number"
              value={floorArea}
              onChange={(e) => setFloorArea(e.target.value)}
              placeholder="e.g. 93"
              className="input-field"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Storey Range
            </label>
            <select
              value={storey}
              onChange={(e) => setStorey(e.target.value)}
              className="input-field"
            >
              <option value="">Any</option>
              <option value="01 TO 03">01 TO 03</option>
              <option value="04 TO 06">04 TO 06</option>
              <option value="07 TO 09">07 TO 09</option>
              <option value="10 TO 12">10 TO 12</option>
              <option value="13 TO 15">13 TO 15</option>
              <option value="16 TO 18">16 TO 18</option>
              <option value="19 TO 21">19 TO 21</option>
              <option value="22 TO 24">22 TO 24</option>
              <option value="25 TO 27">25 TO 27</option>
              <option value="28 TO 30">28 TO 30</option>
              <option value="31 TO 33">31 TO 33</option>
              <option value="34 TO 36">34 TO 36</option>
              <option value="37 TO 39">37 TO 39</option>
              <option value="40 TO 42">40 TO 42</option>
            </select>
          </div>
        </div>

        <div className="flex gap-3">
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? "Analyzing..." : "Analyze Price"}
          </button>
        </div>
      </form>

      {error && (
        <div className="card bg-red-50 border-red-200 text-red-800">
          {error}
        </div>
      )}

      {analysis && <InsightCard analysis={analysis} />}
    </div>
  );
}
