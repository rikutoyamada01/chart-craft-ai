import { StrictMode } from "react"
import ReactDOM from "react-dom/client"

import { CustomProvider } from "./components/ui/provider"
import HomePage from "./routes/index"

const rootElement = document.getElementById("root")

if (rootElement) {
  ReactDOM.createRoot(rootElement).render(
    <StrictMode>
      <CustomProvider>
        <HomePage />
      </CustomProvider>
    </StrictMode>,
  )
}
