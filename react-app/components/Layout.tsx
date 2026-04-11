import React from "react";
import Head from "next/head";
import Header from "./Header";

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <>
      <Head>
        <title>Stock Trading Platform</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>
      <div className="flex min-h-screen flex-col">
        <Header />
        <main className="flex-1 px-4 py-6 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full">
          {children}
        </main>
        <footer className="border-t border-terminal-border py-4 text-center text-xs text-terminal-muted">
          Stock Trading Platform &middot; Built with NextJS, GraphQL, Flask &amp; Anthropic Claude
        </footer>
      </div>
    </>
  );
};

export default Layout;
