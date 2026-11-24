"use client";

import { useEffect, useState, useCallback } from "react";
import { Header } from "@/components/Header";
import { api } from "@/lib/api";
import { Review, Property } from "@/types";
import {
  Search,
  Filter,
  Download,
  Star,
  Globe,
  User,
  ChevronLeft,
  ChevronRight,
  RotateCcw,
} from "lucide-react";
import { formatRating, formatDate, getSentimentBadgeColor } from "@/lib/utils";

const TOPICS_LIST = [
  "Cleanliness",
  "Check-in experience",
  "Staff and receptionist behaviour",
  "Noise",
  "Facilities",
  "Location",
  "Room condition",
  "Value for money",
];

const SENTIMENTS_LIST = ["Positive", "Negative", "Mixed", "Neutral"];

export default function ReviewsExplorerPage() {
  const [properties, setProperties] = useState<Property[]>([]);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [page, setPage] = useState(1);
  const [limit] = useState(15);
  const [loading, setLoading] = useState(true);

  // Filters
  const [propertyId, setPropertyId] = useState<string>("");
  const [selectedTopic, setSelectedTopic] = useState<string>("");
  const [selectedSentiment, setSelectedSentiment] = useState<string>("");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [minRating, setMinRating] = useState<string>("");
  const [maxRating, setMaxRating] = useState<string>("");
  const [sortBy, setSortBy] = useState<string>("review_date");
  const [sortOrder, setSortOrder] = useState<string>("desc");

  useEffect(() => {
    api.getProperties().then(setProperties).catch(console.error);
  }, []);

  const loadReviews = useCallback(() => {
    setLoading(true);
    api.getReviews({
      property_id: propertyId ? parseInt(propertyId, 10) : undefined,
      topic: selectedTopic || undefined,
      sentiment: selectedSentiment || undefined,
      search: searchQuery || undefined,
      min_rating: minRating ? parseFloat(minRating) : undefined,
      max_rating: maxRating ? parseFloat(maxRating) : undefined,
      sort_by: sortBy,
      sort_order: sortOrder,
      page,
      limit,
    })
      .then((data) => {
        setReviews(data.items);
        setTotalCount(data.total);
        setTotalPages(data.pages);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [propertyId, selectedTopic, selectedSentiment, searchQuery, minRating, maxRating, sortBy, sortOrder, page, limit]);

  useEffect(() => {
    loadReviews();
  }, [loadReviews]);

  const handleResetFilters = () => {
    setPropertyId("");
    setSelectedTopic("");
    setSelectedSentiment("");
    setSearchQuery("");
    setMinRating("");
    setMaxRating("");
    setSortBy("review_date");
    setSortOrder("desc");
    setPage(1);
  };

  const handleExportCSV = () => {
    const query = propertyId ? `?property_id=${propertyId}` : "";
    window.open(`http://127.0.0.1:8000/api/reviews/export${query}`, "_blank");
  };

  return (
    <div className="flex-1 flex flex-col min-h-screen">
      <Header
        selectedPropertyId={propertyId ? parseInt(propertyId, 10) : null}
        onPropertyChange={(id) => {
          setPropertyId(id ? id.toString() : "");
          setPage(1);
        }}
      />

      <div className="p-8 space-y-6 max-w-7xl mx-auto w-full">
        {/* Header Title & Actions */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-slate-900">
              Reviews Explorer
            </h1>
            <p className="text-sm text-slate-500 mt-1">
              Search, filter, and inspect verified guest feedback across properties and operational topics.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={handleExportCSV}
              className="flex items-center gap-2 border border-slate-300 hover:bg-slate-50 text-slate-700 text-xs font-semibold px-4 py-2 rounded-lg transition shadow-sm"
            >
              <Download size={14} />
              <span>Export Filtered CSV</span>
            </button>
          </div>
        </div>

        {/* Filter Toolbar */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Search Input */}
            <div className="relative">
              <Search size={16} className="absolute left-3 top-3 text-slate-400" />
              <input
                type="text"
                placeholder="Search keywords in reviews..."
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  setPage(1);
                }}
                className="w-full pl-9 pr-3 py-2 text-xs border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Property Filter */}
            <div>
              <select
                value={propertyId}
                onChange={(e) => {
                  setPropertyId(e.target.value);
                  setPage(1);
                }}
                className="w-full py-2 px-3 text-xs border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
              >
                <option value="">All Properties</option>
                {properties.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Operational Topic Filter */}
            <div>
              <select
                value={selectedTopic}
                onChange={(e) => {
                  setSelectedTopic(e.target.value);
                  setPage(1);
                }}
                className="w-full py-2 px-3 text-xs border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
              >
                <option value="">All Operational Topics</option>
                {TOPICS_LIST.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            </div>

            {/* Sentiment Filter */}
            <div>
              <select
                value={selectedSentiment}
                onChange={(e) => {
                  setSelectedSentiment(e.target.value);
                  setPage(1);
                }}
                className="w-full py-2 px-3 text-xs border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
              >
                <option value="">All Sentiments</option>
                {SENTIMENTS_LIST.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Secondary Sorting and Reset Row */}
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pt-3 border-t border-slate-100 text-xs">
            <div className="flex items-center gap-3">
              <span className="text-slate-500 font-medium">Sort by:</span>
              <select
                value={`${sortBy}:${sortOrder}`}
                onChange={(e) => {
                  const [sb, so] = e.target.value.split(":");
                  setSortBy(sb);
                  setSortOrder(so);
                  setPage(1);
                }}
                className="border border-slate-300 rounded px-2.5 py-1 text-xs bg-white text-slate-700"
              >
                <option value="review_date:desc">Newest First</option>
                <option value="review_date:asc">Oldest First</option>
                <option value="rating:desc">Highest Rating</option>
                <option value="rating:asc">Lowest Rating</option>
              </select>

              <button
                onClick={handleResetFilters}
                className="flex items-center gap-1 text-slate-500 hover:text-slate-800 ml-2"
              >
                <RotateCcw size={12} />
                <span>Reset Filters</span>
              </button>
            </div>

            <div className="text-slate-500">
              Showing <strong>{reviews.length}</strong> of <strong>{totalCount}</strong> reviews
            </div>
          </div>
        </div>

        {/* Reviews Feed */}
        {loading ? (
          <div className="text-center py-16 bg-white rounded-xl border border-slate-200 text-slate-500 text-sm">
            Loading reviews...
          </div>
        ) : reviews.length === 0 ? (
          <div className="text-center py-16 bg-white rounded-xl border border-slate-200 text-slate-500 text-sm">
            No reviews match the selected filter criteria.
          </div>
        ) : (
          <div className="space-y-4">
            {reviews.map((r) => (
              <div
                key={r.id}
                className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm hover:border-slate-300 transition-all space-y-3"
              >
                {/* Review Header */}
                <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 pb-3">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-slate-900 text-sm">{r.property_name}</span>
                    {r.is_demo && (
                      <span className="text-[10px] uppercase font-bold bg-amber-100 text-amber-800 px-1.5 py-0.5 rounded">
                        DEMO
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-3 text-xs text-slate-500">
                    <span
                      className={`px-2 py-0.5 rounded border text-[11px] font-semibold ${getSentimentBadgeColor(
                        r.overall_sentiment || "Neutral"
                      )}`}
                    >
                      {r.overall_sentiment}
                    </span>
                    <span className="font-extrabold text-slate-900 bg-slate-100 px-2 py-0.5 rounded flex items-center gap-1">
                      <Star size={12} className="text-amber-500 fill-amber-400" />
                      {formatRating(r.rating)}
                    </span>
                    <span>{formatDate(r.review_date)}</span>
                  </div>
                </div>

                {/* Metadata tags */}
                <div className="flex flex-wrap items-center gap-4 text-xs text-slate-500">
                  {r.reviewer_country && (
                    <div className="flex items-center gap-1">
                      <Globe size={13} className="text-slate-400" />
                      <span>{r.reviewer_country}</span>
                    </div>
                  )}
                  {r.traveler_type && (
                    <div className="flex items-center gap-1">
                      <User size={13} className="text-slate-400" />
                      <span>{r.traveler_type}</span>
                    </div>
                  )}
                  {r.room_type && (
                    <span className="text-slate-400 italic">Room: {r.room_type}</span>
                  )}
                  {r.external_id && (
                    <span className="text-slate-400 font-mono text-[11px]">ID: {r.external_id}</span>
                  )}
                </div>

                {/* Review Title */}
                {r.title && (
                  <h4 className="font-semibold text-slate-900 text-sm">{r.title}</h4>
                )}

                {/* Positive & Negative Text Boxes */}
                <div className="space-y-2">
                  {r.positive_text && (
                    <div className="text-xs text-emerald-900 bg-emerald-50/80 p-3 rounded-lg border border-emerald-100">
                      <strong className="text-emerald-800">What they liked:</strong> {r.positive_text}
                    </div>
                  )}
                  {r.negative_text && (
                    <div className="text-xs text-rose-900 bg-rose-50/80 p-3 rounded-lg border border-rose-100">
                      <strong className="text-rose-800">What could be improved:</strong>{" "}
                      {r.negative_text}
                    </div>
                  )}
                </div>

                {/* Classified Topic Tags */}
                <div className="pt-2 flex flex-wrap items-center gap-2">
                  <span className="text-[11px] text-slate-400 font-medium">Classified Topics:</span>
                  {r.topics.length === 0 ? (
                    <span className="text-[11px] text-slate-400">None detected</span>
                  ) : (
                    r.topics.map((t) => (
                      <span
                        key={t.topic}
                        className={`text-[11px] font-medium px-2 py-0.5 rounded border ${
                          t.sentiment === "Positive"
                            ? "bg-emerald-50 text-emerald-800 border-emerald-200"
                            : t.sentiment === "Negative"
                            ? "bg-rose-50 text-rose-800 border-rose-200"
                            : "bg-slate-50 text-slate-700 border-slate-200"
                        }`}
                      >
                        {t.topic} • {t.sentiment}
                      </span>
                    ))
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Pagination Controls */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between bg-white px-6 py-4 rounded-xl border border-slate-200 text-xs text-slate-600 shadow-sm">
            <div>
              Page <strong>{page}</strong> of <strong>{totalPages}</strong>
            </div>
            <div className="flex items-center gap-2">
              <button
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                className="p-1.5 rounded border border-slate-200 hover:bg-slate-50 disabled:opacity-40 disabled:pointer-events-none"
              >
                <ChevronLeft size={16} />
              </button>
              <button
                disabled={page >= totalPages}
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                className="p-1.5 rounded border border-slate-200 hover:bg-slate-50 disabled:opacity-40 disabled:pointer-events-none"
              >
                <ChevronRight size={16} />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
