import React from "react";
import { bffJson } from "../harness";

export function PackConnectorPanel(): JSX.Element {
  return (
    <section>
      <h2>Packs and Connectors</h2>
      <button onClick={() => bffJson("/bff/packs")}>Load packs</button>
      <button onClick={() => bffJson("/bff/connectors/reference_app_connector/health")}>Check connector</button>
    </section>
  );
}

