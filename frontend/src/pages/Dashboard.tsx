import { useState } from "react";
import SearchBar from "../components/SearchBar";
import PriceChart from "../components/PriceChart";
import TransactionTable from "../components/TransactionTable";
import AlertSetup from "../components/AlertSetup";
import {
  getTransactions,
  getTrends,
  syncDataGov,
} from "../api/client";
import type { Transaction, TrendPoint } from "../api/client";

export default function Dashboard() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [trendData, setTrendData] = useState<TrendPoint[]>([]);
  const [selectedTown, setSelectedTown] = useState("");
  const [selectedFlatType, setSelectedFlatType] = useState("");
  const [loading, setLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [syncStatus, setSyncStatus] = useState("");

  const handleSearch = async (town: string, flatType: string) => {
    setLoading(true);
    setSelectedTown(town);
    setSelectedFlatType(flatType);

    try {
      const [txns, trends] = await Promise.all([
        getTransactions({ town, flat_type: flatType || undefined, limit: 50 }),
        getTrends(town, flatType || undefined),
      ]);
      setTransactions(txns);
      setTrendData(trends.data);
    } catch (err) {
      console.error("Search failed:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSync = async () => {
    setSyncing(true);
    setSyncStatus("Syncing data from data.gov.sg...");
    try {
      const result = await syncDataGov(selectedTown || undefined, 2000);
      setSyncStatus(
        `Synced ${result.records_synced} records (${result.total_available} available)`
      );
      // Re-fetch if we have a search active
      if (selectedTown) {
        handleSearch(selectedTown, selectedFlatType);
      }
    } catch (err) {
      setSyncStatus("Sync failed. Check backend connection.");
    } finally {
      setSyncing(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-500">
            Monitor HDB resale prices across Singapore
          </p>
        </div>
        <div className="flex items-center gap-3">
          {syncStatus && (
            <span className="text-sm text-gray-600">{syncStatus}</span>
          )}
          <button
            onClick={handleSync}
            disabled={syncing}
            className="btn-secondary"
          >
            {syncing ? "Syncing..." : "Sync Data"}
          </button>
        </div>
      </div>

      <SearchBar onSearch={handleSearch} loading={loading} />

      {selectedTown && (
        <>
          <PriceChart
            data={trendData}
            town={selectedTown}
            flatType={selectedFlatType || null}
          />
          <TransactionTable transactions={transactions} />
        </>
      )}

      <AlertSetup />
    </div>
  );
}
