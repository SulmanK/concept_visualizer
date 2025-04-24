import { describe, it, expect } from "vitest";
import { queryKeys } from "../queryKeys";

describe("Query Keys Configuration", () => {
  describe("concepts", () => {
    it("should return the correct base concepts key", () => {
      expect(queryKeys.concepts.all()).toEqual(["concepts"]);
    });

    it("should return the correct recent concepts key without params", () => {
      expect(queryKeys.concepts.recent()).toEqual([
        "concepts",
        "recent",
        undefined,
        undefined,
      ]);
    });

    it("should return the correct recent concepts key with params", () => {
      const userId = "user-123";
      const limit = 5;
      expect(queryKeys.concepts.recent(userId, limit)).toEqual([
        "concepts",
        "recent",
        userId,
        limit,
      ]);
    });

    it("should return the correct concept detail key without params", () => {
      expect(queryKeys.concepts.detail()).toEqual([
        "concepts",
        "detail",
        undefined,
        undefined,
      ]);
    });

    it("should return the correct concept detail key with params", () => {
      const conceptId = "concept-123";
      const userId = "user-123";
      expect(queryKeys.concepts.detail(conceptId, userId)).toEqual([
        "concepts",
        "detail",
        conceptId,
        userId,
      ]);
    });
  });

  describe("tasks", () => {
    it("should return the correct base tasks key", () => {
      expect(queryKeys.tasks.all()).toEqual(["tasks"]);
    });

    it("should return the correct task detail key without id", () => {
      expect(queryKeys.tasks.detail()).toEqual(["tasks", "detail", undefined]);
    });

    it("should return the correct task detail key with id", () => {
      const taskId = "task-123";
      expect(queryKeys.tasks.detail(taskId)).toEqual([
        "tasks",
        "detail",
        taskId,
      ]);
    });
  });

  describe("mutations", () => {
    it("should return the correct concept generation key", () => {
      expect(queryKeys.mutations.conceptGeneration()).toEqual([
        "conceptGeneration",
      ]);
    });

    it("should return the correct concept refinement key", () => {
      expect(queryKeys.mutations.conceptRefinement()).toEqual([
        "conceptRefinement",
      ]);
    });

    it("should return the correct export image key", () => {
      expect(queryKeys.mutations.exportImage()).toEqual(["exportImage"]);
    });
  });

  describe("rateLimits", () => {
    it("should return the correct rate limits key", () => {
      expect(queryKeys.rateLimits()).toEqual(["rateLimits"]);
    });
  });

  describe("user", () => {
    it("should return the correct base user key", () => {
      expect(queryKeys.user.all()).toEqual(["user"]);
    });

    it("should return the correct user preferences key without userId", () => {
      expect(queryKeys.user.preferences()).toEqual([
        "user",
        "preferences",
        undefined,
      ]);
    });

    it("should return the correct user preferences key with userId", () => {
      const userId = "user-123";
      expect(queryKeys.user.preferences(userId)).toEqual([
        "user",
        "preferences",
        userId,
      ]);
    });
  });
});
