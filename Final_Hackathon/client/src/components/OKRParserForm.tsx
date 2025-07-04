import React, { useState } from "react";

const OKRParserForm = () => {
  const [okrInput, setOkrInput] = useState("");
  const [parsedResult, setParsedResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [warning, setWarning] = useState("");

  const handleSubmit = async () => {
    if (!okrInput.trim()) return;

    setLoading(true);
    setParsedResult(null);
    setError("");
    setWarning("");

    try {
      const response = await fetch("/api/parse-okr", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ okr_text: okrInput }),
      });

      const data = await response.json();
      if (data.error) {
        setError(data.details || data.error.details || data.error || 'Unknown error from backend');
      } else {
        setParsedResult(data);
        if (data.context_warning) {
          setWarning(data.context_warning);
        }
      }
    } catch (err) {
      setError('Failed to connect to the server.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto p-6 space-y-6">
      <div className="bg-white shadow-md rounded-lg p-6">
        <h2 className="text-2xl font-bold mb-4">OKR Parser</h2>
        <textarea
          className="w-full border border-gray-300 rounded-lg p-3 min-h-[100px] focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Enter OKR here..."
          value={okrInput}
          onChange={(e) => setOkrInput(e.target.value)}
        />
        <button
          onClick={handleSubmit}
          disabled={loading}
          className="mt-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold px-6 py-2 rounded-md transition duration-200"
        >
          {loading ? "Parsing..." : "Parse OKR"}
        </button>
      </div>

      {warning && (
        <div className="bg-yellow-100 text-yellow-800 p-2 rounded mb-2">{warning}</div>
      )}
      {error && (
        <div className="bg-red-100 text-red-800 p-2 rounded mb-2">{error}</div>
      )}

      {parsedResult && !error && (
        <div className="bg-gray-100 shadow-inner rounded-lg p-6">
          <h3 className="text-xl font-semibold mb-2">Parsed Output</h3>
          <pre className="whitespace-pre-wrap text-sm bg-white p-4 rounded-md overflow-x-auto border border-gray-200">
            {JSON.stringify(parsedResult, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};

export default OKRParserForm;
