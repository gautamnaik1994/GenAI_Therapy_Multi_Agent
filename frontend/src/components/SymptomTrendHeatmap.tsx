import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';

const SymptomTrendHeatmap = ({ sessions }) => {
  const symptomKeys = Object.keys(sessions[0].estimated_scores);
  const data = sessions.map((session) => ({
    session: `S${session.therapy_session_number}`,
    ...session.estimated_scores,
  }));

  return (
    <div className='mb-4'>
      <h5>Symptom Trends Over Sessions</h5>
      <BarChart width={800} height={400} data={data}>
        <CartesianGrid strokeDasharray='3 3' />
        <XAxis dataKey='session' />
        <YAxis allowDecimals={false} />
        <Tooltip />
        <Legend />
        {symptomKeys.map((symptom, idx) => (
          <Bar
            key={symptom}
            dataKey={symptom}
            fill={`hsl(${idx * 30}, 50%, 50%)`}
          />
        ))}
      </BarChart>
    </div>
  );
};

export default SymptomTrendHeatmap;
