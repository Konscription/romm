// Script to ensure the test user exists in the database
import axios from "axios";
import { execSync } from "child_process";

// Get test credentials from environment variables
// These should be set in the .env file and loaded by Playwright
const testUsername = process.env.TEST_USERNAME || "romm";
const testPassword = process.env.TEST_PASSWORD || "romm";

// Export a function that will be used as a global setup
export default async function globalSetup() {
  console.log(`Setting up test user: ${testUsername}`);

  try {
    // First, try to authenticate as admin to get a token
    const adminAuth = await axios.post(
      "http://localhost:3000/api/login",
      {},
      {
        auth: {
          username: "romm",
          password: "romm",
        },
      },
    );

    const token = adminAuth.data.access_token;

    // Check if the test user already exists
    try {
      await axios.post(
        "http://localhost:3000/api/login",
        {},
        {
          auth: {
            username: testUsername,
            password: testPassword,
          },
        },
      );
      console.log("Test user already exists and credentials are valid");
      return Promise.resolve();
    } catch (error) {
      // User doesn't exist or password is incorrect, continue to create/update
      console.log("Test user needs to be created or updated");
    }

    // Try to create the user
    try {
      await axios.post(
        "http://localhost:3000/api/users",
        {
          username: testUsername,
          password: testPassword,
          email: `${testUsername}@example.com`,
          role: "VIEWER",
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      );
      console.log(`Created test user: ${testUsername}`);
    } catch (error) {
      if (error.response && error.response.status === 409) {
        // User exists but password might be wrong, try to update
        console.log(
          `User ${testUsername} already exists, updating password...`,
        );

        // There's no direct API to update a user's password, so we'll use a SQL command
        // This is a bit of a hack, but it's just for testing purposes
        const dbPath = process.env.ROMM_BASE_PATH || "/romm";
        const updatePasswordCmd = `
          echo "UPDATE users SET hashed_password = '$(echo -n "${testPassword}" | python -c "import bcrypt; import sys; print(bcrypt.hashpw(sys.stdin.read().encode(), bcrypt.gensalt()).decode())")' WHERE username = '${testUsername}';" | sqlite3 ${dbPath}/database/romm.db
        `;

        try {
          execSync(updatePasswordCmd);
          console.log(`Updated password for user: ${testUsername}`);
        } catch (sqlError) {
          console.error("Failed to update password via SQL:", sqlError);
          console.log(
            "You may need to manually ensure the test user exists with the correct password",
          );
        }
      } else {
        console.error("Failed to create test user:", error.message);
        console.log(
          "You may need to manually ensure the test user exists with the correct password",
        );
      }
    }
  } catch (error) {
    console.error("Failed to authenticate as admin:", error.message);
    console.log(
      "You may need to manually ensure the test user exists with the correct password",
    );
  }

  // Return a promise that resolves when setup is complete
  return Promise.resolve();
}
