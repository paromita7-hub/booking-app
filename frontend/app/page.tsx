"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/Header";
import { api } from "@/lib/api";
import {
  KPISummary,
  WeeklyTrendPoint,
  PropertyComparison,
  TopicDistribution,
  Review,
} from "@/types";
import {
  TrendingUp,
  TrendingDown,
  Star,
  ThumbsUp,
  ThumbsDown,
  AlertCircle,
  MessageSquare,
  Building2,
  Calendar,
} from "lucide-react";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { formatRating, formatDate, getSentimentBadgeColor } from "@/lib/utils";

export default function OverviewPage() {
  const [selectedPropertyId, setSelectedPropertyId] = useState<number | null>(null);
  const [kpi, setKpi] = useState<KPISummary | null>(null);
  const [trends, setTrends] = useState<WeeklyTrendPoint[]>([]);
  const [propertyComparisons, setPropertyComparisons] = useState<PropertyComparison[]>([]);
  const [topics, setTopics] = useState<TopicDistribution[]>([]);
  const [recentReviews, setRecentReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      api.getOverviewKPI(selectedPropertyId || undefined),
      api.getWeeklyTrends(selectedPropertyId || undefined, 6),
      api.getPropertyComparisons(),
      api.getTopicDistributions(selectedPropertyId || undefined),
      api.getReviews({
        property_id: selectedPropertyId || undefined,
        limit: 5,
        sort_by: "review_date",
        sort_order: "desc",
      }),
    ])
      .then(([kpiData, trendData, propData, topicData, reviewsData]) => {
        setKpi(kpiData);
        setTrends(trendData);
        setPropertyComparisons(propData);
        setTopics(topicData);
        setRecentReviews(reviewsData.items);
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
        {/* Page Title & Scope Note */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-slate-900">
              Operations & Performance Overview
            </h1>
            <p className="text-sm text-slate-500 mt-1">
              Performance metrics for Azzurro Hotels calculated in Australia/Sydney calendar weeks.
            </p>
          </div>
          {kpi && (
            <div className="flex items-center gap-2 bg-white px-3.5 py-2 rounded-lg border border-slate-200 text-xs text-slate-600 shadow-sm">
              <Calendar size={14} className="text-slate-400" />
              <span>
                Current Period: <strong className="text-slate-800">{kpi.period_start}</strong> to{" "}
                <strong className="text-slate-800">{kpi.period_end}</strong> ({kpi.current_week_reviews_count} reviews)
              </span>
            </div>
          )}
        </div>

        {/* 6 Top KPI Cards */}
        {kpi && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
            {/* Avg Rating This Week */}
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                  Rating (Current)
                </span>
                <Star size={18} className="text-amber-500 fill-amber-400" />
              </div>
              <div className="mt-3">
                <div className="text-3xl font-bold text-slate-900">
                  {formatRating(kpi.current_week_avg_rating)}
                  <span className="text-sm font-normal text-slate-400 ml-1">/10</span>
                </div>
                <div className="text-xs text-slate-500 mt-1">
                  Based on {kpi.current_week_reviews_count} reviews
                </div>
              </div>
            </div>

            {/* Avg Rating Prev Week */}
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                  Rating (Previous)
                </span>
                <Calendar size={18} className="text-slate-400" />
              </div>
              <div className="mt-3">
                <div className="text-3xl font-bold text-slate-700">
                  {formatRating(kpi.previous_week_avg_rating)}
                  <span className="text-sm font-normal text-slate-400 ml-1">/10</span>
                </div>
                <div className="text-xs text-slate-500 mt-1">
                  {kpi.previous_period_start} ({kpi.previous_week_reviews_count} revs)
                </div>
              </div>
            </div>

            {/* Weekly Change */}
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                  WoW Change
                </span>
                {kpi.rating_change >= 0 ? (
                  <TrendingUp size={18} className="text-emerald-600" />
                ) : (
                  <TrendingDown size={18} className="text-rose-600" />
                )}
              </div>
              <div className="mt-3">
                <div
                  className={`text-3xl font-bold ${
                    kpi.rating_change >= 0 ? "text-emerald-600" : "text-rose-600"
                  }`}
                >
                  {kpi.rating_change > 0 ? `+${kpi.rating_change}` : kpi.rating_change}
                </div>
                <div className="text-xs text-slate-500 mt-1">vs previous elapsed week</div>
              </div>
            </div>

            {/* Total Reviews */}
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                  Total Reviews
                </span>
                <MessageSquare size={18} className="text-blue-600" />
              </div>
              <div className="mt-3">
                <div className="text-3xl font-bold text-slate-900">
                  {kpi.total_reviews_count}
                </div>
                <div className="text-xs text-slate-500 mt-1">Monitored across portfolio</div>
              </div>
            </div>

            {/* Positive % */}
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                  Positive Reviews
                </span>
                <ThumbsUp size={18} className="text-emerald-600" />
              </div>
              <div className="mt-3">
                <div className="text-3xl font-bold text-emerald-700">
                  {kpi.positive_review_percentage}%
                </div>
                <div className="text-xs text-slate-500 mt-1">High sentiment feedback</div>
              </div>
            </div>

            {/* Negative % */}
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                  Negative Reviews
                </span>
                <ThumbsDown size={18} className="text-rose-600" />
              </div>
              <div className="mt-3">
                <div className="text-3xl font-bold text-rose-700">
                  {kpi.negative_review_percentage}%
                </div>
                <div className="text-xs text-slate-500 mt-1">Requires ops intervention</div>
              </div>
            </div>
          </div>
        )}

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Weekly Rating Trend Line Chart */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-semibold text-slate-900 text-base">Weekly Rating Trend</h3>
                <p className="text-xs text-slate-500">Average guest rating evolution over time</p>
              </div>
            </div>
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={trends}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                  <XAxis dataKey="week_label" stroke="#64748B" fontSize={12} tickLine={false} />
                  <YAxis domain={[0, 10]} stroke="#64748B" fontSize={12} tickLine={false} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#FFFFFF",
                      borderRadius: "8px",
                      border: "1px solid #CBD5E1",
                      fontSize: "12px",
                    }}
                  />
                  <Line
                    type="monotone"
                    dataKey="average_rating"
                    name="Avg Rating"
                    stroke="#1E3A8A"
                    strokeWidth={2.5}
                    dot={{ fill: "#1E3A8A", r: 4 }}
                    activeDot={{ r: 6 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Positive vs Negative Volume Bar Chart */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-semibold text-slate-900 text-base">
                  Sentiment Volume Breakdown
                </h3>
                <p className="text-xs text-slate-500">Weekly count of positive vs negative feedback</p>
              </div>
            </div>
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={trends}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                  <XAxis dataKey="week_label" stroke="#64748B" fontSize={12} tickLine={false} />
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
                  <Bar dataKey="positive_count" name="Positive" fill="#15803D" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="negative_count" name="Negative" fill="#B91C1C" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Property-Wise Rating Comparison */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-semibold text-slate-900 text-base">
                  Property Performance Comparison
                </h3>
                <p className="text-xs text-slate-500">Overall ratings across Azzurro properties</p>
              </div>
            </div>
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={propertyComparisons} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#E2E8F0" />
                  <XAxis type="number" domain={[0, 10]} stroke="#64748B" fontSize={12} />
                  <YAxis
                    dataKey="property_name"
                    type="category"
                    stroke="#64748B"
                    fontSize={11}
                    width={130}
                    tickLine={false}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#FFFFFF",
                      borderRadius: "8px",
                      border: "1px solid #CBD5E1",
                      fontSize: "12px",
                    }}
                  />
                  <Bar dataKey="average_rating" name="Rating" fill="#0284C7" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Operational Issue Distribution */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-semibold text-slate-900 text-base">
                  Operational Issue Distribution
                </h3>
                <p className="text-xs text-slate-500">
                  Negative mentions across the 8 standard operational categories
                </p>
              </div>
            </div>
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={topics.slice(0, 6)} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#E2E8F0" />
                  <XAxis type="number" stroke="#64748B" fontSize={12} />
                  <YAxis
                    dataKey="topic"
                    type="category"
                    stroke="#64748B"
                    fontSize={11}
                    width={130}
                    tickLine={false}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#FFFFFF",
                      borderRadius: "8px",
                      border: "1px solid #CBD5E1",
                      fontSize: "12px",
                    }}
                  />
                  <Bar dataKey="negative_count" name="Complaints" fill="#DC2626" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Bottom Section: Top Recurring Issues & Recent Reviews */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Top Recurring Issues */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4 lg:col-span-1">
            <div className="flex items-center gap-2">
              <AlertCircle size={20} className="text-rose-600" />
              <h3 className="font-semibold text-slate-900 text-base">Top Recurring Issues</h3>
            </div>
            <p className="text-xs text-slate-500">
              Operational categories requiring priority attention from hotel management.
            </p>
            <div className="space-y-3 mt-4">
              {topics
                .filter((t) => t.negative_count > 0)
                .slice(0, 4)
                .map((t, idx) => (
                  <div
                    key={t.topic}
                    className="p-3.5 rounded-lg border border-slate-200 bg-slate-50 flex flex-col gap-1"
                  >
                    <div className="flex items-center justify-between text-sm font-semibold text-slate-800">
                      <span>
                        #{idx + 1} {t.topic}
                      </span>
                      <span className="text-rose-700 bg-rose-50 border border-rose-200 px-2 py-0.5 rounded text-xs">
                        {t.negative_count} complaints
                      </span>
                    </div>
                    <div className="text-xs text-slate-500">
                      Mentioned in {t.negative_percentage_of_negative_reviews}% of all negative reviews.
                    </div>
                  </div>
                ))}
            </div>
          </div>

          {/* Recent Guest Reviews Feed */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4 lg:col-span-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <MessageSquare size={20} className="text-blue-700" />
                <h3 className="font-semibold text-slate-900 text-base">Recent Guest Reviews</h3>
              </div>
              <a
                href="/reviews"
                className="text-xs font-semibold text-blue-800 hover:underline"
              >
                View all reviews &rarr;
              </a>
            </div>
            <div className="space-y-3">
              {recentReviews.map((r) => (
                <div
                  key={r.id}
                  className="p-4 rounded-lg border border-slate-200 hover:border-slate-300 transition-all flex flex-col gap-2"
                >
                  <div className="flex items-center justify-between text-xs text-slate-500">
                    <span className="font-semibold text-slate-800">{r.property_name}</span>
                    <div className="flex items-center gap-2">
                      <span
                        className={`px-2 py-0.5 rounded border text-[11px] font-medium ${getSentimentBadgeColor(
                          r.overall_sentiment || "Neutral"
                        )}`}
                      >
                        {r.overall_sentiment}
                      </span>
                      <span className="font-bold text-slate-900 bg-slate-100 px-2 py-0.5 rounded">
                        ★ {formatRating(r.rating)}
                      </span>
                      <span>{formatDate(r.review_date)}</span>
                    </div>
                  </div>
                  {r.title && <div className="text-sm font-semibold text-slate-800">{r.title}</div>}
                  {r.negative_text && (
                    <div className="text-xs text-rose-800 bg-rose-50/70 p-2 rounded border border-rose-100">
                      <strong>Negative:</strong> {r.negative_text}
                    </div>
                  )}
                  {r.positive_text && (
                    <div className="text-xs text-emerald-800 bg-emerald-50/70 p-2 rounded border border-emerald-100">
                      <strong>Positive:</strong> {r.positive_text}
                    </div>
                  )}
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {r.topics.map((t) => (
                      <span
                        key={t.topic}
                        className="text-[10px] font-medium px-2 py-0.5 rounded bg-slate-100 text-slate-600 border border-slate-200"
                      >
                        {t.topic} ({t.sentiment})
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
