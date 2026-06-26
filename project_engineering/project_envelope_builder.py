from project_engineering.project_envelope import ProjectEnvelope


def build_project_envelope(
    envelopes: list[ProjectEnvelope],
) -> ProjectEnvelope:
    if not envelopes:
        raise ValueError("envelopes must not be empty")

    return ProjectEnvelope(
        x_min=min(envelope.x_min for envelope in envelopes),
        y_min=min(envelope.y_min for envelope in envelopes),
        z_min=min(envelope.z_min for envelope in envelopes),
        x_max=max(envelope.x_max for envelope in envelopes),
        y_max=max(envelope.y_max for envelope in envelopes),
        z_max=max(envelope.z_max for envelope in envelopes),
        source="project-envelope-builder",
    )
