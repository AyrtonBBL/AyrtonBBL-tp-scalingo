import { describe, expect, it, vi } from "vitest";

vi.stubEnv("VITE_API_URL", "https://api.example.com");
const { buildBaseUrl } = await import("./api");

describe("buildBaseUrl", () => {
  it("retire le slash final", () => {
    expect(buildBaseUrl("https://api.example.com/")).toBe("https://api.example.com");
  });
  it("garde une URL propre intacte", () => {
    expect(buildBaseUrl("https://api.example.com")).toBe("https://api.example.com");
  });
  it("échoue si la variable est absente", () => {
    expect(() => buildBaseUrl(undefined)).toThrow(/VITE_API_URL/);
  });
});
