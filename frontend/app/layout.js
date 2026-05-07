import "./globals.css";
import AuthGuard from "./components/AuthGuard";

export const metadata = { title: "HR Evaluation Dashboard", description: "Evaluation Sheet Management" };

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <AuthGuard>{children}</AuthGuard>
      </body>
    </html>
  );
}
