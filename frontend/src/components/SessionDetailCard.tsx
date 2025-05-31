import Badge from './Badge';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
} from 'recharts';

const getSeverity = (score: number) => {
  if (score <= 4) return <Badge variant='success'>Minimal</Badge>;
  if (score <= 9) return <Badge variant='warning'>Mild</Badge>;
  if (score <= 14) return <Badge variant='orange'>Moderate</Badge>;
  return <Badge variant='danger'>Severe</Badge>;
};

const SessionDetailCard = ({
  session,
  metric,
}: {
  session: any;
  metric: string;
}) => (
  <>
    <h3>Session {session.therapy_session_number}</h3>
    <div className='session-details-inner'>
      <div className='left'>
        <div>
          <label>{metric} Score : </label>
          <span className='text-primary inter-bold'>
            {session.total_score}
          </span>{' '}
          {getSeverity(session.total_score)}
        </div>

        <div className='summary'>
          <h4>Justification</h4>
          <p>{session.justification}</p>
        </div>
      </div>
      <div className='symptom-scores'>
        <ResponsiveContainer width='100%' height={300}>
          <RadarChart
            outerRadius='70%'
            data={Object.entries(session.estimated_scores).map(
              ([symptom, score]) => ({ symptom, score })
            )}
          >
            <PolarGrid />
            <PolarAngleAxis dataKey='symptom' />
            <PolarRadiusAxis domain={[0, 3]} allowDecimals={false} />
            <Radar
              name='Estimated Scores'
              dataKey='score'
              stroke='#8884d8'
              fill='#8884d8'
              fillOpacity={0.6}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </div>
  </>
);

export default SessionDetailCard;
