import { useState } from 'react';
import Navbar from './components/Navbar';
import FileUpload from './components/FileUpload';
import type { ApiResponse } from './types';
import { response } from './utils';
import PHQ9 from './components/TherapySummary';

function App() {
  const [data, setData] = useState<ApiResponse | null>(null);

  return (
    <>
      <Navbar />
      <div className='container'>
        <FileUpload onSuccess={setData} />
        {/* {JSON.stringify(response)} */}
        {data && <PHQ9 data={data} />}
        <PHQ9 data={response} />
      </div>
    </>
  );
}

export default App;
