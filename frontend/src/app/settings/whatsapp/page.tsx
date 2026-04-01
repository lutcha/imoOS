"use client";

import { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { AlertCircle, CheckCircle2, MessageSquare, Plus, RefreshCw, XCircle } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

// Temporary mock types until we connect the real API
type WhatsAppTemplate = {
  id: string;
  name: string;
  template_id_meta: string;
  language: string;
  is_active: boolean;
};

type WhatsAppMessage = {
  id: string;
  lead_name: string;
  phone: string;
  template_name: string;
  status: "SENT" | "DELIVERED" | "READ" | "FAILED";
  sent_at: string;
  error?: string;
};

export default function WhatsAppSettingsPage() {
  const [templates, setTemplates] = useState<WhatsAppTemplate[]>([]);
  const [messages, setMessages] = useState<WhatsAppMessage[]>([]);
  const [loading, setLoading] = useState(true);

  // In a real implementation this would fetch from /api/settings/whatsapp/
  useEffect(() => {
    // Mock data for initial UI setup
    setTimeout(() => {
      setTemplates([
        { id: "1", name: "novo_lead", template_id_meta: "novo_lead_v1", language: "pt_PT", is_active: true },
        { id: "2", name: "lembrete_visita", template_id_meta: "visit_reminder_v2", language: "pt_PT", is_active: true },
      ]);
      setMessages([
        { id: "101", lead_name: "João Silva", phone: "+351912345678", template_name: "novo_lead", status: "READ", sent_at: new Date().toISOString() },
        { id: "102", lead_name: "Maria Costa", phone: "+2389912345", template_name: "lembrete_visita", status: "DELIVERED", sent_at: new Date(Date.now() - 3600000).toISOString() },
        { id: "103", lead_name: "Pedro Santos", phone: "+351923456789", template_name: "novo_lead", status: "FAILED", error: "Opt-out", sent_at: new Date(Date.now() - 86400000).toISOString() },
      ]);
      setLoading(false);
    }, 1000);
  }, []);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "READ": return <Badge className="bg-blue-500 hover:bg-blue-600">Lido</Badge>;
      case "DELIVERED": return <Badge className="bg-green-500 hover:bg-green-600">Entregue</Badge>;
      case "SENT": return <Badge variant="secondary">Enviado</Badge>;
      case "FAILED": return <Badge variant="destructive">Falhou</Badge>;
      default: return <Badge variant="outline">{status}</Badge>;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "READ": return <CheckCircle2 className="h-4 w-4 text-blue-500" />;
      case "DELIVERED": return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case "SENT": return <CheckCircle2 className="h-4 w-4 text-gray-500" />;
      case "FAILED": return <XCircle className="h-4 w-4 text-red-500" />;
      default: return null;
    }
  };

  return (
    <div className="flex-1 space-y-4 p-8 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">WhatsApp Automação</h2>
        <div className="flex items-center space-x-2">
          <Button variant="outline" size="sm" onClick={() => setLoading(true)}>
            <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            Actualizar
          </Button>
        </div>
      </div>

      <Alert>
        <MessageSquare className="h-4 w-4" />
        <AlertTitle>Configuração Meta Cloud API</AlertTitle>
        <AlertDescription>
          Esta página permite gerir os templates oficiais aprovados pela Meta para envio de mensagens estruturadas (HSM) e visualizar o histórico de envios e opt-outs para efeitos de auditoria (LGPD / Lei 133/V/2019).
        </AlertDescription>
      </Alert>

      <div className="grid gap-4 md:grid-cols-2">
        <Card className="col-span-1">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <div className="space-y-1">
              <CardTitle>Templates Activos</CardTitle>
              <CardDescription>
                Modelos pré-aprovados pela Meta
              </CardDescription>
            </div>
            <Button size="sm" className="h-8">
              <Plus className="mr-2 h-4 w-4" />
              Sincronizar Meta
            </Button>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="space-y-2">
                 <div className="h-10 bg-muted animate-pulse rounded"></div>
                 <div className="h-10 bg-muted animate-pulse rounded"></div>
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Nome Interno</TableHead>
                    <TableHead>ID Meta</TableHead>
                    <TableHead>Idioma</TableHead>
                    <TableHead className="text-right">Estado</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {templates.map((tpl) => (
                    <TableRow key={tpl.id}>
                      <TableCell className="font-medium">{tpl.name}</TableCell>
                      <TableCell className="text-xs text-muted-foreground">{tpl.template_id_meta}</TableCell>
                      <TableCell>{tpl.language}</TableCell>
                      <TableCell className="text-right">
                        {tpl.is_active ? (
                          <Badge variant="default" className="bg-green-600 hover:bg-green-700">Activo</Badge>
                        ) : (
                          <Badge variant="secondary">Inactivo</Badge>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                  {templates.length === 0 && (
                     <TableRow>
                      <TableCell colSpan={4} className="text-center text-muted-foreground py-4">Nenhum template configurado</TableCell>
                     </TableRow>
                  )}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        <Card className="col-span-1">
           <CardHeader>
            <CardTitle>Estatísticas (Últimos 30 Dias)</CardTitle>
            <CardDescription>Resumo de envios por template</CardDescription>
           </CardHeader>
           <CardContent>
             <div className="space-y-4">
                 <div className="flex items-center">
                    <div className="flex items-center space-x-2 w-full">
                       <MessageSquare className="h-4 w-4 text-muted-foreground" />
                       <span className="text-sm font-medium">novo_lead</span>
                       <div className="ml-auto text-sm text-right">
                           <span className="font-bold">45</span> envios (98% lidos)
                       </div>
                    </div>
                 </div>
                 <div className="flex items-center">
                    <div className="flex items-center space-x-2 w-full">
                       <MessageSquare className="h-4 w-4 text-muted-foreground" />
                       <span className="text-sm font-medium">lembrete_visita</span>
                       <div className="ml-auto text-sm text-right">
                           <span className="font-bold">12</span> envios (100% lidos)
                       </div>
                    </div>
                 </div>
                  <div className="flex items-center mt-6 pt-6 border-t">
                    <div className="flex items-center space-x-2 w-full">
                       <AlertCircle className="h-4 w-4 text-orange-500" />
                       <span className="text-sm font-medium">Opt-outs Registados</span>
                       <div className="ml-auto text-sm font-bold text-orange-500 text-right">
                           2
                       </div>
                    </div>
                 </div>
             </div>
           </CardContent>
        </Card>

        <Card className="col-span-2">
          <CardHeader>
            <CardTitle>Histórico Recente</CardTitle>
            <CardDescription>
              Registo de auditoria de interacções
            </CardDescription>
          </CardHeader>
          <CardContent>
             {loading ? (
              <div className="space-y-2">
                 <div className="h-10 bg-muted animate-pulse rounded"></div>
                 <div className="h-10 bg-muted animate-pulse rounded"></div>
                 <div className="h-10 bg-muted animate-pulse rounded"></div>
              </div>
            ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Data/Hora</TableHead>
                  <TableHead>Contacto</TableHead>
                  <TableHead>Template</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead>Detalhes</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {messages.map((msg) => (
                  <TableRow key={msg.id}>
                    <TableCell className="text-sm">
                        {new Date(msg.sent_at).toLocaleString('pt-PT', { day: '2-digit', month: '2-digit', hour: '2-digit', minute:'2-digit' })}
                    </TableCell>
                    <TableCell>
                        <div className="font-medium">{msg.lead_name}</div>
                        <div className="text-xs text-muted-foreground">{msg.phone}</div>
                    </TableCell>
                    <TableCell>{msg.template_name}</TableCell>
                    <TableCell>
                        <div className="flex items-center space-x-2">
                            {getStatusIcon(msg.status)}
                            {getStatusBadge(msg.status)}
                        </div>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                        {msg.error ? (
                             <span className="text-red-500 flex items-center"><XCircle className="h-3 w-3 mr-1"/> {msg.error}</span>
                        ): '-'}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
