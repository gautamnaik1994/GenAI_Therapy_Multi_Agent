const ProgressSummaryCard = ({ summary, status }) => (
  <div className='mb-4'>
    <div className='card-body'>
      <div className='card-title'>Progress Summary</div>
      <div>Status : {status}</div>
      <div className='card-text'>{summary}</div>
    </div>
  </div>
);

export default ProgressSummaryCard;
