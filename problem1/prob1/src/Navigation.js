import React from "react";
import { Link } from "react-router-dom";

const Navigation = () => {
  return (
    <header className="bg-blue-700 text-white px-6 py-3 flex space-x-6">
      <Link to="/" className="hover:underline">
        User Leaderboard
      </Link>
      <Link to="/trending" className="hover:underline">
        Hot Posts
      </Link>
      <Link to="/feed" className="hover:underline">
        Live Updates
      </Link>
    </header>
  );
};

export default Navigation;
