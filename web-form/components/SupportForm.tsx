// web-form/components/SupportForm.tsx
"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import axios from "axios";
import {
  CheckCircle,
  AlertCircle,
  Loader2,
  Send,
  Package,
  MessageSquare,
  Search,
  Phone,
} from "lucide-react";

// ─── Validation Schema ────────────────────────
const formSchema = z.object({
  name: z
    .string()
    .min(2, "Name must be at least 2 characters")
    .max(100),
  email: z
    .string()
    .email("Please enter a valid email"),
  phone: z
    .string()
    .optional()
    .refine(
      (val) =>
        !val ||
        /^(\+92|0)?[0-9]{10,11}$/.test(
          val.replace(/-/g, "")
        ),
      "Enter valid Pakistani number"
    ),
  subject: z
    .string()
    .min(5, "Subject too short")
    .max(200),
  category: z.enum([
    "product_query",
    "order",
    "tracking",
    "complaint",
    "general",
  ]),
  message: z
    .string()
    .min(10, "Message too short")
    .max(2000, "Message too long"),
});

type FormData = z.infer<typeof formSchema>;

// ─── Category Options ─────────────────────────
const CATEGORIES = [
  {
    value: "product_query",
    label: "Product Query / Product Inquiry",
    icon: Search,
    color: "text-purple-600",
  },
  {
    value: "order",
    label: "Place Order / Order Dena",
    icon: Package,
    color: "text-green-600",
  },
  {
    value: "tracking",
    label: "Order Tracking / Track Karna",
    icon: Phone,
    color: "text-blue-600",
  },
  {
    value: "complaint",
    label: "Complaint / Shikayat",
    icon: AlertCircle,
    color: "text-red-600",
  },
  {
    value: "general",
    label: "General Inquiry / Aam Sawal",
    icon: MessageSquare,
    color: "text-gray-600",
  },
];

// ─── Ticket Status Checker ────────────────────
function TicketStatusChecker() {
  const [ticketId, setTicketId] = useState("");
  const [status, setStatus] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const checkStatus = async () => {
    if (!ticketId.trim()) return;
    setLoading(true);
    setError("");
    setStatus(null);

    try {
      const res = await axios.get(
        `${process.env.NEXT_PUBLIC_API_URL}/support/ticket/${ticketId}`
      );
      setStatus(res.data);
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          "Ticket not found. Please check the ID."
      );
    } finally {
      setLoading(false);
    }
  };

  const statusColors: Record<string, string> = {
    open: "bg-yellow-100 text-yellow-800",
    in_progress: "bg-blue-100 text-blue-800",
    resolved: "bg-green-100 text-green-800",
    escalated: "bg-red-100 text-red-800",
    closed: "bg-gray-100 text-gray-800",
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">
        🔍 Track Your Ticket / Ticket Track Karein
      </h3>

      <div className="flex gap-2">
        <input
          type="text"
          value={ticketId}
          onChange={(e) => setTicketId(e.target.value)}
          placeholder="Enter Ticket ID (e.g. TKT-001000)"
          className="flex-1 px-4 py-2 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-amber-400 text-sm"
          onKeyDown={(e) =>
            e.key === "Enter" && checkStatus()
          }
        />
        <button
          onClick={checkStatus}
          disabled={loading || !ticketId.trim()}
          className="px-4 py-2 bg-amber-500 text-white rounded-xl hover:bg-amber-600 disabled:opacity-50 transition-colors text-sm font-medium"
        >
          {loading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            "Check"
          )}
        </button>
      </div>

      {error && (
        <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
          {error}
        </div>
      )}

      {status && (
        <div className="mt-4 p-4 bg-gray-50 rounded-xl space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-600">
              Ticket Number
            </span>
            <span className="font-mono text-sm font-bold text-gray-800">
              {status.ticket_number}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-600">
              Status
            </span>
            <span
              className={`px-3 py-1 rounded-full text-xs font-semibold capitalize ${
                statusColors[status.status] ||
                "bg-gray-100 text-gray-800"
              }`}
            >
              {status.status.replace("_", " ")}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-600">
              Channel
            </span>
            <span className="text-sm text-gray-700 capitalize">
              {status.channel}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-600">
              Created
            </span>
            <span className="text-sm text-gray-700">
              {new Date(
                status.created_at
              ).toLocaleDateString("en-PK")}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

// ─── Success Screen ───────────────────────────
function SuccessScreen({
  ticketId,
  response,
  onReset,
}: {
  ticketId: string;
  response: string;
  onReset: () => void;
}) {
  return (
    <div className="text-center py-8 px-4">
      <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
        <CheckCircle className="w-10 h-10 text-green-600" />
      </div>

      <h2 className="text-2xl font-bold text-gray-800 mb-2">
        Shukriya! / Thank You! 🌹
      </h2>
      <p className="text-gray-500 mb-6">
        Aapka message hamein mil gaya hai.
        <br />
        Your message has been received.
      </p>

      {ticketId && ticketId !== "PENDING" && (
        <div className="bg-amber-50 border border-amber-200 rounded-2xl p-4 mb-6">
          <p className="text-sm text-amber-700 font-medium mb-1">
            Aapka Ticket ID / Your Ticket ID:
          </p>
          <p className="text-2xl font-mono font-bold text-amber-600">
            {ticketId}
          </p>
          <p className="text-xs text-amber-500 mt-1">
            Save this ID to track your request
          </p>
        </div>
      )}

      {response && (
        <div className="bg-blue-50 border border-blue-200 rounded-2xl p-4 mb-6 text-left">
          <p className="text-sm font-semibold text-blue-700 mb-2">
            🤖 AI Response:
          </p>
          <p className="text-sm text-blue-800 whitespace-pre-wrap">
            {response}
          </p>
        </div>
      )}

      <div className="bg-gray-50 rounded-2xl p-4 mb-6 text-sm text-gray-600">
        <p>⏱️ Expected response: within 2 hours</p>
        <p className="mt-1">
          📱 Ya WhatsApp karein:{" "}
          {process.env.NEXT_PUBLIC_BUSINESS_PHONE}
        </p>
      </div>

      <button
        onClick={onReset}
        className="px-6 py-3 bg-amber-500 text-white rounded-xl hover:bg-amber-600 transition-colors font-medium"
      >
        Submit Another Request
      </button>
    </div>
  );
}

// ─── Main Support Form ────────────────────────
export default function SupportForm() {
  const [submitted, setSubmitted] = useState(false);
  const [ticketId, setTicketId] = useState("");
  const [aiResponse, setAiResponse] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [serverError, setServerError] = useState("");

  const {
    register,
    handleSubmit,
    reset,
    watch,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      category: "general",
    },
  });

  const selectedCategory = watch("category");

  const onSubmit = async (data: FormData) => {
    setSubmitting(true);
    setServerError("");

    try {
      const res = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/support/submit`,
        {
          name: data.name,
          email: data.email,
          phone: data.phone || "",
          subject: data.subject,
          category: data.category,
          message: data.message,
        }
      );

      setTicketId(res.data.ticket_id || "");
      setAiResponse(res.data.response || "");
      setSubmitted(true);
    } catch (err: any) {
      setServerError(
        err.response?.data?.detail ||
          "Submission failed. Please try again."
      );
    } finally {
      setSubmitting(false);
    }
  };

  const handleReset = () => {
    setSubmitted(false);
    setTicketId("");
    setAiResponse("");
    setServerError("");
    reset();
  };

  if (submitted) {
    return (
      <div className="max-w-lg mx-auto">
        <SuccessScreen
          ticketId={ticketId}
          response={aiResponse}
          onReset={handleReset}
        />
      </div>
    );
  }

  return (
    <div className="max-w-lg mx-auto space-y-6">
      {/* Header */}
      <div className="text-center">
        <div className="w-16 h-16 bg-amber-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <span className="text-3xl">🌹</span>
        </div>
        <h1 className="text-2xl font-bold text-gray-800">
          Nur Scents Support
        </h1>
        <p className="text-gray-500 mt-1 text-sm">
          Hamse rabta karein / Get in touch with us
        </p>
      </div>

      {/* Main Form */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <form
          onSubmit={handleSubmit(onSubmit)}
          className="space-y-5"
        >
          {/* Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Aapka Naam / Your Name{" "}
              <span className="text-red-500">*</span>
            </label>
            <input
              {...register("name")}
              placeholder="Ahmed Khan"
              className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 focus:ring-amber-400 text-sm transition-colors ${
                errors.name
                  ? "border-red-400 bg-red-50"
                  : "border-gray-200"
              }`}
            />
            {errors.name && (
              <p className="mt-1 text-xs text-red-600">
                {errors.name.message}
              </p>
            )}
          </div>

          {/* Email */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email{" "}
              <span className="text-red-500">*</span>
            </label>
            <input
              {...register("email")}
              type="email"
              placeholder="ahmed@gmail.com"
              className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 focus:ring-amber-400 text-sm transition-colors ${
                errors.email
                  ? "border-red-400 bg-red-50"
                  : "border-gray-200"
              }`}
            />
            {errors.email && (
              <p className="mt-1 text-xs text-red-600">
                {errors.email.message}
              </p>
            )}
          </div>

          {/* Phone */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Phone / WhatsApp Number{" "}
              <span className="text-gray-400 text-xs">
                (Optional)
              </span>
            </label>
            <input
              {...register("phone")}
              placeholder="0300-1234567"
              className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 focus:ring-amber-400 text-sm transition-colors ${
                errors.phone
                  ? "border-red-400 bg-red-50"
                  : "border-gray-200"
              }`}
            />
            {errors.phone && (
              <p className="mt-1 text-xs text-red-600">
                {errors.phone.message}
              </p>
            )}
          </div>

          {/* Category */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Category / Qisam{" "}
              <span className="text-red-500">*</span>
            </label>
            <div className="grid grid-cols-1 gap-2">
              {CATEGORIES.map((cat) => {
                const Icon = cat.icon;
                const isSelected =
                  selectedCategory === cat.value;
                return (
                  <label
                    key={cat.value}
                    className={`flex items-center gap-3 p-3 border rounded-xl cursor-pointer transition-all ${
                      isSelected
                        ? "border-amber-400 bg-amber-50"
                        : "border-gray-200 hover:border-gray-300"
                    }`}
                  >
                    <input
                      type="radio"
                      value={cat.value}
                      {...register("category")}
                      className="hidden"
                    />
                    <Icon
                      className={`w-4 h-4 ${cat.color}`}
                    />
                    <span className="text-sm text-gray-700">
                      {cat.label}
                    </span>
                    {isSelected && (
                      <CheckCircle className="w-4 h-4 text-amber-500 ml-auto" />
                    )}
                  </label>
                );
              })}
            </div>
          </div>

          {/* Subject */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Subject / Mauzu{" "}
              <span className="text-red-500">*</span>
            </label>
            <input
              {...register("subject")}
              placeholder="e.g. Oud attar price inquiry"
              className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 focus:ring-amber-400 text-sm transition-colors ${
                errors.subject
                  ? "border-red-400 bg-red-50"
                  : "border-gray-200"
              }`}
            />
            {errors.subject && (
              <p className="mt-1 text-xs text-red-600">
                {errors.subject.message}
              </p>
            )}
          </div>

          {/* Message */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Message / Paigham{" "}
              <span className="text-red-500">*</span>
            </label>
            <textarea
              {...register("message")}
              rows={4}
              placeholder="Apna sawal ya masla yahan likhein... / Write your question or issue here..."
              className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 focus:ring-amber-400 text-sm resize-none transition-colors ${
                errors.message
                  ? "border-red-400 bg-red-50"
                  : "border-gray-200"
              }`}
            />
            {errors.message && (
              <p className="mt-1 text-xs text-red-600">
                {errors.message.message}
              </p>
            )}
          </div>

          {/* Server Error */}
          {serverError && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm flex items-center gap-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              {serverError}
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={submitting}
            className="w-full py-4 bg-amber-500 text-white rounded-xl font-semibold hover:bg-amber-600 disabled:opacity-70 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2 text-base"
          >
            {submitting ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Bhej rahe hain... / Sending...
              </>
            ) : (
              <>
                <Send className="w-5 h-5" />
                Bhejein / Submit Request
              </>
            )}
          </button>
        </form>
      </div>

      {/* Ticket Status Checker */}
      <TicketStatusChecker />

      {/* Contact Info */}
      <div className="bg-amber-50 border border-amber-200 rounded-2xl p-4 text-center">
        <p className="text-sm text-amber-800 font-medium">
          🕐 Response time: within 2 hours
        </p>
        <p className="text-xs text-amber-600 mt-1">
          Ya seedha WhatsApp karein:{" "}
          {process.env.NEXT_PUBLIC_BUSINESS_PHONE}
        </p>
      </div>
    </div>
  );
}
