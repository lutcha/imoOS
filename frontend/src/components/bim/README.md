# BIM Viewer Module

Módulo de visualização BIM (Building Information Modeling) para o ImoOS.

## Funcionalidades

- **Visualizador 3D**: Renderização de modelos IFC com Three.js + @thatopen/components
- **TreeView Hierárquico**: Navegação estruturada (IfcProject > IfcSite > IfcBuilding > ...)
- **Propriedades de Elementos**: Visualização de dados IFC e links para tasks/unidades
- **Color Coding**: Colorir elementos por status, fase, responsável ou tipo
- **Plano de Corte**: Criar cortes/plantas do modelo 3D
- **Upload IFC**: Carregar ficheiros .ifc diretamente

## Instalação

As dependências já foram instaladas:

```bash
npm install @thatopen/components @thatopen/fragments web-ifc three
npm install -D @types/three
```

## Estrutura

```
components/bim/
├── IFCViewer.tsx           # Viewer 3D principal
├── BIMViewerControls.tsx   # Controlos de navegação
├── ElementProperties.tsx   # Painel de propriedades
├── BIMTreeView.tsx         # Árvore de elementos
├── ColorBySelector.tsx     # Seletor de coloração
├── SectionPlane.tsx        # Plano de corte
└── index.ts                # Exportações

hooks/
├── useBIMModel.ts          # Gerir modelos IFC
├── useBIMElements.ts       # Listar elementos
└── useBIMSelection.ts      # Gerir seleção

lib/bim/
├── ifc-loader.ts           # Loader IFC.js
└── element-mapper.ts       # Mapear elementos → Tasks/Units

app/projects/[id]/
├── bim/page.tsx            # Página BIM 3D
└── plans/page.tsx          # Página Plantas 2D
```

## Uso

### Página BIM

Aceder a `/projects/{id}/bim` para visualizar o modelo 3D.

Layout:
- Esquerda (20%): TreeView de elementos
- Centro (60%): Viewer 3D
- Direita (20%): Propriedades + ColorBy

### Componentes

```tsx
import { IFCViewer, ElementProperties, BIMTreeView } from '@/components/bim';
import { useBIMModel, useBIMElements, useBIMSelection } from '@/hooks';

function MyBIMComponent() {
  const { model, loadModel } = useBIMModel(projectId);
  const { elements } = useBIMElements(model?.id);
  const { selected, selectElement } = useBIMSelection();

  return (
    <IFCViewer
      projectId={projectId}
      modelUrl={model?.url}
      selectedElements={Array.from(selected)}
      onElementSelect={(guid) => selectElement(guid)}
      colorBy="status"
    />
  );
}
```

### Upload de IFC

1. Arrastar ficheiro .ifc para a área de upload
2. Ou clicar em "Upload IFC" e selecionar ficheiro
3. O modelo é processado automaticamente

### Seleção de Elementos

- **Click**: Selecionar elemento
- **Ctrl+Click**: Seleção múltipla
- **Click na TreeView**: Sincronizado com viewer 3D

### Color Coding

Opções disponíveis:
- `none`: Cores originais do modelo
- `status`: Cores por estado da tarefa (verde/azul/vermelho)
- `phase`: Cores por fase de construção
- `responsible`: Cores por responsável
- `type`: Cores por tipo de elemento

## Integração com Backend

Endpoints necessários:

```
GET  /api/v1/bim/models/?project={id}
POST /api/v1/bim/models/upload-url/
POST /api/v1/bim/models/{id}/process/
GET  /api/v1/bim/models/{id}/download

GET  /api/v1/bim/elements/?model={id}
GET  /api/v1/bim/elements/{guid}/
PATCH /api/v1/bim/elements/{guid}/
POST /api/v1/bim/elements/bulk-update/

GET  /api/v1/bim/elements/tree/?model={id}
```

## Mapeamento Elementos ↔ Tarefas/Unidades

O sistema permite associar elementos BIM a:
- **Tarefas de construção**: Para acompanhamento de progresso
- **Unidades habitacionais**: Para gestão de vendas

Use as funções em `lib/bim/element-mapper.ts`:

```ts
import { autoMapElements, createTaskMapping } from '@/lib/bim/element-mapper';

// Mapeamento automático por regras
const mapped = autoMapElements(elements, rules, tasks, units);

// Mapeamento manual
const mapping = createTaskMapping(elementGuid, taskId, taskData);
```

## Limitações

- **Desktop apenas**: Viewer 3D não otimizado para mobile
- **Formatos**: Apenas IFC (Industry Foundation Classes)
- **Tamanho**: Modelos muito grandes (>100MB) podem demorar a carregar

## Próximos Passos

- [ ] Implementar timeline 4D (visualização temporal)
- [ ] Adicionar medições no modelo 3D
- [ ] Suporte a anotações/markups
- [ ] Sincronização bidirecional com tasks
- [ ] Visualização de conflitos (clash detection)
