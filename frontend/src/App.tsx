import { useState } from 'react';
import Navbar from './components/Navbar';
import FileUpload from './components/FileUpload';
import type { ApiResponse } from './types';
// import { response } from './constants/dummyResponse';
import TherapySummary from './components/TherapySummary';
import HowItWorks from './components/HowItWorks';

function App() {
  const [data, setData] = useState<ApiResponse | null>(null);

  return (
    <>
      <Navbar />
      <div className='container'>
        <FileUpload onSuccess={setData} />
        {/* {JSON.stringify(response)} */}
        {data && 'sessions' in data ? (
          <TherapySummary data={data} />
        ) : (
          <p>Something is wrong, please try again later.</p>
        )}
        <hr />
        <HowItWorks />
      </div>
    </>
  );
}

export default App;
