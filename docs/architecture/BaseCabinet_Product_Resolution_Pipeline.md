# Base Cabinet Product Resolution Pipeline

## 1. Purpose

`BaseCabinetSpecification` is the canonical product definition for a base cabinet.

It must not be forced entirely into `CabinetParams` because `CabinetParams` is only a partial input contract for the current cabinet system. Some fields are direct engineering inputs, but others represent product structure, manufacturing intent, or hardware selection that require dedicated resolvers or later domain consumers.

The resolution pipeline exists to preserve meaning, avoid semantic overload, and prevent unsupported fields from being guessed or collapsed into unrelated parameters.

## 2. Resolution Flow

BaseCabinetSpecification  
↓  
Product Resolution Pipeline  
↓  
Engineering Resolution  
↓  
Manufacturing Intent Resolution  
↓  
Hardware Resolution  
↓  
Cost/Commercial Resolution later

## 3. Field Routing Table

| Field | Owner | Target Resolver/Consumer | Current Status | Action |
| --- | --- | --- | --- | --- |
| `width_mm` | Engineering / Product Specification | `CabinetParams.width` | Supported now | Map directly |
| `height_mm` | Engineering / Product Specification | `CabinetParams.height` | Supported now | Map directly |
| `depth_mm` | Engineering / Product Specification | `CabinetParams.depth` | Supported now | Map directly |
| `door_count` | Product Structure | Future `DoorStructureResolver` | Deferred | Keep in metadata until resolver exists |
| `shelf_count` | Product Structure | Future `ShelfStructureResolver` | Deferred | Keep in metadata until resolver exists |
| `has_back_panel` | Product Structure / Manufacturing Intent | Future `BackPanelIntentResolver` | Deferred | Keep in metadata until resolver exists |
| `edge_banding_required` | Manufacturing Intent | Future `EdgeBandingIntentResolver` | Deferred | Keep in metadata until resolver exists |
| `toe_kick_required` | Product Structure | Future `ToeKickStructureResolver` | Deferred | Keep in metadata until resolver exists |
| `hinge_family` | Hardware Selection | `CabinetParams.hinge_sku` | Supported now | Map directly |
| `drawer_family` | Hardware Selection | Future `DrawerFamilyResolver` | Deferred / unsupported | Keep in metadata until proper resolver exists |

## 4. Allowed Direct `CabinetParams` Mappings

Only the following direct mappings are supported at this stage:

- `width_mm -> CabinetParams.width`
- `height_mm -> CabinetParams.height`
- `depth_mm -> CabinetParams.depth`
- `hinge_family -> CabinetParams.hinge_sku`

## 5. Deferred Fields

The following fields must remain in metadata until proper resolvers exist:

- `door_count`
- `shelf_count`
- `has_back_panel`
- `edge_banding_required`
- `toe_kick_required`
- `drawer_family`

These values are part of the product definition and should not be guessed into unrelated `CabinetParams` fields.

## 6. Future Resolvers

The following future resolvers are documented for the resolution pipeline but are not implemented here:

- `DoorStructureResolver`
- `ShelfStructureResolver`
- `BackPanelIntentResolver`
- `EdgeBandingIntentResolver`
- `ToeKickStructureResolver`
- `DrawerFamilyResolver`

## 7. Boundary Rules

- `CabinetParams` must not become a product model.
- Product structure must not be encoded into unrelated fields.
- Manufacturing intent must not be encoded into engineering flags.
- Adapter must only map evidence-based fields.
- Unsupported fields must be preserved, not guessed.

## 8. Conclusion

`BaseCabinetSpecification` should be resolved through a layered product resolution pipeline rather than being flattened wholesale into `CabinetParams`.

This preserves semantic correctness and keeps future resolver work isolated from existing engineering inputs.
