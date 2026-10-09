# Assets

Store acquisition instructions and model provenance in Git; keep downloaded
weights under ignored `assets/models/` or the runtime's model store. Owner
acquisition has downloaded the initial model assets locally.

See [model inventory](../docs/DISCLOSURES.md) and [preparation](../docs/PREPARATION.md).
Record source, licence, exact version/hash and actual size. Bundle application
fonts/icons locally when selected and record their licences. Do not commit
private recordings or the participant briefing PDF.

[Runtime manifest](runtime-manifest.json) pins candidate acquisition sources.
Owner preparation writes actual sizes/hashes to ignored `.runtime/assets-receipt.json`;
the Python checker validates those local bytes. Qwen, EfficientDet and Face Landmarker weights are
present locally; genuine camera/matching and earlier bounded Qwen inference ran. Full
quality/offline acceptance remains pending. Tracked acquired hashes are
in the manifest; they are distinct from independent publisher checksums.

[Scene manifest](scene-models.json) lists versioned face and historical optional
pose assets. Face acquisition is recorded in ignored `.runtime/scene-assets.json`;
pose is not enabled in the current demo. LBPH comes from the installed OpenCV
contrib package and trains on the local parent-labeled example; it has no separately
downloaded recognition weights. Private reference images remain in ignored SQLite.
