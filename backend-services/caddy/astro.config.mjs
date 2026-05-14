import { defineConfig } from "astro/config";
import react from "@astrojs/react";

export default defineConfig({
  devToolbar: { enabled: false },
  integrations: [react()],
  output: "static",
});
