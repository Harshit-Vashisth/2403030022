import axios from "axios";
import { retrieveToken as getAuthToken, getApiRoot as getBaseUrl } from "./auth";


// Axios config with auth header
const getAuthHeaders = () => ({
  headers: {
    Authorization: `Bearer ${getAuthToken()}`
  }
});

// Fetch list of registered users
export const loadAllUsers = async () => {
  try {
    const endpoint = `${getBaseUrl()}/users`;
    const response = await axios.get(endpoint, getAuthHeaders());
    return response.data?.users || [];
  } catch (error) {
    console.error("Failed to load users:", error);
    return [];
  }
};

// Fetch posts by a specific user ID
export const loadUserPosts = async (userId) => {
  try {
    const url = `${getBaseUrl()}/users/${userId}/posts`;
    const result = await axios.get(url, getAuthHeaders());
    return result.data?.posts || [];
  } catch (err) {
    console.error(`Could not fetch posts for user ${userId}:`, err);
    return [];
  }
};

// Fetch comments for a specific post ID
export const loadPostComments = async (postId) => {
  try {
    const path = `${getBaseUrl()}/posts/${postId}/comments`;
    const res = await axios.get(path, getAuthHeaders());
    return res.data?.comments || [];
  } catch (err) {
    console.error(`Error retrieving comments for post ${postId}:`, err);
    return [];
  }
};
