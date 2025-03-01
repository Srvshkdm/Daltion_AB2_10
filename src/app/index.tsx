import { useState, useEffect } from 'react'
import axios from 'axios'
import { useDropzone } from 'react-dropzone'

export default function Home() {
  const [file, setFile] = useState<File | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [redactedImageUrl, setRedactedImageUrl] = useState<string | null>(null)
  
  const { getRootProps, getInputProps } = useDropzone({
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png'],
      'application/pdf': ['.pdf']
    },
    maxFiles: 1,
    onDrop: acceptedFiles => {
      const selectedFile = acceptedFiles[0]
      setFile(selectedFile)
      
      // Create preview for image files
      if (selectedFile.type.startsWith('image/')) {
        const url = URL.createObjectURL(selectedFile)
        setPreviewUrl(url)
      } else {
        setPreviewUrl(null)
      }
    }
  })

  // Clean up object URLs when component unmounts
  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl)
      }
      if (redactedImageUrl) {
        URL.revokeObjectURL(redactedImageUrl)
      }
    }
  }, [previewUrl, redactedImageUrl])

  const handleUpload = async () => {
    if (!file) return
    
    setIsLoading(true)
    setResult(null)
    setRedactedImageUrl(null)
    
    try {
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await axios.post('http://localhost:8000/api/v1/upload', formData)
      setResult(response.data)
      
      // If it's an image, also get the redacted version
      if (file.type.startsWith('image/')) {
        try {
          const redactedResponse = await axios.post(
            'http://localhost:8000/api/v1/redact-image', 
            formData, 
            { responseType: 'blob' }
          )
          
          const url = URL.createObjectURL(redactedResponse.data)
          setRedactedImageUrl(url)
        } catch (error) {
          console.error('Error getting redacted image:', error)
        }
      }
    } catch (error) {
      console.error('Error uploading file:', error)
      alert('Error processing file. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'Low': return 'bg-green-100 text-green-800'
      case 'Medium': return 'bg-yellow-100 text-yellow-800'
      case 'High': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <main className="flex min-h-screen flex-col items-center p-4 md:p-8">
      <h1 className="text-2xl md:text-3xl font-bold mb-4 md:mb-8">PII Detection & Redaction System</h1>
      
      <div className="w-full max-w-4xl grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Left column: Upload and Preview */}
        <div>
          <div {...getRootProps()} className="border-2 border-dashed rounded-lg p-6 text-center cursor-pointer hover:bg-gray-50">
            <input {...getInputProps()} />
            <p>Drag and drop a document here, or click to select a file</p>
            <p className="text-sm text-gray-500 mt-2">Supported formats: PDF, JPEG, PNG</p>
          </div>
          
          {file && (
            <div className="mt-4">
              <p className="text-sm">Selected file: {file.name}</p>
              <button 
                onClick={handleUpload} 
                disabled={isLoading}
                className="mt-2 bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50"
              >
                {isLoading ? 'Processing...' : 'Upload & Process'}
              </button>
            </div>
          )}
          
          {previewUrl && (
            <div className="mt-4">
              <h3 className="font-semibold mb-2">Original Image:</h3>
              <img src={previewUrl} alt="Preview" className="max-w-full h-auto border rounded" />
            </div>
          )}
          
          {redactedImageUrl && (
            <div className="mt-4">
              <h3 className="font-semibold mb-2">Redacted Image:</h3>
              <img src={redactedImageUrl} alt="Redacted" className="max-w-full h-auto border rounded" />
            </div>
          )}
        </div>
        
        {/* Right column: Results */}
        <div>
          {isLoading && (
            <div className="p-4 text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
              <p className="mt-2">Processing document...</p>
            </div>
          )}
          
          {result && (
            <div className="p-4 border rounded-lg">
              <h2 className="font-bold text-lg mb-4">Analysis Results</h2>
              
              {/* Risk Assessment */}
              <div className="mb-4">
                <h3 className="font-semibold mb-1">Risk Assessment</h3>
                <div className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getRiskColor(result.risk_assessment.risk_level)}`}>
                  {result.risk_assessment.risk_level} Risk
                </div>
                <p className="text-sm mt-1">
                  Found {result.risk_assessment.pii_count} PII items (Score: {result.risk_assessment.risk_score})
                </p>
              </div>
              
              {/* Detected PII */}
              {result.detected_pii.length > 0 && (
                <div className="mb-4">
                  <h3 className="font-semibold mb-1">Detected PII</h3>
                  <div className="bg-gray-50 rounded p-2 max-h-40 overflow-y-auto">
                    <table className="min-w-full">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left text-xs font-medium text-gray-500 py-1">Type</th>
                          <th className="text-left text-xs font-medium text-gray-500 py-1">Value</th>
                        </tr>
                      </thead>
                      <tbody>
                        {result.detected_pii.map((pii: any, index: number) => (
                          <tr key={index} className="border-b border-gray-100">
                            <td className="py-1 pr-2 text-sm">{pii.type}</td>
                            <td className="py-1 text-sm font-mono">{pii.value}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
              
              {/* Text Content */}
              <div className="grid grid-cols-1 gap-4">
                <div>
                  <h3 className="font-semibold mb-1">Extracted Text</h3>
                  <div className="bg-gray-50 p-2 rounded text-sm max-h-40 overflow-y-auto whitespace-pre-wrap">
                    {result.extracted_text || "No text extracted"}
                  </div>
                </div>
                
                <div>
                  <h3 className="font-semibold mb-1">Redacted Text</h3>
                  <div className="bg-gray-50 p-2 rounded text-sm max-h-40 overflow-y-auto whitespace-pre-wrap">
                    {result.redacted_text || "No text redacted"}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </main>
  )
}