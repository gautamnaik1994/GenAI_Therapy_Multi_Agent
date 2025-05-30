import ClientHeader from './ClientHeader';
import ProgressSummaryCard from './ProgressSummaryCard';
import SessionDetailCard from './SessionDetailCard';
import SymptomTrendHeatmap from './SymptomTrendHeatmap';
import TrendChart from './TrendChart';

interface PHQ9Session {
  therapy_session_number: number;
  total_phq9_score: number;
  estimated_scores: string;
  justification: string;
}

interface PHQ9Props {
  data: {
    sessions: PHQ9Session[];
  };
}

function PHQ9({ data }: PHQ9Props) {
  return (
    <>
      <ClientHeader
        clientId={data.client_id}
        sessionCount={data.sessions.length}
      />
      <ProgressSummaryCard summary={data.progress_summary} />
      <TrendChart metric='PHQ-9' sessions={data.sessions} />
      <SymptomTrendHeatmap sessions={data.sessions} />
      <h4 className='mt-4'>Session Details</h4>
      {data.sessions.map((session) => (
        <SessionDetailCard
          key={session.therapy_session_number}
          session={session}
        />
      ))}
    </>
  );
}

export default PHQ9;
