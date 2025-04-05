import axios from "axios";

// Core service endpoint
const SERVICE_ROOT = "/evaluation-service";
const AUTH_ENDPOINT = `${SERVICE_ROOT}/auth`;

// Developer credentials (do not expose in production)
const userProfile = {
  email: "2403030022@mail.jiit.ac.in",
  name: "harshit vashisth",
  rollNo: "2403030022",
  accessCode: "SrMQqR",
  clientID: "97d015cd-7d61-4e88-9f19-92718db56d2d",
  clientSecret: "CZgpZHQxyHrznYFx"
};

// Cached token storage
let sessionToken = "";

/**
 * Performs user authentication and stores the access token.
 */
export const initAuthentication = async () => {
  try {
    const response = await axios.post(AUTH_ENDPOINT, userProfile);
    sessionToken = response.data?.token || "";
    if (!sessionToken) {
      console.warn("Received empty token from authentication service.");
    } else {
      console.log("Authenticated. Token:", sessionToken);
    }
  } catch (error) {
    console.error("Error during authentication process:", error.response?.data || error.message);
  }
};


/**
 * Returns the current bearer token.
 */
export const retrieveToken = () => sessionToken;

/**
 * Returns the base URL for all API requests.
 */
export const getApiRoot = () => SERVICE_ROOT;
