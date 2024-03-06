import React from 'react';

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="layout">
      <header className="header">
        <h1 className="title">Stock Trading Platform</h1>
      </header>
      <main className="main">
        {children}
      </main>
      <footer className="footer">
        <p>© 2024 Stock Trading Platform</p>
      </footer>
      <style jsx>{`
        .layout {
          display: flex;
          flex-direction: column;
          min-height: 100vh;
        }
        .header {
          background-color: #20232a;
          color: #61dafb;
          text-align: center;
          padding: 20px;
        }
        .title {
          margin: 0;
          font-size: 2rem;
        }
        .main {
          flex: 1;
          padding: 20px;
        }
        .footer {
          background-color: #20232a;
          color: #61dafb;
          text-align: center;
          padding: 10px;
        }
      `}</style>
    </div>
  );
};

export default Layout;