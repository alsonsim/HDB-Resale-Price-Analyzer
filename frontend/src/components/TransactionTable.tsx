import type { Transaction } from "../api/client";

interface TransactionTableProps {
  transactions: Transaction[];
}

export default function TransactionTable({ transactions }: TransactionTableProps) {
  if (!transactions.length) {
    return (
      <div className="card text-center text-gray-500 py-8">
        No transactions found.
      </div>
    );
  }

  return (
    <div className="card overflow-hidden">
      <h3 className="text-lg font-semibold mb-4">Recent Transactions</h3>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-gray-50 text-left">
              <th className="px-3 py-2 font-medium text-gray-600">Month</th>
              <th className="px-3 py-2 font-medium text-gray-600">Address</th>
              <th className="px-3 py-2 font-medium text-gray-600">Type</th>
              <th className="px-3 py-2 font-medium text-gray-600">Storey</th>
              <th className="px-3 py-2 font-medium text-gray-600">Area (sqm)</th>
              <th className="px-3 py-2 font-medium text-gray-600">Price</th>
              <th className="px-3 py-2 font-medium text-gray-600">$/sqm</th>
              <th className="px-3 py-2 font-medium text-gray-600">Lease Left</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {transactions.map((txn) => (
              <tr key={txn.id} className="hover:bg-gray-50 transition-colors">
                <td className="px-3 py-2 whitespace-nowrap">{txn.month}</td>
                <td className="px-3 py-2">
                  {txn.block} {txn.street_name}
                </td>
                <td className="px-3 py-2 whitespace-nowrap">{txn.flat_type}</td>
                <td className="px-3 py-2 whitespace-nowrap">{txn.storey_range}</td>
                <td className="px-3 py-2 text-right">{txn.floor_area_sqm}</td>
                <td className="px-3 py-2 text-right font-medium">
                  ${txn.resale_price.toLocaleString()}
                </td>
                <td className="px-3 py-2 text-right text-gray-600">
                  {txn.price_per_sqm
                    ? `$${txn.price_per_sqm.toLocaleString()}`
                    : "—"}
                </td>
                <td className="px-3 py-2 text-sm text-gray-500">
                  {txn.remaining_lease}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
