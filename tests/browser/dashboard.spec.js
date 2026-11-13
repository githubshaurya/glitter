import { test, expect } from "@playwright/test";
import fs from "node:fs/promises";
import path from "node:path";

test("unlock, inspect, navigate, halt and lock the dashboard", async ({
  page,
}, testInfo) => {
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  const fixture = {
    control: {
      mode: "ACTIVE",
      loss_latched: false,
      reason: "Synthetic UI test fixture",
    },
    execution_enabled: false,
    model: "openai/gpt-oss-120b",
    policy: {
      max_order_fraction: ".01",
      max_symbol_fraction: ".02",
      max_total_fraction: ".04",
      max_daily_loss: ".01",
      max_drawdown: ".02",
    },
    equity: [
      {
        time: "2026-11-13T00:00:00Z",
        data: {
          equity: "100000",
          cash: "100000",
          positions: {},
          drawdown: "0",
        },
      },
      {
        time: "2026-11-13T01:00:00Z",
        data: {
          equity: "100000",
          cash: "100000",
          positions: {},
          drawdown: "0",
        },
      },
    ],
    runs: [],
    intents: [],
    decisions: [],
    observations: [],
    experiments: [],
  };
  await page.route("**/*", async (route) => {
    const url = new URL(route.request().url());
    if (url.origin !== "http://glitter.test") return route.abort();
    if (url.pathname === "/api/overview") {
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(fixture),
      });
    }
    if (url.pathname === "/api/control") {
      expect(route.request().headers().authorization).toBe(
        "Bearer synthetic-test-token",
      );
      fixture.control.mode = route.request().postDataJSON().mode;
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ control: fixture.control }),
      });
    }
    const filename =
      url.pathname === "/" ? "index.html" : path.basename(url.pathname);
    const contentType = filename.endsWith(".css")
      ? "text/css"
      : filename.endsWith(".js")
        ? "text/javascript"
        : "text/html";
    return route.fulfill({
      status: 200,
      contentType,
      body: await fs.readFile(path.join("trading/static", filename)),
    });
  });
  await page.goto("http://glitter.test/");
  await page.getByLabel("Dashboard token").fill("synthetic-test-token");
  await page.getByRole("button", { name: "Unlock dashboard" }).click();
  await expect(page.locator("#equity-value")).toHaveText("$100,000.00");
  await expect(page.locator("#chart svg")).toBeVisible();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  await page
    .getByRole("button", { name: "Decision journal", exact: true })
    .click();
  await expect(page.locator("#journal")).toBeVisible();
  await page
    .getByRole("button", { name: "Overview", exact: false })
    .first()
    .click();
  page.once("dialog", (dialog) => dialog.accept());
  await page.getByRole("button", { name: "Halt & cancel open orders" }).click();
  await expect(page.locator("#mode-badge")).toHaveText("HALTED");
  await page.screenshot({
    path: testInfo.outputPath("dashboard.png"),
    fullPage: true,
  });
  await page.getByRole("button", { name: "Lock", exact: true }).click();
  await expect(page.locator("#login")).toBeVisible();
  expect(errors).toEqual([]);
});
