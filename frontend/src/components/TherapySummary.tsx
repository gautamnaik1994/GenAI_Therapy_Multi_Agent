import ClientHeader from './ClientHeader';
import SessionDetailCard from './SessionDetailCard';
import SymptomTrendHeatmap from './SymptomTrendHeatmap';
import TrendChart from './TrendChart';

function TherapySummary({ data }) {
  return (
    <>
      <ClientHeader data={data} />
      <TrendChart metric={data.metric} sessions={data.sessions} />
      <SymptomTrendHeatmap sessions={data.sessions} />
      <h4 className='mt-4'>Session Details</h4>
      {data.sessions.map((session) => (
        <SessionDetailCard
          metric={data.metric}
          key={session.therapy_session_number}
          session={session}
        />
      ))}
    </>
  );
}

export default TherapySummary;
