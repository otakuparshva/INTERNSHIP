import React from 'react';
import { Document, Page } from 'react-pdf';
import { useState } from 'react';

const ResumeViewer = ({ file }) => {
  const [numPages, setNumPages] = useState(null);
  const [pageNumber, setPageNumber] = useState(1);

  function onDocumentLoadSuccess({ numPages }) {
    setNumPages(numPages);
  }

  return (
    <div className="flex flex-col items-center">
      <Document
        file={file}
        onLoadSuccess={onDocumentLoadSuccess}
        className="max-w-full"
      >
        <Page pageNumber={pageNumber} />
      </Document>
      {numPages && (
        <div className="mt-4 flex items-center gap-4">
          <button
            onClick={() => setPageNumber(pageNumber - 1)}
            disabled={pageNumber <= 1}
            className="px-4 py-2 bg-blue-500 text-white rounded disabled:bg-gray-300"
          >
            Previous
          </button>
          <p>
            Page {pageNumber} of {numPages}
          </p>
          <button
            onClick={() => setPageNumber(pageNumber + 1)}
            disabled={pageNumber >= numPages}
            className="px-4 py-2 bg-blue-500 text-white rounded disabled:bg-gray-300"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
};

export default ResumeViewer; 