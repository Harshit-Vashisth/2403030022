import React, { useEffect, useState } from "react";
import { initAuthentication as authenticate } from "./api/auth";
import { loadAllUsers as fetchUsers, loadUserPosts as fetchUserPosts, loadPostComments as fetchPostComments } from "./api/api";

const Feed = () => {
  const [posts, setPosts] = useState([]);

  const loadFeed = async () => {
    await authenticate();
    const usersData = await fetchUsers();
    let combinedPosts = [];

    for (const userId in usersData) {
      const individualPosts = await fetchUserPosts(userId);
      const enrichedPosts = await Promise.all(
        individualPosts.map(async (post) => {
          const postComments = await fetchPostComments(post.id);
          return {
            ...post,
            username: usersData[userId],
            commentCount: postComments.length,
          };
        })
      );
      combinedPosts = [...combinedPosts, ...enrichedPosts];
    }

    combinedPosts.sort((a, b) => b.id - a.id);
    setPosts(combinedPosts);
  };

  useEffect(() => {
    loadFeed();
    const interval = setInterval(loadFeed, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">User Activity Feed</h1>
      {posts.map((post) => (
        <div key={post.id} className="bg-gray-100 p-4 rounded-lg shadow-sm mb-3">
          <p className="text-indigo-800 font-medium">{post.username}</p>
          <p>{post.content}</p>
          <p className="text-sm text-gray-600">Comments: {post.commentCount}</p>
        </div>
      ))}
    </div>
  );
};

export default Feed;
