# mxGraph XML Templates

Starter templates for each diagram type. Adapt these to the actual project. All templates follow drawio-mcp conventions: no XML comments, proper cell IDs, adequate spacing.

## Base Structure

Every diagram starts with this wrapper:

```xml
<mxGraphModel dx="1422" dy="762" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" math="0" shadow="0">
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
    [diagram cells starting from id="2" go here]
  </root>
</mxGraphModel>
```

## ERD Template

Table node with columns:

```xml
<mxCell id="2" value="&lt;b&gt;users&lt;/b&gt;" style="shape=table;startSize=30;container=1;collapsible=0;childLayout=tableLayout;fixedRows=1;rowLines=0;fontStyle=1;align=center;resizeLast=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
  <mxGeometry x="40" y="40" width="220" height="150" as="geometry"/>
</mxCell>
<mxCell id="3" value="" style="shape=tableRow;horizontal=0;startSize=0;swimlaneHead=0;swimlaneBody=0;fillColor=#dae8fc;collapsible=0;dropTarget=0;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;fontSize=12;top=0;left=0;right=0;bottom=1;" vertex="1" parent="2">
  <mxGeometry y="30" width="220" height="30" as="geometry"/>
</mxCell>
<mxCell id="4" value="PK" style="shape=partialRectangle;connectable=0;fillColor=#dae8fc;top=0;left=0;bottom=0;right=1;fontStyle=1;overflow=hidden;" vertex="1" parent="3">
  <mxGeometry width="40" height="30" as="geometry"/>
</mxCell>
<mxCell id="5" value="id INTEGER" style="shape=partialRectangle;connectable=0;fillColor=#dae8fc;top=0;left=0;bottom=0;right=0;align=left;spacingLeft=6;overflow=hidden;" vertex="1" parent="3">
  <mxGeometry x="40" width="180" height="30" as="geometry"/>
</mxCell>
```

FK relationship edge:

```xml
<mxCell id="100" style="edgeStyle=entityRelationEdgeStyle;fontSize=12;strokeColor=#6c8ebf;" edge="1" source="20" target="3" parent="1">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```

## Flowchart Template

Start/end node (rounded):

```xml
<mxCell id="2" value="Start" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;arcSize=50;" vertex="1" parent="1">
  <mxGeometry x="340" y="40" width="120" height="40" as="geometry"/>
</mxCell>
```

Action step:

```xml
<mxCell id="3" value="Validate form data" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;" vertex="1" parent="1">
  <mxGeometry x="310" y="120" width="180" height="50" as="geometry"/>
</mxCell>
```

Decision diamond:

```xml
<mxCell id="4" value="Valid?" style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;" vertex="1" parent="1">
  <mxGeometry x="340" y="210" width="120" height="60" as="geometry"/>
</mxCell>
```

Arrow edge:

```xml
<mxCell id="10" value="Yes" style="edgeStyle=orthogonalEdgeStyle;rounded=1;" edge="1" source="4" target="5" parent="1">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```

## Sequence Diagram Template

Lifeline header:

```xml
<mxCell id="2" value="Browser" style="shape=umlLifeline;perimeter=lifelinePerimeter;whiteSpace=wrap;html=1;container=1;collapsible=0;recursiveResize=0;outlineConnect=0;fillColor=#fff2cc;strokeColor=#d6b656;size=40;" vertex="1" parent="1">
  <mxGeometry x="80" y="40" width="100" height="400" as="geometry"/>
</mxCell>
```

Activation bar:

```xml
<mxCell id="3" value="" style="html=1;points=[];perimeter=orthogonalPerimeter;outlineConnect=0;fillColor=#d5e8d4;strokeColor=#82b366;" vertex="1" parent="2">
  <mxGeometry x="45" y="80" width="10" height="60" as="geometry"/>
</mxCell>
```

Message arrow:

```xml
<mxCell id="10" value="POST /login" style="html=1;verticalAlign=bottom;endArrow=block;rounded=0;" edge="1" parent="1" source="3" target="7">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```

Return arrow (dashed):

```xml
<mxCell id="11" value="302 Redirect" style="html=1;verticalAlign=bottom;endArrow=open;dashed=1;endSize=8;rounded=0;" edge="1" parent="1" source="7" target="3">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```

## C4 Container Template

Container box:

```xml
<mxCell id="2" value="&lt;b&gt;Flask Web App&lt;/b&gt;&lt;br&gt;Python 3.x" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=13;verticalAlign=middle;" vertex="1" parent="1">
  <mxGeometry x="200" y="160" width="200" height="80" as="geometry"/>
</mxCell>
```

Database cylinder:

```xml
<mxCell id="3" value="&lt;b&gt;PostgreSQL&lt;/b&gt;&lt;br&gt;User data, deals, leads" style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;" vertex="1" parent="1">
  <mxGeometry x="240" y="360" width="120" height="80" as="geometry"/>
</mxCell>
```

External service (cloud):

```xml
<mxCell id="4" value="&lt;b&gt;drawio-mcp&lt;/b&gt;&lt;br&gt;Diagram rendering" style="ellipse;shape=cloud;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontSize=12;" vertex="1" parent="1">
  <mxGeometry x="500" y="160" width="180" height="80" as="geometry"/>
</mxCell>
```

User/actor:

```xml
<mxCell id="5" value="Developer" style="shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;outlineConnect=0;fillColor=#e1d5e7;strokeColor=#9673a6;" vertex="1" parent="1">
  <mxGeometry x="270" y="20" width="30" height="55" as="geometry"/>
</mxCell>
```

System boundary:

```xml
<mxCell id="6" value="CRM Application" style="rounded=1;whiteSpace=wrap;html=1;dashed=1;fillColor=none;strokeColor=#666666;fontSize=14;fontStyle=1;verticalAlign=top;align=left;spacingLeft=10;spacingTop=5;" vertex="1" parent="1">
  <mxGeometry x="120" y="120" width="360" height="340" as="geometry"/>
</mxCell>
```

## Dependency Graph Template

Module node:

```xml
<mxCell id="2" value="routes/deals.py" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;" vertex="1" parent="1">
  <mxGeometry x="200" y="40" width="160" height="40" as="geometry"/>
</mxCell>
```

Dependency edge:

```xml
<mxCell id="10" value="imports" style="edgeStyle=orthogonalEdgeStyle;rounded=1;endArrow=block;endFill=1;strokeColor=#666666;" edge="1" source="2" target="3" parent="1">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```

Cluster (directory grouping):

```xml
<mxCell id="20" value="routes/" style="rounded=1;whiteSpace=wrap;html=1;dashed=1;fillColor=none;strokeColor=#82b366;fontSize=12;fontStyle=1;verticalAlign=top;align=left;spacingLeft=8;" vertex="1" parent="1">
  <mxGeometry x="160" y="20" width="280" height="200" as="geometry"/>
</mxCell>
```

## Layout Guidelines

- **Minimum spacing**: 40px between nodes, 80px between clusters
- **Canvas size**: start with 1169x827 (A4 landscape), expand if needed
- **Title placement**: top-left, font size 16, bold
- **Legend placement**: bottom-right corner for color legend
- **Flow direction**: top-to-bottom for flowcharts, left-to-right for sequences
- **ID numbering**: start from 2 (0 and 1 are reserved), increment sequentially