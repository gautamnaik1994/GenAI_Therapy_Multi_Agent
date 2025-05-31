import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

const TrendChart = ({
  sessions,
  metric,
}: {
  sessions: any[];
  metric: string;
}) => {
  const data = sessions.map((session) => ({
    session: `Session ${session.therapy_session_number}`,
    score: session.total_score,
  }));

  return (
    <div className='trend-chart'>
      <h3>Total {metric} Score Over Sessions</h3>
      <ResponsiveContainer width='100%' height={300}>
        <LineChart data={data}>
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
      </ResponsiveContainer>
    </div>
  );
};

export default TrendChart;
