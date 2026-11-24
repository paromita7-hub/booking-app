export interface Property {
  id: number;
  name: string;
  booking_url: string;
  location: string;
  created_at: string;
  total_reviews: number;
  average_rating: number;
  positive_percentage: number;
  negative_percentage: number;
  weekly_rating_change: number;
  top_negative_topic?: string | null;
}

export interface ReviewTopic {
  topic: string;
  sentiment: "Positive" | "Negative" | "Mixed" | "Neutral";
  confidence: number;
  matched_keywords: string[];
}

export interface Review {
  id: number;
  external_id?: string | null;
  property_id: number;
  property_name?: string | null;
  title?: string | null;
  positive_text?: string | null;
  negative_text?: string | null;
  rating: number;
  review_date: string;
  stay_date?: string | null;
  reviewer_country?: string | null;
  traveler_type?: string | null;
  room_type?: string | null;
  language: string;
  source: string;
  content_fingerprint: string;
  is_demo: boolean;
  created_at: string;
  updated_at: string;
  topics: ReviewTopic[];
  overall_sentiment?: string | null;
}

export interface PaginatedReviews {
  items: Review[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface KPISummary {
  current_week_avg_rating: number;
  previous_week_avg_rating: number;
  rating_change: number;
  total_reviews_count: number;
  current_week_reviews_count: number;
  previous_week_reviews_count: number;
  positive_review_percentage: number;
  negative_review_percentage: number;
  mixed_review_percentage: number;
  neutral_review_percentage: number;
  period_start: string;
  period_end: string;
  previous_period_start: string;
  previous_period_end: string;
  timezone: string;
}

export interface WeeklyTrendPoint {
  week_label: string;
  week_start: string;
  week_end: string;
  average_rating: number;
  total_reviews: number;
  positive_count: number;
  negative_count: number;
  mixed_count: number;
}

export interface PropertyComparison {
  property_id: number;
  property_name: string;
  average_rating: number;
  total_reviews: number;
  positive_percentage: number;
  negative_percentage: number;
  weekly_rating_change: number;
  top_negative_topic?: string | null;
}

export interface TopicDistribution {
  topic: string;
  positive_count: number;
  negative_count: number;
  total_mentions: number;
  negative_percentage_of_negative_reviews: number;
  positive_percentage_of_positive_reviews: number;
}

export interface SupportingReviewSample {
  id: number;
  property_name: string;
  rating: number;
  review_date: string;
  title?: string | null;
  negative_text?: string | null;
  positive_text?: string | null;
}

export interface OperationalInsight {
  headline: string;
  topic: string;
  category: "warning" | "positive" | "neutral" | string;
  negative_reviews_percentage_current: number;
  negative_reviews_percentage_previous: number;
  percentage_change: number;
  affected_properties: string[];
  supporting_reviews: SupportingReviewSample[];
  interpretation: string;
}

export interface IngestionLog {
  id: number;
  source: string;
  property_id?: number | null;
  property_name?: string | null;
  status: string;
  records_processed: number;
  records_added: number;
  records_skipped: number;
  error_message?: string | null;
  started_at: string;
  completed_at?: string | null;
}

export interface IngestionStatus {
  automated_scraping_enabled: boolean;
  allowed_sources: string[];
  total_imports_run: number;
  last_import_timestamp?: string | null;
  last_import_status?: string | null;
}
