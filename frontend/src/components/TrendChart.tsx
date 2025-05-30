import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';

const PHQ9TrendChart = ({ sessions, metric }) => {
  const data = sessions.map((session) => ({
    session: `Session ${session.therapy_session_number}`,
    // score: session.total_phq9_score
    score:
      metric === 'PHQ-9' ? session.total_phq9_score : session.total_gad7_score,
  }));

  return (
    <div className='mb-4'>
      <h5>Total {metric} Score Over Sessions</h5>
      <LineChart width={600} height={300} data={data}>
        <CartesianGrid strokeDasharray='3 3' />
        <XAxis dataKey='session' />
        <YAxis domain={[0, 27]} />
        <Tooltip />
        <Legend />
        <Line
          type='monotone'
          dataKey='score'
          stroke='#dc3545'
          activeDot={{ r: 8 }}
        />
      </LineChart>
    </div>
  );
};

export default PHQ9TrendChart;
