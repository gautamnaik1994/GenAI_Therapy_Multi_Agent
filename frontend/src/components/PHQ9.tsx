import ClientHeader from './ClientHeader';
import ProgressSummaryCard from './ProgressSummaryCard';
import SessionDetailCard from './SessionDetailCard';
import SymptomTrendHeatmap from './SymptomTrendHeatmap';
import TrendChart from './TrendChart';

function PHQ9({ data }) {
  return (
    <>
      <ClientHeader
        clientId={data.client_id}
        sessionCount={data.sessions.length}
      />
      <ProgressSummaryCard
        summary={data.progress_summary}
        status={data.progress_status}
      />
      <TrendChart metric='PHQ-9' sessions={data.sessions} />
      <SymptomTrendHeatmap sessions={data.sessions} />
      <h4 className='mt-4'>Session Details</h4>
      {data.sessions.map((session) => (
        <SessionDetailCard
          metric='PHQ-9'
          key={session.therapy_session_number}
          session={session}
        />
      ))}
    </>
  );
}

export default PHQ9;
