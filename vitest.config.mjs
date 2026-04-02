export default {
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["./frontend/src/__tests__/setup.ts"],
    include: ["frontend/src/**/*.{test,spec}.{ts,tsx}"],
    exclude: ["**/node_modules/**", "**/dist/**", "frontend/e2e/**"],
  },
};
