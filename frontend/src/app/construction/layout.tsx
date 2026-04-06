import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Obras | ImoOS",
  description: "Gestão de obras e projetos de construção",
};

export default function ConstructionLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return children;
}
