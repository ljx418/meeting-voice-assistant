# Reference App BFF Config

Use the reusable Full BFF template in `templates/bff/fastapi` with this example
configuration. The BFF owns the server-side harnessOS capability token and
binds browser identity to a reference app scope.

The browser must call `/bff/*` routes only.

