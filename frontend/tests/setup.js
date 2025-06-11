// Mock FormData since it's not available in the test environment
global.FormData = class FormData {
  constructor() {
    this.data = {};
  }

  append(key, value, filename) {
    this.data[key] = { value, filename };
  }
};

// Mock Blob since it's not available in the test environment
global.Blob = class Blob {
  constructor(content, options) {
    this.content = content;
    this.options = options;
  }
};

// Add any other global mocks or setup needed for tests

// Default test credentials if not provided in environment variables
process.env.TEST_USERNAME = process.env.TEST_USERNAME || "romm";
process.env.TEST_PASSWORD = process.env.TEST_PASSWORD || "romm";
