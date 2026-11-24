"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/Header";
import { api } from "@/lib/api";
import { Property, TopicDistribution, Review } from "@/types";
import {
  Building2,
  ExternalLink,
  Star,
  ThumbsUp,
  ThumbsDown,
  AlertTriangle,
  ArrowRight,
  TrendingUp,
  TrendingDown,
  MapPin,
} from "lucide-react";
import { formatRating, getSentimentBadgeColor, formatDate } from "@/lib/utils";
import Link from "next/link";

export default function PropertiesPage() {
  const [properties, setProperties] = useState<Property[]>([]);
  const [selectedPropertyId, setSelectedPropertyId] = useState<number | null>(null);
  const [activePropReviews, setActivePropReviews] = useState<Review[]>([]);
  const [activePropTopics, setActivePropTopics] = useState<TopicDistribution[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api.getProperties()
      .then((data) => {
        setProperties(data);
        if (data.length > 0 && !selectedPropertyId) {
          setSelectedPropertyId(data[0].id);
        }
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!selectedPropertyId) return;
    Promise.all([
      api.getReviews({ property_id: selectedPropertyId, limit: 5 }),
      api.getTopicDistributions(selectedPropertyId),
    ])
      .then(([revData, topicData]) => {
        setActivePropReviews(revData.items);
        setActivePropTopics(topicData);
      })
      .catch(console.error);
  }, [selectedPropertyId]);

  const activeProp = properties.find((p) => p.id === selectedPropertyId);

  return (
    <div className="flex-1 flex flex-col min-h-screen">
      <Header
        selectedPropertyId={selectedPropertyId}
        onPropertyChange={setSelectedPropertyId}
      />

      <div className="p-8 space-y-8 max-w-7xl mx-auto w-full">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">
            Hotel Properties Portfolio
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Compare operations and guest satisfaction benchmarks across all 4 Azzurro properties.
          </p>
        </div>

        {/* 4 Property Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {properties.map((p) => {
            const isSelected = p.id === selectedPropertyId;
            return (
              <div
                key={p.id}
                onClick={() => setSelectedPropertyId(p.id)}
                className={`cursor-pointer rounded-xl p-6 bg-white border transition-all duration-200 flex flex-col justify-between ${
                  isSelected
                    ? "border-blue-700 ring-2 ring-blue-600/20 shadow-md"
                    : "border-slate-200 hover:border-slate-300 shadow-sm"
                }`}
              >
                <div>
                  <div className="flex items-start justify-between">
                    <div>
                      <span className="text-xs font-semibold uppercase tracking-wider text-blue-800">
                        Property #{p.id}
                      </span>
                      <h3 className="font-bold text-slate-900 text-lg mt-0.5">{p.name}</h3>
                    </div>
                    <a
                      href={p.booking_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      onClick={(e) => e.stopPropagation()}
                      className="text-slate-400 hover:text-blue-700 p-1"
                      title="View Booking.com Listing"
                    >
                      <ExternalLink size={16} />
                    </a>
                  </div>

                  <div className="flex items-center gap-1.5 text-xs text-slate-500 mt-1.5">
                    <MapPin size={13} className="text-slate-400" />
                    <span>{p.location}</span>
                  </div>

                  {/* Rating Highlight */}
                  <div className="mt-5 flex items-baseline gap-2">
                    <div className="text-3xl font-extrabold text-slate-900">
                      {formatRating(p.average_rating)}
                    </div>
                    <div className="flex items-center gap-0.5 text-amber-500">
                      <Star size={16} className="fill-amber-400" />
                    </div>
                    <span className="text-xs text-slate-400 ml-auto font-medium">
                      {p.total_reviews} reviews
                    </span>
                  </div>

                  {/* Positive / Negative Progress Bar */}
                  <div className="mt-4 space-y-1.5">
                    <div className="flex justify-between text-xs font-medium text-slate-600">
                      <span className="text-emerald-700">{p.positive_percentage}% Pos</span>
                      <span className="text-rose-700">{p.negative_percentage}% Neg</span>
                    </div>
                    <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden flex">
                      <div
                        className="bg-emerald-500 h-full"
                        style={{ width: `${p.positive_percentage}%` }}
                      />
                      <div
                        className="bg-rose-500 h-full"
                        style={{ width: `${p.negative_percentage}%` }}
                      />
                    </div>
                  </div>

                  {/* Top Negative Issue */}
                  <div className="mt-4 pt-4 border-t border-slate-100 text-xs">
                    <span className="text-slate-400 block mb-1">Top Concern:</span>
                    <span className="inline-flex items-center gap-1 font-semibold text-rose-700 bg-rose-50 px-2 py-0.5 rounded border border-rose-200">
                      <AlertTriangle size={12} />
                      {p.top_negative_topic || "No critical issues"}
                    </span>
                  </div>
                </div>

                <div className="mt-5 pt-3 border-t border-slate-100 flex items-center justify-between text-xs font-semibold text-blue-800">
                  <span>{isSelected ? "Inspecting" : "Select Property"}</span>
                  <ArrowRight size={14} />
                </div>
              </div>
            );
          })}
        </div>

        {/* Selected Property Inspection Drawer / View */}
        {activeProp && (
          <div className="bg-white rounded-xl border border-slate-200 p-8 shadow-sm space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-100 pb-6">
              <div>
                <span className="text-xs font-semibold text-blue-800 uppercase tracking-wider">
                  Deep-Dive Operational Inspection
                </span>
                <h2 className="text-xl font-bold text-slate-900 mt-1">
                  {activeProp.name}
                </h2>
                <p className="text-xs text-slate-500 mt-0.5">{activeProp.location}</p>
              </div>
              <div className="flex items-center gap-3">
                <Link
                  href={`/reviews?property_id=${activeProp.id}`}
                  className="bg-blue-900 hover:bg-blue-800 text-white text-xs font-semibold px-4 py-2 rounded-lg transition"
                >
                  View All {activeProp.name} Reviews
                </Link>
                <a
                  href={activeProp.booking_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="border border-slate-300 hover:bg-slate-50 text-slate-700 text-xs font-medium px-4 py-2 rounded-lg transition flex items-center gap-1.5"
                >
                  <span>Booking.com URL</span>
                  <ExternalLink size={14} />
                </a>
              </div>
            </div>

            {/* Operational Topic Breakdown for this Property */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div>
                <h4 className="font-semibold text-slate-900 text-sm mb-3">
                  Topic Satisfaction Breakdown
                </h4>
                <div className="space-y-3">
                  {activePropTopics.map((t) => (
                    <div
                      key={t.topic}
                      className="p-3 rounded-lg border border-slate-200 bg-slate-50 flex items-center justify-between"
                    >
                      <div>
                        <span className="font-semibold text-xs text-slate-800 block">
                          {t.topic}
                        </span>
                        <span className="text-[11px] text-slate-500">
                          Total Mentions: {t.total_mentions}
                        </span>
                      </div>
                      <div className="flex items-center gap-2 text-xs">
                        <span className="text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded">
                          +{t.positive_count} Pos
                        </span>
                        <span className="text-rose-700 bg-rose-50 border border-rose-200 px-2 py-0.5 rounded">
                          -{t.negative_count} Neg
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Sample Reviews for Property */}
              <div>
                <h4 className="font-semibold text-slate-900 text-sm mb-3">
                  Recent Guest Feedback at {activeProp.name}
                </h4>
                <div className="space-y-3">
                  {activePropReviews.map((r) => (
                    <div
                      key={r.id}
                      className="p-4 rounded-lg border border-slate-200 bg-white flex flex-col gap-2 text-xs"
                    >
                      <div className="flex items-center justify-between text-slate-500">
                        <span className="font-bold text-slate-800 bg-slate-100 px-2 py-0.5 rounded">
                          ★ {formatRating(r.rating)}
                        </span>
                        <span>{formatDate(r.review_date)}</span>
                      </div>
                      {r.title && <div className="font-semibold text-slate-800">{r.title}</div>}
                      {r.negative_text && (
                        <div className="text-rose-800 bg-rose-50 p-2 rounded border border-rose-100">
                          <strong>Negative:</strong> {r.negative_text}
                        </div>
                      )}
                      {r.positive_text && (
                        <div className="text-emerald-800 bg-emerald-50 p-2 rounded border border-emerald-100">
                          <strong>Positive:</strong> {r.positive_text}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
