import { useState, useEffect } from "react";
import { getTowns, getFlatTypes } from "../api/client";

interface SearchBarProps {
  onSearch: (town: string, flatType: string) => void;
  loading?: boolean;
}

export default function SearchBar({ onSearch, loading }: SearchBarProps) {
  const [towns, setTowns] = useState<string[]>([]);
  const [flatTypes, setFlatTypes] = useState<string[]>([]);
  const [selectedTown, setSelectedTown] = useState("");
  const [selectedFlatType, setSelectedFlatType] = useState("");

  useEffect(() => {
    getTowns().then(setTowns);
    getFlatTypes().then(setFlatTypes);
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedTown) {
      onSearch(selectedTown, selectedFlatType);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="card">
      <div className="flex flex-wrap gap-4 items-end">
        <div className="flex-1 min-w-[200px]">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Town
          </label>
          <select
            value={selectedTown}
            onChange={(e) => setSelectedTown(e.target.value)}
            className="input-field"
          >
            <option value="">Select a town...</option>
            {towns.map((town) => (
              <option key={town} value={town}>
                {town}
              </option>
            ))}
          </select>
        </div>

        <div className="flex-1 min-w-[200px]">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Flat Type
          </label>
          <select
            value={selectedFlatType}
            onChange={(e) => setSelectedFlatType(e.target.value)}
            className="input-field"
          >
            <option value="">All types</option>
            {flatTypes.map((ft) => (
              <option key={ft} value={ft}>
                {ft}
              </option>
            ))}
          </select>
        </div>

        <button type="submit" className="btn-primary" disabled={!selectedTown || loading}>
          {loading ? "Loading..." : "Search"}
        </button>
      </div>
    </form>
  );
}
