import { mkdir } from "node:fs/promises";
import { spawn } from "node:child_process";
import { chromium } from "playwright";

const port = Number(process.env.PORT ?? "4179");
const host = "127.0.0.1";
const baseUrl = `http://${host}:${port}`;
const outputDir =
  process.env.RALPH_PRESENTATION_REVIEW_DIR ??
  "/tmp/ralph-loop-presentation-review";

const viewports = [
  {
    name: "desktop",
    width: 1440,
    height: 900,
  },
  {
    name: "mobile",
    width: 390,
    height: 844,
  },
];

const screenshotSlides = [
  {
    index: 0,
    name: "cover",
  },
  {
    index: 3,
    name: "delivery-mode",
  },
  {
    index: 5,
    name: "local-qa",
  },
  {
    index: 7,
    name: "local-integration",
  },
  {
    index: 8,
    name: "promotion",
  },
  {
    index: 9,
    name: "failure",
  },
  {
    index: 10,
    name: "demo-path",
  },
  {
    index: 11,
    name: "trust-points",
  },
];

const server = spawn(
  "npx",
  ["vite", "preview", "--host", host, "--port", String(port), "--strictPort"],
  {
    shell: false,
    stdio: ["ignore", "pipe", "pipe"],
  },
);

const serverLogs = [];
server.stdout.on("data", (chunk) => serverLogs.push(chunk.toString()));
server.stderr.on("data", (chunk) => serverLogs.push(chunk.toString()));

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function waitForServer() {
  const deadline = Date.now() + 15_000;
  while (Date.now() < deadline) {
    try {
      const response = await fetch(baseUrl);
      if (response.ok) {
        return;
      }
    } catch {
      await delay(250);
    }
  }

  throw new Error(`Vite preview did not respond at ${baseUrl}.`);
}

async function stopServer() {
  if (server.exitCode !== null || server.signalCode !== null) {
    return;
  }

  const stopped = new Promise((resolve) => {
    server.once("exit", resolve);
  });

  server.kill("SIGTERM");
  await Promise.race([
    stopped,
    delay(2_000).then(() => {
      if (server.exitCode === null && server.signalCode === null) {
        server.kill("SIGKILL");
      }
    }),
  ]);
}

async function revealFragments(page) {
  await page.evaluate(() => {
    let guard = 0;
    while (window.Reveal.availableFragments().next && guard < 30) {
      window.Reveal.nextFragment();
      guard += 1;
    }

    window.Reveal.getCurrentSlide()
      .querySelectorAll(".fragment")
      .forEach((fragment) => {
        fragment.classList.add("visible");
        fragment.classList.remove("future");
      });
  });
}

async function goToSlide(page, slideIndex) {
  await page.evaluate((index) => {
    window.Reveal.configure({
      backgroundTransition: "none",
      transition: "none",
    });
    window.Reveal.slide(index, 0, -1);
    window.Reveal.layout();
  }, slideIndex);
  await revealFragments(page);
  await page.waitForTimeout(180);
}

async function visibleTextProblems(page) {
  return page.evaluate(() => {
    const margin = 2;
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;
    const slide = window.Reveal.getCurrentSlide();

    return Array.from(slide.querySelectorAll("h1, p, strong, small, span, code, li"))
      .filter((element) => {
        const text = element.textContent?.trim();
        const style = window.getComputedStyle(element);
        return text && style.visibility !== "hidden" && style.display !== "none";
      })
      .flatMap((element) => {
        const rect = element.getBoundingClientRect();
        const text = element.textContent.trim().replace(/\s+/g, " ");
        const outside =
          rect.left < -margin ||
          rect.top < -margin ||
          rect.right > viewportWidth + margin ||
          rect.bottom > viewportHeight + margin;

        return outside
          ? [
              {
                bottom: Math.round(rect.bottom),
                left: Math.round(rect.left),
                right: Math.round(rect.right),
                text,
                top: Math.round(rect.top),
              },
            ]
          : [];
      });
  });
}

async function run() {
  await waitForServer();
  await mkdir(outputDir, { recursive: true });

  const browser = await chromium.launch();
  const failures = [];

  try {
    for (const viewport of viewports) {
      const page = await browser.newPage({ viewport });
      const consoleErrors = [];

      page.on("console", (message) => {
        if (message.type() === "error") {
          consoleErrors.push(message.text());
        }
      });
      page.on("pageerror", (error) => consoleErrors.push(error.message));

      await page.goto(baseUrl, { waitUntil: "networkidle" });
      const slideCount = await page.locator("section.slide").count();

      if (slideCount !== 12) {
        failures.push(
          `${viewport.name}: expected 12 slides, found ${slideCount}.`,
        );
      }

      for (let slideIndex = 0; slideIndex < slideCount; slideIndex += 1) {
        await goToSlide(page, slideIndex);
        const problems = await visibleTextProblems(page);
        if (problems.length > 0) {
          failures.push(
            `${viewport.name} slide ${slideIndex + 1}: ${problems
              .slice(0, 4)
              .map((problem) => `"${problem.text}" ${JSON.stringify(problem)}`)
              .join("; ")}`,
          );
        }
      }

      for (const screenshotSlide of screenshotSlides) {
        await goToSlide(page, screenshotSlide.index);
        await page.screenshot({
          fullPage: false,
          path: `${outputDir}/${viewport.name}-${screenshotSlide.name}.png`,
        });
      }

      if (consoleErrors.length > 0) {
        failures.push(
          `${viewport.name}: console errors: ${consoleErrors.join(" | ")}`,
        );
      }

      await page.close();
    }
  } finally {
    await browser.close();
    await stopServer();
  }

  if (failures.length > 0) {
    throw new Error(failures.join("\n"));
  }

  console.log(`Visual check passed. Screenshots: ${outputDir}`);
  process.exit(0);
}

run().catch((error) => {
  stopServer()
    .catch(() => undefined)
    .finally(() => {
      console.error(error.message);
      if (serverLogs.length > 0) {
        console.error(serverLogs.join(""));
      }
      process.exit(1);
    });
});
