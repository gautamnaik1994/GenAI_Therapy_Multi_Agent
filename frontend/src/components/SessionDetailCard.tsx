import React from 'react';
import Badge from './Badge';

const getSeverity = (score) => {
  if (score <= 4) return <Badge variant='success'>Minimal</Badge>;
  if (score <= 9) return <Badge variant='warning'>Mild</Badge>;
  if (score <= 14) return <Badge variant='orange'>Moderate</Badge>;
  return <Badge variant='danger'>Severe</Badge>;
};

const SessionDetailCard = ({ session }) => (
  <div>
    <div>
      <h5>Session {session.therapy_session_number}</h5>
      <h6 className='mb-2 text-muted'>
        Total PHQ-9 Score: {session.total_phq9_score}{' '}
        {getSeverity(session.total_phq9_score)}
      </h6>
      <p>{session.justification}</p>
    </div>
  </div>
);

export default SessionDetailCard;
