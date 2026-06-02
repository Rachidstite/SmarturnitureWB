Current State:
- SceneGraph owns DRAWER_FACE only.
- DrawerBuilder owns physical drawer box parts.
- Manufacturing recognizes DRAWER_FACE only.

Problem:
- Drawer geometry has multiple owners.
- Manufacturing output diverges from rendered geometry.

Decision:
- SceneGraph becomes the single owner of all drawer components.

Target Roles:
- DRAWER_FACE
- DRAWER_BOX_SIDE
- DRAWER_BOX_BACK
- DRAWER_BOX_BOTTOM
- DRAWER_BOX_FRONT

Migration Strategy:
1. Add SceneGraph nodes.
2. Teach Renderer to consume nodes.
3. Verify runtime parity.
4. Remove duplicated ownership from DrawerBuilder.

Status:
Approved
