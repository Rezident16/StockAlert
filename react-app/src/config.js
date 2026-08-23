// The backend's origin. In production the built React app is served by
// the same Flask process, so relative URLs already resolve correctly and
// no explicit origin is needed. In dev, CRA's dev server runs on a
// different port, so requests to endpoints that bypass the "proxy" field
// in package.json (OAuth redirects, Socket.IO) need an explicit origin.
export const API_BASE_URL =
  process.env.NODE_ENV === "production"
    ? ""
    : process.env.REACT_APP_BASE_URL || "http://localhost:5000";
