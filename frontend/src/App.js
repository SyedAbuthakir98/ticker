import { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [stocks, setStocks] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [months, setMonths] = useState(6);

  // Fetch Top 10 stocks (Today snapshot)
  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/stocks/top10")
      .then(res => res.json())
      .then(data => setStocks(data))
      .catch(() => alert("Backend not reachable"));
  }, []);

  const analyzeStock = async (ticker) => {
    setLoading(true);
    setAnalysis(null);

    try {
      const res = await fetch(
        `http://127.0.0.1:8000/api/stocks/${ticker}/analyze?months=${months}`,
        { method: "POST" }
      );

      const data = await res.json();
      setAnalysis(data);
    } catch {
      alert("Analysis failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <h2>RealTicker Dashboard</h2>

      <p><b>Market Snapshot (Today)</b></p>

      <table border="2" cellPadding="20">
        <thead>
          <tr>
            <th>Ticker</th>
            <th>Company</th>
            <th>Price</th>
            <th>Today %</th>
            <th>Volume</th>
            <th>AI</th>
          </tr>
        </thead>
        <tbody>
          {stocks.map(stock => (
            <tr key={stock.ticker}>
              <td>{stock.ticker}</td>
              <td>{stock.company}</td>
              <td>{stock.price}</td>
              <td>{stock.change_percent}</td>
              <td>{stock.volume}</td>
              <td>
                <button onClick={() => analyzeStock(stock.ticker)} disabled={loading}>
                  Analyze
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div style={{ marginTop: "15px" }}>
        <label><b>Analyze trend for: </b></label>
        <select value={months} onChange={(e) => setMonths(Number(e.target.value))}>
          <option value={1}>1 Month</option>
          <option value={3}>3 Months</option>
          <option value={6}>6 Months</option>
        </select>
      </div>

      {loading && (
        <p style={{ color: "blue", marginTop: "10px" }}>
          AI analyzing... please wait
        </p>
      )}

      {analysis && (
        <div style={{ marginTop: "20px", border: "1px solid #ddd", padding: "15px" }}>
          <h3>AI Analysis ({analysis.analysis_period})</h3>
          <p><b>Trend:</b> {analysis.trend}</p>
          <p><b>Risk Level:</b> {analysis.risk_level}</p>
          <p><b>Suggested Action:</b> {analysis.suggested_action}</p>
          <p><b>Reason:</b> {analysis.reason}</p>
          <p style={{ color: "red" }}>{analysis.disclaimer}</p>
        </div>
      )}
    </div>
  );
}

export default App;
