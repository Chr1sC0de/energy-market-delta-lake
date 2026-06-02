import Reveal from "reveal.js";
import "reveal.js/dist/reveal.css";

import { renderSlide } from "./slide-components.js";
import { slides } from "./slide-data.js";
import "./theme.css";

const deckRoot = document.querySelector(".slides");

if (deckRoot === null) {
  throw new Error("Reveal slide root was not found.");
}

deckRoot.innerHTML = slides.map(renderSlide).join("");

window.Reveal = Reveal;

Reveal.initialize({
  center: false,
  controls: true,
  controlsLayout: "edges",
  disableLayout: false,
  embedded: false,
  fragments: true,
  hash: true,
  height: 720,
  margin: 0.04,
  maxScale: 1.35,
  minScale: 0.2,
  progress: true,
  slideNumber: "c/t",
  transition: "fade",
  width: 1280,
});
