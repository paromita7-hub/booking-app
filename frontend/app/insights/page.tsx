"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/Header";
import { api } from "@/lib/api";
import { OperationalInsight, TopicDistribution } from "@/types";
import {
  AlertTriangle,
  TrendingDown,
  TrendingUp,
  CheckCircle2,
  Info,
  Building,
  Quote,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { formatRating } from "@/lib/utils";

export default function OperationalInsightsPage() {
  const [selectedPropertyId, setSelectedPropertyId] = useState<number | null>(null);
  const [insights, setInsights] = useState<OperationalInsight[]>([]);
  const [topics, setTopics] = useState<TopicDistribution[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      api.getOperationalInsights(selectedPropertyId || undefined),
      api.getTopicDistributions(selectedPropertyId || undefined),
    ])
      .then(([insightData, topicData]) => {
        setInsights(insightData);
        setTopics(topicData);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [selectedPropertyId]);

  return (
    <div className="flex-1 flex flex-col min-h-screen">
      <Header
        selectedPropertyId={selectedPropertyId}
        onPropertyChange={setSelectedPropertyId}
      />

      <div className="p-8 space-y-8 max-w-7xl mx-auto w-full">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">
            Operational Insights & Action Center
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Prioritized operational problem detection comparing current week-to-date with previous period baselines.
          </p>
        </div>

        {/* Informative Disclaimer Card distinguishing Measured Data from Interpretation */}
        <div className="bg-blue-50 border border-blue-200 p-4 rounded-xl flex items-start gap-3 text-xs text-blue-900">
          <Info size={18} className="text-blue-700 flex-shrink-0 mt-0.5" />
          <div className="space-y-1">
            <strong>Methodology Note:</strong> Denominators are strictly documented. Topic percentages reflect the proportion of negative reviews mentioning that specific topic during the evaluated calendar period. A single review may discuss multiple operational topics.
          </div>
        </div>

        {/* Operational Topics Overview Chart (Pos vs Neg) */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h3 className="font-semibold text-slate-900 text-base">
            Topic Sentiment Volume (Positive vs Negative Mentions)
          </h3>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={topics}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                <XAxis dataKey="topic" stroke="#64748B" fontSize={11} interval={0} angle={-15} textAnchor="end" height={50} />
                <YAxis stroke="#64748B" fontSize={12} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#FFFFFF",
                    borderRadius: "8px",
                    border: "1px solid #CBD5E1",
                    fontSize: "12px",
                  }}
                />
                <Legend wrapperStyle={{ fontSize: "12px" }} />
                <Bar dataKey="positive_count" name="Positive Mentions" fill="#15803D" radius={[4, 4, 0, 0]} />
                <Bar dataKey="negative_count" name="Negative Complaints" fill="#DC2626" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Dynamic Operational Insights Feed */}
        <div className="space-y-6">
          <h2 className="text-lg font-bold text-slate-900">
            Detected Operational Shifts & Root-Cause Evidence
          </h2>

          {loading ? (
            <div className="text-center py-16 bg-white rounded-xl border border-slate-200 text-slate-500 text-sm">
              Analyzing review patterns...
            </div>
          ) : insights.length === 0 ? (
            <div className="text-center py-16 bg-white rounded-xl border border-slate-200 text-slate-500 text-sm">
              No significant operational shifts detected for the selected period.
            </div>
          ) : (
            insights.map((ins, idx) => {
              const isWarning = ins.category === "warning";
              const isPositive = ins.category === "positive";

              return (
                <div
                  key={idx}
                  className={`bg-white rounded-xl border p-6 shadow-sm space-y-5 transition-all ${
                    isWarning
                      ? "border-rose-200 bg-rose-50/10"
                      : isPositive
                      ? "border-emerald-200 bg-emerald-50/10"
                      : "border-slate-200"
                  }`}
                >
                  {/* Insight Header */}
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-slate-100 pb-4">
                    <div className="flex items-start gap-3">
                      {isWarning ? (
                        <AlertTriangle size={22} className="text-rose-600 flex-shrink-0 mt-0.5" />
                      ) : isPositive ? (
                        <CheckCircle2 size={22} className="text-emerald-600 flex-shrink-0 mt-0.5" />
                      ) : (
                        <Info size={22} className="text-slate-500 flex-shrink-0 mt-0.5" />
                      )}
                      <div>
                        <div className="flex items-center gap-2">
                          <span
                            className={`text-[11px] font-bold uppercase tracking-wider px-2 py-0.5 rounded ${
                              isWarning
                                ? "bg-rose-100 text-rose-800"
                                : isPositive
                                ? "bg-emerald-100 text-emerald-800"
                                : "bg-slate-100 text-slate-800"
                            }`}
                          >
                            {ins.topic}
                          </span>
                          <span className="text-xs text-slate-400">•</span>
                          <span className="text-xs font-semibold text-slate-500">
                            {isWarning ? "Worsening Trend" : isPositive ? "Improving Trend" : "Stable Baseline"}
                          </span>
                        </div>
                        <h3 className="font-bold text-slate-900 text-base mt-1">
                          {ins.headline}
                        </h3>
                      </div>
                    </div>

                    {/* Numeric Metric Delta */}
                    <div className="flex items-center gap-3">
                      <div className="text-right">
                        <div className="text-xs text-slate-400">Current vs Prev Week</div>
                        <div className="text-sm font-extrabold text-slate-900">
                          {ins.negative_reviews_percentage_current}% vs {ins.negative_reviews_percentage_previous}%
                        </div>
                      </div>
                      <div
                        className={`flex items-center gap-1 font-bold text-sm px-2.5 py-1 rounded-lg ${
                          ins.percentage_change > 0
                            ? "bg-rose-100 text-rose-800"
                            : "bg-emerald-100 text-emerald-800"
                        }`}
                      >
                        {ins.percentage_change > 0 ? (
                          <TrendingUp size={16} />
                        ) : (
                          <TrendingDown size={16} />
                        )}
                        <span>
                          {ins.percentage_change > 0 ? `+${ins.percentage_change}%` : `${ins.percentage_change}%`}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Operational Interpretation vs Measured Data */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
                    <div className="bg-slate-50 p-3.5 rounded-lg border border-slate-200 md:col-span-2">
                      <strong className="text-slate-800 block mb-1">
                        Operational Interpretation & Corrective Action:
                      </strong>
                      <p className="text-slate-600 leading-relaxed">{ins.interpretation}</p>
                    </div>

                    <div className="bg-slate-50 p-3.5 rounded-lg border border-slate-200">
                      <strong className="text-slate-800 block mb-1">
                        Most Affected Properties:
                      </strong>
                      <div className="space-y-1 mt-1 text-slate-600">
                        {ins.affected_properties.length === 0 ? (
                          <span className="text-slate-400 italic">None currently flagged</span>
                        ) : (
                          ins.affected_properties.map((propName) => (
                            <div key={propName} className="flex items-center gap-1.5 font-medium">
                              <Building size={13} className="text-blue-700" />
                              <span>{propName}</span>
                            </div>
                          ))
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Supporting Reviews Evidence */}
                  {ins.supporting_reviews && ins.supporting_reviews.length > 0 && (
                    <div className="space-y-2 pt-2">
                      <div className="flex items-center gap-1.5 text-xs font-bold text-slate-700">
                        <Quote size={13} className="text-slate-400" />
                        <span>Supporting Guest Review Evidence:</span>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                        {ins.supporting_reviews.map((rev) => (
                          <div
                            key={rev.id}
                            className="p-3 bg-white rounded-lg border border-slate-200 text-xs space-y-1.5"
                          >
                            <div className="flex items-center justify-between text-[11px] text-slate-500">
                              <span className="font-semibold text-slate-800">{rev.property_name}</span>
                              <span className="font-bold text-slate-900 bg-slate-100 px-1.5 py-0.5 rounded">
                                ★ {formatRating(rev.rating)}
                              </span>
                            </div>
                            {rev.title && (
                              <div className="font-medium text-slate-800 truncate">{rev.title}</div>
                            )}
                            {rev.negative_text && (
                              <p className="text-rose-800 bg-rose-50/60 p-2 rounded border border-rose-100 text-[11px] leading-relaxed italic">
                                &ldquo;{rev.negative_text}&rdquo;
                              </p>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
