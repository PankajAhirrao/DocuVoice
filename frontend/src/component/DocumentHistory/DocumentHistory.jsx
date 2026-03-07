import "./DocumentHistory.css";

export default function DocumentHistory() {

  return (
    <div className="history-card">
      <div className="card-header">
        <h2 className="card-title">Recent Papers</h2>
        <p className="card-description">
          Your latest uploads and analyses will appear here.
        </p>
      </div>

      <div className="card-content">
        <table className="history-table">
          <thead>
            <tr>
              <th>Paper</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Transformer based text summarization</td>
              <td>
                <span className="status">Ready</span>
              </td>
              <td>
                <a className="view-btn" href="#">
                  View
                </a>
              </td>
            </tr>
            <tr>
              <td>Graph Neural Networks for Citation Analysis</td>
              <td>
                <span className="status">Ready</span>
              </td>
              <td>
                <a className="view-btn" href="#">
                  View
                </a>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}