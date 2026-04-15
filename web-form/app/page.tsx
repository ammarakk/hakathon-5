"use client";
import { useState } from "react";
import axios from "axios";
import {
  Package, MessageSquare, Search,
  CheckCircle, Clock, Truck,
  AlertCircle, Phone
} from "lucide-react";
import Header from "@/components/shared/Header";
import SupportForm from "@/components/SupportForm";

const API = process.env.NEXT_PUBLIC_API_URL
  || "http://localhost:8000";

const STATUS_STEPS = [
  { key: "confirmed",  label: "Confirmed",  icon: CheckCircle },
  { key: "processing", label: "Processing", icon: Clock },
  { key: "dispatched", label: "Dispatched", icon: Truck },
  { key: "delivered",  label: "Delivered",  icon: Package },
];

function OrderCard({ order }: { order: any }) {
  const currentStep = STATUS_STEPS.findIndex(
    s => s.key === order.status
  );

  return (
    <div className="bg-white rounded-2xl border border-gray-100 p-6 mt-4">
      <div className="flex items-start justify-between mb-6">
        <div>
          <p className="text-xs text-gray-400 mb-1">Order ID</p>
          <p className="font-mono font-bold text-gray-800">
            {order.order_number || order.ticket_number}
          </p>
        </div>
        <span className={`px-3 py-1.5 rounded-xl text-xs font-semibold capitalize ${
          order.status === "delivered"
            ? "bg-green-50 text-green-700"
            : order.status === "dispatched"
            ? "bg-purple-50 text-purple-700"
            : "bg-amber-50 text-amber-700"
        }`}>
          {order.status || "open"}
        </span>
      </div>

      {/* Timeline */}
      <div className="flex items-center mb-6">
        {STATUS_STEPS.map((step, i) => {
          const Icon = step.icon;
          const done = i <= currentStep;
          const isLast = i === STATUS_STEPS.length - 1;
          return (
            <div key={step.key} className="flex items-center flex-1">
              <div className="flex flex-col items-center">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${
                  done
                    ? "bg-amber-500 border-amber-500 text-white"
                    : "bg-white border-gray-200 text-gray-300"
                }`}>
                  <Icon className="w-3.5 h-3.5" />
                </div>
                <p className={`text-xs mt-1.5 font-medium ${
                  done ? "text-amber-600" : "text-gray-300"
                }`}>
                  {step.label}
                </p>
              </div>
              {!isLast && (
                <div className={`flex-1 h-0.5 mx-1 mb-4 ${
                  i < currentStep ? "bg-amber-400" : "bg-gray-100"
                }`} />
              )}
            </div>
          );
        })}
      </div>

      {/* Details */}
      <div className="grid grid-cols-2 gap-3 text-sm">
        {[
          { label: "Products", value: Array.isArray(order.products) ? order.products.join(", ") : order.products },
          { label: "Delivery Area", value: order.delivery_area },
          { label: "Payment", value: order.payment_method },
          { label: "Channel", value: order.channel },
        ].map(item => item.value && (
          <div key={item.label} className="bg-gray-50 rounded-xl p-3">
            <p className="text-xs text-gray-400 mb-1">{item.label}</p>
            <p className="font-medium text-gray-700 text-xs capitalize">
              {item.value}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

function OrderTracker() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [searched, setSearched] = useState(false);

  const search = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError("");
    setResults([]);
    setSearched(true);

    try {
      const res = await axios.get(
        `${API}/support/ticket/${query.trim()}`
      );
      setResults([res.data]);
    } catch {
      try {
        const res = await axios.get(
          `${API}/customers/lookup`,
          { params: { phone: query.trim() } }
        );
        if (res.data.found) {
          setResults([res.data.customer]);
        } else {
          setError("Koi order nahi mila. Check karein number ya order ID.");
        }
      } catch {
        setError("Koi order nahi mila. Check karein number ya order ID.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-gray-100 p-6">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 bg-amber-50 rounded-xl flex items-center justify-center">
          <Search className="w-5 h-5 text-amber-600" />
        </div>
        <div>
          <h3 className="font-semibold text-gray-800">
            Track Your Order
          </h3>
          <p className="text-xs text-gray-400">
            Order ID ya phone number daalein
          </p>
        </div>
      </div>

      <div className="flex gap-2">
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={e => e.key === "Enter" && search()}
          placeholder="NUR-20240101-0001 ya 0300-1234567"
          className="flex-1 px-4 py-3 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-amber-400"
        />
        <button
          onClick={search}
          disabled={loading || !query.trim()}
          className="px-5 py-3 bg-amber-500 text-white rounded-xl text-sm font-semibold hover:bg-amber-600 disabled:opacity-50 transition-colors"
        >
          {loading ? "..." : "Track"}
        </button>
      </div>

      {error && (
        <div className="mt-3 flex items-center gap-2 text-red-600 text-sm">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          {error}
        </div>
      )}

      {results.map((r, i) => (
        <OrderCard key={i} order={r} />
      ))}
    </div>
  );
}

export default function CustomerPortal() {
  const [tab, setTab] = useState<"track"|"support">("track");

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      {/* Hero */}
      <div className="bg-white border-b border-gray-100">
        <div className="max-w-2xl mx-auto px-4 py-10 text-center">
          <div className="w-16 h-16 bg-amber-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <span className="text-3xl">🌹</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            Nur Scents Support
          </h1>
          <p className="text-gray-500 text-sm">
            Premium Fragrances — Karachi, Pakistan
          </p>
          <div className="flex items-center justify-center gap-4 mt-6">
            <a
              href={`https://wa.me/923252886031`}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-4 py-2 bg-green-500 text-white rounded-xl text-sm font-medium hover:bg-green-600 transition-colors"
            >
              <Phone className="w-4 h-4" />
              WhatsApp Karein
            </a>
            <div className="flex items-center gap-2 text-sm text-gray-400">
              <Clock className="w-4 h-4" />
              Mon-Sat 10am-10pm
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-2xl mx-auto px-4 py-8">
        {/* Tabs */}
        <div className="flex bg-white border border-gray-200 rounded-2xl p-1 mb-6">
          <button
            onClick={() => setTab("track")}
            className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-xl text-sm font-medium transition-all ${
              tab === "track"
                ? "bg-amber-500 text-white shadow-sm"
                : "text-gray-500 hover:text-gray-700"
            }`}
          >
            <Package className="w-4 h-4" />
            Track Order
          </button>
          <button
            onClick={() => setTab("support")}
            className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-xl text-sm font-medium transition-all ${
              tab === "support"
                ? "bg-amber-500 text-white shadow-sm"
                : "text-gray-500 hover:text-gray-700"
            }`}
          >
            <MessageSquare className="w-4 h-4" />
            Get Support
          </button>
        </div>

        {tab === "track" ? <OrderTracker /> : <SupportForm />}

        {/* Trust Badges */}
        <div className="mt-6 grid grid-cols-3 gap-3">
          {[
            { icon: "⚡", title: "Fast Reply", sub: "Within 2 hours" },
            { icon: "🚚", title: "Karachi Delivery", sub: "1-3 days" },
            { icon: "✅", title: "Easy Return", sub: "7 days policy" },
          ].map(item => (
            <div key={item.title} className="bg-white rounded-xl p-3 border border-gray-100 text-center">
              <span className="text-xl">{item.icon}</span>
              <p className="text-xs font-semibold text-gray-700 mt-1">{item.title}</p>
              <p className="text-xs text-gray-400">{item.sub}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
