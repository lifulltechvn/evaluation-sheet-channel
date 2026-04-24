import "./globals.css";

export const metadata = { title: "HR Evaluation Dashboard", description: "Evaluation Sheet Management" };

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
