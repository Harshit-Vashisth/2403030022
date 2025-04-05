import React, { useEffect, useState } from "react";
import { initAuthentication as authenticate } from "./api/auth";
import { loadAllUsers as fetchUsers, loadUserPosts as fetchUserPosts, loadPostComments as fetchPostComments } from "./api/api";

const TopUsers = () => {
  const [leadingUsers, setLeadingUsers] = useState([]);

  useEffect(() => {
    const getTopContributors = async () => {
      await authenticate();
      const userList = await fetchUsers();
      const userPostStats = [];

      for (const userId in userList) {
        const userPosts = await fetchUserPosts(userId);
        userPostStats.push({
          username: userList[userId],
          totalPosts: userPosts.length,
        });
      }

      userPostStats.sort((a, b) => b.totalPosts - a.totalPosts);
      setLeadingUsers(userPostStats.slice(0, 5));
    };

    getTopContributors();
  }, []);

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Top 5 Active Users</h1>
      <ul className="space-y-2">
        {leadingUsers.map((user, idx) => (
          <li key={idx} className="bg-white p-4 rounded-lg shadow-md">
            <span className="font-semibold text-blue-700">{user.username}</span> —{" "}
            <span className="text-gray-700">{user.totalPosts} Posts</span>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default TopUsers;
