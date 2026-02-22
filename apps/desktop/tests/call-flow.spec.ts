import { test, expect } from "@playwright/test";

test("user can start and end a session", async ({ page }) => {
  await page.goto("http://localhost:5173");
  await page.getByRole("button", { name: "Start Call" }).click();
  await expect(page.getByText("Call in progress")).toBeVisible();
  await page.getByRole("button", { name: "End Call" }).click();
  await expect(page.getByText("Post-Call Scorecard")).toBeVisible();
});
