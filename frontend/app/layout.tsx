import React from "react";
import "./globals.css";

export const metadata = {
  title: "PersonalMind Pro",
  description: "Персональный ИИ с памятью и документами"
};

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ru">
      <body className="layout-wrapper">{children}</body>
    </html>
  );
}
