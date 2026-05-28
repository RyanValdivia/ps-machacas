import { type LucideIcon } from 'lucide-react';

interface StatsCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  iconColor: string;
  borderColor: string;
  trend?: {
    value: number;
    isPositive: boolean;
  };
}

const StatsCard = ({ title, value, subtitle, icon: Icon, iconColor, borderColor, trend }: StatsCardProps) => {
  return (
    <div className={`bg-white rounded-xl shadow-lg p-6 border-l-4 ${borderColor} hover:shadow-xl transition-shadow`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-3">
          <div className={`p-2 rounded-lg ${iconColor}`}>
            <Icon className="w-6 h-6 text-white" />
          </div>
          <h3 className="text-sm font-semibold text-gray-600 uppercase tracking-wide">{title}</h3>
        </div>
        {trend && (
          <span className={`text-xs font-semibold ${trend.isPositive ? 'text-green-600' : 'text-red-600'}`}>
            {trend.isPositive ? '↑' : '↓'} {Math.abs(trend.value)}%
          </span>
        )}
      </div>
      <p className="text-3xl font-bold text-gray-900 mb-1">{value}</p>
      {subtitle && <p className="text-sm text-gray-500">{subtitle}</p>}
    </div>
  );
};

export default StatsCard;
