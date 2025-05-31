import React, { useState } from 'react';

interface FileUploadProps {
  onSuccess: (result: any) => void;
}

function FileUpload({ onSuccess }: FileUploadProps) {
  const [files, setFiles] = useState<FileList | null>(null);
  const [uploadResult, setUploadResult] = useState<{ error?: string } | null>(
    null
  );
  const [uploading, setUploading] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFiles(e.target.files);
  };

  const handleUpload = async () => {
    if (!files) return;
    // Validate file names before upload
    const invalidFiles: string[] = [];
    Array.from(files).forEach((file) => {
      if (!/^client\d+_session\d+\.(txt|json)$/i.test(file.name)) {
        invalidFiles.push(file.name);
      }
    });
    if (invalidFiles.length > 0) {
      setUploadResult({
        error: `Invalid file name(s): ${invalidFiles.join(', ')}. File names must match client<id>_session<id>.txt or .json`,
      });
      return;
    }
    setUploading(true);
    setUploadResult(null);
    onSuccess(null);
    const formData = new FormData();
    Array.from(files).forEach((file) => {
      formData.append('files', file);
    });
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/analyze-sessions/`,
        {
          method: 'POST',
          body: formData,
        }
      );
      const result = await response.json();
      onSuccess(result);
    } catch {
      setUploadResult({ error: 'Upload failed' });
    } finally {
      setUploading(false);
    }
  };

  const handleSampleLoad = async (clientID: string) => {
    setUploadResult(null);
    setUploading(true);
    onSuccess(null);
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/analyze-sample-data/${clientID}`,
        {
          method: 'GET',
        }
      );
      const result = await response.json();
      onSuccess(result);
      setUploading(false);
    } catch {
      setUploadResult({ error: 'Sample load failed' });
    } finally {
      setUploading(false);
    }
  };

  return (
    <>
      <div className='session-files-container'>
        <div className='left'>
          <h3>Upload Therapy Session Files</h3>
          <p>
            <small>
              Note: Upload your therapy session files in client1_session1.txt
              format.
            </small>{' '}
          </p>
          <div>
            <input
              type='file'
              multiple
              accept='.txt,application/json'
              onChange={handleFileChange}
            />
            <button
              onClick={handleUpload}
              disabled={!files || uploading}
              style={{ marginLeft: '1em' }}
            >
              {uploading ? 'Uploading...' : 'Upload'}
            </button>
          </div>

          {uploadResult && (
            <div
              style={{
                marginTop: '1em',
                color: uploadResult.error ? 'red' : 'green',
              }}
            >
              {uploadResult.error
                ? uploadResult.error
                : 'Files uploaded successfully!'}
            </div>
          )}
        </div>
        <div className='right'>
          <h3>Or, Load Sample Data</h3>
          <p>
            <small>
              Click on one of the sample clients below to load pre-populated
              data for analysis.
            </small>{' '}
          </p>
          <div className='sample-holder'>
            <button onClick={() => handleSampleLoad('client1')}>
              Client 1
            </button>
            <button onClick={() => handleSampleLoad('client2')}>
              Client 2
            </button>
            <button onClick={() => handleSampleLoad('client3')}>
              Client 3 (Synthetic Data)
            </button>
          </div>
        </div>
      </div>
      {uploading && (
        <div className='loading-indicator'>
          <p>Processing ...</p>
        </div>
      )}
    </>
  );
}

export default FileUpload;
