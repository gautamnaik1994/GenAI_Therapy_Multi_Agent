import ClientHeader from './ClientHeader';
import SessionDetailCard from './SessionDetailCard';
import SymptomTrendHeatmap from './SymptomTrendHeatmap';
import TrendChart from './TrendChart';

function TherapySummary({ data }) {
  return (
    <>
      <ClientHeader data={data} />
      <div className='card'>
        <TrendChart metric={data.metric} sessions={data.sessions} />
        <SymptomTrendHeatmap sessions={data.sessions} />
      </div>
      <div className='card'>
        <h2 className='session-details-title'>Detailed Session Information</h2>
        {data.sessions.map((session) => (
          <div key={session.therapy_session_number}>
            <SessionDetailCard metric={data.metric} session={session} />
            {session.therapy_session_number !== data.sessions.length && <hr />}
          </div>
        ))}
      </div>
    </>
  );
}

export default TherapySummary;
