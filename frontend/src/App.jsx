/**
 * App.jsx — root component.
 * Composes the Navbar + single RegisterPage.
 */

import Navbar from "./components/Navbar";
import RegisterPage from "./pages/RegisterPage";

export default function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <RegisterPage />
    </div>
  );
}
