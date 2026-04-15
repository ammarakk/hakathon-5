import { LucideIcon } from "lucide-react";

interface Props {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  color: "amber" | "green" | "blue" | "red";
  loading?: boolean;
}

const colorMap = {
  amber: "bg-amber-50 text-amber-600",
  green: "bg-green-50 text-green-600",
  blue:  "bg-blue-50 text-blue-600",
  red:   "bg-red-50 text-red-600",
};

export default function StatCard({
  title, value, subtitle,
  icon: Icon, color, loading
}: Props) {
  if (loading) {
    return (
      <div className="bg-white rounded-2xl p-5 border border-gray-100 animate-pulse">
        <div className="h-4 bg-gray-100 rounded w-24 mb-3" />
        <div className="h-8 bg-gray-100 rounded w-16 mb-2" />
        <div className="h-3 bg-gray-100 rounded w-20" />
      </div>
    );
  }
  return (
    <div className="bg-white rounded-2xl p-5 border border-gray-100 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between mb-3">
        <p className="text-sm text-gray-500 font-medium">{title}</p>
        <div className={`p-2 rounded-xl ${colorMap[color]}`}>
          <Icon className="w-4 h-4" />
        </div>
      </div>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
      {subtitle && (
        <p className="text-xs text-gray-400 mt-1">{subtitle}</p>
      )}
    </div>
  );
}
