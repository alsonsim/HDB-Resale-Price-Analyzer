import { useState, useEffect } from "react";
import {
  getAlerts,
  createAlert,
  deleteAlert,
  getTowns,
  getFlatTypes,
} from "../api/client";
import type { Alert } from "../api/client";

export default function AlertSetup() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [towns, setTowns] = useState<string[]>([]);
  const [flatTypes, setFlatTypes] = useState<string[]>([]);
  const [town, setTown] = useState("");
  const [flatType, setFlatType] = useState("");
  const [maxPrice, setMaxPrice] = useState("");

  useEffect(() => {
    getAlerts().then(setAlerts);
    getTowns().then(setTowns);
    getFlatTypes().then(setFlatTypes);
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!town || !flatType || !maxPrice) return;

    const alert = await createAlert({
      town,
      flat_type: flatType,
      max_price: parseFloat(maxPrice),
    });
    setAlerts([alert, ...alerts]);
    setTown("");
    setFlatType("");
    setMaxPrice("");
  };

  const handleDelete = async (id: number) => {
    await deleteAlert(id);
    setAlerts(alerts.filter((a) => a.id !== id));
  };

  return (
    <div className="card">
      <h3 className="text-lg font-semibold mb-4">Price Alerts</h3>

      <form onSubmit={handleCreate} className="flex flex-wrap gap-3 mb-6">
        <select
          value={town}
          onChange={(e) => setTown(e.target.value)}
          className="input-field flex-1 min-w-[150px]"
        >
          <option value="">Town...</option>
          {towns.map((t) => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>

        <select
          value={flatType}
          onChange={(e) => setFlatType(e.target.value)}
          className="input-field flex-1 min-w-[120px]"
        >
          <option value="">Flat type...</option>
          {flatTypes.map((ft) => (
            <option key={ft} value={ft}>{ft}</option>
          ))}
        </select>

        <input
          type="number"
          value={maxPrice}
          onChange={(e) => setMaxPrice(e.target.value)}
          placeholder="Max price ($)"
          className="input-field flex-1 min-w-[140px]"
        />

        <button type="submit" className="btn-primary">
          Add Alert
        </button>
      </form>

      {alerts.length === 0 ? (
        <p className="text-sm text-gray-500">
          No alerts set. Create one to get notified when matching listings appear.
        </p>
      ) : (
        <ul className="space-y-2">
          {alerts.map((alert) => (
            <li
              key={alert.id}
              className="flex items-center justify-between py-2 px-3 bg-gray-50 rounded-lg"
            >
              <div className="text-sm">
                <span className="font-medium">{alert.town}</span>
                <span className="text-gray-500 mx-2">/</span>
                <span>{alert.flat_type}</span>
                <span className="text-gray-500 mx-2">under</span>
                <span className="font-medium text-green-700">
                  ${alert.max_price.toLocaleString()}
                </span>
              </div>
              <button
                onClick={() => handleDelete(alert.id)}
                className="text-red-500 hover:text-red-700 text-sm"
              >
                Remove
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
