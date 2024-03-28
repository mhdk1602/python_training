import React from "react";
import Modal from "react-modal";
import { useQuery } from "@apollo/client";
import { GET_STOCKS } from "../graphql/getStocks";
import { GET_PORTFOLIO_SUMMARY } from "../graphql/getPortfolioSummaries";
import { GET_PORTFOLIO_TRANSACTIONS } from "graphql/getPortfolioTransactions";
import Layout from "../components/Layout";
import { useState } from "react";

Modal.setAppElement("#__next"); // Set the app element for accessibility

const HomePage: React.FC = () => {
  const [modalIsOpen, setModalIsOpen] = useState(false);
  const [selectedTicker, setSelectedTicker] = useState(null);

  const {
    loading: stocksLoading,
    error: stocksError,
    data: stocksData,
    refetch: refetchStocks,  // Add this line to get the refetch function
  } = useQuery(GET_STOCKS);
  
  const {
    loading: portfolioLoading,
    error: portfolioError,
    data: portfolioData,
    refetch: refetchPortfolio,  // Add this line to get the refetch function
  } = useQuery(GET_PORTFOLIO_SUMMARY);
  
  const {
    loading: transactionsLoading,
    error: transactionsError,
    data: transactionsData,
    refetch: refetchTransactions,  // Add this line to get the refetch function
  } = useQuery(GET_PORTFOLIO_TRANSACTIONS, {
    skip: !selectedTicker,
    variables: { ticker: selectedTicker },
  });

  const openModal = (ticker: React.SetStateAction<null>) => {
    setSelectedTicker(ticker);
    setModalIsOpen(true);
  };

  const closeModal = () => {
    setModalIsOpen(false);
    setSelectedTicker(null);
  };

  const [tradeModalIsOpen, setTradeModalIsOpen] = useState(false);
  const [tradeType, setTradeType] = useState<string | null>(null);

  const [stockTicker, setStockTicker] = useState<string>("");
  const [volume, setVolume] = useState<number | null>(null);

  const [tradeFeedback, setTradeFeedback] = useState<string | null>(null);

  const openBuyModal = () => {
    setTradeType("Buy");
    setTradeModalIsOpen(true);
  };

  const openSellModal = () => {
    setTradeType("Sell");
    setTradeModalIsOpen(true);
  };

  const closeTradeModal = () => {
    setTradeModalIsOpen(false);
    setTradeType(null);
    setTradeFeedback(null); // Reset feedback message
  };

  const handleTrade = async () => {
    if (stockTicker && volume && tradeType) {
      try {
        const response = await fetch("http://localhost:5002/trade", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            symbol: stockTicker,
            volume,
            trade_type: tradeType,
          }),
        });
  
        const result = await response.json();
        if (result.error) {
          console.error("Trade Error:", result.error);
          setTradeFeedback("Trade Error: " + result.error);
        } else {
          console.log("Trade Successful:", result.message);
          setTradeFeedback("Trade Successful: " + result.message);
          closeTradeModal();
  
          // Trigger refetches to update your data
          refetchStocks();
          refetchPortfolio();
          refetchTransactions({ ticker: selectedTicker });
        }
      } catch (error: any) {
        console.error("Error executing trade:", error);
        setTradeFeedback("Error executing trade: " + error.message);
      }
    } else {
      console.error("Please enter valid inputs for stock ticker and volume");
      setTradeFeedback("Please enter valid inputs for stock ticker and volume");
    }
  };

  if (stocksLoading || portfolioLoading || transactionsLoading)
    return <p>Loading...</p>;
  if (stocksError) return <p>Error: {stocksError.message}</p>;
  if (portfolioError) return <p>Error: {portfolioError.message}</p>;
  if (transactionsError) return <p>Error: {transactionsError.message}</p>;

  return (
    <Layout>
      <div className="content-section">
        <div className="stocks-section">
          <h2>
            <img
              width="20"
              height="20"
              src="https://img.icons8.com/ios-filled/50/combo-chart--v2.png"
              alt="combo-chart--v2"
            />{" "}
            Holdings
          </h2>
          <table className="table-style">
            <thead>
              <tr>
                <th>Ticker</th>
                <th>Name</th>
              </tr>
            </thead>
            <tbody>
              {stocksData?.allStocks?.nodes.map((stock: any) => (
                <tr key={stock.ticker}>
                  <td>{stock.ticker}</td>
                  <td>{stock.name}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="portfolio-summary-section">
          <h2>
            <img
              width="20"
              height="20"
              src="https://img.icons8.com/external-nawicon-glyph-nawicon/64/external-Portfolio-investment-nawicon-glyph-nawicon.png"
              alt="external-Portfolio-investment-nawicon-glyph-nawicon"
            />{" "}
            Portfolio Summary
          </h2>
          <table className="table-style">
            <thead>
              <tr>
                <th>Ticker</th>
                <th>Stock Name</th>
                <th>Total Shares</th>
                <th>Total Asset Value</th>
                <th>As of Date</th>
              </tr>
            </thead>
            <tbody>
              {portfolioData?.allPortfolioSummaries?.nodes.map(
                (summary: any) => (
                  <tr
                    key={summary.ticker}
                    onClick={() => openModal(summary.ticker)}
                  >
                    <td>{summary.ticker}</td>
                    <td>{summary.stockByTicker.name}</td>
                    <td>{summary.totalShares}</td>
                    <td>
                      $
                      {summary.totalAssetValue
                        ? Number(summary.totalAssetValue).toFixed(2)
                        : "N/A"}
                    </td>
                    <td>{new Date(summary.asOfDate).toLocaleDateString()}</td>
                  </tr>
                )
              )}
            </tbody>
          </table>
        </div>
      </div>
      <div className="button-group">
        <button onClick={openBuyModal} className="trade-button">
          <img
            src="https://img.icons8.com/pulsar-line/48/buy-sign.png"
            alt="Buy"
          />
          Buy
        </button>
        <button onClick={openSellModal} className="trade-button">
          <img
            src="https://img.icons8.com/pulsar-line/48/sell-sign.png"
            alt="Sell"
          />
          Sell
        </button>
      </div>
      <Modal
        isOpen={modalIsOpen}
        onRequestClose={closeModal}
        contentLabel="Portfolio Transactions"
        style={{
          content: {
            top: "50%",
            left: "50%",
            right: "auto",
            bottom: "auto",
            marginRight: "-50%",
            transform: "translate(-50%, -50%)",
            width: "60%",
            border: "1px solid #ccc",
            borderRadius: "10px",
            padding: "20px",
          },
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <h2>Portfolio Transactions for {selectedTicker}</h2>
          <button
            onClick={closeModal}
            style={{ background: "none", border: "none", fontSize: "1.5rem" }}
          >
            ×
          </button>
        </div>
        {transactionsData && (
          <table className="table-style">
            <thead>
              <tr>
                <th>Date</th>
                <th>Action</th>
                <th>Volume</th>
                <th>Close Price</th>
                <th>Total Transaction Amount ($)</th>
              </tr>
            </thead>
            <tbody>
              {transactionsData.allPortfolioTransactions.nodes.map(
                (
                  transaction: {
                    transactionDate: string | number | Date;
                    action:
                      | string
                      | number
                      | boolean
                      | React.ReactElement<
                          any,
                          string | React.JSXElementConstructor<any>
                        >
                      | Iterable<React.ReactNode>
                      | React.ReactPortal
                      | React.PromiseLikeOfReactNode
                      | null
                      | undefined;
                    volume:
                      | string
                      | number
                      | boolean
                      | React.ReactElement<
                          any,
                          string | React.JSXElementConstructor<any>
                        >
                      | Iterable<React.ReactNode>
                      | React.ReactPortal
                      | React.PromiseLikeOfReactNode
                      | null
                      | undefined;
                    close:
                      | string
                      | number
                      | boolean
                      | React.ReactElement<
                          any,
                          string | React.JSXElementConstructor<any>
                        >
                      | Iterable<React.ReactNode>
                      | React.ReactPortal
                      | React.PromiseLikeOfReactNode
                      | null
                      | undefined;
                    totalTransactionAmount:
                      | string
                      | number
                      | boolean
                      | React.ReactElement<
                          any,
                          string | React.JSXElementConstructor<any>
                        >
                      | Iterable<React.ReactNode>
                      | React.ReactPortal
                      | React.PromiseLikeOfReactNode
                      | null
                      | undefined;
                    stockByTicker: {
                      name:
                        | string
                        | number
                        | boolean
                        | React.ReactElement<
                            any,
                            string | React.JSXElementConstructor<any>
                          >
                        | Iterable<React.ReactNode>
                        | React.ReactPortal
                        | React.PromiseLikeOfReactNode
                        | null
                        | undefined;
                    };
                  },
                  index: React.Key | null | undefined
                ) => (
                  <tr key={index}>
                    <td>
                      {new Date(
                        transaction.transactionDate
                      ).toLocaleDateString()}
                    </td>
                    <td>{transaction.action}</td>
                    <td>{transaction.volume}</td>
                    <td>{transaction.close}</td>
                    <td>{transaction.totalTransactionAmount}</td>
                  </tr>
                )
              )}
            </tbody>
          </table>
        )}
      </Modal>
      <Modal
        isOpen={tradeModalIsOpen}
        onRequestClose={closeTradeModal}
        contentLabel="Trade Modal"
        style={{
          content: {
            top: "50%",
            left: "50%",
            right: "auto",
            bottom: "auto",
            marginRight: "-50%",
            transform: "translate(-50%, -50%)",
            width: "40%",
            border: "1px solid #ccc",
            borderRadius: "10px",
            padding: "20px",
            backgroundColor: "#f8f9fa",
            boxShadow: "0 0 10px rgba(0, 0, 0, 0.1)",
          },
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <h2>{tradeType} Stock</h2>
          <button
            onClick={closeTradeModal}
            style={{ background: "none", border: "none", fontSize: "1.5rem" }}
          >
            ×
          </button>
        </div>
        <div style={{ margin: "20px 0" }}>
          <label style={{ display: "block", marginBottom: "10px" }}>
            Enter Stock:
            <input
              type="text"
              value={stockTicker}
              onChange={(e) => setStockTicker(e.target.value)}
              style={{
                width: "100%",
                padding: "8px",
                borderRadius: "4px",
                border: "1px solid #ccc",
                marginTop: "5px",
              }}
            />
          </label>
          <label style={{ display: "block", marginBottom: "10px" }}>
            Enter Volume (no of shares):
            <input
              type="number"
              value={volume || ""}
              onChange={(e) => setVolume(Number(e.target.value))}
              style={{
                width: "100%",
                padding: "8px",
                borderRadius: "4px",
                border: "1px solid #ccc",
                marginTop: "5px",
              }}
            />
          </label>
        </div>
        <button
          onClick={handleTrade}
          style={{
            padding: "10px 20px",
            borderRadius: "5px",
            border: "none",
            backgroundColor: "#28a745",
            color: "#fff",
            cursor: "pointer",
          }}
        >
          Submit Trade
        </button>
        {tradeFeedback && (
          <div style={{ marginTop: "20px", textAlign: "center" }}>
            <p>{tradeFeedback}</p>
          </div>
        )}
      </Modal>
      <style jsx>{`
        .content-section {
          display: flex;
          justify-content: space-around;
          margin-bottom: 20px;
          background-color: #f8f9fa;
          border-radius: 10px;
          padding: 20px;
          box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        .stocks-section,
        .portfolio-summary-section {
          width: 45%;
        }
        h2 {
          margin: 0 0 10px;
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }
        .table-style {
          width: 100%;
          border-collapse: collapse;
          border-radius: 10px;
          overflow: hidden;
        }
        .table-style th,
        .table-style td {
          border: 1px solid #ddd;
          padding: 8px;
        }
        .table-style th {
          padding-top: 12px;
          padding-bottom: 12px;
          text-align: left;
          background-color: #f4f4f4;
          color: black;
        }
        .table-style tbody tr:hover {
          background-color: #f1f1f1;
        }
        .button-group {
          display: flex;
          justify-content: center;
          margin: 20px;
        }
        .trade-button {
          background-color: #f8f9fa;
          border: 1px solid #ccc;
          padding: 10px 20px;
          margin: 0 10px;
          cursor: pointer;
          display: flex;
          align-items: center;
          gap: 10px;
          font-size: 1rem;
          border-radius: 5px;
          box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        .trade-button img {
          width: 24px;
          height: 24px;
        }
      `}</style>
    </Layout>
  );
};

export default HomePage;
