import Badge from './Badge';

const ClientHeader = ({ data }) => (
  <div className='client-header'>
    <div className='left'>
      <h1>
        <small>Client ID:</small>
        {data.client_id}
      </h1>
      <div>Diagnosis: {data.diagnosis}</div>
      <div>Total {data.sessions.length} Sessions</div>
      <div>
        <h4>Summary</h4> {data.progress_summary}
      </div>
    </div>
    <div className='right'>
      <h4>Last {data.metric} Score</h4>
      <div className='score'>
        {data.sessions[data.sessions.length - 1].total_score}
      </div>
      <div>Status: {data.progress_status}</div>
    </div>
  </div>
);

export default ClientHeader;
