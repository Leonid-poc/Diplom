import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "./providers";

export const metadata: Metadata = {
  title: "ПИС «Маршрут» — проектирование городских маршрутов",
  description:
    "Программно-информационная система автоматизированного проектирования " +
    "городских маршрутов пассажирских перевозок. ОГУ, 09.03.04, ВКР Л.Е. Георга.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru">
      <body className="min-h-screen bg-background antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
