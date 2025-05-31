import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

const pastelColors = [
  '#6FA8DC',
  '#E06666',
  '#76C7A3',
  '#F6B26B',
  '#93C47D',
  '#8E7CC3',
  '#FFD966',
  '#6D9EEB',
  '#C27BA0',
];

const SymptomTrendHeatmap = ({ sessions }: { sessions: any }) => {
  const symptomKeys = Object.keys(sessions[0].estimated_scores);
  const data = sessions.map((session: any) => ({
    session: `S${session.therapy_session_number}`,
    ...session.estimated_scores,
  }));

  return (
    <div className='trend-chart'>
      <h3>Symptom Trend Over Sessions</h3>
      <ResponsiveContainer width='100%' height={400}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray='3 3' />
          <XAxis dataKey='session' />
          <YAxis allowDecimals={false} domain={[0, 3]} />
          <Tooltip />
          <Legend />
          {symptomKeys.map((symptom, idx) => (
            <Bar
              key={symptom}
              dataKey={symptom}
              fill={pastelColors[idx % pastelColors.length]}
            />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default SymptomTrendHeatmap;
