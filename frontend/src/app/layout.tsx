import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Header from "../components/Header";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "GomGom AI",
  description: "AI 기반 음식 추천 서비스",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <head>
        <script
          async
          src="https://developers.kakao.com/sdk/js/kakao.js"
        ></script>
      </head>
      <body className={inter.className}>
        <Header />
        {children}
      </body>
    </html>
  );
}
