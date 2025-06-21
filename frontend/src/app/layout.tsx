export const metadata = {
  title: 'GomGom AI',
  description: 'GPT와 함께 기분에 딱 맞는 음식과 레시피를 추천받아보세요!',
  metadataBase: new URL('http://localhost:3000'),
};


export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
