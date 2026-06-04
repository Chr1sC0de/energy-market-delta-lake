import { spawn } from "node:child_process";
import net from "node:net";
import { chromium } from "playwright";

const identifier = "maintainer@example.test";
const password = "correct horse battery staple";
const failureText = "Sign in failed. Check your details and try again.";

async function findFreePort() {
  return await new Promise((resolve, reject) => {
    const server = net.createServer();
    server.once("error", reject);
    server.listen(0, "127.0.0.1", () => {
      const address = server.address();
      server.close(() => {
        if (address && typeof address === "object") {
          resolve(address.port);
          return;
        }
        reject(new Error("Could not find a free local port."));
      });
    });
  });
}

async function waitForPreview(process, baseUrl) {
  const startedAt = Date.now();
  let output = "";

  process.stdout.on("data", (chunk) => {
    output += chunk.toString();
  });
  process.stderr.on("data", (chunk) => {
    output += chunk.toString();
  });

  while (Date.now() - startedAt < 30_000) {
    if (process.exitCode !== null) {
      throw new Error(`Vite preview exited early.\n${output}`);
    }

    try {
      const response = await fetch(baseUrl);
      if (response.ok) {
        return;
      }
    } catch {
      await new Promise((resolve) => setTimeout(resolve, 250));
    }
  }

  throw new Error(`Timed out waiting for Vite preview.\n${output}`);
}

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

async function assertNoCredentialExposure(page) {
  const currentUrl = page.url();
  assert(!currentUrl.includes(identifier), "Identifier was written to the URL.");
  assert(!currentUrl.includes(password), "Password was written to the URL.");

  const storageValues = await page.evaluate(() => ({
    local: Object.entries(localStorage),
    session: Object.entries(sessionStorage),
  }));
  const storageText = JSON.stringify(storageValues);

  assert(
    !storageText.includes(identifier),
    "Identifier was written to browser storage.",
  );
  assert(!storageText.includes(password), "Password was written to browser storage.");

  const visibleText = await page.locator("body").innerText();
  assert(!visibleText.includes(identifier), "Identifier was shown in visible text.");
  assert(!visibleText.includes(password), "Password was shown in visible text.");
}

async function assertNoAuthInternalExposure(page) {
  const visibleText = await page.locator("body").innerText();
  const internalFragments = [
    "Cognito",
    "NotAuthorizedException",
    "PASSWORD_VERIFIER",
  ];

  for (const fragment of internalFragments) {
    assert(
      !visibleText.includes(fragment),
      `Auth internal text was shown: ${fragment}.`,
    );
  }
}

async function assertNoHorizontalOverflow(page) {
  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth > window.innerWidth,
  );
  assert(!overflow, "Login page has horizontal document overflow.");
}

async function runCase(browser, baseUrl, config) {
  const context = await browser.newContext({ viewport: config.viewport });
  const page = await context.newPage();
  const loginUrl = `${baseUrl}/login?next=${encodeURIComponent(config.next)}`;
  let submittedRequest = null;
  let requestCount = 0;

  await page.route("**/*", async (route) => {
    const requestUrl = new URL(route.request().url());

    if (
      route.request().isNavigationRequest() &&
      requestUrl.pathname === config.redirectTo
    ) {
      await route.fulfill({
        body: "<!doctype html><title>Redirect accepted</title>",
        contentType: "text/html",
        status: 200,
      });
      return;
    }

    await route.fallback();
  });

  await page.route("**/auth/login", async (route) => {
    const request = route.request();
    requestCount += 1;
    submittedRequest = {
      method: request.method(),
      postData: request.postDataJSON(),
      url: request.url(),
    };

    if (requestCount === 1) {
      await route.fulfill({
        body: JSON.stringify({
          code: "NotAuthorizedException",
          message: "Cognito challenge PASSWORD_VERIFIER failed.",
          username: identifier,
        }),
        contentType: "application/json",
        status: 401,
      });
      return;
    }

    await route.fulfill({
      body: JSON.stringify({ redirect_to: config.redirectTo }),
      contentType: "application/json",
      status: 200,
    });
  });

  await page.goto(loginUrl);
  await page.getByRole("heading", { name: "Sign in to continue." }).waitFor();
  await page.getByLabel("Email or username").fill(identifier);
  await page.getByLabel("Password").fill(password);
  await assertNoHorizontalOverflow(page);

  await page.getByRole("button", { name: "Sign in" }).click();
  await page.getByText(failureText).waitFor();
  await assertNoAuthInternalExposure(page);

  assert(submittedRequest, "Login form did not submit.");
  assert(submittedRequest.method === "POST", "Login did not use POST.");
  assert(
    new URL(submittedRequest.url).pathname === "/auth/login",
    "Login did not post to /auth/login.",
  );
  assert(
    !submittedRequest.url.includes(identifier) &&
      !submittedRequest.url.includes(password),
    "Credentials were placed in the login request URL.",
  );
  assert(
    submittedRequest.postData.identifier === identifier,
    "Identifier was not sent in the request body.",
  );
  assert(
    submittedRequest.postData.password === password,
    "Password was not sent in the request body.",
  );
  assert(
    submittedRequest.postData.next === config.next,
    "The next query value was not sent as the requested return path.",
  );
  await assertNoCredentialExposure(page);

  await page.getByRole("button", { name: "Sign in" }).click();
  await page.waitForURL(`${baseUrl}${config.redirectTo}`);

  assert(
    page.url() !== `${baseUrl}${config.next}`,
    "Login redirected directly from the raw next query value.",
  );
  assert(
    page.url() === `${baseUrl}${config.redirectTo}`,
    "Login did not follow the API-returned redirect_to path.",
  );
  await assertNoCredentialExposure(page);

  await context.close();
}

async function main() {
  const port = await findFreePort();
  const baseUrl = `http://127.0.0.1:${port}`;
  const preview = spawn(
    process.platform === "win32"
      ? "node_modules\\.bin\\vite.cmd"
      : "node_modules/.bin/vite",
    ["preview", "--host", "127.0.0.1", "--port", String(port), "--strictPort"],
    { stdio: ["ignore", "pipe", "pipe"] },
  );

  let browser;

  try {
    await waitForPreview(preview, baseUrl);
    browser = await chromium.launch();

    await runCase(browser, baseUrl, {
      next: "/dagster-webserver/admin",
      redirectTo: "/dagster-webserver/guest",
      viewport: { height: 900, width: 1280 },
    });
    await runCase(browser, baseUrl, {
      next: "/marimo",
      redirectTo: "/",
      viewport: { height: 820, width: 360 },
    });
  } finally {
    if (browser) {
      await browser.close();
    }
    preview.kill("SIGTERM");
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
