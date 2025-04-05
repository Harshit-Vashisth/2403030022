import React, { useEffect, useState } from "react";
import { initAuthentication as authenticate } from "./api/auth";
import { loadAllUsers as fetchUsers, loadUserPosts as fetchUserPosts, loadPostComments as fetchPostComments } from "./api/api";

const TrendingPosts = () => {
  const [topPosts, setTopPosts] = useState([]);

  useEffect(() => {
    const fetchTrendingContent = async () => {
      await authenticate();
      const userMap = await fetchUsers();
      const postData = [];

      for (const userId in userMap) {
        const userPosts = await fetchUserPosts(userId);

        for (const singlePost of userPosts) {
          const postReplies = await fetchPostComments(singlePost.id);
          postData.push({
            post: singlePost,
            totalComments: postReplies.length,
          });
        }
      }

      const highestCommentCount = Math.max(...postData.map(entry => entry.totalComments));
      const mostActivePosts = postData.filter(entry => entry.totalComments === highestCommentCount);
      setTopPosts(mostActivePosts);
    };

    fetchTrendingContent();
  }, []);

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Trending Discussions</h1>
      {topPosts.map((item, idx) => (
        <div key={idx} className="bg-gray-50 border border-gray-300 p-4 rounded shadow-sm mb-3">
          <p className="font-semibold text-blue-800">User ID: {item.post.userid}</p>
          <p className="text-gray-800">{item.post.content}</p>
          <p className="text-sm text-gray-500">Comments: {item.totalComments}</p>
        </div>
      ))}
    </div>
  );
};

export default TrendingPosts;
