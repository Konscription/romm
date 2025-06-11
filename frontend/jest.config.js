export default {
  transform: {
    "^.+\\.(js|jsx|ts|tsx)$": "babel-jest",
    "^.+\\.vue$": "@vue/vue3-jest",
  },
  moduleNameMapper: {
    "^@/(.*)$": "<rootDir>/src/$1",
  },
  testEnvironment: "jsdom",
  transformIgnorePatterns: [
    "/node_modules/(?!(axios|vuetify|@mdi/font|@vue|pinia)/)",
  ],
  setupFilesAfterEnv: ["<rootDir>/tests/setup.js"],
  extensionsToTreatAsEsm: [".ts", ".tsx", ".vue"],
  moduleFileExtensions: ["js", "jsx", "ts", "tsx", "json", "node", "vue"],
};
