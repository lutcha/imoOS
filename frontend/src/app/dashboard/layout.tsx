import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Dashboard de Gestão | ImoOS",
  description: "Visão geral de todas as obras e projetos",
};

export default function DashboardLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return children;
}
