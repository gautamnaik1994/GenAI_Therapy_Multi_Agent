type PHQ9Scores = {
  little_interest: number;
  feeling_down: number;
  trouble_sleeping: number;
  feeling_tired: number;
  poor_appetite: number;
  feeling_bad_about_self: number;
  trouble_concentrating: number;
  slow_or_fast: number;
  thoughts_of_self_harm: number;
};

export type Session = {
  therapy_session_number: number;
  estimated_phq9_scores: PHQ9Scores;
  total_phq9_score: number;
  justification: string;
};

export type ApiResponse = {
  client_id: string;
  sessions: Session[];
  progress_summary: string;
};
