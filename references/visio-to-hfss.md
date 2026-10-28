# Visio-to-HFSS translation

## Geometry intake

`.vsdx` is an OPC/ZIP package. The helper extracts page XML, shape transforms, geometry rows, text, colors, and embedded media without requiring Microsoft Visio. Use the extracted JSON as evidence, then compare it with the rendered drawing or user-provided screenshot.

For each physical layer, establish:

- drawing units and scale;
- the HFSS plane/height;
- conductor/dielectric material and thickness;
- whether a shape is positive copper, a void, a substrate outline, a reference plane, or annotation;
- group transforms, rotation, mirroring, and nested shape transforms;
- shared edges that must remain electrically connected.

Do not use screenshot pixels as millimetres unless the user explicitly defines that scale. Prefer Visio ShapeSheet values, dimension annotations, or a known board outline.

## Color mapping

Color is project-specific input, not a universal rule. Preserve mappings explicitly supplied by the user. A common layout may use, for example:

- light orange: bottom conductor;
- gray: ground conductor;
- white: void cut from ground;
- dark orange: top conductor.

Confirm ambiguous antialiased colors, gradients, transparency, or stacked objects before modeling. Ignore arrows, circles, labels, page borders, and other markup unless the user identifies them as geometry.

## Coordinate conversion

Visio uses page coordinates with its own origin and may use inches internally. HFSS commonly uses millimetres. Apply one documented transform from page coordinates to model coordinates:

`HFSS_x = scale * (Visio_x - origin_x)`

`HFSS_y = scale * (Visio_y - origin_y)`

Apply group-local transforms before the page transform. Keep sufficient precision during extraction; round only user-facing dimensions.

## Modeling strategy

- Rectilinear copper: create covered polylines or rectangles, unite pieces that are physically one conductor, and thicken by copper thickness if volumetric copper is required.
- Ground voids: subtract void tools from the ground body and delete tools after Boolean completion.
- Substrate: use a solid box with the requested dielectric properties and loss tangent.
- Layer Z positions: derive from named variables such as `SubH`, `CuT`, and `GndZ`.
- Parameterized features: rebuild the affected polygon with variable expressions rather than scaling a frozen import when the user needs dimension tuning.

After construction, export top, bottom, and isometric views from HFSS and compare them against the source before assigning ports or solving.
