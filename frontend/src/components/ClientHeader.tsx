import Badge from './Badge';

const ClientHeader = ({ clientId, sessionCount }) => (
  <div className=''>
    <h3>Client ID: {clientId}</h3>
    <Badge variant='primary'>{sessionCount} Sessions</Badge>
  </div>
);

export default ClientHeader;
