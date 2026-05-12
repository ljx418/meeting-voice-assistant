import React from "react";
import { loadEmbedBootstrap } from "../harness";

export function EmbedPanel(): JSX.Element {
  return (
    <section>
      <h2>Embed</h2>
      <button onClick={() => loadEmbedBootstrap()}>Load embed bootstrap</button>
    </section>
  );
}

