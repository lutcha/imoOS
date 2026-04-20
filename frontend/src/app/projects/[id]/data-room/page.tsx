"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { 
  ArrowLeft, 
  FileText, 
  Upload, 
  Download, 
  Search, 
  Filter, 
  MoreVertical, 
  History,
  FileCheck,
  ShieldCheck,
  AlertCircle
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useProject, featureToProject } from "@/hooks/useProjects";
import { useProjectDocuments, useUploadDocument } from "@/hooks/useProjectDocuments";
import { Skeleton } from "@/components/ui/Skeleton";
import { formatDate } from "@/lib/format";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
} from "@/components/ui/dialog";

const CATEGORIES = [
  { id: "PLAN", label: "Plantas e Projetos", icon: FileText, color: "text-blue-600" },
  { id: "LICENSE", label: "Licenças e Alvarás", icon: ShieldCheck, color: "text-emerald-600" },
  { id: "CONTRACT", label: "Contratos e Cadernos", icon: FileCheck, color: "text-violet-600" },
  { id: "OTHER", label: "Outros Documentos", icon: AlertCircle, color: "text-amber-600" },
] as const;

export default function ProjectDataRoomPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState<string | "all">("all");
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  
  // Data
  const { data: feature, isLoading: projectLoading } = useProject(id);
  const project = feature ? featureToProject(feature) : null;
  const { data: documents = [], isLoading: docsLoading } = useProjectDocuments(id);
  const { mutate: uploadDoc, isPending: isUploading } = useUploadDocument();

  // Filtered docs
  const filteredDocs = documents.filter(doc => {
    const matchesSearch = doc.title.toLowerCase().includes(search.toLowerCase());
    const matchesCategory = categoryFilter === "all" || doc.category === categoryFilter;
    return matchesSearch && matchesCategory;
  });

  const handleUpload = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    uploadDoc({ projectId: id, formData }, {
      onSuccess: () => {
        setIsUploadOpen(false);
      }
    });
  };

  if (projectLoading) {
    return (
      <div className="p-8 space-y-6">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-64 w-full rounded-2xl" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => router.back()}
            className="h-10 w-10 flex items-center justify-center rounded-full hover:bg-gray-100 transition-colors"
          >
            <ArrowLeft className="h-5 w-5 text-gray-500" />
          </button>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Project Data Room</h1>
            <p className="text-sm text-muted-foreground font-medium">
              Repositório central de documentação técnica para {project?.name}
            </p>
          </div>
        </div>

        <Dialog open={isUploadOpen} onOpenChange={setIsUploadOpen}>
          <DialogTrigger asChild>
            <Button className="gap-2 bg-primary hover:bg-primary/90 text-white px-6">
              <Upload className="h-4 w-4" />
              Submeter Documento
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[425px]">
            <form onSubmit={handleUpload} className="space-y-4">
              <DialogHeader>
                <DialogTitle>Submeter Novo Documento</DialogTitle>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <label className="text-sm font-bold">Título do Documento</label>
                  <Input name="title" placeholder="Ex: Planta de Estrutura - Bloco A" required />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-bold">Categoria</label>
                  <select 
                    name="category" 
                    className="w-full h-10 px-3 rounded-md border border-input bg-background text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                    required
                  >
                    {CATEGORIES.map(cat => (
                      <option key={cat.id} value={cat.id}>{cat.label}</option>
                    ))}
                  </select>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-bold">Ficheiro (PDF)</label>
                  <Input name="file" type="file" accept=".pdf" required className="cursor-pointer" />
                </div>
              </div>
              <DialogFooter>
                <Button type="submit" disabled={isUploading} className="w-full">
                  {isUploading ? "A processar..." : "Upload Documento"}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Stats Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {CATEGORIES.map(cat => (
          <div key={cat.id} className="bg-white border border-border p-4 rounded-2xl shadow-sm">
            <div className="flex items-center space-x-3 mb-2">
              <cat.icon className={cn("h-5 w-5", cat.color)} />
              <span className="text-[10px] uppercase tracking-widest font-bold text-muted-foreground">{cat.label}</span>
            </div>
            <p className="text-2xl font-black text-foreground">
              {documents.filter(d => d.category === cat.id).length}
            </p>
          </div>
        ))}
      </div>

      {/* Filters & Search */}
      <div className="bg-white border border-border p-4 rounded-2xl shadow-sm flex flex-col md:flex-row gap-4 items-center">
        <div className="relative flex-1 w-full">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input 
            placeholder="Procurar documentos..." 
            className="pl-10" 
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="flex items-center gap-2 w-full md:w-auto">
          <Filter className="h-4 w-4 text-muted-foreground" />
          <select 
            className="h-10 px-3 rounded-md border border-input bg-slate-50 text-xs font-bold ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring"
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
          >
            <option value="all">Todas as Categorias</option>
            {CATEGORIES.map(cat => (
              <option key={cat.id} value={cat.id}>{cat.label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Documents Table */}
      <div className="bg-white border border-border rounded-2xl shadow-sm overflow-hidden">
        {docsLoading ? (
          <div className="p-8 space-y-4">
            {Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} className="h-14 w-full rounded-xl" />
            ))}
          </div>
        ) : filteredDocs.length === 0 ? (
          <div className="p-20 text-center flex flex-col items-center">
            <div className="h-16 w-16 rounded-2xl bg-slate-50 flex items-center justify-center mb-4">
              <FileText className="h-8 w-8 text-gray-300" />
            </div>
            <h3 className="text-sm font-bold text-foreground">Sem documentos encontrados</h3>
            <p className="text-xs text-muted-foreground mt-1">
              {search || categoryFilter !== "all" 
                ? "Tenta ajustar os teus filtros de pequisa." 
                : "Ainda não foram submetidos documentos técnicos para este projecto."}
            </p>
          </div>
        ) : (
          <Table>
            <TableHeader className="bg-slate-50/50">
              <TableRow>
                <TableHead className="font-bold text-[10px] uppercase tracking-widest px-6">Documento</TableHead>
                <TableHead className="font-bold text-[10px] uppercase tracking-widest px-6">Categoria</TableHead>
                <TableHead className="font-bold text-[10px] uppercase tracking-widest px-6">Versão</TableHead>
                <TableHead className="font-bold text-[10px] uppercase tracking-widest px-6">Submetido Por</TableHead>
                <TableHead className="font-bold text-[10px] uppercase tracking-widest px-6">Data</TableHead>
                <TableHead className="text-right px-6"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredDocs.map((doc) => {
                const category = CATEGORIES.find(c => c.id === doc.category);
                return (
                  <TableRow key={doc.id} className="group hover:bg-slate-50/50 transition-colors">
                    <TableCell className="px-6 py-4">
                      <div className="flex items-center space-x-3">
                        <div className="h-9 w-9 rounded-lg bg-gray-100 flex items-center justify-center shrink-0 group-hover:bg-white transition-colors">
                          <FileText className="h-5 w-5 text-gray-500" />
                        </div>
                        <div>
                          <p className="text-sm font-bold text-foreground leading-none">{doc.title}</p>
                          <p className="text-[10px] text-muted-foreground mt-1 font-mono uppercase tracking-tighter">
                            {doc.file.split('/').pop()}
                          </p>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell className="px-6 py-4">
                      <span className={cn(
                        "inline-flex items-center px-2 py-1 rounded text-[10px] font-black uppercase tracking-tighter",
                        category?.color.replace('text-', 'bg-').replace('-600', '-100'),
                        category?.color
                      )}>
                        {category?.label}
                      </span>
                    </TableCell>
                    <TableCell className="px-6 py-4">
                      <div className="flex items-center space-x-1.5 font-bold text-foreground">
                        <History className="h-3.5 w-3.5 text-muted-foreground" />
                        <span className="text-sm">v{doc.version}.0</span>
                      </div>
                    </TableCell>
                    <TableCell className="px-6 py-4">
                      <span className="text-xs font-medium text-muted-foreground">{doc.uploaded_by_name}</span>
                    </TableCell>
                    <TableCell className="px-6 py-4">
                      <span className="text-xs font-medium text-muted-foreground">{formatDate(doc.created_at)}</span>
                    </TableCell>
                    <TableCell className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end space-x-2">
                        <a 
                          href={doc.file} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="h-8 w-8 flex items-center justify-center rounded-lg border border-border bg-white text-muted-foreground hover:text-primary hover:border-primary/30 transition-all opacity-0 group-hover:opacity-100"
                        >
                          <Download className="h-4 w-4" />
                        </a>
                        <button className="h-8 w-8 flex items-center justify-center rounded-lg border border-border bg-white text-muted-foreground hover:bg-gray-50 transition-all opacity-0 group-hover:opacity-100">
                          <MoreVertical className="h-4 w-4" />
                        </button>
                      </div>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        )}
      </div>
    </div>
  );
}
