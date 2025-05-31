const ClientHeader = ({ data }) => (
  <div className='client-header card'>
    <div className='left'>
      <h1>{data.client_id}</h1>
      <div>
        {' '}
        <label>Diagnosis:</label> {data.diagnosis}
      </div>
      <div>
        {' '}
        <label>Sessions Count:</label> {data.sessions.length} Sessions
      </div>
      <div className='summary'>
        <h4>Summary</h4>
        <div>{data.progress_summary}</div>
      </div>
    </div>
    <div className='score-box'>
      <h4>Last {data.metric} Score</h4>
      <div className='score'>
        {data.sessions[data.sessions.length - 1].total_score}
      </div>
      <div className='status-box'>
        <label>Status</label>
        <div className={` status ${data.progress_status.toLowerCase()}`}>
          {data.progress_status}
        </div>
      </div>
    </div>
  </div>
);

export default ClientHeader;
