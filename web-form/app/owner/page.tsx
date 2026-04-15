"use client";
import { useState, useEffect } from "react";
import axios from "axios";
import {
  BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip,
  ResponsiveContainer, PieChart,
  Pie, Cell, Legend
} from "recharts";
import {
  Package, Users, Smartphone,
  AlertTriangle, RefreshCw,
  Mail, Globe
} from "lucide-react";
import Header from "@/components/shared/Header";
import StatCard from "@/components/shared/StatCard";

const API = process.env.NEXT_PUBLIC_API_URL
  || "http://localhost:8000";
const OWNER = process.env.NEXT_PUBLIC_OWNER_PHONE
  || "";

const CHANNEL_COLORS = ["#f59e0b","#3b82f6","#10b981"];

const statusStyles: Record<string, string> = {
  confirmed:  "bg-blue-50 text-blue-700",
  processing: "bg-yellow-50 text-yellow-700",
  dispatched: "bg-purple-50 text-purple-700",
  delivered:  "bg-green-50 text-green-700",
  cancelled:  "bg-red-50 text-red-700",
};

const channelIcons: Record<string, any> = {
  whatsapp: Smartphone,
  email: Mail,
  webform: Globe,
};

export default function OwnerDashboard() {
  const [orders, setOrders] = useState<any[]>([]);
  const [metrics, setMetrics] = useState<any>({});
  const [report, setReport] = useState<any>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null);
  const [mounted, setMounted] = useState(false);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError("");

      const [ordersRes, metricsRes, reportRes] =
        await Promise.allSettled([
          axios.get(`${API}/owner/orders/today`, {
            params: { owner_phone: OWNER }
          }),
          axios.get(`${API}/metrics/channels`),
          axios.get(`${API}/owner/report/today`, {
            params: { owner_phone: OWNER }
          }),
        ]);

      if (ordersRes.status === "fulfilled")
        setOrders(ordersRes.value.data.orders || []);
      if (metricsRes.status === "fulfilled")
        setMetrics(metricsRes.value.data || {});
      if (reportRes.status === "fulfilled")
        setReport(reportRes.value.data || {});

      setLastRefresh(new Date());
    } catch {
      setError("Failed to load — check FastAPI");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setMounted(true);
    setLastRefresh(new Date());
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const channelData = [
    { name: "WhatsApp", value: metrics.whatsapp?.total_conversations || 0 },
    { name: "Email",    value: metrics.email?.total_conversations || 0 },
    { name: "Web Form", value: metrics.webform?.total_conversations || 0 },
  ];

  const escalations =
    (metrics.whatsapp?.escalated || 0) +
    (metrics.email?.escalated || 0) +
    (metrics.webform?.escalated || 0);

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

        {/* Page Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Owner Dashboard
            </h1>
            <p className="text-sm text-gray-500 mt-1">
              {new Date().toLocaleDateString("en-PK", {
                weekday: "long",
                year: "numeric",
                month: "long",
                day: "numeric"
              })}
            </p>
          </div>
          <button
            onClick={fetchData}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-xl text-sm text-gray-600 hover:bg-gray-50 disabled:opacity-50 transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </button>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
            {error}
          </div>
        )}

        {/* Stats */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatCard
            title="Aaj ke Orders"
            value={report.total_orders || 0}
            subtitle="Today's total"
            icon={Package}
            color="amber"
            loading={loading}
          />
          <StatCard
            title="Customers"
            value={report.unique_customers || 0}
            subtitle="Unique buyers"
            icon={Users}
            color="blue"
            loading={loading}
          />
          <StatCard
            title="WhatsApp"
            value={report.channels?.whatsapp || 0}
            subtitle="Messages today"
            icon={Smartphone}
            color="green"
            loading={loading}
          />
          <StatCard
            title="Escalations"
            value={escalations}
            subtitle="Need attention"
            icon={AlertTriangle}
            color="red"
            loading={loading}
          />
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-2xl p-6 border border-gray-100">
            <h3 className="font-semibold text-gray-800 mb-4">
              Channel Breakdown
            </h3>
            {loading ? (
              <div className="h-48 bg-gray-50 rounded-xl animate-pulse" />
            ) : (
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie
                    data={channelData}
                    cx="50%" cy="50%"
                    innerRadius={50} outerRadius={80}
                    dataKey="value"
                  >
                    {channelData.map((_, i) => (
                      <Cell key={i} fill={CHANNEL_COLORS[i]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>

          <div className="lg:col-span-2 bg-white rounded-2xl p-6 border border-gray-100">
            <h3 className="font-semibold text-gray-800 mb-4">
              Today's Orders
            </h3>
            {loading ? (
              <div className="h-48 bg-gray-50 rounded-xl animate-pulse" />
            ) : orders.length > 0 ? (
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={orders.slice(0, 8).map((o, i) => ({
                  name: `#${i + 1}`,
                  items: o.products?.length || 1
                }))}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Bar dataKey="items" fill="#f59e0b" radius={[6,6,0,0]} name="Items" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-48 flex items-center justify-center text-gray-400 text-sm">
                No orders yet today
              </div>
            )}
          </div>
        </div>

        {/* Orders Table */}
        <div className="bg-white rounded-2xl border border-gray-100 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
            <h3 className="font-semibold text-gray-800">
              Recent Orders
            </h3>
            <span className="text-xs text-gray-400">
              Updated: {lastRefresh ? lastRefresh.toLocaleTimeString("en-PK") : "..."}
            </span>
          </div>

          {loading ? (
            <div className="p-6 space-y-3">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="h-12 bg-gray-50 rounded-xl animate-pulse" />
              ))}
            </div>
          ) : orders.length === 0 ? (
            <div className="p-12 text-center text-gray-400">
              <Package className="w-10 h-10 mx-auto mb-3 opacity-30" />
              <p className="text-sm">No orders today yet</p>
              <p className="text-xs mt-1">
                Submit a web form or send WhatsApp message
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-100">
                  <tr>
                    {["Order ID","Customer","Products","Area","Payment","Channel","Status","Time"].map(h => (
                      <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {orders.map((order: any, i: number) => {
                    const Icon = channelIcons[order.channel] || Globe;
                    return (
                      <tr key={i} className="hover:bg-gray-50 transition-colors">
                        <td className="px-4 py-3">
                          <span className="font-mono text-xs text-gray-600">
                            {order.order_number}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <p className="text-sm font-medium text-gray-800">
                            {order.customer_name}
                          </p>
                          <p className="text-xs text-gray-400">
                            {order.customer_phone}
                          </p>
                        </td>
                        <td className="px-4 py-3">
                          <p className="text-sm text-gray-600 max-w-32 truncate">
                            {Array.isArray(order.products)
                              ? order.products.join(", ")
                              : order.products}
                          </p>
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-600">
                          {order.delivery_area}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-600">
                          {order.payment_method}
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-1.5">
                            <Icon className="w-3.5 h-3.5 text-gray-400" />
                            <span className="text-xs text-gray-500 capitalize">
                              {order.channel}
                            </span>
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <span className={`inline-flex px-2.5 py-1 rounded-lg text-xs font-medium capitalize ${statusStyles[order.status] || "bg-gray-50 text-gray-600"}`}>
                            {order.status}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-xs text-gray-400">
                          {order.time}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
