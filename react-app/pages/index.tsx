import React from 'react';
import { useQuery } from '@apollo/client';
import { GET_STOCKS } from '../graphql/getStocks';
import Layout from '../components/Layout';

const HomePage: React.FC = () => {
  const { loading, error, data } = useQuery(GET_STOCKS);

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error.message}</p>;

  return (
    <Layout>
      <div className="stocks-section">
        <h2>Holdings</h2>
        <table className="stocks-table">
          <thead>
            <tr>
              <th>Ticker</th>
              <th>Name</th>
            </tr>
          </thead>
          <tbody>
            {data?.allStocks?.nodes.map((stock: any) => (
              <tr key={stock.ticker}>
                <td>{stock.ticker}</td>
                <td>{stock.name}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="portfolio-summary-section">
        <h2>Portfolio Summary</h2>
        {/* Portfolio Summary Table Component will go here */}
      </div>
      <style jsx>{`
        .stocks-section, .portfolio-summary-section {
          margin-bottom: 20px;
        }
        h2 {
          margin: 0 0 10px;
        }
        .stocks-table {
          width: 100%;
          border-collapse: collapse;
        }
        .stocks-table th, .stocks-table td {
          border: 1px solid #ddd;
          padding: 8px;
        }
        .stocks-table th {
          padding-top: 12px;
          padding-bottom: 12px;
          text-align: left;
          background-color: #f4f4f4;
          color: black;
        }
      `}</style>
    </Layout>
  );
};

export default HomePage;